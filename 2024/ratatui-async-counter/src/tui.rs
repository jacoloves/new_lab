use color_eyre::eyre::Result;
use crossterm::event::{KeyEvent, MouseEvent};
use futures::{channel::mpsc::UnboundedReceiver, FutureExt, StreamExt};
use ratatui::backend::Backend;
use tokio::{
    sync::mpsc::{self, UnboundedSender},
    task::JoinHandle,
};

#[derive(Clone, Debug)]
pub enum Event {
    Error,
    Tick,
    Key(KeyEvent),
    Init,
    Quit,
    Closed,
    Render,
    FocusGained,
    FocusLost,
    Paste(String),
    Mouse(MouseEvent),
    Resize(u16, u16),
}

pub struct Tui {
    pub terminal: ratatui::Terminal<Backend<std::io::Stderr>>,
    pub task: JoinHandle<()>,
    pub event_rx: UnboundedReceiver<Event>,
    pub event_tx: UnboundedSender<Event>,
    pub frame_rate: f64,
    pub tick_rate: f64,
}

#[derive(Debug)]
pub struct EventHandler {
    _tx: mpsc::UnboundedSender<Event>,
    rx: mpsc::UnboundedReceiver<Event>,
    task: Option<JoinHandle<()>>,
}

impl EventHandler {
    pub fn new() -> Self {
        let tick_rate = std::time::Duration::from_millis(250);

        let (tx, rx) = mpsc::unbounded_channel();
        let _tx = tx.clone();

        let task = tokio::spawn(async move {
            let mut reader = crossterm::event::EventStream::new();
            let mut interval = tokio::time::interval(tick_rate);
            loop {
                let delay = interval.tick();
                let crossterm_event = reader.next().fuse();
                tokio::select! {
                    maybe_event = crossterm_event => {
                        match maybe_event {
                            Some(Ok(evt)) -> {
                                match evt {
                                    crossterm::event::Event::Key(key) => {
                                        if key.kind == crossterm::event::KeyEventKind::Press {
                                            tx.send(Event::Key(key)).unwrap();
                                        }
                                    },
                                    _ => {},
                                }
                            }
                            Some(Err(_)) => {
                                tx.send(Event::Error).unwrap();
                            }
                            None => {},
                        }
                    },
                    _ = delay => {
                        tx.send(Event::Tick).unwrap();
                    },
                }
            }
        });

        Self {
            _tx,
            rx,
            task: Some(task),
        }
    }

    pub async fn next(&mut self) -> Result<Event> {
        self.rx
            .recv()
            .await
            .ok_or(color_eyre::eyre::eyre!("Unable to get event"))
    }
}

impl Tui {
    pub fn start(&mut self) {
        let tick_delay = std::time::Duration::from_secs_f64(1.0 / self.tick_rate);
        let render_delay = std::time::Duration::from_secs_f64(1.0 / self.frame_rate);
        let _event_tx = self.event_tx.clone();
        self.task = tokio::spawn(async move {
            let mut reader = crossterm::event::EventStream::new();
            let mut tick_interval = tokio::time::interval(tick_delay);
            let mut render_interval = tokio::time::interval(render_delay);
            loop {}
        })
    }
}
