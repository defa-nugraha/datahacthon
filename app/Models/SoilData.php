<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class SoilData extends Model
{
    protected $fillable = [
        'zone_id',
        'source',
        'point_label',
        'nitrogen',
        'phosphorus',
        'potassium',
        'ph',
        'soil_moisture',
        'recommended_plant',
        'ai_analysis',
        'ai_payload',
        'sampled_at',
    ];

    protected $casts = [
        'nitrogen' => 'float',
        'phosphorus' => 'float',
        'potassium' => 'float',
        'ph' => 'float',
        'soil_moisture' => 'float',
        'ai_payload' => 'array',
        'sampled_at' => 'datetime',
    ];

    public function zone(): BelongsTo
    {
        return $this->belongsTo(Zone::class);
    }
}
