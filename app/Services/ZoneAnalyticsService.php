<?php

namespace App\Services;

use App\Models\SoilData;
use App\Models\Zone;
use Carbon\Carbon;
use Illuminate\Contracts\Pagination\LengthAwarePaginator;
use Illuminate\Support\Collection;

class ZoneAnalyticsService
{
    public function buildDashboardSummary(): array
    {
        $zones = Zone::with(['soilData' => fn ($query) => $query->latest('sampled_at')])->get();
        $samplesLast24Hours = SoilData::where('sampled_at', '>=', now()->subDay())->count();
        $activeZones = $zones->filter(fn (Zone $zone) => filled($zone->active_crop))->count();
        $readyZones = $zones->filter(fn (Zone $zone) => $this->sampleCount($zone) >= $zone->sample_target_count)->count();

        return [
            'zones' => $zones->map(fn (Zone $zone) => $this->buildZoneCard($zone))->values(),
            'stats' => [
                'total_zones' => $zones->count(),
                'active_zones' => $activeZones,
                'latest_samples' => $samplesLast24Hours,
                'new_ai_recommendations' => $zones->filter(fn (Zone $zone) => filled($zone->latest_recommendation_label))->count(),
                'ready_zones' => $readyZones,
            ],
            'telemetry' => $this->buildTelemetrySummary($zones),
            'trend_chart' => $this->buildTrendChart(),
            'recent_activity' => $this->recentActivity(),
        ];
    }

    public function buildZoneCard(Zone $zone): array
    {
        $sampleCount = $this->sampleCount($zone);
        $aggregate = $this->aggregateSamples($zone->soilData);
        $status = $this->deriveZoneStatus($zone, $sampleCount);

        return [
            'id' => $zone->id,
            'name' => $zone->name,
            'slug' => $zone->slug,
            'area_label' => $zone->area_label,
            'location_description' => $zone->location_description,
            'status' => $status,
            'sample_count' => $sampleCount,
            'target_sample_count' => $zone->sample_target_count,
            'active_crop' => $zone->active_crop,
            'latest_recommendation_label' => $zone->latest_recommendation_label,
            'latest_recommendation_confidence' => $zone->latest_recommendation_confidence,
            'aggregate' => $aggregate,
            'has_complete_data' => $sampleCount >= $zone->sample_target_count,
        ];
    }

    public function buildZoneDetail(Zone $zone): array
    {
        $samples = $zone->soilData()
            ->orderByDesc('sampled_at')
            ->orderByDesc('id')
            ->take(max($zone->sample_target_count, 8))
            ->get()
            ->reverse()
            ->values();

        $aggregate = $this->aggregateSamples($samples);
        $latestAdvice = $zone->careAdvices()->first();

        return [
            'zone' => $zone,
            'samples' => $samples,
            'sample_cards' => $samples->map(function (SoilData $sample, int $index) {
                return [
                    'point_label' => $sample->point_label ?: 'PT-'.str_pad((string) ($index + 1), 2, '0', STR_PAD_LEFT),
                    'ph' => $sample->ph,
                    'nitrogen' => $sample->nitrogen,
                    'phosphorus' => $sample->phosphorus,
                    'potassium' => $sample->potassium,
                    'soil_moisture' => $sample->soil_moisture,
                    'sampled_at' => optional($sample->sampled_at ?? $sample->created_at)?->format('d M Y, H:i'),
                    'status' => $sample->ph < 6 || $sample->phosphorus < 20 ? 'attention' : 'good',
                ];
            })->values(),
            'aggregate' => $aggregate,
            'quality_notice' => $this->qualityNotice($zone, $samples->count()),
            'radar_profile' => $this->buildRadarProfile($aggregate),
            'history_chart' => $this->buildZoneHistoryChart($zone),
            'latest_advice' => $latestAdvice,
            'status' => $this->deriveZoneStatus($zone, $samples->count()),
        ];
    }

    public function buildMonitoringView(Zone $zone): array
    {
        $history = $this->lastHourHistory($zone);
        $aggregate = $this->aggregateSamples($history);

        return [
            'health_score' => $this->calculateHealthScore($aggregate),
            'aggregate' => $aggregate,
            'history_chart' => $this->buildHourlyHistoryChart($history),
            'latest_advice' => $zone->careAdvices()->first(),
            'alerts' => $this->buildAlerts($aggregate),
            'history_count' => $history->count(),
        ];
    }

