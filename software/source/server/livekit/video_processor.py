from livekit.rtc import VideoStream, VideoFrame, VideoBufferType
from livekit.agents import JobContext
from datetime import datetime
import os
import asyncio
from typing import Callable, Coroutine, Any


# Interval settings
INTERVAL = 30  # seconds

# Define the path to the log file
LOG_FILE_PATH = 'video_processor.txt'
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

def log_message(message: str):
    """Append a message to the log file with a timestamp."""
    if not DEBUG:
        return
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE_PATH, 'a') as log_file:
        log_file.write(f"{timestamp} - {message}\n")

class RemoteVideoProcessor:
    def __init__(self, video_stream: VideoStream, job_ctx: JobContext):
        log_message("Initializing RemoteVideoProcessor")
        self.video_stream = video_stream
        self.job_ctx = job_ctx
        self.current_frame = None
        self.lock = asyncio.Lock()
        
        self.interval = INTERVAL
        self.video_context = False
        self.last_capture_time = 0
        
        # Add callback for safety checks
        self.on_instruction_check: Callable[[VideoFrame], Coroutine[Any, Any, None]] | None = None

    async def process_frames(self):
        """Process incoming video frames."""
        async for frame_event in self.video_stream:
            try:
                video_frame = frame_event.frame
                timestamp = frame_event.timestamp_us
                
                log_message(f"Processing frame at timestamp {timestamp/1000000:.3f}s")
                log_message(f"Frame details: size={video_frame.width}x{video_frame.height}, type={video_frame.type}")

                async with self.lock:
                    self.current_frame = video_frame
                    
                    if self.video_context and self._check_interrupt(timestamp):
                        self.last_capture_time = timestamp
                        # Trigger instruction check callback if registered
                        if self.on_instruction_check:
                            await self.on_instruction_check(video_frame)

            except Exception as e:
                log_message(f"Error processing frame: {str(e)}")
                import traceback
                log_message(f"Traceback: {traceback.format_exc()}")


    def register_safety_check_callback(self, callback: Callable[[VideoFrame], Coroutine[Any, Any, None]]):
        """Register a callback for safety checks"""
        self.on_instruction_check = callback
        log_message("Registered instruction check callback")


    async def get_current_frame(self) -> VideoFrame | None:
        """Get the most recent video frame."""
        log_message("Getting current frame")
        async with self.lock:
            if self.current_frame is None:
                log_message("No current frame available")
            return self.current_frame
        
    
    def set_video_context(self, context: bool):
        """Set the video context."""
        log_message(f"Setting video context to: {context}")
        self.video_context = context


    def get_video_context(self) -> bool:
        """Get the video context."""
        return self.video_context


    def _check_interrupt(self, timestamp: int) -> bool:
        """Determine if the video context should be interrupted."""
        return timestamp - self.last_capture_time > self.interval * 1000000
