"""Global on-demand SHIFT+ENTER keyboard approval & ESC emergency stop listener."""

from typing import Set, Optional
from PySide6.QtCore import QObject, Signal
from pynput import keyboard

class KeyboardApprovalListener(QObject):
    """Global keyboard hook active ONLY during WAITING FOR APPROVAL and RUNNING states."""

    approval_hotkey = Signal()
    stop_hotkey = Signal()

    def __init__(self):
        super().__init__()
        self._waiting_for_approval: bool = False
        self._approval_listener_armed: bool = False
        self._is_running: bool = False
        self._shift_pressed: bool = False
        self._listener: Optional[keyboard.Listener] = None

    def _ensure_listener_started(self):
        """Starts the low-level Windows keyboard hook only when needed."""
        if self._listener is None or not self._listener.is_alive():
            try:
                self._listener = keyboard.Listener(
                    on_press=self._on_press,
                    on_release=self._on_release
                )
                self._listener.daemon = True
                self._listener.start()
            except Exception as e:
                print(f"[KeyboardApprovalListener] Error starting listener: {e}")

    def set_waiting(self, waiting: bool):
        """Activates waiting mode and starts listener hook."""
        self._waiting_for_approval = waiting
        self._approval_listener_armed = False
        self._shift_pressed = False
        if waiting:
            self._ensure_listener_started()

    def set_armed(self, armed: bool):
        """Arms the approval listener after the safety delay."""
        self._approval_listener_armed = armed

    def set_running(self, running: bool):
        """Notifies listener whether automation is actively typing (for ESC emergency stop)."""
        self._is_running = running
        if running:
            self._waiting_for_approval = False
            self._approval_listener_armed = False
            self._ensure_listener_started()
        else:
            # If not running and not waiting, stop the hook completely to free Windows message loop
            if not self._waiting_for_approval:
                self.stop()

    def _is_shift_key(self, key) -> bool:
        if key in (keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r):
            return True
        if hasattr(key, 'vk') and key.vk in (16, 160, 161):
            return True
        return False

    def _is_enter_key(self, key) -> bool:
        if key in (keyboard.Key.enter, keyboard.Key.enter):
            return True
        if hasattr(key, 'vk') and key.vk in (13,):
            return True
        return False

    def _is_esc_key(self, key) -> bool:
        if key == keyboard.Key.esc:
            return True
        if hasattr(key, 'vk') and key.vk in (27,):
            return True
        return False

    def _on_press(self, key):
        # 1. Global ESC key: emergency stop when waiting or running
        if self._is_esc_key(key):
            if self._waiting_for_approval or self._is_running:
                self._waiting_for_approval = False
                self._approval_listener_armed = False
                self._is_running = False
                self.stop_hotkey.emit()
                return

        # 2. Track Shift key state
        if self._is_shift_key(key):
            self._shift_pressed = True

        # 3. Detect SHIFT + ENTER for target approval
        if self._is_enter_key(key):
            if self._waiting_for_approval and self._approval_listener_armed and self._shift_pressed:
                # Disarm immediately to prevent duplicate triggers
                self._waiting_for_approval = False
                self._approval_listener_armed = False
                self.approval_hotkey.emit()

    def _on_release(self, key):
        if self._is_shift_key(key):
            self._shift_pressed = False

    def stop(self):
        """Terminates listener thread and unhooks from Windows."""
        self._waiting_for_approval = False
        self._approval_listener_armed = False
        self._is_running = False
        self._shift_pressed = False
        if self._listener:
            try:
                self._listener.stop()
            except Exception:
                pass
            self._listener = None
