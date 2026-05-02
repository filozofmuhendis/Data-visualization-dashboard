# MSA Dashboard - Military Situational Awareness Dashboard

A comprehensive real-time military situational awareness dashboard built with FastAPI, Dash, and PostgreSQL. This system provides role-based access control, real-time data visualization, and advanced military operational monitoring capabilities.

## 🚀 Features

### Core Capabilities
- **Real-time Data Visualization**: Live updates via WebSocket connections
- **Role-Based Access Control**: Commander, Health Officer, and Operations Analyst roles
- **Interactive Tactical Map**: Unit positions, threats, and mission areas
- **Health Monitoring**: Personnel vital signs and stress levels
- **Logistics Tracking**: Fuel, ammunition, medical supplies, and food status
- **Alert Management**: Automated rule-based alerting with acknowledgment system
- **Mission Planning**: Mission objectives and timeline tracking
- **Data Fusion**: Multi-source intelligence integration

### Technical Features
- **Authentication**: JWT-based secure authentication
- **Database**: PostgreSQL with optional TimescaleDB for time-series data
- **API**: RESTful API with comprehensive endpoints
- **Real-time Updates**: WebSocket integration for live data streaming
- **Data Simulation**: Built-in simulators for testing and demonstration
- **Responsive Design**: Military-themed UI with role-specific layouts

## 🏗️ Architecture

```
MSA Dashboard/
├── app/                    # Main application
│   ├── main.py            # FastAPI application with Dash integration
│   ├── dash_layout.py     # Dashboard UI components
│   ├── dash_callbacks.py  # Interactive callbacks and data handling
│   └── assets/            # CSS styles and static assets
├── core/                  # Core configuration and database
│   ├── database.py        # Database connection and models
│   ├── models.py          # SQLAlchemy ORM models
│   ├── settings.py        # Application configuration
│   └── schemas.sql        # Database schema definition
├── services/              # Business logic services
│   ├── role_manager.py    # Authentication and role management
│   ├── rules.py           # Alert rules engine
│   └── fusion.py          # Data fusion and analysis
├── ingest/                # Data ingestion and simulation
│   ├── simulator.py       # Military data simulator
│   ├── mqtt_consumer.py   # MQTT data ingestion
│   └── drone_feed_mock.py # Drone surveillance simulation
└── tests/                 # Test suite
```

## 🛠️ Installation

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Git

### Quick Start

1. **Clone the repository**
```bash
git clone <repository-url>
cd Data-visualization-dashboard
```

2. **Create virtual environment**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
Create a `.env` file in the root directory:
```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/msa_dashboard
POSTGRES_USER=msa_user
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=msa_dashboard

# Application Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# Optional: MQTT Configuration
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=

# Optional: External APIs
WEATHER_API_KEY=your-weather-api-key
```

5. **Set up PostgreSQL database**
```bash
# Create database
createdb msa_dashboard

# Run schema setup
psql -d msa_dashboard -f core/schemas.sql
```

6. **Run the application**
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

7. **Access the dashboard**
Open your browser and navigate to: `http://localhost:8000/dashboard`

## 🔐 Authentication

The system includes three predefined user roles with different access levels:

### Demo Credentials
- **Commander**: `admin` / `admin123`
  - Full system access
  - All panels and data visible
  - Can acknowledge all alerts
  - Mission planning capabilities

- **Health Officer**: `health` / `health123`
  - Health monitoring focus
  - Limited to health-related data and alerts
  - Personnel vital signs access
  - Medical supply tracking

- **Operations Analyst**: `ops` / `ops123`
  - Operational data focus
  - Logistics and mission data
  - Operational alerts only
  - Resource planning tools

### Role-Based Features

| Feature | Commander | Health Officer | Operations Analyst |
|---------|-----------|----------------|-------------------|
| Tactical Map | ✅ Full Access | ✅ Limited | ✅ Limited |
| Health Monitoring | ✅ | ✅ | ❌ |
| Mission Planning | ✅ | ❌ | ✅ |
| Logistics Tracking | ✅ | ✅ Medical Only | ✅ |
| Alert Management | ✅ All Alerts | ✅ Health Alerts | ✅ Ops Alerts |
| System Administration | ✅ | ❌ | ❌ |

## 📡 API Documentation

### Authentication Endpoints

#### POST `/api/auth/login`
Authenticate user and receive JWT token.

**Request Body:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "user_id": "admin",
    "username": "admin",
    "role": "commander"
  }
}
```

#### POST `/api/auth/logout`
Invalidate current session.

#### GET `/api/auth/me`
Get current user information.

### Data Endpoints

#### GET `/api/units`
Retrieve all military units with role-based filtering.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
[
  {
    "unit_id": "UNIT-001",
    "callsign": "Alpha-1",
    "unit_type": "infantry",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "altitude": 10.5,
    "heading": 45.0,
    "speed": 5.2,
    "status": "operational",
    "last_seen": "2024-01-15T10:30:00Z"
  }
]
```

#### GET `/api/health-metrics`
Get personnel health metrics.

**Query Parameters:**
- `unit_id` (optional): Filter by specific unit

