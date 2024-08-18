use std::fs::File;
use std::io;

mod module1;

fn main() -> io::Result<()> {
    let f = File::open("input.txt")?;

    let lines_vec = module1::get_line(f);

    println!("{:?}", lines_vec);
    Ok(())
}
