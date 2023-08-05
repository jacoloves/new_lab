use std::{env, fs};
use std::io::{self, Stdout, Write};

use crossterm::{
    event::{self, Event, KeyCode},
    execute,
    terminal::{disable_raw_mode, enable_raw_mode},
    Result,
};


// use tui::backend::CrosstermBackend;
use tui::layout::{Constraint, Direction, Layout};
use tui::style::{Style, Color, Modifier};
use tui::widgets::{ListItem, Borders, Block, List, Paragraph};
use tui::Terminal;
use tui::text::Text;

fn main() -> Result<()> {
    let current_dir = match env::current_dir() {
        Ok(dir) => dir,
        Err(err) => {
            eprintln!("Gailef to get current directory: {}", err);
            return Ok(());
        }
    };

    let entries = match fs::read_dir(&current_dir) {
        Ok(entries) => entries,
        Err(err) => {
            eprintln!("Failed to read directory: {}", err);
            return Ok(());
        }
    };

    // TUI init
    enable_raw_mode()?;
    let mut stdout = io::stdout();
    execute!(stdout, crossterm::terminal::EnterAlternateScreen)?;
    let backend = tui::backend::CrosstermBackend::new(stdout);
    let mut terminal = Terminal::new(backend)?;

    // create TUI widget
    let items: Vec<ListItem> = entries
        .filter_map(|entry| {
            if let Ok(entry) = entry {
                let name = entry.file_name().to_string_lossy().to_string();
                Some(ListItem::new(Text::raw(name)))
            } else {
                None
            }
        })
        .collect();
    let list = List::new(items)
        .block(Block::default().title("Directoru Contents").borders(Borders::ALL))
        .highlight_style(Style::default().fg(Color::Yellow).add_modifier(Modifier::BOLD));

    // TUI main loop
    loop {
        terminal.draw(|f| {
            let chunks = Layout::default()
                .direction(Direction::Vertical)
                .margin(1)
                .constraints([Constraint::Min(0)].as_ref())
                .split(f.size());
            f.render_widget(list.clone(), chunks[0]);
        })?;

        // event handling
        if let Event::Key(key) = event::read()? {
            match key.code {
                KeyCode::Char('q') => break,
                KeyCode::Enter => {
                    let selected_index = list.state().selected().unwrap_or(0);
                    let selected_item = list.items()[selected_index].clone();
                    if let Some(file_name) = selected_item.contents().get(0) {
                        let file_name = file_name.to_string();
                        println!("Selected file: {}", file_name);
                    }
                }
                KeyCode::Char('j') => list.state_mut().move_down(1),
                KeyCode::Char('k') => list.state_mut().move_up(1),
                KeyCode::Char('h') => list.state_mut().move_left(1),
                KeyCode::Char('l') => list.state_mut().move_right(1),
                _ => {}
            }
        }
    }

    execute!(terminal.backend_mut(), crossterm::terminal::LeaveAlternateScreen)?;
    disable_raw_mode()?;
    Ok(())
}
