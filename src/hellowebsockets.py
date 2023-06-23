import websockets
import asyncio
import datetime
import json

messages = []
bids = {}
asks = {}

async def handle_message(message):
    # Process the received message from the WebSocket stream
    print("Handling message")
    message = json.loads(message)
    messages.append(message)
    
    print(message)
    for price, quantity in message["b"]:
        price, quantity = float(price), float(quantity)
        if price in bids:
            if quantity > 0:
                bids[price] += quantity
            else:
                del bids[price]
        elif quantity > 0:
            bids[price] = quantity
    for price, quantity in message["a"]:
        price, quantity = float(price), float(quantity)
        if price in asks:
            if quantity > 0:
                asks[price] += quantity
            else:
                del asks[price]
        elif quantity > 0:
            asks[price] = quantity
    print(bids)
    print(asks)

async def connect_websocket(url):
    async with websockets.connect(url) as websocket:
        print("WebSocket connection established")

        try:
            while True:
                message = await websocket.recv()
                await handle_message(message)
        except websockets.exceptions.ConnectionClosedOK:
            print("WebSocket connection closed")

if __name__ == "__main__":
    #url = "wss://example.com/stream"  # Replace with your desired link
    url = " wss://stream.binance.us:9443/ws/bnbbtc@depth@100ms"
    asyncio.run(connect_websocket(url))