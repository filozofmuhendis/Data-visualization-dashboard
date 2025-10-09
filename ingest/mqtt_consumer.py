"""
MSA Dashboard - MQTT Consumer
Real-time sensor data ingestion from military field units
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Callable, Optional

import paho.mqtt.client as mqtt
from paho.mqtt.client import MQTTMessage

from core.models import (
    Unit, HealthMetrics, LogisticsStatus, WeatherData, ThreatDetection,
    Alert, RiskLevel, UnitType, AlertSeverity
)
from core.settings import settings


class MQTTConsumer:
    """MQTT consumer for military sensor data"""
    
    def __init__(self, message_handler: Optional[Callable] = None):
        self.client = mqtt.Client(client_id=f"msa_dashboard_{datetime.now().timestamp()}")
        self.message_handler = message_handler
        self.connected = False
        self.logger = logging.getLogger(__name__)
        
        # Set up MQTT client callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.client.on_subscribe = self._on_subscribe
        
        # Message processors for different topics
        self.processors = {
            settings.mqtt_topics["unit_position"]: self._process_unit_position,
            settings.mqtt_topics["health_metrics"]: self._process_health_metrics,
            settings.mqtt_topics["logistics_status"]: self._process_logistics_status,
            settings.mqtt_topics["weather_data"]: self._process_weather_data,
            settings.mqtt_topics["threat_detection"]: self._process_threat_detection,
            settings.mqtt_topics["alerts"]: self._process_alerts,
            settings.mqtt_topics["mission_updates"]: self._process_mission_updates
        }
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback for MQTT connection"""
        if rc == 0:
            self.connected = True
            self.logger.info("Connected to MQTT broker")
            
            # Subscribe to all military data topics
            topics = [
                (settings.mqtt_topics["unit_position"], 1),
                (settings.mqtt_topics["health_metrics"], 1),
                (settings.mqtt_topics["logistics_status"], 1),
                (settings.mqtt_topics["weather_data"], 1),
                (settings.mqtt_topics["threat_detection"], 2),  # Higher QoS for threats
                (settings.mqtt_topics["alerts"], 2),  # Higher QoS for alerts
                (settings.mqtt_topics["mission_updates"], 1)
            ]
            
            for topic, qos in topics:
                client.subscribe(topic, qos)
                self.logger.info(f"Subscribed to topic: {topic}")
        else:
            self.logger.error(f"Failed to connect to MQTT broker: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback for MQTT disconnection"""
        self.connected = False
        if rc != 0:
            self.logger.warning("Unexpected MQTT disconnection")
        else:
            self.logger.info("Disconnected from MQTT broker")
    
    def _on_subscribe(self, client, userdata, mid, granted_qos):
        """Callback for successful subscription"""
        self.logger.info(f"Subscription confirmed with QoS: {granted_qos}")
    
    def _on_message(self, client, userdata, msg: MQTTMessage):
        """Main message handler"""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode('utf-8'))
            
            self.logger.debug(f"Received message on topic {topic}: {payload}")
            
            # Process message based on topic
            if topic in self.processors:
                processed_data = self.processors[topic](payload)
                
                # Send to message handler if available
                if self.message_handler and processed_data:
                    asyncio.create_task(self.message_handler(topic, processed_data))
            else:
                self.logger.warning(f"No processor found for topic: {topic}")
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode JSON message: {e}")
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
    
    def _process_unit_position(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process unit position updates"""
        try:
            required_fields = ["unit_id", "latitude", "longitude", "timestamp"]
            if not all(field in payload for field in required_fields):
                self.logger.error(f"Missing required fields in unit position: {payload}")
                return None
            
            # Validate coordinates
            lat, lon = float(payload["latitude"]), float(payload["longitude"])
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                self.logger.error(f"Invalid coordinates: lat={lat}, lon={lon}")
                return None
            
            return {
                "type": "unit_position",
                "unit_id": payload["unit_id"],
                "latitude": lat,
                "longitude": lon,
                "altitude": payload.get("altitude", 0.0),
                "heading": payload.get("heading", 0.0),
                "speed": payload.get("speed", 0.0),
                "timestamp": payload["timestamp"],
                "status": payload.get("status", "active")
            }
            
        except (ValueError, KeyError) as e:
            self.logger.error(f"Error processing unit position: {e}")
            return None
    
    def _process_health_metrics(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process health sensor data"""
        try:
            required_fields = ["unit_id", "timestamp"]
            if not all(field in payload for field in required_fields):
                self.logger.error(f"Missing required fields in health metrics: {payload}")
                return None
            
            # Validate health metrics ranges
            heart_rate = payload.get("heart_rate", 0)
            spo2 = payload.get("spo2", 0)
            stress_index = payload.get("stress_index", 0)
            
            if not (30 <= heart_rate <= 220):
                self.logger.warning(f"Heart rate out of range: {heart_rate}")
            if not (70 <= spo2 <= 100):
                self.logger.warning(f"SpO2 out of range: {spo2}")
            if not (0 <= stress_index <= 100):
                self.logger.warning(f"Stress index out of range: {stress_index}")
            
            # Calculate risk level
            risk_level = "green"
            if heart_rate > 120 or spo2 < 92 or stress_index > 70:
                risk_level = "red"
            elif heart_rate > 100 or spo2 < 95 or stress_index > 50:
                risk_level = "amber"
            
            return {
                "type": "health_metrics",
                "unit_id": payload["unit_id"],
                "timestamp": payload["timestamp"],
                "heart_rate": heart_rate,
                "spo2": spo2,
                "stress_index": stress_index,
                "body_temperature": payload.get("body_temperature", 36.5),
                "fatigue_level": payload.get("fatigue_level", 0),
                "risk_level": risk_level
            }
            
        except (ValueError, KeyError) as e:
            self.logger.error(f"Error processing health metrics: {e}")
            return None
    
    def _process_logistics_status(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process logistics and supply data"""
        try:
            required_fields = ["unit_id", "timestamp"]
            if not all(field in payload for field in required_fields):
                self.logger.error(f"Missing required fields in logistics status: {payload}")
                return None
            
            # Get supply levels
            ammo_percent = max(0, min(100, payload.get("ammo_percent", 100)))
            fuel_percent = max(0, min(100, payload.get("fuel_percent", 100)))
            water_percent = max(0, min(100, payload.get("water_percent", 100)))
            medical_supplies = max(0, min(100, payload.get("medical_supplies", 100)))
            
            # Calculate risk level based on lowest supply
            min_supply = min(ammo_percent, fuel_percent, water_percent, medical_supplies)
            risk_level = "green"
            if min_supply < 20:
                risk_level = "red"
            elif min_supply < 40:
                risk_level = "amber"
            
            return {
                "type": "logistics_status",
                "unit_id": payload["unit_id"],
                "timestamp": payload["timestamp"],
                "ammo_percent": ammo_percent,
                "fuel_percent": fuel_percent,
                "water_percent": water_percent,
                "medical_supplies": medical_supplies,
                "food_rations": payload.get("food_rations", 100),
                "equipment_status": payload.get("equipment_status", "operational"),
                "risk_level": risk_level
            }
            
        except (ValueError, KeyError) as e:
            self.logger.error(f"Error processing logistics status: {e}")
            return None
    
    def _process_weather_data(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process weather station data"""
        try:
            required_fields = ["station_id", "timestamp"]
            if not all(field in payload for field in required_fields):
                self.logger.error(f"Missing required fields in weather data: {payload}")
                return None
            
            return {
                "type": "weather_data",
                "station_id": payload["station_id"],
                "timestamp": payload["timestamp"],
                "latitude": payload.get("latitude", 0.0),
                "longitude": payload.get("longitude", 0.0),
                "temperature": payload.get("temperature", 20.0),
                "humidity": payload.get("humidity", 50.0),
                "wind_speed": payload.get("wind_speed", 0.0),
                "wind_direction": payload.get("wind_direction", 0.0),
                "visibility": payload.get("visibility", 10.0),
                "pressure": payload.get("pressure", 1013.25),
                "weather_condition": payload.get("weather_condition", "clear")
            }
            
        except (ValueError, KeyError) as e:
            self.logger.error(f"Error processing weather data: {e}")
            return None
    
    def _process_threat_detection(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process threat detection data"""
        try:
            required_fields = ["threat_id", "threat_type", "latitude", "longitude", "timestamp"]
            if not all(field in payload for field in required_fields):
                self.logger.error(f"Missing required fields in threat detection: {payload}")
                return None
            
            # Validate threat data
            lat, lon = float(payload["latitude"]), float(payload["longitude"])
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                self.logger.error(f"Invalid threat coordinates: lat={lat}, lon={lon}")
                return None
            
            confidence = max(0.0, min(1.0, payload.get("confidence", 0.5)))
            
            # Determine severity based on threat type and confidence
            threat_type = payload["threat_type"]
            severity = "low"
            if threat_type in ["hostile_vehicle", "weapon_signature"] and confidence > 0.7:
                severity = "high"
            elif confidence > 0.6:
                severity = "medium"
            
            return {
                "type": "threat_detection",
                "threat_id": payload["threat_id"],
                "threat_type": threat_type,
                "latitude": lat,
                "longitude": lon,
                "confidence": confidence,
                "severity": severity,
                "detected_by": payload.get("detected_by", "unknown"),
                "timestamp": payload["timestamp"],
                "description": payload.get("description", f"Detected {threat_type}")
            }
            
        except (ValueError, KeyError) as e:
            self.logger.error(f"Error processing threat detection: {e}")
            return None
    
    def _process_alerts(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process system alerts"""
        try:
            required_fields = ["alert_id", "alert_type", "message", "timestamp"]
            if not all(field in payload for field in required_fields):
                self.logger.error(f"Missing required fields in alert: {payload}")
                return None
            
            return {
                "type": "alert",
                "alert_id": payload["alert_id"],
                "unit_id": payload.get("unit_id"),
                "alert_type": payload["alert_type"],
                "severity": payload.get("severity", "medium"),
                "message": payload["message"],
                "timestamp": payload["timestamp"],
                "acknowledged": payload.get("acknowledged", False),
                "source": payload.get("source", "field")
            }
            
        except (ValueError, KeyError) as e:
            self.logger.error(f"Error processing alert: {e}")
            return None
    
    def _process_mission_updates(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process mission status updates"""
        try:
            required_fields = ["mission_id", "timestamp"]
            if not all(field in payload for field in required_fields):
                self.logger.error(f"Missing required fields in mission update: {payload}")
                return None
            
            return {
                "type": "mission_update",
                "mission_id": payload["mission_id"],
                "timestamp": payload["timestamp"],
                "phase": payload.get("phase", "planning"),
                "progress": max(0, min(100, payload.get("progress", 0))),
                "status": payload.get("status", "active"),
                "updated_by": payload.get("updated_by", "system")
            }
            
        except (ValueError, KeyError) as e:
            self.logger.error(f"Error processing mission update: {e}")
            return None
    
    async def connect(self):
        """Connect to MQTT broker"""
        try:
            if settings.mqtt_username and settings.mqtt_password:
                self.client.username_pw_set(settings.mqtt_username, settings.mqtt_password)
            
            self.client.connect(settings.mqtt_host, settings.mqtt_port, settings.mqtt_keepalive)
            self.client.loop_start()
            
            # Wait for connection
            timeout = 10
            while not self.connected and timeout > 0:
                await asyncio.sleep(0.1)
                timeout -= 0.1
            
            if not self.connected:
                raise ConnectionError("Failed to connect to MQTT broker within timeout")
                
            self.logger.info("MQTT consumer connected and ready")
            
        except Exception as e:
            self.logger.error(f"Failed to connect to MQTT broker: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.connected:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
            self.logger.info("MQTT consumer disconnected")
    
    def publish_message(self, topic: str, payload: Dict[str, Any], qos: int = 1):
        """Publish message to MQTT topic"""
        if self.connected:
            try:
                message = json.dumps(payload)
                result = self.client.publish(topic, message, qos)
                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    self.logger.debug(f"Published message to {topic}")
                else:
                    self.logger.error(f"Failed to publish message to {topic}: {result.rc}")
            except Exception as e:
                self.logger.error(f"Error publishing message: {e}")
        else:
            self.logger.warning("Cannot publish message: MQTT client not connected")


class MQTTSimulator:
    """MQTT simulator for testing purposes"""
    
    def __init__(self, mqtt_consumer: MQTTConsumer):
        self.consumer = mqtt_consumer
        self.running = False
        self.logger = logging.getLogger(__name__)
    
    async def start_simulation(self):
        """Start publishing simulated MQTT messages"""
        self.running = True
        self.logger.info("Starting MQTT simulation")
        
        while self.running:
            try:
                # Simulate unit position update
                unit_position = {
                    "unit_id": "ALPHA-001",
                    "latitude": 39.9042 + (random.uniform(-0.01, 0.01)),
                    "longitude": 32.6195 + (random.uniform(-0.01, 0.01)),
                    "heading": random.uniform(0, 360),
                    "speed": random.uniform(0, 20),
                    "timestamp": datetime.now().isoformat(),
                    "status": "active"
                }
                
                self.consumer.publish_message(
                    settings.mqtt_topics["unit_position"],
                    unit_position
                )
                
                # Simulate health metrics
                health_metrics = {
                    "unit_id": "ALPHA-001",
                    "heart_rate": random.randint(70, 120),
                    "spo2": random.randint(92, 99),
                    "stress_index": random.randint(20, 80),
                    "timestamp": datetime.now().isoformat()
                }
                
                self.consumer.publish_message(
                    settings.mqtt_topics["health_metrics"],
                    health_metrics
                )
                
                await asyncio.sleep(5)  # Publish every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Error in MQTT simulation: {e}")
                await asyncio.sleep(1)
    
    def stop_simulation(self):
        """Stop the simulation"""
        self.running = False
        self.logger.info("MQTT simulation stopped")


# Example usage and testing
if __name__ == "__main__":
    import random
    
    async def message_handler(topic: str, data: Dict[str, Any]):
        """Example message handler"""
        print(f"Received data on {topic}: {data}")
    
    async def main():
        # Create MQTT consumer
        consumer = MQTTConsumer(message_handler)
        
        try:
            # Connect to broker
            await consumer.connect()
            
            # Start simulator for testing
            simulator = MQTTSimulator(consumer)
            simulation_task = asyncio.create_task(simulator.start_simulation())
            
            # Run for 30 seconds
            await asyncio.sleep(30)
            
            # Stop simulation
            simulator.stop_simulation()
            await simulation_task
            
        finally:
            await consumer.disconnect()
    
    # Run the example
    asyncio.run(main())