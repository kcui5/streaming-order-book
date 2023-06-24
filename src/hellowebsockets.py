import requests
import websockets
import asyncio
import json
import bisect

"""
Note: Due to depth snapshots having a limit on the number of price levels, a price level outside of the initial snapshot that doesn't have a quantity change 
won't have an update in the Diff. Depth Stream. Consequently, those price levels will not be visible in the local order book even when applying all updates 
from the Diff. Depth Stream correctly and cause the local order book to have some slight differences with the real order book. However, for most use cases the 
depth limit of 5000 is enough to understand the market and trade effectively. --Binance Spot API Documentation
"""

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
            return self.timestamp < other.timestamp
        return False
    
    #Bid 1 is greater than Bid 2 if Bid 1 has lower priority (lower price or later timestamp if same price)
    def __gt__(self, other):
        if self.price < other.price:
            return True
        if self.price == other.price:
            return self.timestamp > other.timestamp
        return False
    
#A custom class for Asks with comparison for priority    
class Ask(Order):
    #Ask 1 is less than Ask 2 if Ask 1 has higher priority (lower price or earlier timestamp if same price)
    def __lt__(self, other):
        if self.price < other.price:
            return True
        if self.price == other.price:
            return self.timestamp < other.timestamp
        return False
    
    #Ask 1 is greater than Ask 2 if Ask 1 has lower priority (higher price or later timestamp if same price)
    def __gt__(self, other):
        if self.price > other.price:
            return True
        if self.price == other.price:
            return self.timestamp > other.timestamp
        return False

#Print current order book
def printBook():
    for a in asks[::-1]:
        print("Ask", a.price, a.quantity)
    print("-----")
    for b in bids:
        print("Bid", b.price, b.quantity)
    print("---")

#Insert this bid or ask order into the list of bids or asks respectively
def orderInsert(order):
    if type(order) == Bid:
        orders = bids
    elif type(order) == Ask:
        orders = asks
    else:
        print("Unrecognized order type!")
        return
    for i in range(len(orders)):
        ba = orders[i]
        if ba.price == order.price:
            if order.quantity > 0:
                ba.quantity += order.quantity
            elif order.quantity == 0:
                del orders[i]
            else:
                print("Invalid order quantity!")
                return
            break
    if order.quantity > 0:
        bisect.insort(orders, order)
        return
    elif order.quantity == 0:
        return
    elif order.quantity < 0:
        print("Invalid order quantity!")
        return

async def handle_binance_message(message, lastUpdateId):
    # Process the received message from the WebSocket stream
    print("Handling message")
    message = json.loads(message)
    print(message)

    messageFinalUpdate = message["u"]
    messageTime = message["E"]
    global firstReceivedEvent
    global previousEventFinalUpdate
    if messageFinalUpdate < lastUpdateId:
        print("Dropped event with u ", messageFinalUpdate)
    if firstReceivedEvent:
        # Webstream opened after snapshot accessed so events are skipped, id check will always be invalid
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
        curr = Bid(price, quantity, messageTime, "Binance")
        orderInsert(curr)

    messageAsks = message["a"]
    for price, quantity in messageAsks:
        price, quantity = float(price), float(quantity)
        curr = Ask(price, quantity, messageTime, "Binance")
        orderInsert(curr)
    printBook()

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
            price, quantity = float(price), float(quantity)
            bisect.insort(bids, Bid(price, quantity, 0, "Binance"))
        for order in depth_snapshot["asks"]:
            price, quantity = order
            price, quantity = float(price), float(quantity)
            bisect.insort(asks, Ask(price, quantity, 0, "Binance"))
        printBook()
        depthSnapshotLastUpdateId = depth_snapshot["lastUpdateId"]
        print("Depth snapshot last update id ", depthSnapshotLastUpdateId)
        return depthSnapshotLastUpdateId
    else:
        print(f"Error retrieving depth snapshot. Status code: {response.status_code}")

if __name__ == "__main__":
    lastUpdateId = get_binance_snapshot(5)
    asyncio.run(connect_websocket(lastUpdateId))