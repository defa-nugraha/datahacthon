<?php

namespace App\Http\Controllers;

use App\Models\Device;
use App\Models\SoilData;
use App\Models\Zone;
use App\Services\AiAdvisorService;
use App\Services\ZoneAnalyticsService;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Str;
use Illuminate\View\View;

class SoilDataController extends Controller
{
    public function index(Request $request, ZoneAnalyticsService $analytics): View|RedirectResponse
    {
        if ($request->user()?->isAdmin()) {
            return redirect()->route('admin.dashboard');
        }

        return view('welcome', $analytics->buildDashboardSummary());
    }

    public function history(ZoneAnalyticsService $analytics): View
    {
        return view('history', [
            'historicalData' => $analytics->zoneLedger(),
        ]);
    }

    public function zones(ZoneAnalyticsService $analytics): View
    {
        return view('zones.index', [
            'zones' => Zone::with('soilData')->get()->map(fn (Zone $zone) => $analytics->buildZoneCard($zone)),
        ]);
    }

    public function storeZone(Request $request): RedirectResponse
    {
        $data = $this->validateZone($request);

        $baseSlug = Str::slug($data['name']);
        $slug = $baseSlug;
        $counter = 2;

        while (Zone::where('slug', $slug)->exists()) {
            $slug = $baseSlug.'-'.$counter;
            $counter++;
        }

        $zone = Zone::create([
            'name' => $data['name'],
            'slug' => $slug,
            'area_label' => $data['area_label'] ?: 'Blok baru',
            'location_description' => $data['location_description'] ?: 'Belum ada deskripsi lokasi',
            'sample_target_count' => $data['sample_target_count'] ?? 8,
        ]);

        return redirect()->route('zones.show', $zone)->with('success', 'Zona baru berhasil dibuat.');
    }

    public function updateZone(Request $request, Zone $zone): RedirectResponse
    {
        $data = $this->validateZone($request);

        $zone->update([
            'name' => $data['name'],
            'area_label' => $data['area_label'] ?: 'Blok baru',
            'location_description' => $data['location_description'] ?: 'Belum ada deskripsi lokasi',
            'sample_target_count' => $data['sample_target_count'] ?? 8,
        ]);

        return back()->with('success', 'Zona '.$zone->name.' berhasil diperbarui.');
    }

    public function destroyZone(Zone $zone): RedirectResponse
    {
        $zoneName = $zone->name;
        $zone->careAdvices()->delete();
        $zone->soilData()->delete();
        $zone->delete();

        return redirect()->route('zones.index')->with('success', 'Zona '.$zoneName.' berhasil dihapus.');
    }

    public function showZone(Zone $zone, ZoneAnalyticsService $analytics, AiAdvisorService $advisor): View
    {
        $history = $analytics->lastHourHistory($zone);

        if (filled($zone->active_crop) && $history->isNotEmpty()) {
            $advisor->generateCareAdvice($zone, $history);
            $zone->load('careAdvices');
        }

        return view('zones.show', $analytics->buildZoneDetail($zone));
    }

    public function monitorZone(Zone $zone, ZoneAnalyticsService $analytics, AiAdvisorService $advisor): View
    {
        $history = $analytics->lastHourHistory($zone);

        if (filled($zone->active_crop) && $history->isNotEmpty()) {
            $advisor->generateCareAdvice($zone, $history);
            $zone->load('careAdvices');
        }

        return view('zones.monitor', [
            'zone' => $zone,
            'monitoring' => $analytics->buildMonitoringView($zone),
        ]);
    }

    public function samplingForm(Zone $zone): RedirectResponse
    {
        return redirect()->route('zones.show', ['zone' => $zone, 'modal' => 'sampling-create-modal']);
    }

    public function storeSampling(Request $request, Zone $zone): RedirectResponse
    {
        $data = $request->validate([
            'point_label' => ['required', 'array', 'min:1'],
            'point_label.*' => ['required', 'string', 'max:60'],
            'ph' => ['required', 'array'],
            'ph.*' => ['required', 'numeric', 'between:0,14'],
            'nitrogen' => ['required', 'array'],
            'nitrogen.*' => ['required', 'numeric', 'min:0'],
            'phosphorus' => ['required', 'array'],
            'phosphorus.*' => ['required', 'numeric', 'min:0'],
            'potassium' => ['required', 'array'],
            'potassium.*' => ['required', 'numeric', 'min:0'],
            'soil_moisture' => ['nullable', 'array'],
            'soil_moisture.*' => ['nullable', 'numeric', 'min:0', 'max:100'],
            'sampled_at' => ['nullable', 'date'],
        ]);

        foreach ($data['point_label'] as $index => $pointLabel) {
            SoilData::create([
                'zone_id' => $zone->id,
                'source' => 'manual',
                'point_label' => $pointLabel,
                'nitrogen' => $data['nitrogen'][$index],
                'phosphorus' => $data['phosphorus'][$index],
                'potassium' => $data['potassium'][$index],
                'ph' => $data['ph'][$index],
                'soil_moisture' => $data['soil_moisture'][$index] ?? null,
                'sampled_at' => $data['sampled_at'] ? now()->parse($data['sampled_at']) : now(),
            ]);
        }

        $zone->update([
            'status' => $zone->soilData()->count() >= $zone->sample_target_count ? 'siap_analisis' : 'butuh_sampling',
        ]);

        return redirect()->route('zones.show', $zone)->with('success', 'Data sampling zona berhasil disimpan.');
    }

