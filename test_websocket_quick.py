import asyncio
import websockets
import json

async def quick_websocket_test():
    try:
        async with websockets.connect('ws://localhost:8000/ws') as websocket:
            print('✓ WebSocket connected successfully!')
            
            # Wait for first message with timeout
            try:
                data = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                message = json.loads(data)
                print(f'✓ Received message type: {message.get("type")}')
                print(f'✓ Data length: {len(str(message))} characters')
                
                # Check if it's units update
                if message.get("type") == "units_update":
                    units = message.get("data", [])
                    print(f'✓ Units data received: {len(units)} units')
                
                # Check if it's alerts update  
                elif message.get("type") == "alerts_update":
                    alerts = message.get("data", [])
                    print(f'✓ Alerts data received: {len(alerts)} alerts')
                
                # Check if it's dashboard summary
                elif message.get("type") == "dashboard_summary":
                    summary = message.get("data", {})
                    print(f'✓ Dashboard summary: {summary.get("total_units", 0)} units, {summary.get("critical_alerts", 0)} critical alerts')
                
                print('✓ WebSocket real-time data streaming is working!')
                return True
                
            except asyncio.TimeoutError:
                print('⚠ No message received within 10 seconds')
                return False
                
    except Exception as e:
        print(f'✗ WebSocket connection failed: {e}')
        return False

if __name__ == "__main__":
    result = asyncio.run(quick_websocket_test())
    if result:
        print('\n🎉 WebSocket integration test PASSED!')
    else:
        print('\n❌ WebSocket integration test FAILED!')