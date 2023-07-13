from order_book import *

#myBids = []
#myAsks = []
timeOrders = []
trades = []
seq = []
#loadBook("2023 7 13 12:39.json", myBids, myAsks)
loadTimeOrders("../logs/2023 7 13 14:4 time.json", timeOrders)
loadTrades("../logs/2023 7 13 14:4 trades.json", trades)
#printBook(myBids, myAsks)
printTimeOrders(timeOrders)
printTrades(trades)

print(len(timeOrders))
print(len(trades))
getTimeOrderSequence(timeOrders, trades, seq)
print("---")
printSeq(seq)
print(len(seq))

def validateTimeOrder():
    prev_time = 0
    for o in timeOrders:
        if type(o) == Bid:
            if o.timestamp < prev_bid_time:
                print("Invalid!")
            prev_bid_time = o.timestamp
        elif type(o) == Ask:
            if o.timestamp < prev_ask_time:
                print("Invalid!")
            prev_ask_time = o.timestamp

#validateTimeOrder()