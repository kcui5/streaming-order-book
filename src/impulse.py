from order_book import *

timeOrders = []
trades = []
seq = []
date = "7 14 12:17"
loadTimeOrders(f"../logs/2023 {date} time.json", timeOrders)
loadTrades(f"../logs/2023 {date} trades.json", trades)

getTimeOrderSequence(timeOrders, trades, seq)

def validateTimeOrder(seq):
    prev_time = 0
    for s in seq:
        if s.timestamp < prev_time:
            print("Invalid time order!")
            print(s.timestamp)
            return
        prev_time = s.timestamp
    print("Valid time order!")

validateTimeOrder(seq)
#printSeq(seq)
print("***********")
running_sum = 0
orders_seen = 0
bids = []
asks = []
trade_impulse = 0
correct_negative = 0
correct_positive = 0
incorrect_negative = 0
incorrect_positive = 0
total = 0
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
        trade_type = s.type
        if trade_type == "B":
            spread *= -1
        trade_quantity = s.quantity
        trade_impulse = (spread * trade_quantity) / order_size_average
        print(trade_impulse)
        total += 1
        if type(n) == Ask:
            if trade_impulse < 0:
                print("Correct negative impulse")
                correct_negative += 1
            elif trade_impulse > 0:
                print("Incorrect positive impulse")
                incorrect_positive += 1
        elif type(n) == Bid:
            if trade_impulse < 0:
                print("Incorrect negative impulse")
                incorrect_negative += 1
            elif trade_impulse > 0:
                print("Correct positive impulse")
                correct_positive += 1
        elif type(n) == Trade:
            if n.type == "B":
                if trade_impulse > 0:
                    print("Correct positive impulse")
                    correct_positive += 1
                elif trade_impulse < 0:
                    print("Incorrect negative impulse")
                    incorrect_negative += 1
            elif n.type == "S":
                if trade_impulse > 0:
                    print("Incorrect positive impulse")
                    incorrect_positive += 1
                elif trade_impulse < 0:
                    print("Correct negative impulse")
                    correct_negative += 1
            else:
                print("Unrecognized order type!")

if correct_negative + correct_positive + incorrect_negative + incorrect_positive != total:
    print("Wrong computation")
else:
    print("Correct computation")
total_correct = correct_positive + correct_negative
print("Total correct: ", total_correct)
print("Percent correct: ", total_correct / total)