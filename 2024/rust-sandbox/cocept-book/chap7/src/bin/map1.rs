fn add_one_to_vec(vv: Vec<i32>) -> Vec<i32> {
    let mut ret = Vec::new();
    for ee in vv {
        ret.push(ee + 1);
    }
    ret
}

fn main() {
    let vv = vec![0, 1, 2, 3, 4];
    println!("{:?}", add_one_to_vec(vv));
}
