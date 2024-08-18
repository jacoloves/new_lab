use std::error::Error;
use std::io;
use tokio::io::AsyncWriteExt;
use tokio::net::TcpListener;
use tokio::net::TcpStream;

async fn echo_process(stream: &mut TcpStream) -> Result<(), Box<dyn Error>> {
    let mut buf = Vec::with_capacity(1024);
    let mut input_prompt = true;
    loop {
        if input_prompt {
            streamwrite("input => ".as_bytes()).await?;
        }
        let read = stream.try_read_buf(&mut buf);
        match read {
            Ok(0) => break,
            Ok(n) => {
                stream.write("output => ".as_bytes()).await?;
                stream.write(&buf[..n]).await?;
                input_prompt = true;
            }
            Err(ref e) if e.kind() == io::ErrorKind::WouldBlock => {
                input_prompt = false;
                continue;
            }
            Err(e) => return Err(e.into());
        }
        buf.clear();
    }
    Ok(())
}

#[tokio::main]
async fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() != 2 {
        panic!("port is not specified");
    }
    let port: usize = args[1].parse().expect("Failed to get the port number");
    let addr = format!("localhost:{}", port);
    let listener = TcpListener::bind(addr).await.unwrap();
    println!("Listenning to the port {}", port);

    loop {
        let (mut stream, _) = listener.accept().await.unwrap();
        tokio::spawn(async move {
            echo_process(&mut stream).await.unwrap();
        });
    }
}