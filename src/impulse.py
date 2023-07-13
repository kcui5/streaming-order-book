from order_book import *

myBids = []
myAsks = []
timeOrders = []
loadBook("2023 7 13 12:39.json", myBids, myAsks)
loadTimeOrders("2023 7 13 12:51 time.json", timeOrders)
printBook(myBids, myAsks)
print(timeOrders)