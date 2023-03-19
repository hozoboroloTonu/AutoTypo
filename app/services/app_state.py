"""Central state manager with reactive Qt signals."""

from PySide6.QtCore import QObject, Signal
from app.utils.constants import (
    STATUS_READY,
    STATUS_WAITING,
    STATUS_RUNNING,
    STATUS_COMPLETED,
    STATUS_STOPPED,
    STATUS_ERROR,
    DEFAULT_TARGET_COUNT
)

class AppState(QObject):
    """Observable central application state."""
    
    # Signals for reactive UI updates
    status_changed = Signal(str)
    page_changed = Signal(str)
    counts_changed = Signal(int, int, bool)      # sent, target, unlimited
    progress_changed = Signal(int)               # percentage (0-100)
    elapsed_changed = Signal(int)                # elapsed seconds
    approval_state_changed = Signal(bool)        # is waiting for approval
    error_occurred = Signal(str)
    reset_state_signal = Signal()
    
    _instance = None

    @classmethod
    def get_instance(cls) -> "AppState":
        if cls._instance is None:
            cls._instance = AppState()
        return cls._instance

    def __init__(self):
        super().__init__()
        self._current_page: str = "dashboard"
        self._status: str = STATUS_READY
        self._is_running: bool = False
        self._waiting_for_approval: bool = False
        self._sent_count: int = 0
        self._target_count: int = DEFAULT_TARGET_COUNT
        self._unlimited: bool = False
        self._progress: int = 0
        self._elapsed_seconds: int = 0
        self._last_error: str = ""
        self._session_id: str = ""

    # Property getters
    @property
    def current_page(self) -> str:
        return self._current_page

    @property
    def status(self) -> str:
        return self._status

    @property
    def is_running(self) -> bool:
        return self._is_running

    @property
    def waiting_for_approval(self) -> bool:
        return self._waiting_for_approval

    @property
    def sent_count(self) -> int:
        return self._sent_count

    @property
    def target_count(self) -> int:
        return self._target_count

    @property
    def unlimited(self) -> bool:
        return self._unlimited

    @property
    def progress(self) -> int:
        return self._progress

    @property
    def elapsed_seconds(self) -> int:
        return self._elapsed_seconds

    @property
    def last_error(self) -> str:
        return self._last_error

    @property
    def session_id(self) -> str:
        return self._session_id

    # State modification methods with signal emission
    def set_current_page(self, page_name: str):
        if self._current_page != page_name:
            self._current_page = page_name
            self.page_changed.emit(page_name)

    def set_status(self, new_status: str):
        self._status = new_status
        self._is_running = (new_status == STATUS_RUNNING)
        self._waiting_for_approval = (new_status == STATUS_WAITING)
        self.status_changed.emit(new_status)
        self.approval_state_changed.emit(self._waiting_for_approval)

    def set_waiting_approval(self, waiting: bool):
        self._waiting_for_approval = waiting
        if waiting:
            self.set_status(STATUS_WAITING)
        self.approval_state_changed.emit(waiting)

    def set_counts(self, sent: int, target: int, unlimited: bool):
        self._sent_count = sent
        self._target_count = target
        self._unlimited = unlimited
        
        if unlimited:
            self._progress = 0
        else:
            self._progress = int((sent / target * 100)) if target > 0 else 0
            if self._progress > 100:
                self._progress = 100
                
        self.counts_changed.emit(self._sent_count, self._target_count, self._unlimited)
        self.progress_changed.emit(self._progress)

    def increment_sent(self):
        self._sent_count += 1
        if self._unlimited:
            self._progress = 0
        else:
            self._progress = int((self._sent_count / self._target_count * 100)) if self._target_count > 0 else 0
            if self._progress > 100:
                self._progress = 100
                
        self.counts_changed.emit(self._sent_count, self._target_count, self._unlimited)
        self.progress_changed.emit(self._progress)

    def set_elapsed(self, seconds: int):
        self._elapsed_seconds = seconds
        self.elapsed_changed.emit(seconds)

    def set_error(self, error_message: str):
        self._last_error = error_message
        self.set_status(STATUS_ERROR)
        self.error_occurred.emit(error_message)

    def set_session_id(self, session_id: str):
        self._session_id = session_id

    def reset_session_state(self, target_count: int = DEFAULT_TARGET_COUNT, unlimited: bool = False):
        self._sent_count = 0
        self._target_count = target_count
        self._unlimited = unlimited
        self._progress = 0
        self._elapsed_seconds = 0
        self._last_error = ""
        self._is_running = False
        self._waiting_for_approval = False
        self.set_status(STATUS_READY)
        self.counts_changed.emit(self._sent_count, self._target_count, self._unlimited)
        self.progress_changed.emit(self._progress)
        self.elapsed_changed.emit(0)
        self.reset_state_signal.emit()
