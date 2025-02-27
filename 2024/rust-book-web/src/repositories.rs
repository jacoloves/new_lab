pub mod label;
pub mod todo;

use thiserror::Error;

#[derive(Error, Debug)]
enum RepositoryError {
    #[error("Unexpected Error: [{0}]")]
    Unexpected(String),
    #[error("NotFound, id is {0}")]
    NotFound(i32),
    #[error("Duplicate, id is {0}")]
    Duplicate(i32),
}
