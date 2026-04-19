document.addEventListener("DOMContentLoaded", function() {
    // Ambil data dari jembatan global window
    const rawData = window.soilData; 
    const ctx = document.getElementById('soilChart').getContext('2d');

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: rawData.labels,
            datasets: [
                {
                    label: 'Nitrogen (N)',
                    data: rawData.nitrogen,
                    borderColor: '#3b82f6',
                    backgroundColor: '#3b82f6',
                    tension: 0.4
                },
                {
                    label: 'Fosfor (P)',
                    data: rawData.phosphorus,
                    borderColor: '#ef4444',
                    backgroundColor: '#ef4444',
                    tension: 0.4
                },
                {
                    label: 'Kalium (K)',
                    data: rawData.potassium,
                    borderColor: '#10b981',
                    backgroundColor: '#10b981',
                    tension: 0.4
                },
                {
                    label: 'pH Tanah',
                    data: rawData.ph,
                    borderColor: '#eab308',
                    backgroundColor: '#eab308',
                    borderDash: [5, 5],
                    tension: 0.4,
                    yAxisID: 'y_ph'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            scales: {
                y: { type: 'linear', display: true, position: 'left' },
                y_ph: { type: 'linear', display: true, position: 'right', grid: { drawOnChartArea: false } }
            }
        }
    });
});