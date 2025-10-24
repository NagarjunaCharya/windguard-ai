/**
 * ============================================================================
 * WindGuard AI - Main TypeScript Application
 * ============================================================================
 * Description: Client-side application for wind turbine monitoring dashboard
 * Features: Real-time data fetching, chart rendering, prediction display
 * ============================================================================
 */

// Configuration
const CONFIG = {
    API_BASE_URL: 'http://localhost:8000/api/v1',
    REFRESH_INTERVAL: 30000, // 30 seconds
    CHART_UPDATE_INTERVAL: 5000, // 5 seconds
};

// Types
interface TurbineData {
    turbine_id: string;
    timestamp: string;
    wind_speed: number;
    vibration: number;
    gearbox_temperature: number;
    yaw_position: number;
    rotor_speed: number;
    power_output: number;
}

interface PredictionResponse {
    turbine_id: string;
    prediction_time: string;
    failure_probability: number;
    risk_level: string;
    predicted_failure_time: string | null;
    confidence: number | null;
    anomaly_score: number;
    recommendations: string[];
}

interface HealthStatus {
    turbine_id: string;
    status: string;
    overall_health_score: number;
    last_updated: string;
    active_alerts: number;
    metrics: {
        [key: string]: number;
    };
}

interface DataSummary {
    total_records: number;
    date_range_start: string;
    date_range_end: string;
    anomaly_count: number;
    anomaly_rate: number;
    turbines_monitored: string[];
}

// API Service
class APIService {
    private baseURL: string;

    constructor(baseURL: string) {
        this.baseURL = baseURL;
    }

    async fetch<T>(endpoint: string): Promise<T> {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`API Error fetching ${endpoint}:`, error);
            throw error;
        }
    }

    async post<T>(endpoint: string, data: any): Promise<T> {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`API Error posting to ${endpoint}:`, error);
            throw error;
        }
    }

    async getDataSummary(): Promise<DataSummary> {
        return this.fetch<DataSummary>('/data/summary');
    }

    async getTurbineData(turbineId: string, limit: number = 100): Promise<any> {
        return this.fetch(`/data/turbine/${turbineId}?limit=${limit}`);
    }

    async getHealthStatus(turbineId: string): Promise<HealthStatus> {
        return this.fetch<HealthStatus>(`/health-status/${turbineId}`);
    }

    async predictFailure(turbineId: string, horizon: number = 72): Promise<PredictionResponse> {
        return this.post<PredictionResponse>('/predict', {
            turbine_id: turbineId,
            prediction_horizon_hours: horizon,
            include_confidence: true,
        });
    }

    async getAnomalies(turbineId?: string): Promise<any> {
        const query = turbineId ? `?turbine_id=${turbineId}` : '';
        return this.fetch(`/analytics/anomalies${query}`);
    }
}

// Chart Service
class ChartService {
    private timeSeriesChart: any = null;
    private anomalyChart: any = null;

    initTimeSeriesChart(ctx: any, data: any): void {
        if (this.timeSeriesChart) {
            this.timeSeriesChart.destroy();
        }

        this.timeSeriesChart = new (window as any).Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [
                    {
                        label: 'Wind Speed (m/s)',
                        data: data.windSpeed,
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.4,
                        yAxisID: 'y',
                    },
                    {
                        label: 'Power Output (kW)',
                        data: data.powerOutput,
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        tension: 0.4,
                        yAxisID: 'y1',
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    legend: {
                        labels: {
                            color: '#cbd5e1',
                        },
                    },
                },
                scales: {
                    x: {
                        ticks: { color: '#94a3b8' },
                        grid: { color: '#334155' },
                    },
                    y: {
                        type: 'linear',
                        position: 'left',
                        ticks: { color: '#94a3b8' },
                        grid: { color: '#334155' },
                        title: {
                            display: true,
                            text: 'Wind Speed (m/s)',
                            color: '#cbd5e1',
                        },
                    },
                    y1: {
                        type: 'linear',
                        position: 'right',
                        ticks: { color: '#94a3b8' },
                        grid: { display: false },
                        title: {
                            display: true,
                            text: 'Power Output (kW)',
                            color: '#cbd5e1',
                        },
                    },
                },
            },
        });
    }

    initAnomalyChart(ctx: any, data: any): void {
        if (this.anomalyChart) {
            this.anomalyChart.destroy();
        }

        this.anomalyChart = new (window as any).Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [
                    {
                        label: 'Anomalies',
                        data: data.counts,
                        backgroundColor: [
                            '#10b981',
                            '#f59e0b',
                            '#ef4444',
                            '#3b82f6',
                        ],
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false,
                    },
                },
                scales: {
                    x: {
                        ticks: { color: '#94a3b8' },
                        grid: { color: '#334155' },
                    },
                    y: {
                        ticks: { color: '#94a3b8' },
                        grid: { color: '#334155' },
                    },
                },
            },
        });
    }
}

