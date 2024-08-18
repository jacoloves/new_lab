use std::cell::RefCell;
use std::collections::HashMap;
use std::rc::Rc;
use std::rc::Weak;
use thiserror::Error;

#[derive(Debug)]
struct Person {
    name: String,
    age: u8,
}

impl Person {
    fn new(name: String, age: u8) -> Person {
        Person { name, age }
    }

    fn age_incr(&self, incr: u8) -> u8 {
        self.age + incr
    }

    fn age_incr_replace(&mut self, incr: u8) {
        self.age += incr;
    }
}

#[derive(Debug)]
struct Parents<'a, 'b> {
    father: &'a Person,
    mother: &'b Person,
}

impl<'a, 'b> Parents<'a, 'b> {
    fn new(father: &'a Person, mother: &'b Person) -> Parents<'a, 'b> {
        Parents { father, mother }
    }
}

enum Sign {
    Positive,
    Zero,
    Negative,
}

enum EnumExample {
    TupleTypeExample1(String),
    TupleTypeExample2(i32, bool),
    StructTypeExample { name: String, age: u8 },
}

#[derive(Error, Debug)]
enum DivError {
    #[error("{0} diveded by zero")]
    DivByZero(i32),
    #[error("Both numerator {0} and demoninator {1} are negative")]
    BothNegative(i32, i32),
}

enum OddEven {
    Odd,
    Even,
}

const BUFSIZE: usize = 1024;
static OFFSET: usize = 15;

struct DataA {
    number_a: Option<Rc<i32>>,
}

struct DataB {
    number_b: Option<Rc<i32>>,
}

struct Node {
    data: i32,
    child: Option<Weak<RefCell<Node>>>,
}

fn main() {
    f20();
}

fn f22() {
    let node1 = Rc::new(RefCell::new(Node {
        data: 1,
        child: None,
    }));
    let node2 = Rc::new(RefCell::new(Node {
        data: 2,
        child: None,
    }));

    node1.borrow_mut().child = Some(Rc::downgrade(&node2));
    node2.borrow_mut().child = Some(Rc::downgrade(&node1));

    println!("link from node1");
    print_link(Rc::clone(&node1));

    println!("link from node2");
    print_link(Rc::clone(&node2));
}

fn f21() {
    loop {
        let node1 = Rc::new(RefCell::new(Node {
            data: 1,
            child: None,
        }));
        let node2 = Rc::new(RefCell::new(Node {
            data: 2,
            child: None,
        }));

        node1.borrow_mut().child = Some(Rc::downgrade(&node2));
        node2.borrow_mut().child = Some(Rc::downgrade(&node1));
    }
}

fn f20() {
    let node3 = Rc::new(RefCell::new(Node {
        data: 3,
        child: None,
    }));

    let node1 = Rc::new(RefCell::new(Node {
        data: 1,
        child: None,
    }));

    let node2 = Rc::new(RefCell::new(Node {
        data: 2,
        child: None,
    }));

    node1.borrow_mut().child = Some(Rc::clone(&node3));
    node2.borrow_mut().child = Some(Rc::clone(&node3));

    println!("link from node1");
    print_link(Rc::clone(&node1));

    println!("link from node2");
    print_link(Rc::clone(&node2));
}

fn print_link(start_node: Rc<RefCell<Node>>) {
    let mut p = Rc::clone(&start_node);
    loop {
        println!("{}", p.borrow().data);
        if p.borrow().child.is_none()
            || Weak::upgrade(p.borrow().child.as_ref().unwrap())
                .unwrap()
                .as_ptr()
                == start_node.as_ptr()
        {
            println!("reached th first node");
            break;
        }
        let ptmp = Weak::upgrade(p.borrow().child.as_ref().unwrap()).unwrap();
        p = ptmp;
    }
}

