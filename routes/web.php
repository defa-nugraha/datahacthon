<?php

use App\Http\Controllers\ProfileController;
use App\Http\Controllers\SoilDataController;
use Illuminate\Support\Facades\Route;

Route::get('/', function () {
    return redirect()->route('login');
});

Route::get('/welcome', [SoilDataController::class, 'index'])
    ->middleware(['auth', 'verified'])
    ->name('welcome');

Route::get('/dashboard', [SoilDataController::class, 'index'])
    ->middleware(['auth', 'verified'])
    ->name('dashboard');

Route::middleware('auth')->group(function () {
    Route::get('/profile', [ProfileController::class, 'edit'])->name('profile.edit');
    Route::patch('/profile', [ProfileController::class, 'update'])->name('profile.update');
    Route::delete('/profile', [ProfileController::class, 'destroy'])->name('profile.destroy');
});

Route::middleware('auth')->group(function () {
    Route::get('/zones', [SoilDataController::class, 'zones'])->name('zones.index');

    // 2. Simpan Zona Baru (Ini yang tadi bikin error)
    Route::post('/zones', [SoilDataController::class, 'storeZone'])->name('zones.store');

    // 3. Detail, Monitor, dan Hapus Zona
    Route::get('/zones/{zone:slug}', [SoilDataController::class, 'showZone'])->name('zones.show');
    Route::get('/zones/{zone:slug}/monitor', [SoilDataController::class, 'monitorZone'])->name('zones.monitor');
    Route::put('/zones/{zone:slug}', [SoilDataController::class, 'updateZone'])->name('zones.update');
    Route::delete('/zones/{zone:slug}', [SoilDataController::class, 'destroyZone'])->name('zones.destroy');

    // 4. Input Sampling (Form & Simpan)
    Route::get('/zones/{zone:slug}/sampling', [SoilDataController::class, 'samplingForm'])->name('zones.sampling');
    Route::post('/zones/{zone:slug}/sampling', [SoilDataController::class, 'storeSampling'])->name('zones.sampling.store');
    
    // 5. History / Laporan
    Route::get('/history', [SoilDataController::class, 'history'])->name('history');

    // Rute untuk Manajemen Device IoT
    Route::get('/devices', [SoilDataController::class, 'devices'])->name('devices.index');
    Route::post('/devices', [SoilDataController::class, 'storeDevice'])->name('devices.store');
    Route::delete('/devices/{device}', [SoilDataController::class, 'destroyDevice'])->name('devices.destroy');
});

require __DIR__.'/auth.php';
