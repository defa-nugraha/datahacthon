<?php

return [

    /*
    |--------------------------------------------------------------------------
    | Third Party Services
    |--------------------------------------------------------------------------
    |
    | This file is for storing the credentials for third party services such
    | as Mailgun, Postmark, AWS and more. This file provides the de facto
    | location for this type of information, allowing packages to have
    | a conventional file to locate the various service credentials.
    |
    */

    'postmark' => [
        'key' => env('POSTMARK_API_KEY'),
    ],

    'resend' => [
        'key' => env('RESEND_API_KEY'),
    ],

    'ses' => [
        'key' => env('AWS_ACCESS_KEY_ID'),
        'secret' => env('AWS_SECRET_ACCESS_KEY'),
        'region' => env('AWS_DEFAULT_REGION', 'us-east-1'),
    ],

    'slack' => [
        'notifications' => [
            'bot_user_oauth_token' => env('SLACK_BOT_USER_OAUTH_TOKEN'),
            'channel' => env('SLACK_BOT_USER_DEFAULT_CHANNEL'),
        ],
    ],

    'ai_advisor' => [
        'base_url' => env('AI_ADVISOR_BASE_URL', 'http://127.0.0.1:8001'),
        'timeout' => env('AI_ADVISOR_TIMEOUT', 20),
        'care_threshold' => [
            'enabled' => env('AI_ADVISOR_THRESHOLD_ENABLED', true),
            'min_history_points' => env('AI_ADVISOR_THRESHOLD_MIN_HISTORY_POINTS', 2),
            'min_interval_minutes' => env('AI_ADVISOR_MIN_INTERVAL_MINUTES', 60),
            'ph_delta' => env('AI_ADVISOR_THRESHOLD_PH_DELTA', 0.25),
            'nitrogen_delta' => env('AI_ADVISOR_THRESHOLD_N_DELTA', 8),
            'phosphorus_delta' => env('AI_ADVISOR_THRESHOLD_P_DELTA', 5),
            'potassium_delta' => env('AI_ADVISOR_THRESHOLD_K_DELTA', 8),
            'soil_moisture_delta' => env('AI_ADVISOR_THRESHOLD_MOISTURE_DELTA', 8),
            'critical_ph_low' => env('AI_ADVISOR_CRITICAL_PH_LOW', 5.8),
            'critical_ph_high' => env('AI_ADVISOR_CRITICAL_PH_HIGH', 7.5),
            'critical_phosphorus_low' => env('AI_ADVISOR_CRITICAL_P_LOW', 18),
            'critical_soil_moisture_low' => env('AI_ADVISOR_CRITICAL_MOISTURE_LOW', 25),
        ],
    ],

];
