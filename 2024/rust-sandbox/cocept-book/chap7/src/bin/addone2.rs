fn main() {
    let m = 1;
    let add_m = |x: i32| x + m;
    println!("{}", add_m(1));

    let m = 10;
    let add_m = |x: i32| x + m;
    println!("{}", add_m(1));
}
