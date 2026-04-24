<?php

namespace App\Services;

use App\Models\SoilData;
use App\Models\Zone;
use App\Models\ZoneCareAdvice;
use Illuminate\Http\Client\PendingRequest;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\Http;

class AiAdvisorService
{
    public function __construct(
        protected ZoneAnalyticsService $analytics
    ) {
    }

    public function predictZone(Zone $zone, Collection $samples): array
    {
        $payload = [
            'zone_id' => (string) $zone->id,
            'zone_name' => $zone->name,
            'current_crop' => $zone->active_crop,
            'samples' => $samples->map(function (SoilData $sample, int $index) {
                return [
                    'point_id' => $sample->point_label ?: 'PT-'.str_pad((string) ($index + 1), 2, '0', STR_PAD_LEFT),
                    'ph' => (float) $sample->ph,
                    'nitrogen' => (float) $sample->nitrogen,
                    'phosphorus' => (float) $sample->phosphorus,
                    'potassium' => (float) $sample->potassium,
                    'soil_moisture' => $sample->soil_moisture !== null ? (float) $sample->soil_moisture : null,
                    'sampled_at' => optional($sample->sampled_at ?? $sample->created_at)?->toIso8601String(),
                ];
            })->values()->all(),
        ];

        try {
            $response = $this->client()->post('/predict/zone', $payload)->throw()->json();

            return $this->normalizePredictionResponse($response, $zone, $samples);
        } catch (\Throwable $exception) {
            return $this->fallbackZonePrediction($zone, $samples, $exception->getMessage());
        }
    }

    public function generateCareAdvice(Zone $zone, Collection $history, bool $force = false): ?ZoneCareAdvice
    {
        $latestAdvice = $zone->careAdvices()->first();

        if (! $force && $latestAdvice && $latestAdvice->generated_at?->gte(now()->subHour())) {
            return $latestAdvice;
        }

        if ($history->isEmpty() || blank($zone->active_crop)) {
            return $latestAdvice;
        }

        $payload = [
            'zone_id' => (string) $zone->id,
            'zone_name' => $zone->name,
            'current_crop' => $zone->active_crop,
            'history_window_minutes' => 60,
            'nutrient_history' => $history->map(function (SoilData $sample) {
                return [
                    'timestamp' => optional($sample->sampled_at ?? $sample->created_at)?->toIso8601String(),
                    'ph' => (float) $sample->ph,
                    'nitrogen' => (float) $sample->nitrogen,
                    'phosphorus' => (float) $sample->phosphorus,
                    'potassium' => (float) $sample->potassium,
                    'soil_moisture' => $sample->soil_moisture !== null ? (float) $sample->soil_moisture : null,
                ];
            })->values()->all(),
            'current_snapshot' => $this->analytics->aggregateSamples($history),
        ];

        try {
            $response = $this->client()->post('/advice/care', $payload)->throw()->json();
        } catch (\Throwable $exception) {
            $response = $this->fallbackCareAdvice($zone, $history, $exception->getMessage());
        }

        return ZoneCareAdvice::create([
            'zone_id' => $zone->id,
            'crop_name' => $zone->active_crop,
            'advice_summary' => $response['summary'],
            'urgency_level' => $response['urgency'],
            'recommendations' => $response['recommendations'],
            'nutrient_snapshot' => $payload['current_snapshot'],
            'raw_response' => $response,
            'generated_at' => now(),
            'time_window_minutes' => 60,
        ]);
    }

    protected function normalizePredictionResponse(array $response, Zone $zone, Collection $samples): array
    {
        $primary = $response['prediction']['recommended_label'] ?? 'Belum tersedia';
        $confidence = (float) ($response['prediction']['confidence'] ?? 0);
        $topK = collect($response['prediction']['top_k'] ?? [])
            ->map(function (array $item, int $index) {
                return [
                    'rank' => $index + 1,
                    'label' => $item['label'] ?? 'Tidak diketahui',
                    'probability' => round((float) ($item['probability'] ?? 0), 4),
                    'match_rate' => (int) round(((float) ($item['probability'] ?? 0)) * 100),
                ];
            })
            ->skip(1)
            ->values();

        $zone->update([
            'latest_recommendation_label' => $primary,
            'latest_recommendation_confidence' => round($confidence * 100, 2),
        ]);

        return [
            'zone' => $zone,
            'aggregated_features' => $response['aggregated_features'] ?? $this->analytics->aggregateSamples($samples),
            'primary_recommendation' => [
                'label' => $primary,
                'confidence' => round($confidence * 100, 1),
                'reasoning' => $response['prediction']['reasoning'] ?? 'Model menilai profil zona paling dekat dengan pola tanam ini.',
                'water_need' => $response['prediction']['water_need'] ?? 'Sedang',
                'harvest_time_days' => $response['prediction']['harvest_time_days'] ?? 90,
                'risk_factor' => $response['prediction']['risk_factor'] ?? 'Menengah',
                'suitability_score' => $response['prediction']['suitability_score'] ?? round($confidence * 100, 1),
            ],
            'alternatives' => $topK,
            'warnings' => $response['warnings'] ?? [],
            'model_info' => $response['model_info'] ?? ['model_name' => 'external-zone-model'],
        ];
    }