    public function analyzeZone(Zone $zone, ZoneAnalyticsService $analytics, AiAdvisorService $advisor): View
    {
        $samples = $analytics->buildPredictionSamples($zone);

        abort_if($samples->count() < 3, 422, 'Zona membutuhkan minimal 3 titik sampling sebelum dianalisis.');

        $prediction = $advisor->predictZone($zone, $samples);

        return view('recommendation', $prediction);
    }

    public function analyzeManual(Request $request, ZoneAnalyticsService $analytics, AiAdvisorService $advisor): View
    {
        $data = $request->validate([
            'zone_name' => ['nullable', 'string', 'max:120'],
            'ph' => ['required', 'numeric', 'between:0,14'],
            'nitrogen' => ['required', 'numeric', 'min:0'],
            'phosphorus' => ['required', 'numeric', 'min:0'],
            'potassium' => ['required', 'numeric', 'min:0'],
            'soil_moisture' => ['nullable', 'numeric', 'min:0', 'max:100'],
        ]);

        $zone = Zone::firstOrCreate(
            ['slug' => 'zona-manual'],
            [
                'name' => $data['zone_name'] ?? 'Zona Manual',
                'area_label' => 'Mode cepat',
                'location_description' => 'Zona analisis cepat dari dashboard',
                'sample_target_count' => 3,
            ]
        );

        SoilData::create([
            'zone_id' => $zone->id,
            'source' => 'manual',
            'point_label' => 'Quick-'.now()->format('His'),
            'nitrogen' => $data['nitrogen'],
            'phosphorus' => $data['phosphorus'],
            'potassium' => $data['potassium'],
            'ph' => $data['ph'],
            'soil_moisture' => $data['soil_moisture'] ?? null,
            'sampled_at' => now(),
        ]);

        $samples = $analytics->buildPredictionSamples($zone);
        $prediction = $advisor->predictZone($zone, $samples);

        return view('recommendation', $prediction);
    }

    public function startPlanting(Request $request, Zone $zone): RedirectResponse
    {
        $data = $request->validate([
            'crop_name' => ['required', 'string', 'max:120'],
        ]);

        $zone->update([
            'active_crop' => $data['crop_name'],
            'status' => 'sedang_ditanam',
        ]);

        return redirect()->route('zones.show', $zone)->with('success', 'Tanaman aktif untuk '.$zone->name.' diperbarui ke '.$data['crop_name'].'.');
    }

    public function resetPlanting(Zone $zone): RedirectResponse
    {
        $zone->update([
            'active_crop' => null,
            'status' => $zone->soilData()->count() >= $zone->sample_target_count ? 'siap_analisis' : 'butuh_sampling',
        ]);

        return redirect()->route('zones.show', $zone)->with('success', 'Tanaman aktif pada '.$zone->name.' berhasil dihapus.');
    }

    public function refreshCareAdvice(Zone $zone, ZoneAnalyticsService $analytics, AiAdvisorService $advisor): RedirectResponse
    {
        $history = $analytics->lastHourHistory($zone);
        $advisor->generateCareAdvice($zone, $history, true);

        return back()->with('success', 'Adaptive advice berhasil diperbarui untuk '.$zone->name.'.');
    }

    protected function validateZone(Request $request): array
    {
        return $request->validate([
            'name' => ['required', 'string', 'max:120'],
            'area_label' => ['nullable', 'string', 'max:120'],
            'location_description' => ['nullable', 'string', 'max:160'],
            'sample_target_count' => ['nullable', 'integer', 'min:3', 'max:24'],
        ]);
    }

    public function devices(): View
    {
        $devices = \App\Models\Device::latest()->get()->map(function ($device) {
            // Jika data terakhir masuk lebih dari 5 menit, set offline otomatis
            if ($device->last_sync && $device->last_sync->diffInMinutes(now()) > 5) {
                $device->status = 'offline';
            }
            return $device;
        });

        return view('devices.index', compact('devices'));
    }

    public function storeDevice(Request $request)
    {
        $validated = $request->validate([
            'name' => 'required|string|max:255',
            'client_id' => 'required|string|unique:devices,client_id',
            'connection_type' => 'required|string',
        ]);

        Device::create([
            'name' => $validated['name'],
            'client_id' => $validated['client_id'],
            'connection_type' => $validated['connection_type'],
            'status' => 'offline', // Default awal pasti offline
        ]);

        return redirect()->route('devices.index')->with('success', 'Device berhasil didaftarkan!');
    }

    public function destroyDevice(Device $device): RedirectResponse
    {
        $device->delete();

        return redirect()->route('devices.index')->with('success', 'Device berhasil dihapus.');
    }
}
