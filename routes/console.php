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

    $processed = 0;

    foreach ($zones as $zone) {
        $history = $analytics->lastHourHistory($zone);

        if ($history->isEmpty()) {
            continue;
        }

        $advisor->generateCareAdvice($zone, $history);
        $processed++;
    }

    $this->info("Adaptive advice refreshed for {$processed} zone(s).");
})->purpose('Generate hourly care advice from the last 60 minutes of nutrient history');

Schedule::command('zones:refresh-care-advice')->hourly();
