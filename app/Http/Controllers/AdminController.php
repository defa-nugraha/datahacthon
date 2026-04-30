<?php

namespace App\Http\Controllers;

use App\Models\Device;
use App\Models\SoilData;
use App\Models\User;
use App\Models\Zone;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\View\View;

class AdminController extends Controller
{
    public function index(): View
    {
        $users = User::query()->latest()->get();
        $zones = Zone::query()->withCount('soilData')->latest()->get();
        $devices = Device::query()->latest()->get();

        return view('admin.dashboard', [
            'stats' => [
                'total_users' => $users->count(),
                'farmers' => $users->where('role', 'farmer')->count(),
                'admins' => $users->where('role', 'admin')->count(),
                'total_zones' => $zones->count(),
                'active_zones' => $zones->filter(fn (Zone $zone) => filled($zone->active_crop))->count(),
                'samples_24h' => SoilData::where('sampled_at', '>=', now()->subDay())->count(),
                'devices' => $devices->count(),
                'online_devices' => $devices->where('status', 'online')->count(),
            ],
            'users' => $users,
            'zones' => $zones->take(8),
            'devices' => $devices->take(8),
        ]);
    }

    public function updateUserRole(Request $request, User $user): RedirectResponse
    {
        $data = $request->validate([
            'role' => ['required', 'in:admin,farmer'],
        ]);

        if ($request->user()->is($user) && $data['role'] !== 'admin') {
            return back()->withErrors(['role' => 'Admin tidak dapat menurunkan role akunnya sendiri.']);
        }

        $user->update(['role' => $data['role']]);

        return back()->with('success', 'Role '.$user->name.' berhasil diperbarui.');
    }
}
