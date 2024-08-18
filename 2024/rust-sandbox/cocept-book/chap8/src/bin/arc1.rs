use std::sync::{Arc, Mutex};
use std::thread::spawn;

fn main() {
    let data = Arc::new(Mutex::new(Vec::new()));

    let added = vec![1, 2, 3, 4, 5];

    let mut thrd = Vec::new();
    for aa in added {
        let data = Arc::clone(&data);
        let th = spawn(move || {
            let mut data = data.lock().unwrap();
            data.push(aa);
        });
        thrd.push(th);
    }

    thrd.into_iter().for_each(|th| {
        let _ = th.join();
    });

    let x = data.lock().unwrap();
    println!("{:?}", *x);
}
