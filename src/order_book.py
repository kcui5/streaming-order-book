import json
import datetime
import bisect

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
def printBook(print_bids, print_asks):
    for a in print_asks[::-1]:
        print("Ask", a.price, a.quantity)
    print("-----")
    for b in print_bids:
        print("Bid", b.price, b.quantity)
    print("---")

#Save current order book
def saveBook(save_bids, save_asks):
    data = {}
    for a in save_asks:
        data["Ask " + str(a.price)] = [a.price, a.quantity, a.timestamp, a.src]
    for b in save_bids:
        data["Bid " + str(b.price)] = [b.price, b.quantity, b.timestamp, b.src]
    data = json.dumps(data)
    current_time = datetime.datetime.now()
    file_name = str(current_time.year) + " " + str(current_time.month) + " " + str(current_time.day) + " " + str(current_time.hour) + ":" + str(current_time.minute) + ".json"
    with open(file_name, "w") as file:
        json.dump(data, file)
    print("Saved book")

def saveTimeOrders(save_orders):
    data = {}
    for o in save_orders:
        if type(o) == Ask:
            data["Ask " + str(o.price)] = [o.price, o.quantity, o.timestamp, o.src]
        elif type(o) == Bid:
            data["Bid " + str(o.price)] = [o.price, o.quantity, o.timestamp, o.src]
        else:
            print("Unrecognized order type!")
    data = json.dumps(data)
    current_time = datetime.datetime.now()
    file_name = str(current_time.year) + " " + str(current_time.month) + " " + str(current_time.day) + " " + str(current_time.hour) + ":" + str(current_time.minute) + " time.json"
    with open(file_name, "w") as file:
        json.dump(data, file)
    print("Saved time orders")

#Populate bids and asks from saved order book
def loadBook(file_name, new_bids, new_asks):
    with open(file_name, "r") as file:
        data = json.load(file)
        data = json.loads(data)
    for order in data:
        currOrder = data[order]
        if order[0] == "A":
            new_asks.append(Ask(currOrder[0], currOrder[1], currOrder[2], currOrder[3]))
        elif order[0] == "B":
            new_bids.append(Bid(currOrder[0], currOrder[1], currOrder[2], currOrder[3]))
        else:
            print("Unrecognized order type: ")
            print(order)
            print(currOrder)

def loadTimeOrders(file_name, orders):
    with open(file_name, "r") as file:
        data = json.load(file)
        data = json.loads(data)
    for order in data:
        currOrder = data[order]
        if order[0] == "A":
            orders.append(Ask(currOrder[0], currOrder[1], currOrder[2], currOrder[3]))
        elif order[0] == "B":
            orders.append(Bid(currOrder[0], currOrder[1], currOrder[2], currOrder[3]))
        else:
            print("Unrecognized order type: ")
            print(order)
            print(currOrder)

#Insert this bid or ask order into the list of bids or asks respectively
def orderInsert(order, bids, asks):
    if type(order) == Bid:
        orders = bids
    elif type(order) == Ask:
        orders = asks
    else:
        print("Unrecognized order type!")
        return
    #If this price level already in the local order book
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
    #If this price level not already in the local order book
    if order.quantity > 0:
        bisect.insort(orders, order)
        return
    elif order.quantity == 0:
        return
    elif order.quantity < 0:
        print("Invalid order quantity!")
        return
