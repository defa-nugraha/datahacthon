<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Device extends Model
{
    use HasFactory;

    // 1. Kasih tau kolom mana aja yang boleh diisi (Mass Assignment)
    protected $fillable = [
        'name',
        'client_id',
        'status',
        'connection_type',
        'last_sync',
    ];

    // 2. Casting: Biar Laravel otomatis ngerubah teks jadi Object Carbon (Tanggal)
    // Jadi lu bisa pake fungsi ->format() atau ->diffForHumans() di Blade
    protected $casts = [
        'last_sync' => 'datetime',
    ];
}