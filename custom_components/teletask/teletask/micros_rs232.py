
#################################################################################################
# File:    micros_rs232.py
# Version: V06.3 (Fixed mood confirmation - moods are trigger actions)
#
# Project: PHAeleTaskV1
# Author:  Peter Spriet + AI assistant
# Date:    16-jan-2026
#
# Description:
#   Industrial-grade asynchronous RS232 driver for TELETASK MICROS.
#   Includes:
#     - Dedicated RX-thread (never misses frames)
#     - ACK detection (CMD 0x00/0x01)
#     - Event dispatching into queues
#     - Synchronous SET with:  ACK → EVENT → fallback GET
#     - LOG command to enable event reporting for function types
#     - Perfect for GUI or Home Assistant integrations
#
# History:
#   V01  Basic driver
#   V02  Added dimmer GET
#   V04  MICROS ON=255 fix
#   V05  ACK detection
#   V06  Full RX-thread with dispatcher
#   V06.1 Added LOG command (CMD=0x03) to enable event reporting on connect
#################################################################################################

import serial
import time
import threading
import queue
import json
import os
from typing import Optional, Callable, Union, Tuple

from .protocol import (
    STX,
    CMD_SET, CMD_GET, CMD_LOG, CMD_EVENT,
    FUNC_RELAY, FUNC_DIMMER, FUNC_MOTOR,
    FUNC_LOCMOOD, FUNC_TIMEDMOOD, FUNC_GENMOOD,
    FUNC_FLAG, FUNC_SENSOR, FUNC_COND,
    STATE_ON, STATE_OFF
)

from .helpers import bytes_to_hex, checksum


