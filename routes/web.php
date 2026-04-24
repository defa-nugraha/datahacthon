<?php

use App\Http\Controllers\SoilDataController;
use Illuminate\Support\Facades\Route;

Route::get('/', [SoilDataController::class, 'index'])->name('dashboard');
Route::get('/history', [SoilDataController::class, 'history'])->name('history');

Route::post('/analyze-manual', [SoilDataController::class, 'analyzeManual'])->name('analyze.manual');

Route::get('/zones', [SoilDataController::class, 'zones'])->name('zones.index');
Route::post('/zones', [SoilDataController::class, 'storeZone'])->name('zones.store');
Route::get('/zones/{zone}', [SoilDataController::class, 'showZone'])->name('zones.show');
Route::put('/zones/{zone}', [SoilDataController::class, 'updateZone'])->name('zones.update');
Route::delete('/zones/{zone}', [SoilDataController::class, 'destroyZone'])->name('zones.destroy');
Route::get('/zones/{zone}/sampling', [SoilDataController::class, 'samplingForm'])->name('zones.sampling');
Route::post('/zones/{zone}/sampling', [SoilDataController::class, 'storeSampling'])->name('zones.sampling.store');
Route::get('/zones/{zone}/monitor', [SoilDataController::class, 'monitorZone'])->name('zones.monitor');
Route::post('/zones/{zone}/analyze', [SoilDataController::class, 'analyzeZone'])->name('zones.analyze');
Route::post('/zones/{zone}/plant', [SoilDataController::class, 'startPlanting'])->name('zones.plant.start');
Route::post('/zones/{zone}/plant/reset', [SoilDataController::class, 'resetPlanting'])->name('zones.plant.reset');
Route::post('/zones/{zone}/care-advice/refresh', [SoilDataController::class, 'refreshCareAdvice'])->name('zones.care.refresh');

Route::redirect('/welcome', '/');
