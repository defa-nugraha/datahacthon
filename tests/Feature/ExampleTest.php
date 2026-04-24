<?php

namespace Tests\Feature;

use App\Models\Zone;
use Illuminate\Foundation\Http\Middleware\PreventRequestForgery;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class ExampleTest extends TestCase
{
    use RefreshDatabase;

    /**
     * A basic test example.
     */
    public function test_the_application_returns_a_successful_response(): void
    {
        $response = $this->get('/');

        $response->assertStatus(200);
    }

    public function test_field_zones_page_is_accessible(): void
    {
        $response = $this->get('/zones');

        $response->assertStatus(200);
    }

    public function test_zone_detail_page_is_accessible(): void
    {
        $zone = Zone::create([
            'name' => 'Zona Alpha',
            'slug' => 'zona-alpha',
            'area_label' => 'Blok A',
            'location_description' => 'Dekat irigasi utama',
            'sample_target_count' => 8,
        ]);

        $response = $this->get(route('zones.show', $zone));

        $response->assertStatus(200);
        $response->assertSee('Zona Alpha');
        $response->assertSee('Input data sampling');
    }

    public function test_zone_can_be_updated(): void
    {
        $this->withoutMiddleware(PreventRequestForgery::class);

        $zone = Zone::create([
            'name' => 'Zona Beta',
            'slug' => 'zona-beta',
            'area_label' => 'Blok B',
            'location_description' => 'Lokasi awal',
            'sample_target_count' => 8,
        ]);

        $response = $this->put(route('zones.update', $zone), [
            'name' => 'Zona Beta Timur',
            'area_label' => 'Blok B2',
            'location_description' => 'Lokasi yang diperbarui',
            'sample_target_count' => 10,
        ]);

        $response->assertRedirect();
        $this->assertDatabaseHas('zones', [
            'id' => $zone->id,
            'name' => 'Zona Beta Timur',
            'area_label' => 'Blok B2',
            'sample_target_count' => 10,
        ]);
    }

    public function test_zone_can_be_deleted(): void
    {
        $this->withoutMiddleware(PreventRequestForgery::class);

        $zone = Zone::create([
            'name' => 'Zona Gamma',
            'slug' => 'zona-gamma',
            'area_label' => 'Blok C',
            'location_description' => 'Siap dihapus',
            'sample_target_count' => 8,
        ]);

        $response = $this->delete(route('zones.destroy', $zone));

        $response->assertRedirect(route('zones.index'));
        $this->assertDatabaseMissing('zones', [
            'id' => $zone->id,
        ]);
    }
}
