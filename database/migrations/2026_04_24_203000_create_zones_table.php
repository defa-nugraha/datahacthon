<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('zones', function (Blueprint $table) {
            $table->id();
            $table->string('name');
            $table->string('slug')->unique();
            $table->string('area_label')->nullable();
            $table->string('location_description')->nullable();
            $table->string('status')->default('butuh_sampling');
            $table->string('active_crop')->nullable();
            $table->unsignedInteger('sample_target_count')->default(8);
            $table->decimal('latest_recommendation_confidence', 5, 2)->nullable();
            $table->string('latest_recommendation_label')->nullable();
            $table->string('monitoring_status')->default('online');
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('zones');
    }
};
