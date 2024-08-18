fn func_of_func(b: i32) -> impl FnMut(i32) -> i32 {
    let mut count = 0;
    move |x| {
        count += 1;
        println!("count: {}", count);
        x + b
    }
}

fn main() {
    let mut add_2 = func_of_func(2);
    println!("{}", add_2(1));
    println!("{}", add_2(2));

    println!();

    let mut add_3 = func_of_func(3);
    println!("{}", add_3(1));
    println!("{}", add_3(2));
}
