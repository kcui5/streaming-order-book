mod order_book;
use order_book::{CompareOrder, Order, print_book, print_order};
use reqwest;
use tokio;
use json;

async fn get_binance_snapshot(limit: i32) -> Result<i32, reqwest::Error> {
    let snap_url = format!("https://www.binance.us/api/v1/depth?symbol=BTCUSDT&limit={}", limit);
    let response = reqwest::get(snap_url).await?;
    if response.status().is_success() {
        let body = response.text().await?;
        println!("Response body:\n{}", body);
        let resJson = json::parse(&body).expect("parse failed");
        let snapBids = &resJson["bids"];
        println!("bids: {}", snapBids);
        for b in snapBids.members() {
            println!("{}", b);
            let p = b[0].as_f64().unwrap();
            let q = b[1].as_f64().unwrap();
            let currB = Order::create(p, q, "0", "Bid");
            print_order(currB);
        }
    } else {
        println!("Request failed with status: {:?}", response.status());
    }
    
    Ok(1)
}

#[tokio::main]
async fn main() {
    let o = Order::create(123.3, 2.0, "2023", "Bid");
    println!("Order {} {} {} {}", o.get_price(), o.get_quantity(), o.get_timestamp(), o.get_order_type());

    let mut bids: Vec<Order> = vec![];
    let mut asks: Vec<Order> = vec![];

    bids.push(o);
    print_book(bids, asks);
    get_binance_snapshot(100).await;
}
