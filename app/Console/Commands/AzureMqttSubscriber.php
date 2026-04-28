<?php

namespace App\Console\Commands;

use Illuminate\Console\Attributes\Description;
use Illuminate\Console\Attributes\Signature;
use Illuminate\Console\Command;

#[Signature('app:azure-mqtt-subscriber')]
#[Description('Command description')]
class AzureMqttSubscriber extends Command
{
    /**
     * Execute the console command.
     */
    // Bagian Logic Utama di file AzureMqttSubscriber
    public function handle()
    {
        $mqtt = new MqttClient(env('AZURE_IOT_HOST'), env('AZURE_IOT_PORT'), env('AZURE_IOT_CLIENT_ID'));

        // Azure butuh SSL karena port 8883
        $settings = (new ConnectionSettings)
            ->setUsername(env('AZURE_IOT_USER'))
            ->setPassword(env('AZURE_IOT_PASS'))
            ->setUseTls(true);

        $mqtt->connect($settings);

        // Dengerin topik dari Azure
        $mqtt->subscribe('devices/+/messages/events/#', function (string $topic, string $message) {
            $data = json_decode($message, true);

            // MASUKIN KE DATABASE RELL!
            \App\Models\SoilData::create([
                'zone_id' => $data['zone_id'], // Pastiin ESP32 kirim zone_id
                'nitrogen' => $data['n'],
                'phosphorus' => $data['p'],
                'potassium' => $data['k'],
                'ph' => $data['ph'],
                'source' => 'iot',
                'sampled_at' => now(),
            ]);
            
            $this->info("Data masuk dari Azure: " . $message);
        }, 0);

        $mqtt->loop(true);
    }
}
