import requests
import websockets
import asyncio
import json
import bisect

#List of running Bids objects, order maintained with bisect insort
bids = []
#List of running Asks objects, order maintained with bisect insort
asks = []

firstReceivedEvent = True
previousEventFinalUpdate = -1

class Order:
    def __init__(self, p, q, t, src):
        self.price = p
        self.quantity = q
        self.timestamp = t
        self.src = src

#A custom class for Bids with comparison for priority
class Bid(Order):
    #Bid 1 is less than Bid 2 if Bid 1 has higher priority (higher price or earlier timestamp if same price)
    def __lt__(self, other):
        if self.price > other.price:
            return True
        if self.price == other.price:
            return self.time < other.time
        return False
    
    #Bid 1 is greater than Bid 2 if Bid 1 has lower priority (lower price or later timestamp if same price)
    def __gt__(self, other):
        if self.price < other.price:
            return True
        if self.price == other.price:
            return self.time > other.time
        return False
    
#A custom class for Asks with comparison for priority    
class Ask(Order):
    #Ask 1 is less than Ask 2 if Ask 1 has higher priority (lower price or earlier timestamp if same price)
    def __lt__(self, other):
        if self.price < other.price:
            return True
        if self.price == other.price:
            return self.time < other.time
        return False
    
    #Ask 1 is greater than Ask 2 if Ask 1 has lower priority (higher price or later timestamp if same price)
    def __gt__(self, other):
        if self.price > other.price:
            return True
        if self.price == other.price:
            return self.time > other.time
        return False

def orderInsert(Order o):
    

async def handle_binance_message(message, lastUpdateId):
    # Process the received message from the WebSocket stream
    print("Handling message")
    message = json.loads(message)
    print(message)

    messageFinalUpdate = message["u"]
    messageTime = message["E"]
    if messageFinalUpdate < lastUpdateId:
        print("Dropped event with u ", messageFinalUpdate)
    if firstReceivedEvent:
        if message["U"] <= lastUpdateId + 1 and messageFinalUpdate >= lastUpdateId + 1:
            print("Id check OK")
        else:
            print("Id invalid!")
        firstReceivedEvent = False
        previousEventFinalUpdate = messageFinalUpdate
    else:
        if message["U"] == previousEventFinalUpdate + 1:
            print("Id check OK")
        else:
            print("Id invalid!")
        previousEventFinalUpdate = messageFinalUpdate

    messageBids = message["b"]
    for price, quantity in messageBids:
        price, quantity = float(price), float(quantity)
        Bid(price, quantity, messageTime, "Binance")
        if price in bids:
            if quantity > 0:
                bids[price] += quantity
            else:
                del bids[price]
        elif quantity > 0:
            bids[price] = quantity

    messageAsks = message["a"]
    for price, quantity in messageAsks:
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

async def connect_websocket(lastUpdateId):
    url = " wss://stream.binance.us:9443/ws/btcusdt@depth@100ms"
    async with websockets.connect(url) as websocket:
        print("WebSocket connection established")
        try:
            while True:
                message = await websocket.recv()
                await handle_binance_message(message, lastUpdateId)
        except websockets.exceptions.ConnectionClosedOK:
            print("WebSocket connection closed")

def get_binance_snapshot(limit=100):
    url = f"https://www.binance.us/api/v1/depth?symbol=BTCUSDT&limit={limit}"
    response = requests.get(url)

    if response.status_code == 200:
        depth_snapshot = response.json()
        for order in depth_snapshot["bids"]:
            price, quantity = order
            bisect.insort(bids, Bid(price, quantity, 0, "Binance"))
        for order in depth_snapshot["asks"]:
            price, quantity = order
            bisect.insort(asks, Ask(price, quantity, 0, "Binance"))
        for b in bids:
            print("Bid", b.price, b.quantity)
        for a in asks:
            print("Ask", a.price, a.quantity)
        depthSnapshotLastUpdateId = depth_snapshot["lastUpdateId"]
        print("Depth snapshot last update id ", depthSnapshotLastUpdateId)
        return depthSnapshotLastUpdateId
    else:
        print(f"Error retrieving depth snapshot. Status code: {response.status_code}")

if __name__ == "__main__":
    lastUpdateId = get_binance_snapshot(5)
    asyncio.run(connect_websocket(lastUpdateId))