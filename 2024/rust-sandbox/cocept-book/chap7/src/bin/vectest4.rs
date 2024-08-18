fn main() {
    let c = "あいうえお";
    let c_vec = c.chars().collect::<Vec<char>>();
    println!("{:?}", c_vec);
}
