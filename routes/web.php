<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\SoilDataController;

Route::get('/', function () {
    return view('welcome');
});
Route::get('/', [SoilDataController::class, 'index'])->name('welcome');