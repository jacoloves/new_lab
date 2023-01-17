use input_macro::input;

fn main() {
    let mut vec_str: Vec<String> = Vec::new();
    loop {
        let input_str = input!();

        match input_str.as_str() {
            "q" => {
                break;
            }
            _ => {
                vec_str.push(input_str);
            }
        }
    }

    println!("------------");
    for e in vec_str.iter() {
        println!("{}", e);
    }
}
