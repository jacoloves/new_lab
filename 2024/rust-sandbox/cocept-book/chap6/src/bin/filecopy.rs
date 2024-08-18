use std::fs::File;
use std::io::Read;
use std::io::Write;

const BUFSIZE: usize = 1024;

fn main() -> std::io::Result<()> {
    let mut fr = File::open("input.txt")?;
    let mut fw = File::create("output.txt")?;

    let mut buf = [0_u8; BUFSIZE];
    loop {
        let read_size = fr.read(&mut buf)?;
        if read_size == 0 {
            break;
        } else {
            let _ = fw.write(&buf[..read_size])?;
        }
    }

    Ok(())
}
