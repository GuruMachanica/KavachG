# stream_watchdog.py - Self-Healing Camera Stream Watchdog Agent
import threading
import time
from camera_stream import _shared_camera, ensure_camera_started, get_frame


class StreamWatchdog:
    def __init__(self, check_interval_seconds: float = 2.0, freeze_timeout_seconds: float = 4.0):
        self.check_interval = check_interval_seconds
        self.freeze_timeout = freeze_timeout_seconds
        self._last_frame_hash = None
        self._last_change_time = time.time()
        self._running = False
        self._thread = None
        self._heal_count = 0

    def start(self):
        if self._running:
            return
        self._running = True
        self._last_change_time = time.time()
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        print("[Watchdog] Stream Health & Self-Healing Watchdog Agent started.")

    def stop(self):
        self._running = False

    def get_status(self) -> dict:
        return {
            "status": "healthy" if (time.time() - self._last_change_time) < self.freeze_timeout else "recovering",
            "self_heals": self._heal_count,
            "last_active": round(time.time() - self._last_change_time, 1),
            "camera_index": _shared_camera.get_camera_index(),
        }

    def _monitor_loop(self):
        while self._running:
            time.sleep(self.check_interval)
            try:
                frame = _shared_camera.get_latest_frame()
                now = time.time()
                
                if frame is not None:
                    # Quick hash based on downscaled slice to detect frozen video
                    h, w = frame.shape[:2]
                    sample = frame[h // 4 : 3 * h // 4 : 8, w // 4 : 3 * w // 4 : 8]
                    current_hash = hash(sample.tobytes())

                    if current_hash != self._last_frame_hash:
                        self._last_frame_hash = current_hash
                        self._last_change_time = now
                    else:
                        # Frame identical - could be frozen or camera disconnected
                        if now - self._last_change_time > self.freeze_timeout:
                            print(f"[Watchdog] Video stream freeze detected (> {self.freeze_timeout}s). Initiating self-healing...")
                            self._heal_stream()
                else:
                    # No frame at all
                    if now - self._last_change_time > self.freeze_timeout:
                        print("[Watchdog] No frame available. Attempting self-healing restart...")
                        self._heal_stream()

            except Exception as e:
                print(f"[Watchdog] Monitoring loop error: {e}")

    def _heal_stream(self):
        self._heal_count += 1
        current_idx = _shared_camera.get_camera_index()
        _shared_camera.stop()
        time.sleep(0.5)
        _shared_camera.set_camera_index(current_idx)
        self._last_change_time = time.time()
        print(f"[Watchdog] Self-healing complete (Total heals: {self._heal_count}). Camera {current_idx} re-engaged.")


_watchdog_agent = StreamWatchdog()


def start_watchdog():
    _watchdog_agent.start()


def get_watchdog_health():
    return _watchdog_agent.get_status()
