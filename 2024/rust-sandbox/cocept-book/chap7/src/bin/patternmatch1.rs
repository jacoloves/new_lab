fn insert(x: i32, xs: &[i32]) -> Vec<i32> {
    match xs {
        [y, ys @ ..] => {
            if x <= *y {
                [&[x][..], xs].concat()
            } else {
                [&[*y][..], &insert(x, ys)].concat()
            }
        }
        [] => vec![x],
    }
}

fn main() {
    let v: Vec<i32> = Vec::new();
    let v = insert(2, &v);
    println!("{:?}", v);

    let v = insert(1, &v);
    println!("{:?}", v);

    let v = insert(3, &v);
    println!("{:?}", v);
}
