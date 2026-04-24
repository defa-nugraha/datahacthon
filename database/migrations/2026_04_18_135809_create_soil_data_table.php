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
        Schema::create('soil_data', function (Blueprint $table) {
            $table->id();
            $table->enum('source', ['iot', 'manual']);
            $table->float('nitrogen');
            $table->float('phosphorus');
            $table->float('potassium');
            $table->float('ph');
            $table->string('recommended_plant')->nullable();
            $table->text('ai_analysis')->nullable();
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('soil_data');
    }
};
