use std::{
    sync::mpsc,
    thread,
    time::{Duration, Instant},
};

use crossterm::event::{self, Event, KeyCode};
use tui::backend::CrosstermBackend; // Add this import statement
use tui::{
    layout::{Constraint, Direction, Layout},
    style::{Color, Modifier, Style},
    text::Span,
    widgets::{Block, Borders, Paragraph},
    Terminal,
};

fn main() {
    let (tx, rx) = mpsc::channel();
    thread::spawn(move || loop {
        if event::poll(Duration::from_millis(200)).unwrap() {
            if let Event::Key(key_event) = event::read().unwrap() {
                tx.send(key_event.code).unwrap();
            }
        }
    });

    let backend = CrosstermBackend::new(std::io::stdout());
    let mut terminal = Terminal::new(backend).unwrap();
    let mut start_time = Instant::now();
    let mut elapsed = Duration::new(0, 0);
    let mut runnning = false;

    terminal.clear().unwrap();

    loop {
        terminal
            .draw(|f| {
                let chunks = Layout::default()
                    .direction(Direction::Vertical)
                    .margin(2)
                    .constraints([Constraint::Percentage(50), Constraint::Percentage(50)].as_ref())
                    .split(f.size());

                let time = format!(
                    "{:02}:{:02}:{:02}",
                    elapsed.as_secs() / 3600,
                    elapsed.as_secs() / 60 % 60,
                    elapsed.as_secs() % 60,
                );

                let block = Block::default().borders(Borders::ALL).title(Span::styled(
                    "Stopwatch",
                    Style::default()
                        .fg(Color::White)
                        .add_modifier(Modifier::BOLD),
                ));

                let paragraph = Paragraph::new(time).block(block);

                f.render_widget(paragraph, chunks[0]);
            })
            .unwrap();

        if let Ok(key) = rx.try_recv() {
            match key {
                KeyCode::Char('s') => {
                    if runnning {
                        elapsed += start_time.elapsed();
                    } else {
                        start_time = Instant::now();
                    }
                    runnning = !runnning;
                }
                KeyCode::Char('c') => {
                    break;
                }
                _ => {}
            }
        }

        if runnning {
            elapsed = start_time.elapsed();
        }
    }
}