fn f19() {
    let mut data_a_1 = DataA { number_a: None };
    let mut data_b_1 = DataB { number_b: None };
    let mut data_a_2 = DataA { number_a: None };
    let mut data_b_2 = DataB { number_b: None };

    setdata(&mut data_a_1, &mut data_b_1, 1);
    setdata(&mut data_a_2, &mut data_b_2, 2);

    println!(
        "to be 11, 11: {}, {}",
        data_a_1.number_a.unwrap(),
        data_b_1.number_b.unwrap()
    );

    println!(
        "to be 12, 12: {}, {}",
        data_a_2.number_a.unwrap(),
        data_b_2.number_b.unwrap()
    );
}

fn setdata(data_a: &mut DataA, data_b: &mut DataB, value: i32) {
    let number = Rc::new(value + 10);
    data_a.number_a = Some(Rc::clone(&number));
    data_b.number_b = Some(Rc::clone(&number));
}

fn add_static() {
    const INCREMENT: usize = 2;
    static mut ADD: usize = 1;

    unsafe {
        ADD += INCREMENT;
        println!("ADD: {}", ADD);
    }
}

fn f18() {
    let offset_ref = &OFFSET;

    println!("bufsize = {}", BUFSIZE);
    println!("offset = {}", offset_ref);

    add_static();
    add_static();
    add_static();
}

fn f17() {
    let x = 1;
    let x_prt: *const i32 = &x;

    println!("*x_prt: {}", unsafe { *x_prt });

    let mut y = 2;
    let y_ptr = &mut y as *mut i32;

    unsafe {
        *y_ptr = *x_prt + 1;
    }

    println!("*y_ptr: {}", unsafe { *y_ptr });
    println!("y: {}", y);
}

fn f16() {
    let mut capitals = HashMap::new();

    capitals.insert("Japan", "Tokyo");
    capitals.insert("UK", "London");
    capitals.insert("US", "Washington");

    let targets = vec!["Japan", "US", "France"];
    for tg in targets {
        match capitals.get(tg) {
            Some(s) => println!("The capital of {} is {}", tg, s),
            None => println!(" The capital of {} is not found", tg),
        }
    }
}

fn f15() {
    print_only_even(1);
    print_only_even(2);
    print_only_even(3);
    print_only_even(4);
}

fn odd_or_even(x: i32) -> OddEven {
    if x % 2 == 0 {
        OddEven::Even
    } else {
        OddEven::Odd
    }
}

fn print_only_even(x: i32) {
    if let OddEven::Even = odd_or_even(x) {
        println!("{} is even", x);
    }
}

fn f14() {
    print_num(0);
    print_num(1);
    print_num(5);
    print_num(10);
}

fn print_num(x: i32) {
    println!("input: {}", x);
    let s = match x {
        0 => Some("zero"),
        1 | 2 => Some("small"),
        3..=9 => Some("large"),
        _ => None,
    };

    match s {
        Some(st) => {
            println!("output: {}", st);
        }
        None => {
            println!("Not supported");
        }
    };
}

fn f13() {
    println!("1st calc");
    print_repeat_mydiv(repeat_mydiv(&[(2, 1), (9, 3)]));

    println!();

    println!("2nd calc");
    print_repeat_mydiv(repeat_mydiv(&[(2, 1), (-6, -3), (5, 2)]));

    println!();

    println!("3rd calc");
    print_repeat_mydiv(repeat_mydiv(&[(2, 1), (-6, 0), (6, 3)]));

    println!();
}

fn mydiv(x: i32, y: i32) -> Result<i32, DivError> {
    if y == 0 {
        Err(DivError::DivByZero(x))
    } else if x < 0 && y < 0 {
        Err(DivError::BothNegative(x, y))
    } else {
        Ok(x / y)
    }
}

fn repeat_mydiv(ary: &[(i32, i32)]) -> Result<Vec<i32>, DivError> {
    let mut ret = Vec::new();
    for aa in ary {
        let ans = mydiv(aa.0, aa.1)?;
        ret.push(ans);
        println!("pushed: {} / {} = {}", aa.0, aa.1, ans);
    }
    Ok(ret)
}

fn print_repeat_mydiv(result: Result<Vec<i32>, DivError>) {
    match result {
        Ok(v) => println!("{:?}", v),
        Err(e) => println!("{}", e),
    }
}

