import requests
import websockets
import asyncio
import bisect
import json
from order_book import *

"""
Note: Due to depth snapshots having a limit on the number of price levels, a price level outside of the initial snapshot that doesn't have a quantity change 
won't have an update in the Diff. Depth Stream. Consequently, those price levels will not be visible in the local order book even when applying all updates 
from the Diff. Depth Stream correctly and cause the local order book to have some slight differences with the real order book. However, for most use cases the 
depth limit of 5000 is enough to understand the market and trade effectively. --Binance Spot API Documentation

--> This means if the price level moves beyond the initial snapshot's included price levels, the local order book will differ from the actual order book !!!

Documentation Sources:
https://docs.binance.us/?python#order-book-depth-diff-stream
"""

#List of running Bids objects, order maintained with bisect insort
binance_bids = []
#List of running Asks objects, order maintained with bisect insort
binance_asks = []
#List of incoming orders ordered by timestamp
time_orders = []

first_received_event = True
previous_event_final_update = -1
last_update_id = -1

async def handle_binance_message(message):
    # Process the received message from the WebSocket stream
    print("Handling message")
    message = json.loads(message)
    print(message)

    messageFirstUpdate = message["U"]
    messageFinalUpdate = message["u"]
    messageTime = message["E"]
    global first_received_event
    global previous_event_final_update
    if messageFinalUpdate < last_update_id:
        print("Dropped event with u ", messageFinalUpdate)
        return
    if first_received_event:
        # Webstream opened after snapshot accessed so events are skipped, id check will always be invalid
        if message["U"] <= last_update_id + 1:
            if messageFinalUpdate >= last_update_id + 1:
                first_received_event = False
                previous_event_final_update = messageFinalUpdate
                print("Id check OK")
            else:
                print("Dropped event with u ", messageFinalUpdate)
                return
        else:
            print(f"Id invalid! Missed events from {last_update_id} to {messageFirstUpdate}")
            first_received_event = False
            previous_event_final_update = messageFinalUpdate
            return
    else:
        if message["U"] == previous_event_final_update + 1:
            print("Id check OK")
            previous_event_final_update = messageFinalUpdate
        else:
            print("Id invalid!")
            return
        
    messageBids = message["b"]
    for price, quantity in messageBids:
        price, quantity = float(price), float(quantity)
        curr = Bid(price, quantity, messageTime, "Binance")
        orderInsert(curr, binance_bids, binance_asks)
        time_orders.append(curr)

    messageAsks = message["a"]
    for price, quantity in messageAsks:
        price, quantity = float(price), float(quantity)
        curr = Ask(price, quantity, messageTime, "Binance")
        orderInsert(curr, binance_bids, binance_asks)
        time_orders.append(curr)
    printBook(binance_bids, binance_asks)

async def connect_binance():
    binance_stream_url = " wss://stream.binance.us:9443/ws/btcusdt@depth@100ms"
    async with websockets.connect(binance_stream_url) as websocket:
        print("WebSocket connection established")
        try:
            """
            while True:
                message = await websocket.recv()
                # TODO: Open webstream before receiving snapshot
                await handle_binance_message(message)
            """
            for i in range(10):
                message = await websocket.recv()
                await handle_binance_message(message)
            saveBook(binance_bids, binance_asks)
            saveTimeOrders(time_orders)
        except websockets.exceptions.ConnectionClosedOK:
            print("WebSocket connection closed")

def get_binance_snapshot(limit=100):
    binance_snapshot_url = f"https://www.binance.us/api/v1/depth?symbol=BTCUSDT&limit={limit}"
    response = requests.get(binance_snapshot_url)

    if response.status_code == 200:
        depth_snapshot = response.json()
        for order in depth_snapshot["bids"]:
            price, quantity = order
            price, quantity = float(price), float(quantity)
            #bisect.insort(binance_bids, Bid(price, quantity, 0, "Binance"))
            orderInsert(Bid(price, quantity, 0, "Binance"), binance_bids, binance_asks)
        for order in depth_snapshot["asks"]:
            price, quantity = order
            price, quantity = float(price), float(quantity)
            #bisect.insort(binance_asks, Ask(price, quantity, 0, "Binance"))
            orderInsert(Ask(price, quantity, 0, "Binance"), binance_bids, binance_asks)
        printBook(binance_bids, binance_asks)
        depthSnapshotLastUpdateId = depth_snapshot["lastUpdateId"]
        print("Depth snapshot last update id ", depthSnapshotLastUpdateId)
        return depthSnapshotLastUpdateId
    else:
        print(f"Error retrieving depth snapshot. Status code: {response.status_code}")

if __name__ == "__main__":
    #TODO: get snapshot after webstream opened, incorporate snapshot accurately
    last_update_id = get_binance_snapshot(5)
    asyncio.run(connect_binance())