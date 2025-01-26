use std::{
    collections::{hash_map::Entry, HashMap},
    io::stdin,
};

fn main() {
    let mut memory = Memory::new();
    let mut prev_result: f64 = 0.0;

    for line in stdin().lines() {
        let line = line.unwrap();
        if line.is_empty() {
            break;
        }

        let tokens = Token::split(&line);

        match &tokens[0] {
            Token::MemoryPlus(memory_name) => {
                let memory_name = memory_name.to_string();
                let result = memory.add(memory_name, prev_result);
                print_output(result);
            }
            Token::MemoryMinus(memory_name) => {
                let memory_name = memory_name.to_string();
                let result = memory.add(memory_name, -prev_result);
                print_output(result);
            }
            _ => {
                let result = eval_expression(&tokens, &memory);

                print_output(result);
                prev_result = result;
            }
        }
    }
}

fn print_output(value: f64) {
    println!(" => {}", value);
}

struct Memory {
    slots: HashMap<String, f64>,
}

impl Memory {
    fn new() -> Self {
        Self {
            slots: HashMap::new(),
        }
    }

    fn add(&mut self, slot_name: String, prev_result: f64) -> f64 {
        match self.slots.entry(slot_name) {
            Entry::Occupied(mut entry) => {
                *entry.get_mut() += prev_result;
                *entry.get()
            }
            Entry::Vacant(entry) => {
                entry.insert(prev_result);
                prev_result
            }
        }
    }

    fn get(&self, slot_name: &str) -> f64 {
        self.slots.get(slot_name).copied().unwrap_or(0.0)
    }
}

#[derive(Debug, PartialEq)]
enum Token {
    Number(f64),
    MemoryRef(String),
    MemoryPlus(String),
    MemoryMinus(String),
    Plus,
    Minus,
    Asterisk,
    Slash,
    LParen,
    RParen,
}
impl Token {
    fn parse(value: &str) -> Self {
        match value {
            "+" => Self::Plus,
            "-" => Self::Minus,
            "*" => Self::Asterisk,
            "/" => Self::Slash,
            "(" => Self::LParen,
            ")" => Self::RParen,
            _ if value.starts_with("mem") => {
                let mut memory_name = value[3..].to_string();
                if value.ends_with('+') {
                    memory_name.pop();
                    Self::MemoryPlus(memory_name)
                } else if value.ends_with('-') {
                    memory_name.pop();
                    Self::MemoryMinus(memory_name)
                } else {
                    Self::MemoryRef(memory_name)
                }
            }
            _ => Self::Number(value.parse().unwrap()),
        }
    }

    fn split(text: &str) -> Vec<Self> {
        text.split(char::is_whitespace).map(Self::parse).collect()
    }
}

fn eval_expression(tokens: &[Token], memory: &Memory) -> f64 {
    let (result, index) = eval_additive_expression(tokens, 0, memory);
    assert_eq!(tokens.len(), index);
    result
}

fn eval_additive_expression(tokens: &[Token], index: usize, memory: &Memory) -> (f64, usize) {
    let mut index = index;
    let mut result;
    (result, index) = eval_multiplicative_expression(tokens, index, memory);
    while index < tokens.len() {
        match &tokens[index] {
            Token::Plus => {
                let (value, next) = eval_multiplicative_expression(tokens, index + 1, memory);
                result += value;
                index = next;
            }
            Token::Minus => {
                let (value, next) = eval_multiplicative_expression(tokens, index + 1, memory);
                result -= value;
                index = next;
            }
            _ => break,
        }
    }
    (result, index)
}

fn eval_multiplicative_expression(tokens: &[Token], index: usize, memory: &Memory) -> (f64, usize) {
    let mut index = index;
    let mut result;
    (result, index) = eval_primary_expression(tokens, index, memory);
    while index < tokens.len() {
        match &tokens[index] {
            Token::Asterisk => {
                let (value, next) = eval_primary_expression(tokens, index + 1, memory);
                result *= value;
                index = next;
            }
            Token::Slash => {
                let (value, next) = eval_primary_expression(tokens, index + 1, memory);
                result /= value;
                index = next;
            }
            _ => break,
        }
    }
    (result, index)
}

fn eval_primary_expression(tokens: &[Token], index: usize, memory: &Memory) -> (f64, usize) {
    let first_token = &tokens[index];
    match first_token {
        Token::LParen => {
            let (result, next) = eval_additive_expression(tokens, index + 1, memory);
            assert_eq!(Token::RParen, tokens[next]);
            (result, next + 1)
        }
        Token::Number(value) => (*value, index + 1),
        Token::MemoryRef(memory_name) => (memory.get(memory_name), index + 1),
        _ => {
            unreachable!()
        }
    }
}
