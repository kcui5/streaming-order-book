mod order_book;
use order_book::{CompareOrder, Order, print_book};

fn main() {
    let o = Order::create(123.3, 2.0, "2023", "Bid");
    println!("Order {} {} {} {}", o.get_price(), o.get_quantity(), o.get_timestamp(), o.get_order_type());

    let mut bids: Vec<Order> = vec![];
    let mut asks: Vec<Order> = vec![];

    bids.push(o);
    print_book(bids, asks);
}
