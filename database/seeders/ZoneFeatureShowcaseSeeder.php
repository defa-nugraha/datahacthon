<?php

namespace Database\Seeders;

use App\Models\SoilData;
use App\Models\Zone;
use App\Models\ZoneCareAdvice;
use App\Services\ZoneAnalyticsService;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;

class ZoneFeatureShowcaseSeeder extends Seeder
{
    use WithoutModelEvents;

    public function run(): void
    {
        if (app()->environment('production') && ! (bool) env('ALLOW_DEMO_SEEDING_IN_PRODUCTION', false)) {
            $this->command?->warn('ZoneFeatureShowcaseSeeder dilewati di production. Set ALLOW_DEMO_SEEDING_IN_PRODUCTION=true untuk demo Azure.');

            return;
        }

        DB::transaction(function () {
            $this->resetDemoData();

            collect($this->blueprints())->each(function (array $blueprint) {
                $zone = $this->seedZone($blueprint['zone']);
                $this->seedSoilSeries($zone, $blueprint['samples']);

                if (isset($blueprint['advice'])) {
                    $this->seedAdvice($zone, $blueprint['advice']);
                }
            });
        });
    }

    protected function resetDemoData(): void
    {
        DB::table('care_schedules')->delete();
        ZoneCareAdvice::query()->delete();
        SoilData::query()->delete();
        Zone::query()->delete();
    }

    protected function seedZone(array $zoneData): Zone
    {
        return Zone::create([
            'name' => $zoneData['name'],
            'slug' => Str::slug($zoneData['name']),
            'area_label' => $zoneData['area_label'],
            'location_description' => $zoneData['location_description'],
            'status' => $zoneData['status'],
            'active_crop' => $zoneData['active_crop'],
            'sample_target_count' => $zoneData['sample_target_count'],
            'latest_recommendation_label' => $zoneData['latest_recommendation_label'],
            'latest_recommendation_confidence' => $zoneData['latest_recommendation_confidence'],
            'monitoring_status' => $zoneData['monitoring_status'],
        ]);
    }

    protected function seedSoilSeries(Zone $zone, array $profile): void
    {
        $historicalOffsets = $profile['historical_offsets'];
        $recentOffsets = $profile['recent_offsets'];
        $totalSeries = array_merge(
            array_map(fn (int $days) => now()->subDays($days)->setTime(9 + ($days % 4), 15 + (($days * 7) % 35)), $historicalOffsets),
            array_map(fn (int $minutes) => now()->subMinutes($minutes), $recentOffsets)
        );

        foreach (array_values($totalSeries) as $index => $sampledAt) {
            $wave = $this->waveByIndex($index);
            $pointNumber = ($index % $profile['point_slots']) + 1;

            SoilData::create([
                'zone_id' => $zone->id,
                'source' => $profile['source'] ?? 'iot',
                'point_label' => 'PT-'.str_pad((string) $pointNumber, 2, '0', STR_PAD_LEFT),
                'ph' => round($profile['ph'] + $wave['ph'], 2),
                'nitrogen' => round($profile['nitrogen'] + $wave['nitrogen'], 1),
                'phosphorus' => round($profile['phosphorus'] + $wave['phosphorus'], 1),
                'potassium' => round($profile['potassium'] + $wave['potassium'], 1),
                'soil_moisture' => round(max(0, $profile['soil_moisture'] + $wave['soil_moisture']), 1),
                'recommended_plant' => $profile['recommended_plant'],
                'ai_analysis' => $profile['analysis_note'],
                'ai_payload' => [
                    'demo_seeded' => true,
                    'scenario' => $profile['scenario'],
                    'point_slot' => $pointNumber,
                    'captured_at' => $sampledAt->toIso8601String(),
                ],
                'sampled_at' => $sampledAt,
                'created_at' => $sampledAt,
                'updated_at' => $sampledAt,
            ]);
        }
    }

    protected function seedAdvice(Zone $zone, array $advice): void
    {
        $analytics = app(ZoneAnalyticsService::class);
        $history = $zone->soilData()
            ->where('sampled_at', '>=', now()->subHour())
            ->orderBy('sampled_at')
            ->get();

        ZoneCareAdvice::create([
            'zone_id' => $zone->id,
            'crop_name' => $advice['crop_name'],
            'advice_summary' => $advice['summary'],
            'urgency_level' => $advice['urgency'],
            'recommendations' => $advice['recommendations'],
            'nutrient_snapshot' => $analytics->aggregateSamples($history->isNotEmpty() ? $history : $zone->soilData()->get()),
            'raw_response' => [
                'provider' => 'demo-seeder',
                'note' => 'Seed untuk demo UI dan alur fitur.',
                'scenario' => $advice['scenario'],
            ],
            'generated_at' => now()->subMinutes($advice['minutes_ago']),
            'time_window_minutes' => 60,
        ]);
    }

