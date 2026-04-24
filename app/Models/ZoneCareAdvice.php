<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class ZoneCareAdvice extends Model
{
    protected $table = 'zone_care_advices';

    protected $fillable = [
        'zone_id',
        'crop_name',
        'advice_summary',
        'urgency_level',
        'recommendations',
        'nutrient_snapshot',
        'raw_response',
        'time_window_minutes',
        'generated_at',
    ];

    protected $casts = [
        'recommendations' => 'array',
        'nutrient_snapshot' => 'array',
        'raw_response' => 'array',
        'time_window_minutes' => 'integer',
        'generated_at' => 'datetime',
    ];

    public function zone(): BelongsTo
    {
        return $this->belongsTo(Zone::class);
    }
}
