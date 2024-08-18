use std::thread::spawn;

fn main() {
    let mut v_threads = Vec::new();
    let hello = String::from("Hello");
    for i in 0..10 {
        let hello_cloned = hello.clone();
        let thread = spawn(move || println!("{}: {}", i, hello_cloned));
        v_threads.push(thread);
    }
    let _x: Vec<()> = v_threads.into_iter().map(|th| th.join().unwrap()).collect();
}