**Response:**
```json
[
  {
    "unit_id": "UNIT-001",
    "heart_rate": 75,
    "spo2": 98,
    "stress_level": 2.5,
    "body_temperature": 36.8,
    "timestamp": "2024-01-15T10:30:00Z"
  }
]
```

#### GET `/api/logistics`
Get logistics status for units.

**Response:**
```json
[
  {
    "unit_id": "UNIT-001",
    "fuel_percent": 85.5,
    "ammunition_percent": 92.0,
    "medical_supplies_percent": 78.3,
    "food_supplies_percent": 65.2,
    "timestamp": "2024-01-15T10:30:00Z"
  }
]
```

#### GET `/api/alerts`
Get active alerts with role-based filtering.

**Response:**
```json
[
  {
    "alert_id": "ALERT-001",
    "unit_id": "UNIT-001",
    "alert_type": "health_warning",
    "severity": "medium",
    "message": "Elevated stress levels detected",
    "timestamp": "2024-01-15T10:30:00Z",
    "acknowledged": false
  }
]
```

#### POST `/api/alerts/{alert_id}/acknowledge`
Acknowledge an alert.

**Response:**
```json
{
  "message": "Alert acknowledged successfully"
}
```

#### GET `/api/system-status`
Get overall system health summary.

**Response:**
```json
{
  "status": "operational",
  "active_units": 25,
  "critical_alerts": 2,
  "system_health": 85.5,
  "last_updated": "2024-01-15T10:30:00Z"
}
```

### WebSocket Endpoints

#### `/ws`
Real-time data updates via WebSocket connection.

**Connection:** `ws://localhost:8000/ws`

**Message Types:**
- `unit_update`: Unit position/status changes
- `health_update`: Health metric updates
- `alert_new`: New alert notifications
- `logistics_update`: Resource level changes

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `SECRET_KEY` | JWT signing key | Required |
| `DEBUG` | Enable debug mode | `False` |
| `SERVER_HOST` | Server bind address | `0.0.0.0` |
| `SERVER_PORT` | Server port | `8000` |
| `MQTT_BROKER_HOST` | MQTT broker address | `localhost` |
| `MQTT_BROKER_PORT` | MQTT broker port | `1883` |

### Database Configuration

The system supports PostgreSQL with optional TimescaleDB extension for time-series optimization:

```sql
-- Enable TimescaleDB (optional)
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Convert tables to hypertables for time-series optimization
SELECT create_hypertable('health_metrics', 'timestamp');
SELECT create_hypertable('logistics_status', 'timestamp');
SELECT create_hypertable('weather_data', 'timestamp');
```

## 🧪 Testing and Development

### Running Tests
```bash
pytest tests/ -v
```

### Development Mode
```bash
# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run data simulator
python -m ingest.simulator

# Run MQTT simulator
python -m ingest.mqtt_consumer
```

### Data Simulation

The system includes comprehensive data simulators for testing:

1. **Military Data Simulator** (`ingest/simulator.py`)
   - Unit movements and status updates
   - Health metrics with stress factors
   - Logistics consumption and resupply
   - Weather conditions
   - Threat detection scenarios

2. **MQTT Consumer** (`ingest/mqtt_consumer.py`)
   - Real-time sensor data ingestion
   - Message validation and processing
   - Topic-based data routing

3. **Drone Feed Simulator** (`ingest/drone_feed_mock.py`)
   - Surveillance data simulation
   - Threat detection algorithms
   - Patrol pattern generation

## 🚀 Deployment

### Docker Deployment
1. Prepare `.env` (use `.env.example`) and ensure `uploads/` exists.
2. Build backend image:
```bash
docker build -t msa-backend:latest .
```
3. Run with Docker Compose (backend + Nginx):
```yaml
version: "3.8"
services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    env_file:
      - .env
    restart: always
    volumes:
      - ./msa_dashboard.db:/app/msa_dashboard.db
      - ./uploads:/app/uploads
      - ./static:/app/static
  nginx:
    image: nginx:alpine
    depends_on:
      - backend
    ports:
      - "80:80"
    restart: always
    volumes:
      - ./deploy/nginx.conf:/etc/nginx/conf.d/default.conf:ro
```
Start services:
```bash
docker compose up -d
```
Access API via `http://localhost/` (proxied) or `http://localhost:8000/` (direct).

### Production Deployment

1. **Security Considerations**
   - Use strong SECRET_KEY
   - Enable HTTPS/TLS
   - Configure firewall rules
   - Regular security updates
   - Database encryption at rest

2. **Performance Optimization**
   - Use connection pooling
   - Enable database indexing
   - Configure caching (Redis)
   - Load balancing for multiple instances

3. **Monitoring**
   - Application logs
   - Database performance metrics
   - WebSocket connection monitoring
   - Alert system health checks

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the documentation in the `/docs` folder
- Review the API documentation at `/docs` when running the server

## 🔄 Version History

- **v1.0.0** - Initial release with core functionality
- **v1.1.0** - Added role-based access control
- **v1.2.0** - Enhanced data fusion and alert system
- **v1.3.0** - WebSocket real-time updates
- **v1.4.0** - Advanced simulation and testing capabilities

---

**MSA Dashboard** - Enhancing military situational awareness through advanced data visualization and real-time monitoring.