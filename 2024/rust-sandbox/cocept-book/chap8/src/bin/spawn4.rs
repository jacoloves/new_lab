const N_MAX: usize = 100000000;
const N_THREAD: usize = 4;

const N_ELEM_PER_THRD: usize = N_MAX / N_THREAD;
const RESIDUAL: usize = N_MAX % N_THREAD;

fn main() -> std::thread::Result<()> {
    if RESIDUAL != 0 {
        panic!("N_MAX must be divisible by N_THREAD");
    }

    let mut thrd = Vec::new();
    let v = std::sync::Arc::new((1..=N_MAX).collect::<Vec<_>>());

    for ii in 0..N_THREAD {
        let ist = ii * N_ELEM_PER_THRD;
        let ien = ist + N_ELEM_PER_THRD;
        let vv = std::sync::Arc::clone(&v);
        let th = std::thread::spawn(move || vv[ist..ien].iter().sum::<usize>());
        thrd.push(th);
    }

    let ans: usize = thrd.into_iter().map(|r| r.join().unwrap()).sum::<usize>();

    println!("{}", ans);
    assert_eq!(ans, N_MAX * (N_MAX + 1) / 2);
    Ok(())
}
