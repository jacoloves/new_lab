#[allow(unused_imports)]
use proconio::input;

fn main() {
    pascal_math();
}

#[allow(dead_code)]
fn display_num(a: Vec<i32>, blank: String) {
    let mut str1: String = blank;
    for i in a.iter() {
        str1 = format!("{}{} ", str1, *i);
    }
    println!("{}", str1);
}

#[allow(dead_code)]
fn display_arrow(a: Vec<i32>, blank: String) {
    let mut str2: String = blank;
    for _ in 1..=a.len() {
        str2 = format!("{}/\\", str2);
    }
    println!("{}", str2);
}

#[allow(dead_code)]
fn pascal_math() {
    let mut tmp: Vec<i32> = vec![1, 1];
    let mut tmp2: Vec<i32> = vec![];

    let mut blank_cnt: usize = 4;
    let mut blank: String = "".to_string();

    for _ in 0..blank_cnt {
        blank = format!("{} ", blank);
    }

    display_num(tmp.clone(), blank.clone());

    for i in 2..=5 {
        if i % 2 == 0 {
            tmp2 = vec![];
            display_arrow(tmp.clone(), blank);
            tmp2.push(*tmp.clone().first().unwrap());
            for i in 0..tmp.len()-1 {
                tmp2.push(tmp[i] + tmp[i+1]);
            }
            tmp2.push(*tmp.last().unwrap());
            blank_cnt -= 1;
            for _ in 0..blank_cnt {
                blank = format!("{} ", blank);
            }
            display_num(tmp2.clone(), blank.clone());
        } else {
            tmp = vec![];
            display_arrow(tmp2.clone(), blank.clone());
            tmp.push(*tmp2.clone().first().unwrap());
            for i in 0..tmp2.len()-1 {
                tmp.push(tmp2[i] + tmp2[i+1]);
            }
            tmp.push(*tmp2.last().unwrap());
            for _ in 0..blank_cnt {
                blank = format!("{} ", blank).clone();
            }
            display_num(tmp.clone(), blank);
        }
    }

}

#[allow(dead_code)]
fn divisor1() {
    let mut ans = 0;
    for i in 1..=432 {
        if 432 % i == 0 {
            ans += 1;
        }
    }

    println!("{} 個", ans);
}

#[allow(dead_code)]
fn dice_choice1() {
    let mut ans = 0;
    for i in 1..=6 {
        for j in 1..=6 {
            if 10 <= i + j {
                ans += 1;
            }
        }
    }

    println!("{} 通り", ans);
}

#[allow(dead_code)]
fn calc_p() {
    let mut ans = 0;
    for i in 0..=3 {
        for j in 0..=5 {
            for k in 0..=10 {
                if 300 == i * 100 + j * 50 + k * 10 {
                    ans += 1;
                }
            }
        }
    }

    println!("{} 通り", ans);
}
