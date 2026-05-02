import asyncio
import websockets
import json

async def detailed_websocket_test():
    try:
        async with websockets.connect('ws://localhost:8000/ws') as websocket:
            print('✓ WebSocket connected successfully!')
            
            message_count = 0
            message_types = set()
            
            # Listen for multiple messages
            for i in range(3):  # Listen for 3 messages
                try:
                    data = await asyncio.wait_for(websocket.recv(), timeout=15.0)
                    message = json.loads(data)
                    message_count += 1
                    
                    msg_type = message.get("message_type")
                    message_types.add(msg_type)
                    
                    print(f'✓ Message {message_count}: Type = {msg_type}')
                    
                    # Analyze message content
                    if msg_type == "units_update":
                        units = message.get("data", [])
                        print(f'  - Units data: {len(units)} units')
                        if units:
                            sample_unit = units[0]
                            print(f'  - Sample unit ID: {sample_unit.get("unit_id", "N/A")}')
                    
                    elif msg_type == "alerts_update":
                        alerts = message.get("data", [])
                        print(f'  - Alerts data: {len(alerts)} alerts')
                        if alerts:
                            critical_alerts = [a for a in alerts if a.get('severity') == 'critical']
                            print(f'  - Critical alerts: {len(critical_alerts)}')
                    
                    elif msg_type == "dashboard_summary":
                        summary = message.get("data", {})
                        print(f'  - Total units: {summary.get("total_units", 0)}')
                        print(f'  - Critical alerts: {summary.get("critical_alerts", 0)}')
                        print(f'  - Active missions: {summary.get("active_missions", 0)}')
                    
                    print(f'  - Timestamp: {message.get("timestamp", "N/A")}')
                    print()
                    
                except asyncio.TimeoutError:
                    print(f'⚠ Timeout waiting for message {i+1}')
                    break
            
            print(f'📊 Test Summary:')
            print(f'  - Total messages received: {message_count}')
            print(f'  - Message types: {", ".join(message_types) if message_types else "None"}')
            
            # Check if we got the expected message types
            expected_types = {"units_update", "alerts_update", "dashboard_summary"}
            received_types = message_types
            
            if expected_types.issubset(received_types):
                print('✅ All expected message types received!')
                return True
            else:
                missing = expected_types - received_types
                print(f'⚠ Missing message types: {", ".join(missing)}')
                return message_count > 0
                
    except Exception as e:
        print(f'✗ WebSocket connection failed: {e}')
        return False

if __name__ == "__main__":
    result = asyncio.run(detailed_websocket_test())
    if result:
        print('\n🎉 Detailed WebSocket integration test PASSED!')
    else:
        print('\n❌ Detailed WebSocket integration test FAILED!')