import requests
import bisect
import websockets
import asyncio
import json

async def connect_to_websocket():
    url = "wss://ws-feed.exchange.coinbase.com"
    async with websockets.connect(url) as websocket:
        await websocket.send(json.dumps({
            'type': 'subscribe',
            "channels": ["level2"],
            "product_ids": [
                "BTC-USDT"
            ]       
        }))

        while True:
            response = await websocket.recv()
            handle_message(response)

def handle_message(message):
    # Parse the received message and update the local order book
    message_data = json.loads(message)
    # Process the message and update the order book accordingly
    print(message_data)

asyncio.get_event_loop().run_until_complete(connect_to_websocket())
