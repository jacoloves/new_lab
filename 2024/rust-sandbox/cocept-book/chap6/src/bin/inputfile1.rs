use std::fs::File;
use std::io::Read;

const BUFSIZE: usize = 1024;

fn main() -> std::io::Result<()> {
    let mut f = File::open("input.txt")?;

    let mut lines = Vec::new();
    let mut linebuf = String::new();

    let mut buf = Vec::new();
    let read_size = f.read_to_end(&mut buf)?;

    for cc in &buf[..read_size] {
        if *cc == b'\n' {
            lines.push(linebuf);
            linebuf = String::new();
        } else {
            linebuf.push(*cc as char);
        }
    }

    println!("{:?}", lines);

    Ok(())
}
