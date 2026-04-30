<?php

use App\Models\Zone;
use App\Services\AiAdvisorService;
use App\Services\ZoneAnalyticsService;
use Illuminate\Support\Facades\Artisan;
use Illuminate\Support\Facades\Schedule;

Artisan::command('zones:refresh-care-advice', function (
    ZoneAnalyticsService $analytics,
    AiAdvisorService $advisor
) {
    $zones = Zone::query()
        ->whereNotNull('active_crop')
        ->get();

    $generated = 0;
    $skipped = 0;

    foreach ($zones as $zone) {
        $history = $analytics->lastHourHistory($zone);

        if ($history->isEmpty()) {
            $skipped++;
            continue;
        }

        $latestBefore = $zone->careAdvices()->first();
        $advice = $advisor->generateCareAdvice($zone, $history);

        if ($advice && $advice->id !== $latestBefore?->id) {
            $generated++;
        } else {
            $skipped++;
        }
    }

    $this->info("Adaptive advice generated for {$generated} zone(s), skipped {$skipped} zone(s).");
})->purpose('Generate hourly care advice from the last 60 minutes of nutrient history');

Schedule::command('zones:refresh-care-advice')->hourly();