    protected function waveByIndex(int $index): array
    {
        $wavePattern = [
            ['ph' => 0.08, 'nitrogen' => 4, 'phosphorus' => 2, 'potassium' => 3, 'soil_moisture' => 3],
            ['ph' => -0.05, 'nitrogen' => -3, 'phosphorus' => -1.5, 'potassium' => -2, 'soil_moisture' => -2.5],
            ['ph' => 0.12, 'nitrogen' => 2, 'phosphorus' => 1, 'potassium' => 1.5, 'soil_moisture' => 1.2],
            ['ph' => -0.09, 'nitrogen' => -4.5, 'phosphorus' => -2.5, 'potassium' => -3, 'soil_moisture' => -3.5],
            ['ph' => 0.04, 'nitrogen' => 1.5, 'phosphorus' => 0.8, 'potassium' => 2, 'soil_moisture' => 2.2],
            ['ph' => -0.02, 'nitrogen' => -1.2, 'phosphorus' => -0.6, 'potassium' => -1.4, 'soil_moisture' => -1.4],
        ];

        return $wavePattern[$index % count($wavePattern)];
    }

    protected function blueprints(): array
    {
        return [
            [
                'zone' => [
                    'name' => 'Zona Utara',
                    'area_label' => 'Blok A, Sektor 1',
                    'location_description' => 'Demo jagung dataran rendah dengan sensor aktif dan sampling stabil.',
                    'status' => 'sedang_ditanam',
                    'active_crop' => 'Jagung',
                    'sample_target_count' => 8,
                    'latest_recommendation_label' => 'Jagung',
                    'latest_recommendation_confidence' => 91.8,
                    'monitoring_status' => 'online',
                ],
                'samples' => [
                    'scenario' => 'healthy-corn',
                    'source' => 'iot',
                    'ph' => 6.45,
                    'nitrogen' => 100,
                    'phosphorus' => 41,
                    'potassium' => 82,
                    'soil_moisture' => 39,
                    'point_slots' => 6,
                    'historical_offsets' => [6, 5, 4, 3, 2, 1],
                    'recent_offsets' => [55, 45, 35, 25, 15, 5],
                    'recommended_plant' => 'Jagung',
                    'analysis_note' => 'Profil hara seimbang untuk jagung dengan kelembapan yang relatif stabil.',
                ],
                'advice' => [
                    'scenario' => 'stable-maintenance',
                    'crop_name' => 'Jagung',
                    'summary' => 'Kondisi Jagung stabil. Pertahankan pola irigasi ringan dan pantau nitrogen sebelum pemupukan susulan berikutnya.',
                    'urgency' => 'low',
                    'minutes_ago' => 18,
                    'recommendations' => [
                        ['title' => 'Pertahankan irigasi bertahap', 'detail' => 'Kelembapan masih aman. Irigasi cukup dilakukan ringan pada pagi hari.'],
                        ['title' => 'Pantau nitrogen 24 jam ke depan', 'detail' => 'Nilai nitrogen sudah baik, tetapi tetap cek tren sebelum aplikasi pupuk susulan.'],
                    ],
                ],
            ],
            [
                'zone' => [
                    'name' => 'Zona Selatan',
                    'area_label' => 'Blok B, Sektor 4',
                    'location_description' => 'Demo sawah irigasi dengan tanaman aktif dan fosfor mulai menurun.',
                    'status' => 'sedang_ditanam',
                    'active_crop' => 'Padi',
                    'sample_target_count' => 8,
                    'latest_recommendation_label' => 'Padi',
                    'latest_recommendation_confidence' => 88.4,
                    'monitoring_status' => 'online',
                ],
                'samples' => [
                    'scenario' => 'rice-phosphorus-watch',
                    'source' => 'iot',
                    'ph' => 6.12,
                    'nitrogen' => 108,
                    'phosphorus' => 19,
                    'potassium' => 86,
                    'soil_moisture' => 54,
                    'point_slots' => 6,
                    'historical_offsets' => [6, 5, 4, 3, 2, 1],
                    'recent_offsets' => [58, 48, 38, 28, 18, 8],
                    'recommended_plant' => 'Padi',
                    'analysis_note' => 'Kelembapan tinggi mendukung padi, namun fosfor perlu dipantau agar fase generatif tidak tertahan.',
                ],
                'advice' => [
                    'scenario' => 'phosphorus-low',
                    'crop_name' => 'Padi',
                    'summary' => 'Padi membutuhkan perhatian pada unsur fosfor. Kelembapan memadai, tetapi profil P berada di bawah rentang target.',
                    'urgency' => 'high',
                    'minutes_ago' => 12,
                    'recommendations' => [
                        ['title' => 'Prioritaskan sumber fosfor', 'detail' => 'Sesuaikan pemupukan susulan berbasis fosfor untuk menjaga pembentukan anakan dan malai.'],
                        ['title' => 'Jaga genangan tetap stabil', 'detail' => 'Air sudah memadai. Fokuskan intervensi pada nutrisi, bukan penambahan irigasi besar.'],
                    ],
                ],
            ],
            [
                'zone' => [
                    'name' => 'Zona Timur',
                    'area_label' => 'Blok C, Sektor 2',
                    'location_description' => 'Zona hortikultura yang sudah lengkap sampling dan siap dianalisis.',
                    'status' => 'siap_analisis',
                    'active_crop' => null,
                    'sample_target_count' => 8,
                    'latest_recommendation_label' => 'Cabai',
                    'latest_recommendation_confidence' => 83.7,
                    'monitoring_status' => 'manual',
                ],
                'samples' => [
                    'scenario' => 'ready-for-analysis',
                    'source' => 'manual',
                    'ph' => 6.38,
                    'nitrogen' => 86,
                    'phosphorus' => 33,
                    'potassium' => 92,
                    'soil_moisture' => 36,
                    'point_slots' => 5,
                    'historical_offsets' => [6, 4, 3, 2, 1],
                    'recent_offsets' => [50, 32, 14, 6],
                    'recommended_plant' => 'Cabai',
                    'analysis_note' => 'Zona siap dianalisis untuk komoditas hortikultura dengan kalium yang cukup kuat.',
                ],
            ],
            [
                'zone' => [
                    'name' => 'Zona Barat',
                    'area_label' => 'Blok D, Sektor 5',
                    'location_description' => 'Areal observasi baru dengan titik sampling yang masih terbatas.',
                    'status' => 'butuh_sampling',
                    'active_crop' => null,
                    'sample_target_count' => 8,
                    'latest_recommendation_label' => null,
                    'latest_recommendation_confidence' => null,
                    'monitoring_status' => 'manual',
                ],
                'samples' => [
                    'scenario' => 'insufficient-sampling',
                    'source' => 'manual',
                    'ph' => 5.86,
                    'nitrogen' => 77,
                    'phosphorus' => 18,
                    'potassium' => 61,
                    'soil_moisture' => 28,
                    'point_slots' => 4,
                    'historical_offsets' => [5, 3],
                    'recent_offsets' => [42, 11],
                    'recommended_plant' => null,
                    'analysis_note' => 'Sampel belum cukup untuk rekomendasi yang stabil. Zona masih butuh sampling tambahan.',
                ],
            ],
            [
                'zone' => [
                    'name' => 'Zona Tengah',
                    'area_label' => 'Blok E, Sektor 3',
                    'location_description' => 'Demo kedelai dengan kondisi cukup baik namun kelembapan mulai turun.',
                    'status' => 'sedang_ditanam',
                    'active_crop' => 'Kedelai',
                    'sample_target_count' => 6,
                    'latest_recommendation_label' => 'Kedelai',
                    'latest_recommendation_confidence' => 86.2,
                    'monitoring_status' => 'online',
                ],
                'samples' => [
                    'scenario' => 'soybean-moisture-watch',
                    'source' => 'iot',
                    'ph' => 6.34,
                    'nitrogen' => 79,
                    'phosphorus' => 34,
                    'potassium' => 72,
                    'soil_moisture' => 29,
                    'point_slots' => 5,
                    'historical_offsets' => [6, 5, 3, 2],
                    'recent_offsets' => [52, 41, 30, 19, 9],
                    'recommended_plant' => 'Kedelai',
                    'analysis_note' => 'Kedelai masih cocok, tetapi kelembapan turun sehingga irigasi perlu diawasi.',
                ],
                'advice' => [
                    'scenario' => 'moisture-drop',
                    'crop_name' => 'Kedelai',
                    'summary' => 'Kedelai menunjukkan penurunan kelembapan tanah dalam 1 jam terakhir. Irigasi ringan lebih diprioritaskan daripada intervensi hara besar.',
                    'urgency' => 'medium',
                    'minutes_ago' => 22,
                    'recommendations' => [
                        ['title' => 'Irigasi ringan bertahap', 'detail' => 'Tambahkan air secara bertahap untuk mengangkat kelembapan tanpa membuat genangan.'],
                        ['title' => 'Tunda koreksi pupuk besar', 'detail' => 'Komposisi NPK masih cukup seimbang. Fokus pada stabilisasi kelembapan terlebih dahulu.'],
                    ],
                ],
            ],
        ];
    }
}