    public function aggregateSamples(Collection $samples): array
    {
        $metrics = ['ph', 'nitrogen', 'phosphorus', 'potassium', 'soil_moisture'];
        $result = ['sample_count' => $samples->count()];

        foreach ($metrics as $metric) {
            $values = $samples
                ->pluck($metric)
                ->filter(fn ($value) => $value !== null)
                ->map(fn ($value) => (float) $value)
                ->values();

            if ($values->isEmpty()) {
                $result[$metric] = [
                    'mean' => null,
                    'min' => null,
                    'max' => null,
                    'range' => null,
                ];
                continue;
            }

            $result[$metric] = [
                'mean' => round($values->avg(), 2),
                'min' => round($values->min(), 2),
                'max' => round($values->max(), 2),
                'range' => round($values->max() - $values->min(), 2),
            ];
        }

        return $result;
    }

    public function lastHourHistory(Zone $zone): Collection
    {
        $history = $zone->soilData()
            ->where('sampled_at', '>=', now()->subHour())
            ->orderBy('sampled_at')
            ->get();

        if ($history->isNotEmpty()) {
            return $history;
        }

        return $zone->soilData()
            ->orderByDesc('sampled_at')
            ->take(8)
            ->get()
            ->reverse()
            ->values();
    }

    public function buildPredictionSamples(Zone $zone): Collection
    {
        return $zone->soilData()
            ->orderByDesc('sampled_at')
            ->take(max($zone->sample_target_count, 6))
            ->get()
            ->reverse()
            ->values();
    }

    public function zoneLedger(): LengthAwarePaginator
    {
        return SoilData::with('zone')
            ->orderByDesc('sampled_at')
            ->orderByDesc('created_at')
            ->paginate(12);
    }

    protected function sampleCount(Zone $zone): int
    {
        if ($zone->relationLoaded('soilData')) {
            return $zone->soilData->count();
        }

        return $zone->soilData()->count();
    }

    protected function deriveZoneStatus(Zone $zone, int $sampleCount): array
    {
        if (filled($zone->active_crop)) {
            return [
                'key' => 'sedang_ditanam',
                'label' => 'Sedang Ditanam',
                'tone' => 'green',
            ];
        }

        if ($sampleCount >= $zone->sample_target_count) {
            return [
                'key' => 'siap_analisis',
                'label' => 'Siap Analisis',
                'tone' => 'blue',
            ];
        }

        return [
            'key' => 'butuh_sampling',
            'label' => 'Butuh Sampling',
            'tone' => 'amber',
        ];
    }

    protected function buildTelemetrySummary(Collection $zones): array
    {
        $sensorZones = $zones->filter(fn (Zone $zone) => $zone->monitoring_status === 'online')->count();
        $manualZones = max($zones->count() - $sensorZones, 0);
        $total = max($zones->count(), 1);

        return [
            'sensor_percentage' => (int) round(($sensorZones / $total) * 100),
            'manual_percentage' => (int) round(($manualZones / $total) * 100),
        ];
    }

    protected function buildTrendChart(): array
    {
        $days = collect(range(6, 0))->map(function (int $offset) {
            return Carbon::now()->subDays($offset)->startOfDay();
        });

        return [
            'labels' => $days->map(fn (Carbon $day) => $day->translatedFormat('D'))->all(),
            'nitrogen' => $days->map(fn (Carbon $day) => round((float) SoilData::whereDate('sampled_at', $day)->avg('nitrogen'), 1))->all(),
            'phosphorus' => $days->map(fn (Carbon $day) => round((float) SoilData::whereDate('sampled_at', $day)->avg('phosphorus'), 1))->all(),
            'potassium' => $days->map(fn (Carbon $day) => round((float) SoilData::whereDate('sampled_at', $day)->avg('potassium'), 1))->all(),
            'ph' => $days->map(fn (Carbon $day) => round((float) SoilData::whereDate('sampled_at', $day)->avg('ph'), 2))->all(),
        ];
    }