// Dashboard Controller
class Dashboard {
    private api: APIService;
    private charts: ChartService;
    private turbines: string[] = ['WT001', 'WT002', 'WT003', 'WT004'];

    constructor() {
        this.api = new APIService(CONFIG.API_BASE_URL);
        this.charts = new ChartService();
        this.init();
    }

    async init(): Promise<void> {
        console.log('🚀 Initializing WindGuard AI Dashboard...');
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Load initial data
        await this.loadDashboard();
        
        // Setup auto-refresh
        setInterval(() => this.loadDashboard(), CONFIG.REFRESH_INTERVAL);
        
        console.log('✅ Dashboard initialized');
    }

    setupEventListeners(): void {
        // Refresh button
        document.getElementById('refreshBtn')?.addEventListener('click', () => {
            this.loadDashboard();
        });

        // Predict all button
        document.getElementById('predictAllBtn')?.addEventListener('click', () => {
            this.predictAllTurbines();
        });

        // Turbine selector
        document.getElementById('turbineSelect')?.addEventListener('change', (e) => {
            const target = e.target as HTMLSelectElement;
            this.updateCharts(target.value);
        });
    }

    async loadDashboard(): Promise<void> {
        this.showLoading(true);
        
        try {
            // Load data summary
            const summary = await this.api.getDataSummary();
            this.updateOverviewCards(summary);
            
            // Load turbine statuses
            await this.loadTurbineStatuses();
            
            // Load charts
            await this.updateCharts('all');
            
            // Load predictions
            await this.loadPredictions();
            
        } catch (error) {
            console.error('Error loading dashboard:', error);
            this.showError('Failed to load dashboard data. Is the backend running?');
        } finally {
            this.showLoading(false);
        }
    }

    updateOverviewCards(summary: DataSummary): void {
        // Update active turbines
        const activeTurbinesEl = document.getElementById('activeTurbines');
        if (activeTurbinesEl) {
            activeTurbinesEl.textContent = summary.turbines_monitored.length.toString();
        }

        // Update anomaly count
        const anomalyCountEl = document.getElementById('anomalyCount');
        if (anomalyCountEl) {
            anomalyCountEl.textContent = summary.anomaly_count.toString();
        }

        // Calculate total power (mock for now)
        const totalPowerEl = document.getElementById('totalPower');
        if (totalPowerEl) {
            const mockPower = (Math.random() * 3 + 6).toFixed(1);
            totalPowerEl.innerHTML = `${mockPower} <span class="unit">MW</span>`;
        }

        // Calculate system health
        const systemHealthEl = document.getElementById('systemHealth');
        if (systemHealthEl) {
            const health = Math.round((1 - summary.anomaly_rate) * 100);
            systemHealthEl.textContent = `${health}%`;
        }
    }

    async loadTurbineStatuses(): Promise<void> {
        const grid = document.getElementById('turbinesGrid');
        if (!grid) return;

        grid.innerHTML = '';

        for (const turbineId of this.turbines) {
            try {
                const status = await this.api.getHealthStatus(turbineId);
                const card = this.createTurbineCard(status);
                grid.appendChild(card);
            } catch (error) {
                console.error(`Error loading status for ${turbineId}:`, error);
            }
        }
    }

    createTurbineCard(status: HealthStatus): HTMLElement {
        const card = document.createElement('div');
        card.className = `turbine-card status-${status.status}`;
        
        const statusClass = status.status === 'healthy' ? 'healthy' :
                           status.status === 'warning' ? 'warning' : 'critical';
        
        card.innerHTML = `
            <div class="turbine-header">
                <h3 class="turbine-id">${status.turbine_id}</h3>
                <span class="turbine-status-badge ${statusClass}">
                    ${status.status}
                </span>
            </div>
            <div class="turbine-metrics">
                <div class="metric">
                    <span class="metric-label">Health Score</span>
                    <span class="metric-value">${status.overall_health_score.toFixed(1)}%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Active Alerts</span>
                    <span class="metric-value">${status.active_alerts}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Uptime</span>
                    <span class="metric-value">${status.metrics.uptime_percentage?.toFixed(1) || 95}%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Efficiency</span>
                    <span class="metric-value">${status.metrics.power_efficiency?.toFixed(1) || 92}%</span>
                </div>
            </div>
            <button class="btn btn-primary btn-predict" data-turbine="${status.turbine_id}">
                <i class="fas fa-brain"></i> Predict
            </button>
        `;

        // Add predict button listener
        const predictBtn = card.querySelector('.btn-predict');
        predictBtn?.addEventListener('click', () => {
            this.predictFailure(status.turbine_id);
        });

        return card;
    }

