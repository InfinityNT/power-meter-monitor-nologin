// Global variables
let API_BASE_URL = 'http://localhost:8080/api';
let powerData = {};
let charts = {};

// Initialize on page load
document.addEventListener('DOMContentLoaded', async function() {
    // Get configuration first
    await loadConfiguration();
    
    // Initialize charts
    initializeCharts();
    
    // Set up event listeners
    setupEventListeners();
    
    // Update date display
    updateDateDisplay();
    
    // Initial data fetch
    fetchPowerData();
    
    // Set up automatic refresh every 5 seconds
    setInterval(fetchPowerData, 5000);
});

// Load configuration from server
async function loadConfiguration() {
    try {
        const response = await fetch('/api/config');
        if (response.ok) {
            const config = await response.json();
            API_BASE_URL = config.API_BASE_URL || API_BASE_URL;
        }
    } catch (error) {
        console.error('Error loading configuration:', error);
    }
}

// Set up event listeners
function setupEventListeners() {
    // Refresh button
    document.getElementById('refreshBtn').addEventListener('click', fetchPowerData);
    
    // Time filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            updateChartsForTimeRange(this.dataset.filter);
        });
    });
    
    // Navigation items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

// Initialize all charts
function initializeCharts() {
    // Cost Donut Chart
    const costCtx = document.getElementById('costChart').getContext('2d');
    charts.cost = new Chart(costCtx, {
        type: 'doughnut',
        data: {
            labels: ['Electricidad', 'Gas'],
            datasets: [{
                data: [180, 34],
                backgroundColor: ['#00e4b5', '#ffd93d'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.label + ': $' + context.parsed;
                        }
                    }
                }
            }
        }
    });
    
    // Cost Change Bar Chart
    const costChangeCtx = document.getElementById('costChangeChart').getContext('2d');
    charts.costChange = new Chart(costChangeCtx, {
        type: 'bar',
        data: {
            labels: ['May', 'Jun'],
            datasets: [{
                data: [203, 214],
                backgroundColor: ['#00e4b5', '#00e4b5']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    min: 190,
                    ticks: {
                        callback: function(value) {
                            return '$' + value;
                        },
                        color: '#8892b0'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    }
                },
                x: {
                    ticks: { color: '#8892b0' },
                    grid: { display: false }
                }
            }
        }
    });
    
    // Usage Line Chart
    const usageCtx = document.getElementById('usageChart').getContext('2d');
    charts.usage = new Chart(usageCtx, {
        type: 'line',
        data: {
            labels: ['Jun 1', 'Jun 8', 'Jun 15', 'Jun 22', 'Jun 29'],
            datasets: [{
                data: [0, 100, 164, 300, 439],
                borderColor: '#ff4757',
                backgroundColor: 'rgba(255, 71, 87, 0.1)',
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#ff4757',
                pointBorderColor: '#ff4757',
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value + ' kWh';
                        },
                        color: '#8892b0'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    }
                },
                x: {
                    ticks: { color: '#8892b0' },
                    grid: { display: false }
                }
            }
        }
    });
    
    // Energy Intensity Gauge
    const intensityCtx = document.getElementById('intensityChart').getContext('2d');
    charts.intensity = new Chart(intensityCtx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [47, 53],
                backgroundColor: ['#00e4b5', 'rgba(255, 255, 255, 0.05)'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            rotation: -90,
            circumference: 180,
            cutout: '75%',
            plugins: {
                legend: { display: false },
                tooltip: { enabled: false }
            }
        }
    });
}

// Fetch power data from API
async function fetchPowerData() {
    document.getElementById('connectionStatus').textContent = 'Conectando...';
    
    try {
        const response = await fetch(`${API_BASE_URL}/power`);
        if (!response.ok) {
            throw new Error('Error de red');
        }
        
        powerData = await response.json();
        updateDashboard(powerData);
        
        const simMsg = powerData.simulated ? ' (Datos Simulados)' : '';
        document.getElementById('connectionStatus').textContent = 'Conectado' + simMsg;
    } catch (error) {
        console.error('Error obteniendo datos:', error);
        document.getElementById('connectionStatus').textContent = 'Error de conexión';
    }
}

