fn main() {
    chap1_2();
}

#[allow(dead_code)]
fn chap1_1() {
    println!("Hello World!");
    println!("I'm a Rustacean!");
}

#[allow(dead_code)]
fn chap1_2() {
    let x = 5 + /* 90 + */ 5;
    println!("Is `x` 10 or 100? x = {}", x);
}