use std::fs::File;
use std::io::{self, BufRead, BufReader};

fn main() -> io::Result<()> {
    let f = File::open("input.txt")?;
    let f = BufReader::new(f);

    let mut lines_vec = Vec::new();

    for ll in f.lines() {
        lines_vec.push(ll.unwrap());
    }

    println!("{:?}", lines_vec);
    Ok(())
}
