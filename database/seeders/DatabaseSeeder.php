<?php

namespace Database\Seeders;

use App\Models\User;
use App\Models\Zone;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Hash;

class DatabaseSeeder extends Seeder
{
    use WithoutModelEvents;

    /**
     * Seed the application's database.
     */
    public function run(): void
    {
        User::query()->updateOrCreate(
            ['email' => 'test@example.com'],
            [
                'name' => 'Test User',
                'password' => Hash::make('password'),
                'email_verified_at' => now(),
            ]
        );

        User::query()->updateOrCreate(
            ['email' => 'petani@agrozonal.test'],
            [
                'name' => 'Petani Demo',
                'password' => Hash::make('password'),
                'email_verified_at' => now(),
            ]
        );

        User::query()->updateOrCreate(
            ['email' => 'admin@agrozonal.test'],
            [
                'name' => 'Admin AgroZonal',
                'password' => Hash::make('password'),
                'email_verified_at' => now(),
            ]
        );

        if (! Zone::exists()) {
            $this->call(ZoneFeatureShowcaseSeeder::class);
        }
    }
}
