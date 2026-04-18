<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up()
    {
        Schema::create('care_schedules', function (Blueprint $table) {
            $table->id();
            $table->foreignId('soil_data_id')->constrained('soil_data')->onDelete('cascade');
            $table->string('task_name');
            $table->date('due_date');
            $table->boolean('is_completed')->default(false);
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('care_schedules');
    }
};
