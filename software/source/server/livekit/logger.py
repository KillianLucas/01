import os
from datetime import datetime

# Define the path to the log file
LOG_FILE_PATH = 'worker.txt'
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

def log_message(message: str):
    """Append a message to the log file with a timestamp."""
    if not DEBUG:
        return
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE_PATH, 'a') as log_file:
        log_file.write(f"{timestamp} - {message}\n")
