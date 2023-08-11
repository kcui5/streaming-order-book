trait CompareOrder {
    fn create(p: f64, q: f64, t: &str, ot: &str) -> Order;
    fn get_price(&self) -> f64;
    fn get_quantity(&self) -> f64;
    fn get_timestamp(&self) -> &str;
    fn get_order_type(&self) -> &str;
    fn less_than(&self, other: &Self) -> bool;
    fn greater_than(&self, other: &Self) -> bool;
}

struct Order {
    price: f64,
    quantity: f64,
    timestamp: String,
    order_type: String
}

impl CompareOrder for Order {

    fn create(p: f64, q: f64, t: &str, ot: &str) -> Order {
        Order {
            price: p,
            quantity: q,
            timestamp: t.to_string(),
            order_type: ot.to_string()
        }
    }

    fn get_price(&self) -> f64 {
        self.price
    }

    fn get_quantity(&self) -> f64 {
        self.quantity
    }

    fn get_timestamp(&self) -> &str {
        &self.timestamp
    }

    fn get_order_type(&self) -> &str {
        &self.order_type
    }

    fn less_than(&self, other: &Order) -> bool {
        if self.order_type == "Bid" && other.order_type == "Bid" {
            if self.price > other.price {
                true
            } else if self.price == other.price {
                self.timestamp < other.timestamp
            } else {
                false
            }
        } else if self.order_type == "Ask" && other.order_type == "Ask" {
            if self.price < other.price {
                true
            } else if self.price == other.price {
                self.timestamp < other.timestamp
            } else {
                false
            }
        } else {
            println!("ERROR: MISMATCHED ORDER TYPES!");
            false
        }
    }

    fn greater_than(&self, other: &Order) -> bool {
        if self.order_type == "Bid" && other.order_type == "Bid" {
            if self.price < other.price {
                true
            } else if self.price == other.price {
                self.timestamp > other.timestamp
            } else {
                false
            }
        } else if self.order_type == "Ask" && other.order_type == "Ask" {
            if self.price > other.price {
                true
            } else if self.price == other.price {
                self.timestamp > other.timestamp
            } else {
                false
            }
        } else {
            println!("ERROR: MISMATCHED ORDER TYPES!");
            false
        }
    }
}

fn print_book<T: CompareOrder>(bids: Vec<T>, asks: Vec<T>) {
    for a in asks.iter() {
        println!("{} {} {}", a.get_order_type(), a.get_price(), a.get_quantity());
    }
    println!("-----");
    for b in bids.iter() {
        println!("{} {} {}", b.get_order_type(), b.get_price(), b.get_quantity());
    }
}

fn main() {
    let o = Order::create(123.3, 2.0, "2023", "Bid");
    println!("Order {} {} {} {}", o.price, o.quantity, o.timestamp, o.order_type);

    let mut bids: Vec<Order> = vec![];
    let mut asks: Vec<Order> = vec![];

    bids.push(o);
    print_book(bids, asks);
}