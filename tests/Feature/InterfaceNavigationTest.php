<?php

namespace Tests\Feature;

use App\Models\Device;
use App\Models\SoilData;
use App\Models\User;
use App\Models\Zone;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Route;
use Tests\TestCase;

class InterfaceNavigationTest extends TestCase
{
    use RefreshDatabase;

    public function test_guest_is_redirected_to_login(): void
    {
        $this->get('/')->assertRedirect(route('login'));
        $this->get(route('zones.index'))->assertRedirect(route('login'));
    }

    public function test_active_pages_are_accessible_for_authenticated_user(): void
    {
        $user = User::factory()->create();
        $zone = $this->createZoneWithSamples();

        $this->actingAs($user);

        $this->get(route('dashboard'))->assertOk()->assertSee('Vera AI');
        $this->get(route('welcome'))->assertOk()->assertSee('Zona Alpha');
        $this->get(route('zones.index'))->assertOk()->assertSee('Tambah Zona');
        $this->get(route('zones.show', $zone))->assertOk()->assertSee('Zona Alpha');
        $this->get(route('zones.monitor', $zone))->assertOk()->assertSee('Zona Alpha');
        $this->get(route('history'))->assertOk();
        $this->get(route('devices.index'))->assertOk()->assertSee('Register New Device');
        $this->get(route('profile.edit'))->assertOk();
    }

    public function test_zone_buttons_use_slug_urls_instead_of_numeric_ids(): void
    {
        $user = User::factory()->create();
        $zone = $this->createZoneWithSamples();

        $response = $this->actingAs($user)->get(route('zones.index'));

        $response->assertOk();
        $response->assertSee('/zones/'.$zone->slug, false);
        $response->assertDontSee('/zones/'.$zone->id, false);
    }

    public function test_required_zone_and_device_routes_are_registered(): void
    {
        foreach ([
            'zones.index',
            'zones.show',
            'zones.monitor',
            'zones.sampling.store',
            'zones.analyze',
            'zones.plant.start',
            'zones.plant.reset',
            'zones.care.refresh',
            'devices.index',
            'devices.store',
            'devices.destroy',
        ] as $routeName) {
            $this->assertTrue(Route::has($routeName), "Route {$routeName} belum terdaftar.");
        }
    }

    public function test_zone_forms_and_action_buttons_work(): void
    {
        Http::fake([
            '*/predict/zone' => Http::response([
                'prediction' => [
                    'recommended_label' => 'Jagung',
                    'confidence' => 0.82,
                    'top_k' => [
                        ['label' => 'Jagung', 'probability' => 0.82],
                        ['label' => 'Padi', 'probability' => 0.11],
                    ],
                ],
                'aggregated_features' => [
                    'sample_count' => 4,
                    'ph' => ['mean' => 6.5],
                    'nitrogen' => ['mean' => 91],
                    'phosphorus' => ['mean' => 34],
                    'potassium' => ['mean' => 71],
                    'soil_moisture' => ['mean' => 38],
                ],
                'warnings' => [],
                'model_info' => ['model_name' => 'test-model'],
            ], 200),
            '*/advice/care' => Http::response([
                'summary' => 'Kondisi zona stabil, lanjutkan monitoring hara berkala.',
                'urgency' => 'low',
                'recommendations' => [
                    [
                        'title' => 'Pertahankan pemantauan',
                        'detail' => 'Cek pH, NPK, dan kelembapan pada interval berikutnya.',
                        'priority' => 'low',
                    ],
                ],
            ], 200),
        ]);

        $user = User::factory()->create();
        $zone = $this->createZoneWithSamples();

        $this->actingAs($user);

        $this->post(route('zones.sampling.store', $zone), [
            'point_label' => ['A4'],
            'ph' => [6.6],
            'nitrogen' => [94],
            'phosphorus' => [35],
            'potassium' => [74],
            'soil_moisture' => [39],
            'sampled_at' => now()->toDateTimeString(),
        ])->assertRedirect(route('zones.show', $zone));

        $this->assertDatabaseHas('soil_data', [
            'zone_id' => $zone->id,
            'point_label' => 'A4',
        ]);

        $this->post(route('zones.analyze', $zone))
            ->assertOk()
            ->assertSee('Jagung');

        $this->post(route('zones.plant.start', $zone), [
            'crop_name' => 'Jagung',
        ])->assertRedirect(route('zones.show', $zone));

        $this->assertSame('Jagung', $zone->fresh()->active_crop);

        $this->post(route('zones.care.refresh', $zone))->assertRedirect();

        $this->post(route('zones.plant.reset', $zone))
            ->assertRedirect(route('zones.show', $zone));

        $this->assertNull($zone->fresh()->active_crop);
    }

    public function test_device_management_buttons_work(): void
    {
        $user = User::factory()->create();

        $this->actingAs($user);

        $this->post(route('devices.store'), [
            'name' => 'ESP32 Blok A',
            'client_id' => 'esp32-blok-a',
            'connection_type' => 'Azure IoT Hub (MQTT)',
        ])->assertRedirect(route('devices.index'));

        $device = Device::where('client_id', 'esp32-blok-a')->firstOrFail();

        $this->get(route('devices.index'))
            ->assertOk()
            ->assertSee('ESP32 Blok A')
            ->assertSee(route('devices.destroy', $device), false);

        $this->delete(route('devices.destroy', $device))
            ->assertRedirect(route('devices.index'));

        $this->assertDatabaseMissing('devices', [
            'id' => $device->id,
        ]);
    }

    private function createZoneWithSamples(): Zone
    {
        $zone = Zone::create([
            'name' => 'Zona Alpha',
            'slug' => 'zona-alpha',
            'area_label' => 'Blok A',
            'location_description' => 'Dekat irigasi utama',
            'sample_target_count' => 3,
        ]);

        foreach ([
            ['A1', 6.4, 90, 32, 70, 36],
            ['A2', 6.5, 92, 34, 72, 38],
            ['A3', 6.6, 91, 33, 73, 37],
        ] as [$pointLabel, $ph, $nitrogen, $phosphorus, $potassium, $moisture]) {
            SoilData::create([
                'zone_id' => $zone->id,
                'source' => 'manual',
                'point_label' => $pointLabel,
                'ph' => $ph,
                'nitrogen' => $nitrogen,
                'phosphorus' => $phosphorus,
                'potassium' => $potassium,
                'soil_moisture' => $moisture,
                'sampled_at' => now()->subMinutes(10),
            ]);
        }

        return $zone;
    }
}
