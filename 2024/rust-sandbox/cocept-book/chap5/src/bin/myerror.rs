trait MyError: std::fmt::Debug {}

#[derive(Debug)]
struct MyError1;
impl MyError for MyError1 {}

#[derive(Debug)]
struct MyError2;
impl MyError for MyError2 {}

#[derive(Debug)]
struct MyError3;
impl MyError for MyError3 {}

#[derive(Debug)]
struct MyErrorOther;
impl MyError for MyErrorOther {}

fn div4(x: i32) -> Result<(), Box<dyn MyError>> {
    let res = x % 4;
    match res {
        0 => Ok(()),
        1 => Err(Box::new(MyError1)),
        2 => Err(Box::new(MyError2)),
        3 => Err(Box::new(MyError3)),
        _ => Err(Box::new(MyErrorOther)),
    }
}

fn main() {
    println!("{:?}", div4(0));
    println!("{:?}", div4(1));
    println!("{:?}", div4(2));
    println!("{:?}", div4(3));
}
