fn main() {
    let vv = vec![1, 2, 3, 4];
    let mut iter = (&vv).into_iter();

    let x = iter.next().unwrap();
    println!("{}", x);

    let x = iter.next().unwrap();
    println!("{}", x);

    let x = vv[2];
    println!("{}", x);
}
