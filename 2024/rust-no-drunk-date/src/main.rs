use chrono::{Datelike, Local};
use std::{
    fs::{self, OpenOptions},
    io::{self, Write},
    path::{Path, PathBuf},
};

fn main() -> io::Result<()> {
    // ① 'record' ディレクトリの確認と作成
    let record_dir = Path::new("records");
    if !record_dir.exists() {
        fs::create_dir(record_dir)?;
    }

    let today = Local::now();
    let file_name = format!("records/{}-{:02}.csv", today.year(), today.month());
    let file_path = PathBuf::from(&file_name);

    if !file_path.exists() {
        let mut file = fs::File::create(&file_path)?;
        writeln!(file, "date,drunk?")?;
    }

    // ③ 禁酒の質問
    println!("今日は禁酒できましたか？ [y/n]");
    let mut answer = String::new();
    io::stdin().read_line(&mut answer)?;

    // ④ CSVファイルへの追記
    let mut file = OpenOptions::new().append(true).open(&file_path)?;
    let result = match answer.trim() {
        "y" => "○",
        "n" => "x",
        _ => {
            println!("無効な入力です。'y' か 'n' を入力してください。");
            return Ok(());
        }
    };
    writeln!(file, "{},{result}", today.format("%Y-%m-%d"))?;

    Ok(())
}
