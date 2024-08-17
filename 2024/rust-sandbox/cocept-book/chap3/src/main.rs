use core::prelude::v1;

fn myclear(x: &mut String) {
    x.clear();
}

fn main() {
    f4();
}

fn f4() {
    let x = 1;
    let x_ref = &x;
    println!("{}", incr_by_owned(x));
    println!("{}", incr_by_ref(x_ref));
}

fn incr_by_owned(x: i32) -> i32 {
    x + 1
}

fn incr_by_ref(x_ref: &i32) -> i32 {
    *x_ref + 1
}

fn pick2<'a, 'b>(x: &'a [i32], y: &'b [i32], end: usize) -> (&'a [i32], &'b [i32]) {
    (&x[..end], &y[..end])
}

fn f3() {
    let v1 = [1, 2, 3, 4, 5];
    let v2 = [6, 7, 8];

    let p = pick2(&v1, &v2, 2);
    for ss in p.0 {
        println!("{}", ss);
    }
    for ss in p.1 {
        println!("{}", ss);
    }
}

fn pick1(x: &[i32], end: usize) -> &[i32] {
    &x[..end]
}

fn f2() {
    let v1 = vec![1, 2, 3, 4, 5];
    let p = pick1(&v1, 2);
    for ss in p {
        println!("{}", ss);
    }
}

fn f1() {
    let mut s = "Hello".to_string();
    println!("s = {}", s);

    let s_ref = &mut s;
    myclear(s_ref);
    println!("s = {}", s);

    let s_ref2 = &mut s;
    myclear(s_ref2);
    println!("s = {}", s);
}
