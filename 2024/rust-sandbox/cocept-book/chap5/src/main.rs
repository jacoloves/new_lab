struct GenEx<T> {
    value: T,
}

impl<T> GenEx<T> {
    fn return_value(self) -> T {
        self.value
    }
}

struct Rectangle {
    width: f64,
    height: f64,
}

impl CalcArea for Rectangle {
    fn calc_area(&self) -> f64 {
        self.width * self.height
    }
}

struct RightTriangle {
    width: f64,
    height: f64,
}

impl CalcArea for RightTriangle {
    fn calc_area(&self) -> f64 {
        self.width * self.height * 0.5
    }
}

trait CalcArea {
    fn calc_area(&self) -> f64;
}

fn main() {
    f4();
}

fn f4() {
    let rect = Rectangle {
        width: 1.0,
        height: 2.0,
    };
    let tri = RightTriangle {
        width: 1.0,
        height: 2.0,
    };
    println!("{}", area(&rect));
    println!("{}", area(&tri));
}

fn f3() {
    let rect = Rectangle {
        width: 1.0,
        height: 2.0,
    };
    println!("{}", area(&rect));
}

fn area<T>(x: &T) -> f64
where
    T: CalcArea,
{
    x.calc_area()
}

fn f2() {
    let x1 = GenEx { value: 1 };
    let x2 = GenEx {
        value: String::from("Hello World"),
    };
    let x3 = GenEx::<f64> { value: 2.0 };
    println!("x1: {}", x1.return_value());
    println!("x2: {}", x2.return_value());
    println!("x3: {}", x3.return_value());
}

fn return_input<T>(x: T) -> T {
    x
}

fn f1() {
    let x1 = return_input(1);
    let x2 = return_input(String::from("Hello World"));
    let x3 = return_input::<f64>(2.0);
    println!("x1: {}", x1);
    println!("x2: {}", x2);
    println!("x3: {}", x3);
}
