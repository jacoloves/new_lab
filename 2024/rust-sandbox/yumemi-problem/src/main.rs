use std::collections::HashMap;
use std::{error::Error, fs::File};

use csv::{Reader, ReaderBuilder, WriterBuilder};

use serde::Deserialize;
use serde::Serialize;

#[derive(Debug, Deserialize)]
struct ReadRecord {
    create_timestamp: String,
    player_id: String,
    score: u32,
}

#[derive(Debug, Serialize)]
struct WriteRecord {
    rank: u32,
    player_id: String,
    mean_score: u32,
}

fn read_csv() -> Result<(), Box<dyn Error>> {
    let csv_read = "./random_player_scores.csv";
    let csv_write = "./player_ranking.csv";

    let mut rdr = ReaderBuilder::new().has_headers(true).from_path(csv_read)?;
    let mut recs: Vec<ReadRecord> = rdr.deserialize().collect::<Result<_, _>>()?;

    let mut p_scores: HashMap<String, Vec<u32>> = HashMap::new();

    for rec in recs {
        p_scores
            .entry(rec.player_id)
            .or_insert_with(Vec::new)
            .push(rec.score);
    }

    let mut p_ave: Vec<(String, u32)> = p_scores
        .into_iter()
        .map(|(player_id, scores)| {
            let sums: u32 = scores.iter().sum();
            let cnt = scores.len() as u32;
            let m_score = (sums as f64 / cnt as f64).round() as u32;
            (player_id, m_score)
        })
        .collect();

    p_ave.sort_by(|a, b| b.1.cmp(&a.1).then(a.0.cmp(&b.0)));

    let mut w = WriterBuilder::new()
        .has_headers(true)
        .from_path(csv_write)?;
    w.write_record(&["rank", "player_id", "mean_score"])?;

    let mut rnk = 1;
    let mut prev_s = None;
    for (i, (player_id, mean_score)) in p_ave.iter().enumerate() {
        if i >= 10 && prev_s != Some(*mean_score) {
            break;
        }
        if prev_s != Some(*mean_score) {
            rnk = (i + 1) as u32;
        }
    }

    Ok(())
}

fn main() {
    let _ = read_csv();
}
