async fn print_number(n: usize) -> usize {
    for ii in 0..2 {
        tokio::time::sleep(tokio::time::Duration::from_millis(10)).await;
        println!("{} from {}", ii, n);
    }
    n
}

#[tokio::main]
async fn main() [
    let mut handler_vec = Vec::new();
    (1..=3).for_each(|ii| {
        handler_vec.push(tokio::spawn(print_number(ii)));
    });

    let ret = futures::future::join_all(handler_vec).await;
    let retval = ret.iter().map(|r| r.unwrap()).collect::<Vec<_>>();
    println!("{:?}", retval);
]