fn main() {
    let v = vec![0, 1, 2, 3];
    let filtered: Vec<i32> = v.into_iter().filter(|&x| x >= 2).collect();
    println!("{:?}", filtered);

    let w = vec![4, 5, 6];
    let sum = w.into_iter().fold(0, |x, y| x + y);
    println!("{}", sum);
}
