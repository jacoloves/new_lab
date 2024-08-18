fn fact(n: u32) -> u32 {
    if n == 0 {
        1
    } else {
        n * fact(n - 1)
    }
}

fn main() {
    println!("{}", fact(3));
}
