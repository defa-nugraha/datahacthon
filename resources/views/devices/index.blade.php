<x-app-layout>
    <div class="mx-auto max-w-7xl space-y-6">
        <div class="flex items-center justify-between">
            <div>
                <h1 class="text-3xl font-extrabold tracking-tight text-slate-900">Device Management</h1>
                <p class="text-slate-500">Kelola koneksi hardware ESP32 dan Gateway ke Azure IoT Hub.</p>
            </div>
            <button x-data="" x-on:click.prevent="$dispatch('open-modal', 'add-device')" class="rounded-2xl bg-primary px-5 py-3 text-sm font-bold text-white shadow-panel hover:bg-success transition">
                <div class="flex items-center gap-2">
                    <span class="material-symbols-outlined">add</span>
                    Register New Device
                </div>
            </button>

            <x-modal name="add-device" focusable>
                <form method="post" action="{{ route('devices.store') }}" class="p-6">
                    @csrf
                    <h2 class="text-lg font-bold text-slate-900">Register New IoT Device</h2>
                    <p class="mt-1 text-sm text-slate-500">Masukkan detail device untuk mendapatkan akses ke Azure IoT Hub.</p>

                    <div class="mt-6 space-y-4">
                        <div>
                            <x-input-label for="name" value="Device Name" />
                            <x-text-input id="name" name="name" type="text" class="mt-1 block w-full" placeholder="Contoh: ESP32-Blok-A" required />
                        </div>

                        <div>
                            <x-input-label for="client_id" value="Device Connection ID (Client ID)" />
                            <x-text-input id="client_id" name="client_id" type="text" class="mt-1 block w-full" placeholder="Contoh: esp32_01" required />
                        </div>

                        <div>
                            <x-input-label for="connection_type" value="Protocol / Connection Type" />
                            <select name="connection_type" class="mt-1 block w-full rounded-xl border-outline bg-surface-soft text-sm focus:ring-primary">
                                <option value="Azure IoT Hub (MQTT)">Azure IoT Hub (MQTT)</option>
                                <option value="HTTP API Gateway">HTTP API Gateway</option>
                                <option value="Manual Input">Manual Input</option>
                            </select>
                        </div>
                    </div>

                    <div class="mt-6 flex justify-end gap-3">
                        <x-secondary-button x-on:click="$dispatch('close')">Batal</x-secondary-button>
                        <x-primary-button class="ms-3">Register Device</x-primary-button>
                    </div>
                </form>
            </x-modal>
        </div>

        <div class="rounded-3xl border border-outline bg-surface shadow-panel overflow-hidden">
            <table class="w-full text-left border-collapse">
                <thead class="bg-surface-soft border-b border-outline">
                    <tr>
                        <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-400">Device Name</th>
                        <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-400">Connection ID</th>
                        <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-400">Protocol</th>
                        <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-400">Status</th>
                        <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-400">Last Sync</th>
                        <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-400">Action</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-outline">
                    @foreach($devices as $device)
                    <tr class="hover:bg-slate-50 transition">
                        <td class="px-6 py-5">
                            <div class="flex items-center gap-3">
                                <div class="h-10 w-10 rounded-xl bg-primary-soft text-primary flex items-center justify-center">
                                    <span class="material-symbols-outlined">router</span>
                                </div>
                                <span class="font-bold text-slate-700">{{ $device->name }}</span>
                            </div>
                        </td>
                        <td class="px-6 py-5 font-mono text-xs text-slate-500">{{ $device->client_id }}</td>
                        <td class="px-6 py-5 text-sm text-slate-600">{{ $device->connection_type }}</td>
                        <td class="px-6 py-5">
                            <span class="inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-bold {{ $device->status === 'online' ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-500' }}">
                                <span class="h-2 w-2 rounded-full {{ $device->status === 'online' ? 'bg-emerald-500' : 'bg-slate-400' }}"></span>
                                {{ ucfirst($device->status) }}
                            </span>
                        </td>
                        <td class="px-6 py-5 text-sm text-slate-500">{{ $device->last_sync ? $device->last_sync->format('Y-m-d H:i:s') : 'Never' }}</td>
                        <td class="px-6 py-5 text-right">
                            <button class="text-slate-400 hover:text-primary transition">
                                <span class="material-symbols-outlined">settings_suggest</span>
                            </button>
                        </td>
                    </tr>
                    @endforeach
                </tbody>
            </table>
        </div>
    </div>
</x-app-layout>