/**
 * Dashboard Integration Script
 * Integrates WebSocket real-time updates with Dash components
 */

// Dashboard integration functions
class DashboardIntegration {
    constructor() {
        this.wsClient = null;
        this.updateCallbacks = {};
        this.init();
    }
    
    init() {
        // Wait for WebSocket client to be available
        const checkWebSocket = () => {
            if (typeof dashboardWS !== 'undefined' && dashboardWS) {
                this.wsClient = dashboardWS;
                this.setupSubscriptions();
                console.log('Dashboard integration initialized');
            } else {
                setTimeout(checkWebSocket, 100);
            }
        };
        checkWebSocket();
    }
    
    setupSubscriptions() {
        // Subscribe to units updates
        this.wsClient.subscribe('units', (data, timestamp) => {
            this.updateUnitsDisplay(data);
        });
        
        // Subscribe to alerts updates
        this.wsClient.subscribe('alerts', (data, timestamp) => {
            this.updateAlertsDisplay(data);
        });
        
        // Subscribe to dashboard summary updates
        this.wsClient.subscribe('dashboard_summary', (data, timestamp) => {
            this.updateDashboardSummary(data);
        });
    }
    
    updateUnitsDisplay(unitsData) {
        console.log('Updating units display with:', unitsData);
        
        // Update unit status indicators
        this.updateUnitStatusIndicators(unitsData);
        
        // Update unit map if available
        this.updateUnitMap(unitsData);
        
        // Trigger Dash callback if needed
        this.triggerDashCallback('units-update', unitsData);
    }
    
    updateAlertsDisplay(alertsData) {
        console.log('Updating alerts display with:', alertsData);
        
        // Update alert counters
        this.updateAlertCounters(alertsData);
        
        // Update alert list
        this.updateAlertList(alertsData);
        
        // Trigger Dash callback if needed
        this.triggerDashCallback('alerts-update', alertsData);
    }
    
    updateDashboardSummary(summaryData) {
        console.log('Updating dashboard summary with:', summaryData);
        
        // Update summary cards
        this.updateSummaryCards(summaryData);
        
        // Trigger Dash callback if needed
        this.triggerDashCallback('summary-update', summaryData);
    }
    
    updateUnitStatusIndicators(unitsData) {
        // Update unit status indicators in the UI
        const statusCounts = {
            active: 0,
            inactive: 0,
            maintenance: 0
        };
        
        unitsData.forEach(unit => {
            if (unit.status) {
                statusCounts[unit.status.toLowerCase()] = (statusCounts[unit.status.toLowerCase()] || 0) + 1;
            }
        });
        
        // Update DOM elements if they exist
        const activeElement = document.getElementById('active-units-count');
        const inactiveElement = document.getElementById('inactive-units-count');
        const maintenanceElement = document.getElementById('maintenance-units-count');
        
        if (activeElement) activeElement.textContent = statusCounts.active;
        if (inactiveElement) inactiveElement.textContent = statusCounts.inactive;
        if (maintenanceElement) maintenanceElement.textContent = statusCounts.maintenance;
    }
    
    updateAlertCounters(alertsData) {
        // Update alert counters in the UI
        const alertCounts = {
            critical: 0,
            warning: 0,
            info: 0
        };
        
        alertsData.forEach(alert => {
            if (alert.severity) {
                alertCounts[alert.severity.toLowerCase()] = (alertCounts[alert.severity.toLowerCase()] || 0) + 1;
            }
        });
        
        // Update DOM elements if they exist
        const criticalElement = document.getElementById('critical-alerts-count');
        const warningElement = document.getElementById('warning-alerts-count');
        const infoElement = document.getElementById('info-alerts-count');
        
        if (criticalElement) criticalElement.textContent = alertCounts.critical;
        if (warningElement) warningElement.textContent = alertCounts.warning;
        if (infoElement) infoElement.textContent = alertCounts.info;
    }
    
    updateAlertList(alertsData) {
        // Update alert list in the UI
        const alertListElement = document.getElementById('alerts-list');
        if (alertListElement) {
            // Clear existing alerts
            alertListElement.innerHTML = '';
            
            // Add new alerts
            alertsData.slice(0, 5).forEach(alert => { // Show only first 5
                const alertElement = document.createElement('div');
                alertElement.className = `alert-item alert-${alert.severity?.toLowerCase() || 'info'}`;
                alertElement.innerHTML = `
                    <div class="alert-severity">${alert.severity || 'INFO'}</div>
                    <div class="alert-message">${alert.message || 'No message'}</div>
                    <div class="alert-time">${new Date(alert.timestamp || Date.now()).toLocaleTimeString()}</div>
                `;
                alertListElement.appendChild(alertElement);
            });
        }
    }
    
    updateSummaryCards(summaryData) {
        // Update summary cards in the UI
        if (summaryData.total_units !== undefined) {
            const totalUnitsElement = document.getElementById('total-units-count');
            if (totalUnitsElement) totalUnitsElement.textContent = summaryData.total_units;
        }
        
        if (summaryData.active_alerts !== undefined) {
            const activeAlertsElement = document.getElementById('active-alerts-count');
            if (activeAlertsElement) activeAlertsElement.textContent = summaryData.active_alerts;
        }
    }
    
    updateUnitMap(unitsData) {
        // Update unit positions on map if map component exists
        // This would integrate with Plotly map components
        console.log('Map update requested for units:', unitsData.length);
    }
    
    triggerDashCallback(callbackType, data) {
        // Trigger Dash callbacks by updating hidden div content
        const callbackElement = document.getElementById(`ws-${callbackType}-trigger`);
        if (callbackElement) {
            callbackElement.textContent = JSON.stringify({
                timestamp: Date.now(),
                data: data
            });
            
            // Dispatch custom event for Dash to pick up
            const event = new CustomEvent('dashUpdate', {
                detail: {
                    type: callbackType,
                    data: data
                }
            });
            document.dispatchEvent(event);
        }
    }
    
    // Manual refresh function
    refreshData() {
        if (this.wsClient && this.wsClient.isConnected) {
            // Send refresh request to server
            this.wsClient.send({
                type: 'refresh_request',
                timestamp: Date.now()
            });
        }
    }
}

// Initialize dashboard integration when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Wait a bit for other scripts to load
    setTimeout(() => {
        window.dashboardIntegration = new DashboardIntegration();
    }, 500);
});

// Add CSS for alert styling
const style = document.createElement('style');
style.textContent = `
    .alert-item {
        padding: 8px 12px;
        margin: 4px 0;
        border-radius: 4px;
        border-left: 4px solid;
        background: rgba(255, 255, 255, 0.1);
    }
    
    .alert-critical {
        border-left-color: #dc3545;
        background: rgba(220, 53, 69, 0.1);
    }
    
    .alert-warning {
        border-left-color: #ffc107;
        background: rgba(255, 193, 7, 0.1);
    }
    
    .alert-info {
        border-left-color: #17a2b8;
        background: rgba(23, 162, 184, 0.1);
    }
    
    .alert-severity {
        font-weight: bold;
        font-size: 0.8em;
        text-transform: uppercase;
    }
    
    .alert-message {
        margin: 4px 0;
    }
    
    .alert-time {
        font-size: 0.7em;
        opacity: 0.7;
    }
`;
document.head.appendChild(style);