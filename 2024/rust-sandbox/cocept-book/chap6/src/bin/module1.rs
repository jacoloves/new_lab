use std::io::{BufRead, BufReader, Read};

pub fn get_line<T: Read>(f: T) -> Vec<String> {
    let f = BufReader::new(f);
    let mut lines_vec = Vec::new();

    for ll in f.lines() {
        lines_vec.push(ll.unwrap());
    }

    lines_vec
}
