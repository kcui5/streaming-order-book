from order_book import *

timeOrders = []
trades = []
seq = []
loadTimeOrders("../logs/2023 7 13 23:41 time.json", timeOrders)
loadTrades("../logs/2023 7 13 23:41 trades.json", trades)

getTimeOrderSequence(timeOrders, trades, seq)

def validateTimeOrder(seq):
    prev_time = 0
    for s in seq:
        if s.timestamp < prev_time:
            print("Invalid time order!")
            return
        prev_time = s.timestamp
    print("Valid time order!")

validateTimeOrder(seq)
printSeq(seq)
print("***********")
running_sum = 0
orders_seen = 0
bids = []
asks = []
trade_impulse = 0
for i in range(len(seq) - 1):
    s = seq[i]
    n = seq[i + 1]
    if type(s) == Bid:
        orderInsert(s, bids, asks)
        running_sum += s.quantity
        orders_seen += 1
    elif type(s) == Ask:
        orderInsert(s, bids, asks)
        running_sum += s.quantity
        orders_seen += 1
    elif type(s) == Trade:
        if not bids or not asks:
            continue
        best_bid = bids[0]
        best_ask = asks[0]
        spread = best_bid.price - best_ask.price
        order_size_average = running_sum / orders_seen
        trade_quantity = s.quantity
        trade_impulse = (spread * trade_quantity) / order_size_average
        print(trade_impulse)
        if type(n) == Ask:
            if trade_impulse < 0:
                print("Correct negative impulse")
            elif trade_impulse > 0:
                print("Incorrect positive impulse")
        elif type(n) == Bid:
            if trade_impulse < 0:
                print("Incorrect negative impulse")
            elif trade_impulse > 0:
                print("Correct positive impulse")
        elif type(n) == Trade:
            print("Trade next")
        
