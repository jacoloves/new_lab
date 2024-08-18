use std::io::{self, BufReader};
use std::net::TcpListener;

mod module1;

fn main() -> io::Result<()> {
    let listener = TcpListener::bind("127.0.0.1:3210")?;

    for stream in listener.incoming() {
        let lines_vec = module1::get_lines(stream?);
        println!("{:?}", lines_vec);
    }
    Ok(())
}
