fn always_error() -> Result<(), String> {
    Err("This function always returns an error!".to_string())
}

fn might_fail() -> Result<(), String> {
    let _result = always_error()?;
    Ok(())
}

fn main() {
    let message = match might_fail() {
        Ok(_) => "Success!".to_string(),
        Err(cause_message) => cause_message,
    };
    println!("{}", message);
}
