<?php

use App\Http\Controllers\AdminController;
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

Route::middleware(['auth', 'admin'])->prefix('admin')->name('admin.')->group(function () {
    Route::get('/', [AdminController::class, 'index'])->name('dashboard');
    Route::patch('/users/{user}/role', [AdminController::class, 'updateUserRole'])->name('users.role.update');
});

Route::middleware('auth')->group(function () {
    Route::get('/zones', [SoilDataController::class, 'zones'])->name('zones.index');

    Route::post('/zones', [SoilDataController::class, 'storeZone'])->name('zones.store');

    Route::post('/zones/{zone:slug}/analyze', [SoilDataController::class, 'analyzeZone'])->name('zones.analyze');
    Route::post('/zones/{zone:slug}/plant/start', [SoilDataController::class, 'startPlanting'])->name('zones.plant.start');
    Route::post('/zones/{zone:slug}/plant/reset', [SoilDataController::class, 'resetPlanting'])->name('zones.plant.reset');
    Route::post('/zones/{zone:slug}/care-advice/refresh', [SoilDataController::class, 'refreshCareAdvice'])->name('zones.care.refresh');
    Route::get('/zones/{zone:slug}/monitor', [SoilDataController::class, 'monitorZone'])->name('zones.monitor');

    Route::get('/zones/{zone:slug}/sampling', [SoilDataController::class, 'samplingForm'])->name('zones.sampling');
    Route::post('/zones/{zone:slug}/sampling', [SoilDataController::class, 'storeSampling'])->name('zones.sampling.store');
    Route::get('/zones/{zone:slug}', [SoilDataController::class, 'showZone'])->name('zones.show');
    Route::put('/zones/{zone:slug}', [SoilDataController::class, 'updateZone'])->name('zones.update');
    Route::delete('/zones/{zone:slug}', [SoilDataController::class, 'destroyZone'])->name('zones.destroy');
    
    Route::get('/history', [SoilDataController::class, 'history'])->name('history');

    Route::middleware('admin')->group(function () {
        Route::get('/devices', [SoilDataController::class, 'devices'])->name('devices.index');
        Route::post('/devices', [SoilDataController::class, 'storeDevice'])->name('devices.store');
        Route::delete('/devices/{device}', [SoilDataController::class, 'destroyDevice'])->name('devices.destroy');
    });
});

require __DIR__.'/auth.php';