// Update dashboard with new data
function updateDashboard(data) {
    // Get power values
    const power = data.system?.power_kw || data.power_kw || 0;
    const current = data.system?.current_avg || data.current_avg || 0;
    const voltage = data.system?.voltage_ln_avg || data.voltage_ln_avg || 0;
    const pf = data.system?.displacement_pf || data.power_factor || 0;
    const energy = data.system?.energy_kwh || data.energy_kwh || 0;
    
    // Calculate estimated cost (example rates)
    const electricityRate = 0.12; // $/kWh
    const estimatedMonthlyCost = power * 24 * 30 * electricityRate;
    const gasCost = 34; // Fixed gas cost for demo
    const totalCost = estimatedMonthlyCost + gasCost;
    
    // Update cost chart and display
    document.getElementById('totalCost').textContent = '$' + totalCost.toFixed(0);
    charts.cost.data.datasets[0].data = [estimatedMonthlyCost, gasCost];
    charts.cost.update();
    
    // Update usage estimate
    const daysInMonth = 30;
    const currentDay = new Date().getDate();
    const usageNow = (energy % 1000).toFixed(1); // Mock current month usage
    const usagePredicted = (usageNow / currentDay * daysInMonth).toFixed(0);
    
    document.getElementById('usageNow').textContent = usageNow + ' kWh';
    document.getElementById('usagePredicted').textContent = usagePredicted + ' kWh';
    
    // Update appliance data based on phase data
    if (data.phase_1) {
        updateAppliancesList(data);
    }
    
    // Update carbon footprint
    const co2Factor = 0.416; // kg CO2 per kWh
    const co2Emissions = (parseFloat(usageNow) * co2Factor).toFixed(1);
    const co2Predicted = (parseFloat(usagePredicted) * co2Factor).toFixed(1);
    
    document.querySelector('.emission-values .value').textContent = co2Emissions + ' Kg de CO2';
    document.querySelectorAll('.emission-values .value')[1].textContent = co2Predicted + ' Kg de CO2';
}

// Update appliances list with phase data
function updateAppliancesList(data) {
    const appliances = [
        { name: 'Calefacción y AC', power: data.phase_1?.power_kw || 0 },
        { name: 'Carga de VE', power: data.phase_2?.power_kw || 0 },
        { name: 'Cargas Enchufables', power: data.phase_3?.power_kw || 0 },
        { name: 'Refrigeración', power: (data.phase_1?.power_kw || 0) * 0.5 },
        { name: 'Iluminación', power: (data.phase_2?.power_kw || 0) * 0.3 }
    ];
    
    const maxPower = Math.max(...appliances.map(a => a.power));
    const applianceItems = document.querySelectorAll('.appliance-item');
    
    appliances.forEach((appliance, index) => {
        if (applianceItems[index]) {
            const item = applianceItems[index];
            const bar = item.querySelector('.appliance-bar');
            const value = item.querySelector('.appliance-value');
            
            const percentage = maxPower > 0 ? (appliance.power / maxPower * 100) : 0;
            bar.style.width = percentage + '%';
            value.textContent = appliance.power.toFixed(1) + ' kW';
        }
    });
}

// Update charts for different time ranges
function updateChartsForTimeRange(range) {
    // This would typically fetch data for the selected time range
    // For now, we'll just update the display
    console.log('Updating charts for range:', range);
}

// Update date display
function updateDateDisplay() {
    const months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
    const now = new Date();
    const monthYear = months[now.getMonth()] + ' ' + now.getFullYear();
    document.getElementById('currentDate').textContent = monthYear;
}