    protected function recentActivity(): Collection
    {
        return SoilData::with('zone')
            ->latest('sampled_at')
            ->take(6)
            ->get()
            ->map(function (SoilData $sample) {
                return [
                    'title' => 'Sampling baru untuk '.($sample->zone?->name ?? 'Zona tanpa nama'),
                    'description' => 'Titik '.($sample->point_label ?: 'tanpa label').' merekam NPK dan pH terbaru.',
                    'time' => optional($sample->sampled_at ?? $sample->created_at)?->diffForHumans(),
                ];
            });
    }

    protected function qualityNotice(Zone $zone, int $sampleCount): ?string
    {
        if ($sampleCount < $zone->sample_target_count) {
            $remaining = $zone->sample_target_count - $sampleCount;

            return 'Tingkatkan akurasi dengan menambah '.$remaining.' titik sampling lagi.';
        }

        return null;
    }

    protected function buildRadarProfile(array $aggregate): array
    {
        return [
            'labels' => ['Nitrogen', 'Fosfor', 'Kalium', 'pH', 'Kelembapan'],
            'current' => [
                $aggregate['nitrogen']['mean'] ?? 0,
                $aggregate['phosphorus']['mean'] ?? 0,
                $aggregate['potassium']['mean'] ?? 0,
                ($aggregate['ph']['mean'] ?? 0) * 15,
                $aggregate['soil_moisture']['mean'] ?? 0,
            ],
            'ideal' => [100, 45, 85, 97.5, 40],
        ];
    }

    protected function buildZoneHistoryChart(Zone $zone): array
    {
        $samples = $zone->soilData()
            ->orderBy('sampled_at')
            ->take(12)
            ->get();

        return [
            'labels' => $samples->map(fn (SoilData $sample) => optional($sample->sampled_at ?? $sample->created_at)?->format('H:i'))->all(),
            'ph' => $samples->pluck('ph')->map(fn ($value) => round((float) $value, 2))->all(),
            'moisture' => $samples->pluck('soil_moisture')->map(fn ($value) => $value !== null ? round((float) $value, 2) : null)->all(),
        ];
    }

    protected function buildHourlyHistoryChart(Collection $history): array
    {
        return [
            'labels' => $history->map(fn (SoilData $sample) => optional($sample->sampled_at ?? $sample->created_at)?->format('H:i'))->all(),
            'npk' => $history->map(fn (SoilData $sample) => round(($sample->nitrogen + $sample->phosphorus + $sample->potassium) / 3, 2))->all(),
            'moisture' => $history->map(fn (SoilData $sample) => $sample->soil_moisture !== null ? round((float) $sample->soil_moisture, 2) : null)->all(),
        ];
    }

    protected function calculateHealthScore(array $aggregate): int
    {
        $score = 100;

        $ph = $aggregate['ph']['mean'] ?? null;
        $moisture = $aggregate['soil_moisture']['mean'] ?? null;
        $phosphorus = $aggregate['phosphorus']['mean'] ?? null;

        if ($ph !== null && ($ph < 5.8 || $ph > 7.2)) {
            $score -= 12;
        }

        if ($moisture !== null && $moisture < 30) {
            $score -= 10;
        }

        if ($phosphorus !== null && $phosphorus < 20) {
            $score -= 8;
        }

        return max($score, 35);
    }

    protected function buildAlerts(array $aggregate): Collection
    {
        $alerts = collect();

        if (($aggregate['soil_moisture']['mean'] ?? 100) < 30) {
            $alerts->push([
                'title' => 'Kelembapan Rendah',
                'description' => 'Kelembapan tanah turun di bawah ambang ideal. Pertimbangkan irigasi bertahap.',
                'tone' => 'blue',
            ]);
        }

        if (($aggregate['ph']['mean'] ?? 6.5) < 6) {
            $alerts->push([
                'title' => 'pH Mulai Asam',
                'description' => 'Zona cenderung asam. Evaluasi kebutuhan pengapuran ringan.',
                'tone' => 'amber',
            ]);
        }

        if (($aggregate['phosphorus']['mean'] ?? 999) < 20) {
            $alerts->push([
                'title' => 'Fosfor Kritis',
                'description' => 'Nilai fosfor rendah berpotensi menahan fase generatif tanaman.',
                'tone' => 'red',
            ]);
        }

        return $alerts;
    }
}
