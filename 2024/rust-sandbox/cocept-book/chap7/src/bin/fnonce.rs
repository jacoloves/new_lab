#[derive(Debug)]
struct Point {
    x: f64,
    y: f64,
}

fn print_point(p: Point) {
    println!("{:?}", p);
}

fn func_of_func(b: i32, p: Point) -> impl FnOnce(i32) -> i32 {
    move |x| {
        print_point(p);
        x + b
    }
}

fn main() {
    let p = Point { x: 1.0, y: 2.0 };
    let add_2 = func_of_func(2, p);
    println!("{}", add_2(1));
}
