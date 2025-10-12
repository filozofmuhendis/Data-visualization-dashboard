/**
 * WebSocket Client for MSA Dashboard
 * Handles real-time data updates from the server
 */

class DashboardWebSocket {
    constructor(url = 'ws://localhost:8000/ws') {
        this.url = url;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.callbacks = {};
        this.isConnected = false;
        
        this.connect();
    }
    
    connect() {
        try {
            this.ws = new WebSocket(this.url);
            
            this.ws.onopen = (event) => {
                console.log('WebSocket connected');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.onConnectionOpen(event);
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleMessage(data);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };
            
            this.ws.onclose = (event) => {
                console.log('WebSocket disconnected');
                this.isConnected = false;
                this.onConnectionClose(event);
                this.attemptReconnect();
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.onConnectionError(error);
            };
            
        } catch (error) {
            console.error('Failed to create WebSocket connection:', error);
            this.attemptReconnect();
        }
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            
            setTimeout(() => {
                this.connect();
            }, this.reconnectDelay * this.reconnectAttempts);
        } else {
            console.error('Max reconnection attempts reached');
        }
    }
    
    handleMessage(data) {
        console.log('WebSocket message received:', data);
        
        switch (data.type) {
            case 'demo_data_update':
                this.handleDemoDataUpdate(data);
                break;
            case 'pong':
                console.log('Pong received');
                break;
            case 'subscribed':
                console.log('Subscribed to channels:', data.channels);
                break;
            default:
                console.log('Unknown message type:', data.type);
        }
    }
    
    handleDemoDataUpdate(data) {
        const { data_type, data: updateData, timestamp } = data;
        
        // Trigger callbacks for this data type
        if (this.callbacks[data_type]) {
            this.callbacks[data_type].forEach(callback => {
                try {
                    callback(updateData, timestamp);
                } catch (error) {
                    console.error(`Error in callback for ${data_type}:`, error);
                }
            });
        }
        
        // Trigger general update callbacks
        if (this.callbacks['*']) {
            this.callbacks['*'].forEach(callback => {
                try {
                    callback(data_type, updateData, timestamp);
                } catch (error) {
                    console.error('Error in general callback:', error);
                }
            });
        }
    }
    
    // Subscribe to data type updates
    subscribe(dataType, callback) {
        if (!this.callbacks[dataType]) {
            this.callbacks[dataType] = [];
        }
        this.callbacks[dataType].push(callback);
        
        console.log(`Subscribed to ${dataType} updates`);
    }
    
    // Unsubscribe from data type updates
    unsubscribe(dataType, callback) {
        if (this.callbacks[dataType]) {
            const index = this.callbacks[dataType].indexOf(callback);
            if (index > -1) {
                this.callbacks[dataType].splice(index, 1);
            }
        }
    }
    
    // Send message to server
    send(message) {
        if (this.isConnected && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message));
        } else {
            console.warn('WebSocket not connected, message not sent:', message);
        }
    }
    
    // Send ping to keep connection alive
    ping() {
        this.send({ type: 'ping' });
    }
    
    // Subscribe to server channels
    subscribeToChannels(channels) {
        this.send({
            type: 'subscribe',
            channels: channels
        });
    }
    
    // Connection event handlers (can be overridden)
    onConnectionOpen(event) {
        // Send initial subscription
        this.subscribeToChannels(['units', 'alerts', 'missions', 'events']);
        
        // Start ping interval
        this.pingInterval = setInterval(() => {
            this.ping();
        }, 30000); // Ping every 30 seconds
    }
    
    onConnectionClose(event) {
        if (this.pingInterval) {
            clearInterval(this.pingInterval);
        }
    }
    
    onConnectionError(error) {
        // Override this method to handle connection errors
    }
    
    // Close connection
    close() {
        if (this.pingInterval) {
            clearInterval(this.pingInterval);
        }
        if (this.ws) {
            this.ws.close();
        }
    }
}

// Global WebSocket instance
let dashboardWS = null;

// Initialize WebSocket when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    dashboardWS = new DashboardWebSocket();
    
    // Example usage: Subscribe to units updates
    dashboardWS.subscribe('units', function(data, timestamp) {
        console.log('Units updated:', data);
        // Update UI components here
    });
    
    // Example usage: Subscribe to alerts updates
    dashboardWS.subscribe('alerts', function(data, timestamp) {
        console.log('Alerts updated:', data);
        // Update alert components here
    });
    
    // Example usage: Subscribe to all updates
    dashboardWS.subscribe('*', function(dataType, data, timestamp) {
        console.log(`Data update received for ${dataType}:`, data);
        // Handle any data type update
    });
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DashboardWebSocket;
}