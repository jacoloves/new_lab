async fn sum_cunc(n: usize) -> usize {
    let ans = (1..=n).into_iter().sum::<usize>();
    println!("{}", ans);
    ans
}

fn main() {
    let fut = sum_cunc(100000000);

    let ls = tokio::task::LocalSet::new();
    let rt = tokio::runtime::Builder::new_multi_thread()
        .enable_all()
        .build()
        .unwrap();
    ls.block_on(&rt, fut);
}
