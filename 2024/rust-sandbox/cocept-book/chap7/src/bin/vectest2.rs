fn main() {
    let mut vv = vec![1, 2, 3, 4];
    let mut iter = (&mut vv).into_iter();

    let x = iter.next().unwrap();
    println!("{}", x);

    let x = iter.next().unwrap();
    println!("{}", x);

    *x += 10;
    println!("{}", x);
}