fn print_mydiv(x: i32, y: i32) {
    match mydiv(x, y) {
        Ok(ans) => println!("no error. ans = {}", ans),
        Err(e) => println!("{}", e),
    }
}

fn f12() {
    print_mydiv(5, 2);
    print_mydiv(-5, 0);
    print_mydiv(-5, -2);
}

fn func_ex_div_result(x: i32, y: i32) -> Result<i32, &'static str> {
    if y == 0 {
        Err("div by zero")
    } else {
        Ok(x / y)
    }
}

fn func_ex_print_result<T: std::fmt::Display, E: std::fmt::Display>(ans: Result<T, E>) {
    match ans {
        Ok(res) => println!("{}", res),
        Err(str) => println!("{}", str),
    }
}

fn f11() {
    func_ex_print_result(func_ex_div_result(10, 5));
    func_ex_print_result(func_ex_div_result(10, 0));
}

fn f10() {
    let rr1 = func_ex_unwrap(5);
    println!("rr1: {}", rr1.unwrap());

    let rr2 = func_ex_unwrap(-5);
    println!("rr2: {}", rr2.unwrap());
}

fn func_ex_unwrap(x: i32) -> Option<i32> {
    if x >= 0 {
        Some(x)
    } else {
        None
    }
}

fn f9() {
    let mut v: Vec<EnumExample> = Vec::new();

    v.push(EnumExample::TupleTypeExample1(String::from("Hello")));
    v.push(EnumExample::TupleTypeExample2(10, true));
    v.push(EnumExample::StructTypeExample {
        name: String::from("taro"),
        age: 10,
    });

    for e in &v {
        if let EnumExample::StructTypeExample { name: n, age: a } = e {
            println!("StructTypeExample: name={}, age={}", n, a);
        }
    }

    for e in &v {
        match e {
            EnumExample::TupleTypeExample1(s) => println!("TupleTypeExample1: {}", s),
            EnumExample::TupleTypeExample2(n, b) => println!("TupleTypeExample2: {}, {}", n, b),
            EnumExample::StructTypeExample { name: n, .. } => {
                println!("StructTypeExample: name={}", n);
            }
        }
    }
}

fn f8() {
    print_sign(determine_sign(1));
    print_sign(determine_sign(-2));
    print_sign(determine_sign(0));
}

fn print_sign(s: Sign) {
    match s {
        Sign::Positive => println!("+"),
        Sign::Zero => println!("0"),
        Sign::Negative => println!("-"),
    }
}

fn determine_sign(x: i32) -> Sign {
    if x > 0 {
        Sign::Positive
    } else if x < 0 {
        Sign::Negative
    } else {
        Sign::Zero
    }
}

fn f7() {
    let taro = Person {
        name: String::from("taro"),
        age: 50,
    };

    let hanako = Person {
        name: String::from("hanako"),
        age: 48,
    };

    let sato = Parents::new(&taro, &hanako);

    println!("{:?}", sato);
}

fn f6() {
    let taro = Person {
        name: String::from("taro"),
        age: 10,
    };

    println!("taro: {:?}", taro);
}

fn f5() {
    let mut taro = Person::new(String::from("taro"), 10);

    let age_plus1 = taro.age_incr(1);
    println!("age_plus1: {}", age_plus1);

    taro.age_incr_replace(10);
    println!("taro.age: {}", taro.age);
}

fn f4() {
    let mut st = String::from("Hello");

    st.push_str(", World");
    println!("{}", st);
    println!("{}", &st[0..6]);
}

fn f3() {
    let mut v = vec![0, 1, 2, 3];

    println!("before push: {:?}", v);
    v.push(10);
    println!("after push: {:?}", v);

    v[2] += 10;
    println!("after v[2] += 10: {:?}", v);

    println!("&v[3..]: {:?}", &v[3..]);
}

fn f2() {
    let ary = [0, 1, 2, 3];
    let ary_sliced = &ary[0..2];
    for aa in ary_sliced {
        println!("{}", aa);
    }
}

fn f1() {
    let ary = [0, 1, 2, 3];
    for aa in &ary {
        println!("{}", aa);
    }
    println!("ary[1] = {}", ary[1]);
}
