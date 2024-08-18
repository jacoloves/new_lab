fn main() {
    let mut v = Vec::<Box<dyn std::fmt::Debug>>::new();
    v.push(Box::new(1_i32));
    v.push(Box::new(2_i32));
    v.push(Box::new(3.0_f64));
    v.push(Box::new(String::from("Hello")));

    println!("{:?}", v);
}