    protected function fallbackZonePrediction(Zone $zone, Collection $samples, ?string $error = null): array
    {
        $aggregate = $this->analytics->aggregateSamples($samples);
        $ph = $aggregate['ph']['mean'] ?? 6.5;
        $nitrogen = $aggregate['nitrogen']['mean'] ?? 80;
        $phosphorus = $aggregate['phosphorus']['mean'] ?? 35;
        $potassium = $aggregate['potassium']['mean'] ?? 75;
        $moisture = $aggregate['soil_moisture']['mean'] ?? 35;

        $profiles = collect([
            ['label' => 'Jagung', 'ph' => 6.4, 'n' => 95, 'p' => 40, 'k' => 80, 'm' => 38, 'water_need' => 'Sedang', 'harvest' => 95],
            ['label' => 'Padi', 'ph' => 6.2, 'n' => 100, 'p' => 45, 'k' => 85, 'm' => 55, 'water_need' => 'Tinggi', 'harvest' => 110],
            ['label' => 'Kedelai', 'ph' => 6.5, 'n' => 75, 'p' => 38, 'k' => 70, 'm' => 34, 'water_need' => 'Sedang', 'harvest' => 85],
            ['label' => 'Cabai', 'ph' => 6.4, 'n' => 85, 'p' => 32, 'k' => 90, 'm' => 36, 'water_need' => 'Sedang', 'harvest' => 100],
        ])->map(function (array $profile) use ($ph, $nitrogen, $phosphorus, $potassium, $moisture) {
            $distance = abs($profile['ph'] - $ph) * 12
                + abs($profile['n'] - $nitrogen) / 6
                + abs($profile['p'] - $phosphorus) / 4
                + abs($profile['k'] - $potassium) / 6
                + abs($profile['m'] - $moisture) / 5;

            $score = max(0.2, 1 - min($distance / 35, 0.75));

            return [
                'label' => $profile['label'],
                'probability' => $score,
                'water_need' => $profile['water_need'],
                'harvest' => $profile['harvest'],
            ];
        })->sortByDesc('probability')->values();

        $primary = $profiles->first();

        $zone->update([
            'latest_recommendation_label' => $primary['label'],
            'latest_recommendation_confidence' => round($primary['probability'] * 100, 2),
        ]);

        return [
            'zone' => $zone,
            'aggregated_features' => $aggregate,
            'primary_recommendation' => [
                'label' => $primary['label'],
                'confidence' => round($primary['probability'] * 100, 1),
                'reasoning' => 'Fallback lokal menggunakan kedekatan profil pH, NPK, dan kelembapan terhadap profil referensi tanaman.',
                'water_need' => $primary['water_need'],
                'harvest_time_days' => $primary['harvest'],
                'risk_factor' => ($phosphorus < 20 || $ph < 6) ? 'Perlu intervensi' : 'Terkendali',
                'suitability_score' => round($primary['probability'] * 100, 1),
            ],
            'alternatives' => $profiles->map(function (array $item, int $index) {
                return [
                    'rank' => $index + 1,
                    'label' => $item['label'],
                    'probability' => round($item['probability'], 4),
                    'match_rate' => (int) round($item['probability'] * 100),
                ];
            })->skip(1)->values()->all(),
            'warnings' => array_values(array_filter([
                $error ? 'Service model utama tidak tersedia. Sistem memakai fallback lokal.' : null,
                $samples->count() < 4 ? 'Jumlah titik sampling masih rendah untuk hasil zona yang lebih stabil.' : null,
            ])),
            'model_info' => [
                'model_name' => 'fallback-zone-profile',
            ],
        ];
    }

    protected function fallbackCareAdvice(Zone $zone, Collection $history, ?string $error = null): array
    {
        $aggregate = $this->analytics->aggregateSamples($history);
        $recommendations = [];
        $urgency = 'medium';

        if (($aggregate['soil_moisture']['mean'] ?? 100) < 30) {
            $recommendations[] = [
                'title' => 'Atur irigasi bertahap',
                'detail' => 'Kelembapan turun. Jalankan irigasi ringan 10-15 menit dan evaluasi ulang 30 menit sesudahnya.',
                'priority' => 'high',
            ];
            $urgency = 'high';
        }

        if (($aggregate['ph']['mean'] ?? 6.5) < 6) {
            $recommendations[] = [
                'title' => 'Evaluasi pengapuran ringan',
                'detail' => 'pH cenderung asam. Pertimbangkan koreksi bertahap agar penyerapan fosfor tidak terhambat.',
                'priority' => 'medium',
            ];
        }

        if (($aggregate['phosphorus']['mean'] ?? 999) < 20) {
            $recommendations[] = [
                'title' => 'Prioritaskan sumber fosfor',
                'detail' => 'Nilai fosfor rendah. Sesuaikan pemupukan dasar atau susulan dengan fase tanaman '.$zone->active_crop.'.',
                'priority' => 'high',
            ];
            $urgency = 'high';
        }

        if ($recommendations === []) {
            $recommendations[] = [
                'title' => 'Pertahankan pemantauan rutin',
                'detail' => 'Profil hara relatif stabil. Lanjutkan observasi visual dan sampling berkala.',
                'priority' => 'low',
            ];
            $urgency = 'low';
        }

        return [
            'summary' => 'Fallback lokal menyarankan tindakan berdasarkan tren 1 jam terakhir untuk tanaman '.$zone->active_crop.'.',
            'urgency' => $urgency,
            'recommendations' => $recommendations,
            'provider' => 'local-fallback',
            'warning' => $error ? 'Vertex AI tidak tersedia: '.$error : null,
        ];
    }

    protected function client(): PendingRequest
    {
        return Http::baseUrl((string) config('services.ai_advisor.base_url'))
            ->timeout((int) config('services.ai_advisor.timeout', 15))
            ->acceptJson()
            ->asJson();
    }
}
