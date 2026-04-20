<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\SoilDataController;

// 1. Jalur Halaman Utama & Riwayat (Method: GET)
Route::get('/', [SoilDataController::class, 'index'])->name('welcome');
Route::get('/history', [SoilDataController::class, 'history'])->name('history');

// 2. Jalur Terima Data Form Manual (Method: POST) -> INI YANG TADI ERROR
Route::post('/analyze-manual', [SoilDataController::class, 'analyzeManual'])->name('analyze.manual');

// 3. Jalur Aksi Tombol Tanam & Reset (Method: POST)
Route::post('/plant/start', [SoilDataController::class, 'startPlanting'])->name('plant.start');
Route::post('/plant/reset', [SoilDataController::class, 'resetPlanting'])->name('plant.reset');
// Halaman Manajemen IoT & Zona
Route::get('/zones', [SoilDataController::class, 'zones'])->name('zones');