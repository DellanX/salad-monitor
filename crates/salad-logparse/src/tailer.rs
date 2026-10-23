//! Rotation-safe log file tailer for `C:\ProgramData\Salad\logs\log-*.txt`.

use std::fs::{self, File};
use std::io::{BufRead, BufReader, Seek, SeekFrom};
use std::path::{Path, PathBuf};

/// A tailer for log files that automatically handles rotation and size truncation.
pub struct LogTailer {
    dir_path: PathBuf,
    current_file_path: Option<PathBuf>,
    reader: Option<BufReader<File>>,
    last_position: u64,
}

impl LogTailer {
    pub fn new<P: AsRef<Path>>(dir_path: P) -> Self {
        Self {
            dir_path: dir_path.as_ref().to_path_buf(),
            current_file_path: None,
            reader: None,
            last_position: 0,
        }
    }

    /// Finds the newest `log-*.txt` file in the directory based on modification time or name.
    pub fn find_latest_log_file(&self) -> Option<PathBuf> {
        let entries = fs::read_dir(&self.dir_path).ok()?;
        let mut log_files: Vec<(PathBuf, std::time::SystemTime)> = Vec::new();

        for entry in entries.flatten() {
            let path = entry.path();
            if path.is_file() {
                if let Some(file_name) = path.file_name().and_then(|n| n.to_str()) {
                    if file_name.starts_with("log-") && file_name.ends_with(".txt") {
                        let mtime = entry
                            .metadata()
                            .and_then(|m| m.modified())
                            .unwrap_or(std::time::UNIX_EPOCH);
                        log_files.push((path, mtime));
                    }
                }
            }
        }

        log_files.sort_by_key(|(_, mtime)| *mtime);
        log_files.pop().map(|(path, _)| path)
    }

    /// Reads new lines appended since the last call.
    /// Handles log file rotation automatically.
    pub fn read_new_lines(&mut self) -> Vec<String> {
        let latest = match self.find_latest_log_file() {
            Some(path) => path,
            None => return Vec::new(),
        };

        // Check if rotated to a new file
        let is_new_file = self
            .current_file_path
            .as_ref()
            .map_or(true, |cur| cur != &latest);

        if is_new_file {
            if let Ok(file) = File::open(&latest) {
                let mut reader = BufReader::new(file);
                // If opening for the first time or rotated, start from start of file
                self.last_position = 0;
                self.current_file_path = Some(latest.clone());
                self.reader = Some(reader);
            } else {
                return Vec::new();
            }
        }

        // Check file truncation (e.g. file cleared)
        if let Some(ref path) = self.current_file_path {
            if let Ok(meta) = fs::metadata(path) {
                if meta.len() < self.last_position {
                    // File shrank: reset position
                    self.last_position = 0;
                }
            }
        }

        let mut lines = Vec::new();
        if let Some(ref mut reader) = self.reader {
            if reader.seek(SeekFrom::Start(self.last_position)).is_ok() {
                let mut line_buf = String::new();
                while let Ok(bytes) = reader.read_line(&mut line_buf) {
                    if bytes == 0 {
                        break;
                    }
                    lines.push(line_buf.trim_end_matches(['\r', '\n']).to_string());
                    line_buf.clear();
                }
                if let Ok(pos) = reader.stream_position() {
                    self.last_position = pos;
                }
            }
        }

        lines
    }
}

