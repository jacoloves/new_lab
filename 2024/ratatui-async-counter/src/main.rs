use color_eyre::eyre::Ok;
use crossterm::event::Event;

mod tui;

fn update(app: &mut App, event: Event) -> Result<()> {
    if let Event::Key(key) = event {
        match key.code {
            Char('j') => app.counter += 1,
            Char('k') => app.counter -= 1,
            Char('q') => app.should_quit = true,
            _ => {}
        }
    }
    Ok(())
}

#[tokio::main]
async fn main() -> Result<()> {
    startup()?;

    let result = run();

    shutdown()?;

    result?;

    Ok(())
}