class MicrosRS232:
    """V06 - Threaded RS232 driver for TELETASK MICROS."""

    def __init__(
        self,
        config_path: str = "config.json",
        log_callback: Optional[Callable[[str], None]] = None
    ) -> None:
        """
        Initialize the TELETASK MICROS RS232 driver.

        Args:
            config_path: Path to JSON config file with serial and reliability settings.
            log_callback: Optional callback function for log messages.

        Raises:
            FileNotFoundError: If config file does not exist.
            ValueError: If config file is malformed or missing required keys.
        """
        self.log_callback = log_callback

        # Validate and load configuration
        if not os.path.exists(config_path):
            raise FileNotFoundError(
                f"Config file not found: {config_path}. "
                f"Create it with 'serial' and 'reliability' sections."
            )

        try:
            with open(config_path, "r") as f:
                cfg = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file '{config_path}': {e}")

        # Validate required sections
        if "serial" not in cfg:
            raise ValueError("Config missing required section: 'serial'")
        if "reliability" not in cfg:
            raise ValueError("Config missing required section: 'reliability'")

        serial_cfg = cfg["serial"]
        rel_cfg = cfg["reliability"]

        # Serial params with validation
        self.port = serial_cfg.get("port")
        if not self.port:
            raise ValueError("Config missing 'serial.port'")
        self.baudrate = serial_cfg.get("baudrate", 19200)
        self.timeout = serial_cfg.get("timeout", 1.0)

        # Reliability params with defaults
        self.retries = rel_cfg.get("retries", 3)
        self.confirm_timeout_ms = rel_cfg.get("confirm_timeout_ms", 800)
        self.ack_timeout_ms = rel_cfg.get("ack_timeout_ms", 300)
        self.retry_delay_ms = rel_cfg.get("retry_delay_ms", 250)
        self.post_send_gap_ms = rel_cfg.get("post_send_gap_ms", 140)
        self.pre_send_flush = rel_cfg.get("pre_send_flush", True)

        # Serial handle
        self.ser = None

        # Queues for RX-thread
        self.queue_ack    = queue.Queue()
        self.queue_event  = queue.Queue()
        self.queue_get    = queue.Queue()

        # Threading controls
        self._stop_event = threading.Event()
        self._thread = None

        # TX lock
        self._tx_lock = threading.Lock()


    #################################################################################################
    # INTERNAL: Start / Stop RX Thread
    #################################################################################################
    def start(self):
        """Open serial connection and start the RX-thread."""
        self.ser = serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            timeout=self.timeout,
            write_timeout=1,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            rtscts=False,
            dsrdtr=False,
            xonxoff=False
        )

        self.ser.setDTR(True)
        self.ser.setRTS(False)

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._rx_loop, daemon=True)
        self._thread.start()

        self._log("[INFO] RX-thread started")

    def stop(self):
        """Stop RX thread and close serial port."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=1.0)
        if self.ser:
            self.ser.close()
        self._log("[INFO] RX-thread stopped and serial closed")

    #################################################################################################
    # INTERNAL: RX Loop (reads ALL frames)
    #################################################################################################
    def _rx_loop(self) -> None:
        """
        Continuous frame reader with proper synchronization.

        Features:
            - Scans for STX byte to synchronize
            - Validates frame length
            - Handles incomplete reads gracefully
            - Never blocks the main thread
        """
        while not self._stop_event.is_set():
            try:
                # Read first byte, scan for STX
                first = self.ser.read(1)
                if len(first) < 1:
                    continue

                if first[0] != STX:
                    # Discard non-STX byte and continue scanning (common: 0x0A newline)
                    if first[0] not in (0x0A, 0x0D):  # Don't log newline/carriage return
                        self._log(f"[WARN] Resync: discarded byte 0x{first[0]:02X}")
                    continue

                # Read length byte
                length_byte = self.ser.read(1)
                if len(length_byte) < 1:
                    continue

                ln = length_byte[0]

                # Validate length (minimum: STX + LEN + CMD + CHK = 4 bytes, so ln >= 3)
                if ln < 3 or ln > 64:
                    self._log(f"[WARN] Invalid frame length: {ln}, discarding")
                    continue

                # Read remaining payload (ln - 1 because LEN includes itself but not STX)
                payload = self.ser.read(ln - 1)
                if len(payload) < ln - 1:
                    self._log("[WARN] Incomplete frame received, discarding")
                    continue

                frame = bytes([STX, ln]) + payload
                self._handle_incoming_frame(frame)

            except serial.SerialException as e:
                self._log(f"[ERR] Serial error in RX-loop: {e}")
                time.sleep(0.1)
            except Exception as e:
                self._log(f"[ERR] RX-loop exception: {e}")
                time.sleep(0.1)

    #################################################################################################
    # INTERNAL: Dispatcher — routes ACK / EVENT / GET frames
    #################################################################################################
    def _handle_incoming_frame(self, frame: bytes) -> None:
        """Route incoming frame into the proper queue."""

        # Log to GUI / HA
        self._log_hex("RX", frame)

        cmd = frame[2]

        # ACK = CMD 0x00 or 0x01
        if cmd in (0x00, 0x01):
            try:
                self.queue_ack.put_nowait(frame)
            except queue.Full:
                self._log("[WARN] ACK queue full, frame dropped")
            return

        # EVENT frames
        if cmd == CMD_EVENT:
            try:
                self.queue_event.put_nowait(frame)
            except queue.Full:
                self._log("[WARN] EVENT queue full, frame dropped")
            return

        # GET-reply frames
        if cmd == CMD_GET:
            try:
                self.queue_get.put_nowait(frame)
            except queue.Full:
                self._log("[WARN] GET queue full, frame dropped")
            return

        # OTHER → ignore safely
        return

    #################################################################################################
    # INTERNAL: Logging helpers
    #################################################################################################
    def _log(self, msg: str):
        """Safely send log messages to the callback (GUI or HA)."""
        if self.log_callback:
            try:
                self.log_callback(msg)
            except Exception:
                pass

    def _log_hex(self, kind: str, frame: bytes):
        """Log a frame as hex to the callback."""
        ts = time.strftime("%H:%M:%S")
        hexstr = frame.hex(" ").upper()
        self._log(f"{ts}  {kind}: {hexstr}")

    #################################################################################################
    # INTERNAL: Frame helpers (compose + checksum + TX)
    #################################################################################################
    @staticmethod
    def _checksum(data: bytes) -> int:
        return sum(data) & 0xFF

    def _compose_frame(self, cmd: int, payload: bytes) -> bytes:
        ln = 3 + len(payload)
        base = bytes([STX, ln, cmd]) + payload
        return base + bytes([self._checksum(base)])

    def _send_frame(self, frame: bytes):
        """
        Thread-safe transmit:
            - Flush RX buffer (optional)
            - Log TX
            - Write frame
            - Short timing gap so MICROS can issue ACK (outside lock to allow RX processing)
        """
        with self._tx_lock:
            if self.pre_send_flush:
                try:
                    self.ser.reset_input_buffer()
                except Exception:
                    pass

            self._log_hex("TX", frame)
            self.ser.write(frame)
        # Sleep OUTSIDE the lock to allow RX thread to process incoming frames
        time.sleep(self.post_send_gap_ms / 1000.0)

    #################################################################################################
    # INTERNAL: Parser
    #################################################################################################
    def _parse_state(self, frame: bytes):
        """Return (func, num, state) or (None,None,None)."""
        if not frame or len(frame) < 7:
            return None, None, None

        if self._checksum(frame[:-1]) != frame[-1]:
            return None, None, None

        func = frame[3]
        num  = frame[4]
        st   = frame[5]
        return func, num, st

    #################################################################################################
    # INTERNAL: Waiters (ACK / EVENT / GET)
    #################################################################################################
    def _wait_ack(self, timeout_ms: int) -> bool:
        """
        Wait for ANY ACK frame (CMD 0x00 or 0x01).
        RX-thread puts these into queue_ack.
        """
        deadline = time.time() + (timeout_ms / 1000.0)
        while time.time() < deadline:
            remain = deadline - time.time()
            if remain <= 0:
                break
            try:
                fr = self.queue_ack.get(timeout=remain)
                return True
            except queue.Empty:
                pass
        return False

    def _wait_event_for(self, func: int, num: int, desired_state: int, timeout_ms: int) -> bool:
        """
        Wait for matching EVENT frame.

        Args:
            func: Function type to match.
            num: Device number to match.
            desired_state: Expected state value.
            timeout_ms: Maximum wait time in milliseconds.

        Returns:
            True if matching event received, False on timeout.
        """
        deadline = time.time() + (timeout_ms / 1000.0)
        spill: list = []

        while time.time() < deadline:
            remain = deadline - time.time()
            if remain <= 0:
                break
            try:
                fr = self.queue_event.get(timeout=remain)
            except queue.Empty:
                break

            f, n, st = self._parse_state(fr)
            if f == func and n == num and st == desired_state:
                # Found match - restore non-matching events
                for x in spill:
                    try:
                        self.queue_event.put_nowait(x)
                    except queue.Full:
                        pass  # Best effort restoration
                return True
            else:
                spill.append(fr)

        # Restore non-matching events
        for x in spill:
            try:
                self.queue_event.put_nowait(x)
            except queue.Full:
                pass  # Best effort restoration

        return False

    def _wait_get_for(self, func: int, num: int, timeout_ms: int) -> Optional[int]:
        """
        Wait for matching GET-reply.

        Args:
            func: Function type to match.
            num: Device number to match.
            timeout_ms: Maximum wait time in milliseconds.

        Returns:
            State value (int) if found, None on timeout.
        """
        deadline = time.time() + (timeout_ms / 1000.0)
        spill: list = []

        while time.time() < deadline:
            remain = deadline - time.time()
            if remain <= 0:
                break
            try:
                fr = self.queue_get.get(timeout=remain)
            except queue.Empty:
                break

            f, n, st = self._parse_state(fr)
            if f == func and n == num:
                # Restore other frames
                for x in spill:
                    try:
                        self.queue_get.put_nowait(x)
                    except queue.Full:
                        pass  # Best effort restoration
                return st
            else:
                spill.append(fr)

        # Restore non-matching frames
        for x in spill:
            try:
                self.queue_get.put_nowait(x)
            except queue.Full:
                pass  # Best effort restoration

        return None

    #################################################################################################
    # INTERNAL: Synchronous GET (send GET + wait reply)
    #################################################################################################
    def _sync_get_state(self, func: int, num: int, timeout_ms: int = None):
        """
        Send GET and wait for GET-reply or EVENT response.
        MICROS may respond to GET with either CMD_GET or CMD_EVENT frames.
        Returns state or None.
        """
        if timeout_ms is None:
            timeout_ms = self.confirm_timeout_ms

        frame = self._compose_frame(CMD_GET, bytes([func, num]))
        self._send_frame(frame)

        # First try GET queue
        result = self._wait_get_for(func, num, timeout_ms // 2)
        if result is not None:
            return result

        # Fallback: check EVENT queue (MICROS often responds with EVENT frames)
        return self._wait_event_state_for(func, num, timeout_ms // 2)

    def _wait_event_state_for(self, func: int, num: int, timeout_ms: int) -> Optional[int]:
        """
        Wait for matching EVENT frame and return its state value.
        Unlike _wait_event_for, this returns the state instead of checking for a specific state.
        """
        deadline = time.time() + (timeout_ms / 1000.0)
        spill: list = []

        while time.time() < deadline:
            remain = deadline - time.time()
            if remain <= 0:
                break
            try:
                fr = self.queue_event.get(timeout=remain)
            except queue.Empty:
                break

            f, n, st = self._parse_state(fr)
            if f == func and n == num:
                # Found match - restore non-matching events
                for x in spill:
                    try:
                        self.queue_event.put_nowait(x)
                    except queue.Full:
                        pass
                return st
            else:
                spill.append(fr)

        # Restore non-matching events
        for x in spill:
            try:
                self.queue_event.put_nowait(x)
            except queue.Full:
                pass

        return None


    #################################################################################################
    # PUBLIC: Connection API (friendly wrappers)
    #################################################################################################
    def function_log(self, func: int, enable: bool = True) -> None:
        """
        Enable or disable event reporting for a function type.

        Args:
            func: Function type (FUNC_RELAY, FUNC_DIMMER, etc.)
            enable: True to enable event reporting, False to disable.
        """
        state = 1 if enable else 0
        frame = self._compose_frame(CMD_LOG, bytes([func, state]))
        self._send_frame(frame)
        self._log(f"[INFO] LOG {'enabled' if enable else 'disabled'} for func={func}")

    def _enable_event_reporting(self) -> None:
        """Enable event reporting for all supported function types."""
        func_types = [
            FUNC_RELAY,
            FUNC_DIMMER,
            FUNC_LOCMOOD,
            FUNC_TIMEDMOOD,
            FUNC_GENMOOD,
            FUNC_FLAG,
            FUNC_SENSOR,
            FUNC_MOTOR,
            FUNC_COND
        ]
        for func in func_types:
            self.function_log(func, True)
            time.sleep(0.05)  # Small gap between LOG commands
        self._log("[INFO] Event reporting enabled for all function types")

    def connect(self):
        """Open connection and enable event reporting."""
        self.start()
        # Enable event reporting for all function types
        self._enable_event_reporting()

    def disconnect(self):
        """Backward-friendly alias for stop()."""
        self.stop()

    # For compatibility with older code:
    open  = connect
    close = disconnect

    #################################################################################################
    # INTERNAL: SET with confirmation (ACK → EVENT → fallback GET)
    #################################################################################################
    def _set_with_confirm(self, func: int, num: int, desired_state: int, toggle: bool = False) -> bool:
        """
        Perform a SET operation with full confirmation:
             1) If toggle=True → determine target based on current GET
             2) Send SET frame
             3) Wait for ACK (optional - continue even if not received)
             4) Wait for matching EVENT
             5) Fallback: confirm via GET
             6) Retry up to N times
        """

        # Step 1: Toggle handling
        target = desired_state
        if toggle:
            current = self._sync_get_state(func, num, self.confirm_timeout_ms)
            if current is None:
                target = STATE_ON  # best effort default to ON
            else:
                # Toggle: if currently on (1 or 255), turn off; otherwise turn on
                target = STATE_OFF if current in (1, STATE_ON) else STATE_ON

        # Step 2..6: Retries
        for attempt in range(1, int(self.retries) + 1):
            self._log(f"[INFO] SET attempt {attempt}/{self.retries} func={func} num={num} state={target}")

            # Send SET — RX-thread handles responses
            frame = self._compose_frame(CMD_SET, bytes([func, num, target]))
            self._send_frame(frame)

            # Step 3: wait briefly for ACK (optional - MICROS may not send traditional ACKs)
            ack_received = self._wait_ack(100)  # Short timeout, ACK is optional
            if ack_received:
                self._log("[INFO] ACK received")

            # Step 4: wait for EVENT confirmation (check for any state, not just target)
            event_state = self._wait_event_state_for(func, num, self.confirm_timeout_ms)
            if event_state is not None:
                self._log(f"[INFO] EVENT received: state={event_state}, target={target}")
                if event_state == target:
                    self._log("[OK] Confirm via EVENT")
                    return True
                # For dimmers, accept any non-zero as success when turning on
                if func == FUNC_DIMMER and target > 0 and event_state > 0:
                    self._log("[OK] Confirm via EVENT (dimmer on)")
                    return True

            # Step 5: fallback GET confirmation
            state = self._sync_get_state(func, num, self.confirm_timeout_ms)
            self._log(f"[INFO] GET returned: state={state}, target={target}")
            if state == target:
                self._log("[OK] Confirm via GET")
                return True
            # For dimmers, accept any non-zero as success when turning on
            if func == FUNC_DIMMER and target > 0 and state is not None and state > 0:
                self._log("[OK] Confirm via GET (dimmer on)")
                return True

            # Optional backoff before retry
            time.sleep((self.retry_delay_ms + (50 * (attempt - 1))) / 1000.0)

        # Step 6: After retries → fail
        self._log("[FAIL] SET not confirmed after retries")
        return False

    #################################################################################################
    # PUBLIC: Relay API
    #################################################################################################
    def set_relay(self, num: int, state: str) -> None:
        """
        Set a relay to the specified state.

        Args:
            num: Relay number (1-64 typically).
            state: One of 'ON', 'OFF', or 'TOGGLE'.

        Raises:
            ValueError: If state is not valid.
            RuntimeError: If the SET command was not confirmed.
        """
        s = state.upper()
        if s == "ON":
            ok = self._set_with_confirm(FUNC_RELAY, num, STATE_ON)
        elif s == "OFF":
            ok = self._set_with_confirm(FUNC_RELAY, num, STATE_OFF)
        elif s == "TOGGLE":
            ok = self._set_with_confirm(FUNC_RELAY, num, STATE_ON, toggle=True)
        else:
            raise ValueError("State must be 'ON', 'OFF' or 'TOGGLE'.")

        if not ok:
            raise RuntimeError("Relay SET not confirmed.")

    def get_relay(self, num: int) -> Optional[str]:
        """
        Get the current state of a relay.

        Args:
            num: Relay number.

        Returns:
            'ON', 'OFF', 'UNKNOWN(x)', or None if no response.
        """
        st = self._sync_get_state(FUNC_RELAY, num)
        if st is None:
            return None
        return "ON" if st == STATE_ON else "OFF" if st == STATE_OFF else f"UNKNOWN({st})"

    #################################################################################################
    # PUBLIC: Dimmer API (0..255)
    #################################################################################################
    def set_dimmer(self, num: int, value: Union[int, str]) -> None:
        """
        Set a dimmer to the specified value.

        Args:
            num: Dimmer number (1-32 typically).
            value: Integer 0-255, or 'TOGGLE'.

        Raises:
            RuntimeError: If the SET command was not confirmed.
        """
        if isinstance(value, str) and value.upper() == "TOGGLE":
            ok = self._set_with_confirm(FUNC_DIMMER, num, STATE_OFF, toggle=True)
        else:
            val = max(0, min(255, int(value)))
            ok = self._set_with_confirm(FUNC_DIMMER, num, val)

        if not ok:
            raise RuntimeError("Dimmer SET not confirmed.")

    def get_dimmer(self, num: int) -> Optional[int]:
        """
        Get the current value of a dimmer.

        Args:
            num: Dimmer number.

        Returns:
            Value 0-255, or None if no response.
        """
        return self._sync_get_state(FUNC_DIMMER, num)

    #################################################################################################
    # PUBLIC: Moods (Local / General)
    #################################################################################################
    def set_mood(self, num: int, state: str, mood_type: str = "LOCAL") -> None:
        """
        Set a mood to the specified state.

        Moods are trigger actions, not stateful devices, so we use simpler confirmation:
        - Send SET command
        - Wait for ACK (optional, indicates command received)
        - Don't wait for EVENT or GET (moods don't have persistent state to confirm)

        Args:
            num: Mood number.
            state: One of 'ON', 'OFF', or 'TOGGLE'.
            mood_type: 'LOCAL', 'GENERAL', or 'TIMED'.

        Raises:
            ValueError: If state or mood_type is not valid.
        """
        mood_upper = mood_type.upper()
        if mood_upper == "LOCAL":
            func = FUNC_LOCMOOD
        elif mood_upper == "TIMED":
            func = FUNC_TIMEDMOOD
        elif mood_upper == "GENERAL":
            func = FUNC_GENMOOD
        else:
            raise ValueError(f"mood_type must be LOCAL, TIMED, or GENERAL, got: {mood_type}")

        s = state.upper()
        if s not in ("ON", "OFF", "TOGGLE"):
            raise ValueError("state must be ON, OFF or TOGGLE")

        # For TOGGLE, we just send ON (moods don't have queryable state to toggle from)
        target = STATE_ON if s in ("ON", "TOGGLE") else STATE_OFF

        # Send SET command (moods are fire-and-forget triggers)
        self._log(f"[INFO] Mood SET func={func} num={num} state={target}")
        frame = self._compose_frame(CMD_SET, bytes([func, num, target]))
        self._send_frame(frame)

        # Wait briefly for ACK (optional, just to verify command was received)
        ack_received = self._wait_ack(200)
        if ack_received:
            self._log("[OK] Mood triggered (ACK received)")
        else:
            self._log("[INFO] Mood triggered (no ACK, but command sent)")

        # Success - moods are trigger actions, we don't wait for state confirmation

    #################################################################################################
    # PUBLIC: Flags
    #################################################################################################
    def set_flag(self, num: int, state: str) -> None:
        """
        Set a flag to the specified state.

        Args:
            num: Flag number (1-32 typically).
            state: One of 'ON', 'OFF', or 'TOGGLE'.

        Raises:
            ValueError: If state is not valid.
            RuntimeError: If the SET command was not confirmed.
        """
        s = state.upper()

        if s == "ON":
            ok = self._set_with_confirm(FUNC_FLAG, num, STATE_ON)
        elif s == "OFF":
            ok = self._set_with_confirm(FUNC_FLAG, num, STATE_OFF)
        elif s == "TOGGLE":
            ok = self._set_with_confirm(FUNC_FLAG, num, STATE_ON, toggle=True)
        else:
            raise ValueError("state must be ON, OFF or TOGGLE")

        if not ok:
            raise RuntimeError("Flag SET not confirmed.")