    async updateCharts(turbineId: string): Promise<void> {
        // Mock chart data for now
        const hours = 24;
        const labels = Array.from({ length: hours }, (_, i) => `${i}:00`);
        
        const windSpeed = Array.from({ length: hours }, () => 
            Math.random() * 15 + 5
        );
        
        const powerOutput = windSpeed.map(ws => 
            Math.pow(ws / 25, 3) * 3000 + Math.random() * 200
        );

        // Time series chart
        const timeSeriesCtx = document.getElementById('timeSeriesChart');
        if (timeSeriesCtx) {
            this.charts.initTimeSeriesChart(timeSeriesCtx, {
                labels,
                windSpeed,
                powerOutput,
            });
        }

        // Anomaly chart
        const anomalyCtx = document.getElementById('anomalyChart');
        if (anomalyCtx) {
            this.charts.initAnomalyChart(anomalyCtx, {
                labels: this.turbines,
                counts: [2, 5, 3, 2],
            });
        }
    }

    async predictFailure(turbineId: string): Promise<void> {
        try {
            this.showLoading(true);
            const prediction = await this.api.predictFailure(turbineId);
            this.displayPredictionResult(prediction);
        } catch (error) {
            console.error(`Prediction error for ${turbineId}:`, error);
            this.showError(`Failed to predict for ${turbineId}`);
        } finally {
            this.showLoading(false);
        }
    }

    async predictAllTurbines(): Promise<void> {
        for (const turbineId of this.turbines) {
            await this.predictFailure(turbineId);
        }
        await this.loadPredictions();
    }

    displayPredictionResult(prediction: PredictionResponse): void {
        // Show alert with prediction
        alert(`Prediction for ${prediction.turbine_id}:\n\n` +
              `Failure Probability: ${(prediction.failure_probability * 100).toFixed(1)}%\n` +
              `Risk Level: ${prediction.risk_level.toUpperCase()}\n` +
              `Confidence: ${prediction.confidence ? (prediction.confidence * 100).toFixed(1) + '%' : 'N/A'}\n\n` +
              `Recommendations:\n${prediction.recommendations.join('\n')}`);
    }

    async loadPredictions(): Promise<void> {
        const tbody = document.getElementById('predictionsBody');
        if (!tbody) return;

        tbody.innerHTML = '';

        // Load predictions for all turbines (mock data for now)
        for (const turbineId of this.turbines) {
            try {
                const prediction = await this.api.predictFailure(turbineId);
                const row = this.createPredictionRow(prediction);
                tbody.appendChild(row);
            } catch (error) {
                console.error(`Error loading prediction for ${turbineId}:`, error);
            }
        }
    }

    createPredictionRow(prediction: PredictionResponse): HTMLElement {
        const row = document.createElement('tr');
        
        const failureTime = prediction.predicted_failure_time 
            ? new Date(prediction.predicted_failure_time).toLocaleString()
            : 'N/A';
        
        row.innerHTML = `
            <td>${prediction.turbine_id}</td>
            <td>${new Date(prediction.prediction_time).toLocaleString()}</td>
            <td>${(prediction.failure_probability * 100).toFixed(1)}%</td>
            <td><span class="risk-badge ${prediction.risk_level}">${prediction.risk_level}</span></td>
            <td>${failureTime}</td>
            <td>
                <button class="btn btn-secondary btn-sm">View Details</button>
            </td>
        `;

        return row;
    }

    showLoading(show: boolean): void {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.classList.toggle('active', show);
        }
    }

    showError(message: string): void {
        console.error(message);
        // In production, use a proper notification system
        alert(message);
    }
}

// Initialize dashboard when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new Dashboard();
    });
} else {
    new Dashboard();
}

// Export for use in other modules
export { Dashboard, APIService, ChartService };
