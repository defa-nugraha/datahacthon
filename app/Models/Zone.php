<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Zone extends Model
{
    protected $fillable = [
        'name',
        'slug',
        'area_label',
        'location_description',
        'status',
        'active_crop',
        'sample_target_count',
        'latest_recommendation_label',
        'latest_recommendation_confidence',
        'monitoring_status',
    ];

    protected $casts = [
        'latest_recommendation_confidence' => 'float',
        'sample_target_count' => 'integer',
    ];

    public function getRouteKeyName(): string
    {
        return 'slug';
    }

    public function soilData(): HasMany
    {
        return $this->hasMany(SoilData::class);
    }

    public function careAdvices(): HasMany
    {
        return $this->hasMany(ZoneCareAdvice::class)->latest('generated_at');
    }
}
