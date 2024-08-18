use std::sync::mpsc::channel;
use std::thread::spawn;

fn main() {
    let data = vec![1, 2, 3, 4, 5];
    let (tx, rx) = channel();

    let data_len = data.len();

    for dd in data {
        let tx = tx.clone();
        spawn(move || tx.send(dd));
    }

    for _ in 0..data_len {
        println!("{}", rx.recv().unwrap());
    }
}
