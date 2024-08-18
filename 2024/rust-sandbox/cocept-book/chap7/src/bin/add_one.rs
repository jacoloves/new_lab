fn main() {
    let add_one = |x| x + 1;
    let v: Vec<i32> = vec![0, 1, 2, 3].into_iter().map(add_one).collect();
    println!("{:?}", v);
}
