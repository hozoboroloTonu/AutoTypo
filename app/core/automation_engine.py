"""Background automation engine for simulated keyboard typing."""

import time
import threading
import ctypes
from typing import Optional
from PySide6.QtCore import QObject, Signal
from pynput.keyboard import Controller as KeyboardController, Key
from app.utils.constants import (
    FIRST_MESSAGE_DELAY_MS,
    DEFAULT_TARGET_COUNT,
    STATUS_RUNNING,
    STATUS_COMPLETED,
    STATUS_STOPPED,
    STATUS_ERROR
)
from app.services.logger import LoggerService
from app.services.session_manager import SessionManager

class AutomationEngine(QObject):
    """Core keyboard automation engine communicating with UI through Qt signals."""

    message_sent = Signal(int)           # Messages sent count
    progress_changed = Signal(int)       # 0 - 100 percentage
    status_changed = Signal(str)         # RUNNING, COMPLETED, STOPPED, ERROR
    finished = Signal()
    stopped = Signal()
    error = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._message: str = ""
        self._target_count: int = DEFAULT_TARGET_COUNT
        self._unlimited: bool = False
        self._interval_ms: int = 200
        self._first_delay_ms: int = FIRST_MESSAGE_DELAY_MS  # Strictly 1000 ms
        self._session_id: Optional[str] = None

        self._stop_event = threading.Event()
        self._worker: Optional[threading.Thread] = None
        self._sent_count: int = 0
        self._start_time: float = 0.0
        self._keyboard = KeyboardController()
        
        self._logger = LoggerService.get_instance()
        self._sessions = SessionManager.get_instance()

    def is_running(self) -> bool:
        """Returns whether a background worker is currently active."""
        return self._worker is not None and self._worker.is_alive()

    isRunning = is_running

    def wait(self, timeout_ms: int = 2000):
        """Waits for background worker to terminate."""
        if self._worker is not None and self._worker.is_alive():
            self._worker.join(timeout=timeout_ms / 1000.0)

    def start(
        self,
        message: str,
        target_count: int,
        interval_ms: int,
        unlimited: bool = False,
        first_delay_ms: int = FIRST_MESSAGE_DELAY_MS,
        session_id: Optional[str] = None
    ):
        """Prepares configuration and starts background worker thread."""
        if self.is_running():
            self._logger.warning("Attempted to start automation while worker is already running.")
            return

        self._message = message
        self._target_count = max(1, target_count)
        self._interval_ms = max(10, interval_ms)
        self._unlimited = unlimited
        self._first_delay_ms = FIRST_MESSAGE_DELAY_MS  # Always enforce 1000 ms
        self._session_id = session_id

        self._stop_event.clear()
        self._sent_count = 0
        
        self._worker = threading.Thread(target=self._run, name="AutoTyperWorker", daemon=True)
        self._worker.start()

    def stop(self):
        """Immediately signals the background worker to stop."""
        self._stop_event.set()

    def _press_and_release_enter(self):
        """Sends a clean, real Enter keypress and release to the active target application."""
        try:
            # Win32 keybd_event: VK_RETURN (0x0D), scan code (0x1C)
            ctypes.windll.user32.keybd_event(0x0D, 0x1C, 0, 0)
            time.sleep(0.04)  # 40ms key hold time
            ctypes.windll.user32.keybd_event(0x0D, 0x1C, 2, 0)  # 2 = KEYEVENTF_KEYUP
            time.sleep(0.01)
        except Exception:
            # Fallback to pynput
            self._keyboard.press(Key.enter)
            time.sleep(0.04)
            self._keyboard.release(Key.enter)

    def _run(self):
        """Background worker thread execution.
        Flow: TYPE #1 -> 1000ms -> ENTER -> SENT #1 -> INTERVAL -> TYPE #2 -> ENTER -> SENT #2 -> ...
        """
        self._start_time = time.perf_counter()
        self._sent_count = 0
        
        self.status_changed.emit(STATUS_RUNNING)
        self._logger.info(
            f"Automation started. Mode: {'Unlimited' if self._unlimited else f'Target {self._target_count}'}, Interval: {self._interval_ms}ms"
        )

        try:
            # === MESSAGE #1 ===
            if self._stop_event.is_set():
                self._handle_stopped()
                return

            # 1. Type Message #1
            self._keyboard.type(self._message)

            # 2. Wait fixed 1000 ms before first Enter (interruptible in 0 ms)
            if self._stop_event.wait(timeout=self._first_delay_ms / 1000.0):
                # Stopped during first delay: do not press Enter, stop immediately!
                self._handle_stopped()
                return

            if self._stop_event.is_set():
                self._handle_stopped()
                return

            # 3. Press and Release Enter for Message #1
            self._press_and_release_enter()

            # 4. Confirm Sent #1
            self._sent_count = 1
            self._sessions.update_active_sent(1)
            self.message_sent.emit(1)
            self._update_progress()
            self._logger.info("Message sent #1.")

            # If target count was 1, we are done
            if not self._unlimited and self._sent_count >= self._target_count:
                self._handle_completed()
                return

            # === SUBSEQUENT MESSAGES (#2, #3, ...) ===
            current_msg = 2
            while not self._stop_event.is_set():
                # 1. Wait configured Message Interval BEFORE typing the next message
                if self._stop_event.wait(timeout=self._interval_ms / 1000.0):
                    self._handle_stopped()
                    return

                if self._stop_event.is_set():
                    break

                if not self._unlimited and current_msg > self._target_count:
                    break

                # 2. Type the message
                self._keyboard.type(self._message)

                # 3. IMMEDIATELY press and release Enter (no interval between type and enter!)
                self._press_and_release_enter()

                # 4. Confirm Sent
                self._sent_count = current_msg
                self._sessions.update_active_sent(self._sent_count)
                self.message_sent.emit(self._sent_count)
                self._update_progress()
                self._logger.info(f"Message sent #{self._sent_count}.")

                # 5. Check if target count is reached
                if not self._unlimited and self._sent_count >= self._target_count:
                    self._handle_completed()
                    return

                current_msg += 1

            if self._stop_event.is_set():
                self._handle_stopped()
            else:
                self._handle_completed()

        except Exception as e:
            self._handle_error(str(e))

    def _update_progress(self):
        if self._unlimited:
            self.progress_changed.emit(0)
        else:
            pct = int((self._sent_count / self._target_count) * 100) if self._target_count > 0 else 0
            self.progress_changed.emit(min(100, pct))

    def _handle_completed(self):
        duration = int(time.perf_counter() - self._start_time)
        self._logger.success(f"Automation completed. {self._sent_count} message(s) sent in {duration}s.")
        self._sessions.finish_session(
            status=STATUS_COMPLETED,
            sent_count=self._sent_count,
            duration_seconds=duration
        )
        self.status_changed.emit(STATUS_COMPLETED)
        self.finished.emit()

    def _handle_stopped(self):
        duration = int(time.perf_counter() - self._start_time)
        self._logger.warning(f"Automation stopped. {self._sent_count} message(s) were sent in {duration}s.")
        self._sessions.finish_session(
            status=STATUS_STOPPED,
            sent_count=self._sent_count,
            duration_seconds=duration
        )
        self.status_changed.emit(STATUS_STOPPED)
        self.stopped.emit()

    def _handle_error(self, err_msg: str):
        duration = int(time.perf_counter() - self._start_time)
        self._logger.error(f"Typing failed: {err_msg}")
        self._sessions.finish_session(
            status=STATUS_ERROR,
            sent_count=self._sent_count,
            duration_seconds=duration,
            error_msg=err_msg
        )
        self.status_changed.emit(STATUS_ERROR)
        self.error.emit(err_msg)
