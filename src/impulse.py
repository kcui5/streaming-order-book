from order_book import *

myBids = []
myAsks = []
loadBook("2023 7 13 0:23.json", myBids, myAsks)

printBook(myBids, myAsks)