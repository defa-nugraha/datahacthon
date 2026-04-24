<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('soil_data', function (Blueprint $table) {
            $table->foreignId('zone_id')->nullable()->after('id')->constrained('zones')->nullOnDelete();
            $table->string('point_label')->nullable()->after('source');
            $table->float('soil_moisture')->nullable()->after('ph');
            $table->json('ai_payload')->nullable()->after('ai_analysis');
            $table->timestamp('sampled_at')->nullable()->after('ai_payload')->index();
        });
    }

    public function down(): void
    {
        Schema::table('soil_data', function (Blueprint $table) {
            $table->dropConstrainedForeignId('zone_id');
            $table->dropColumn([
                'point_label',
                'soil_moisture',
                'ai_payload',
                'sampled_at',
            ]);
        });
    }
};
