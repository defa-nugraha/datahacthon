<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('zone_care_advices', function (Blueprint $table) {
            $table->id();
            $table->foreignId('zone_id')->constrained('zones')->cascadeOnDelete();
            $table->string('crop_name');
            $table->text('advice_summary');
            $table->string('urgency_level')->default('medium');
            $table->json('recommendations');
            $table->json('nutrient_snapshot');
            $table->json('raw_response')->nullable();
            $table->unsignedInteger('time_window_minutes')->default(60);
            $table->timestamp('generated_at')->index();
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('zone_care_advices');
    }
};
