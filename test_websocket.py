import asyncio
import websockets
import json

async def test_websocket():
    try:
        async with websockets.connect('ws://localhost:8000/ws') as websocket:
            print('WebSocket connected successfully!')
            
            # Wait for initial data
            data = await websocket.recv()
            print(f'Received data: {data[:200]}...')
            
            # Parse JSON
            message = json.loads(data)
            print(f'Message type: {message.get("type")}')
            
            # Wait for a few more messages
            for i in range(3):
                try:
                    data = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    message = json.loads(data)
                    print(f'Message {i+1}: {message.get("type")} - {len(str(message))} chars')
                except asyncio.TimeoutError:
                    print(f'No message received in 5 seconds (attempt {i+1})')
                    
    except Exception as e:
        print(f'WebSocket connection failed: {e}')

if __name__ == "__main__":
    asyncio.run(test_websocket())