import sys
import threading
import time
import os
import cv2

class SharedCamera:
    def __init__(self, index: int = 0):
        self.index = index
        self.cap = None
        self._frame = None
        self._running = False
        self._lock = threading.Lock()
        self._state_lock = threading.Lock()
        self._thread = None
        self._simulated = False

    def start(self) -> bool:
        with self._state_lock:
            return self._start_unlocked()

    def _start_unlocked(self) -> bool:
        if self._running:
            return True

        backend = cv2.CAP_DSHOW if sys.platform.startswith("win") else None
        try:
            self.cap = (
                cv2.VideoCapture(self.index, backend)
                if backend is not None
                else cv2.VideoCapture(self.index)
            )
        except Exception:
            self.cap = None

        if self.cap is None or not self.cap.isOpened():
            self.cap = None
            self._simulated = True
        else:
            self._simulated = False

        self._running = True
        self._thread = threading.Thread(target=self._reader, daemon=True)
        self._thread.start()
        return True

    def _reader(self) -> None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sample_1 = os.path.join(base_dir, "Frontend", "assets", "cctv_factory_1.jpg")
        sample_2 = os.path.join(base_dir, "Frontend", "assets", "cctv_factory_2.jpg")

        fallback_img = None
        if os.path.exists(sample_1):
            fallback_img = cv2.imread(sample_1)
        elif os.path.exists(sample_2):
            fallback_img = cv2.imread(sample_2)

        while self._running:
            if not self._simulated and self.cap is not None and self.cap.isOpened():
                ok, frame = self.cap.read()
                if ok:
                    with self._lock:
                        self._frame = frame
                else:
                    time.sleep(0.03)
            else:
                # Simulated realistic factory camera loop
                if fallback_img is not None:
                    # Pick sample based on camera index
                    img_path = sample_2 if (self.index % 2 == 1 and os.path.exists(sample_2)) else sample_1
                    cur_img = cv2.imread(img_path) if os.path.exists(img_path) else fallback_img
                    with self._lock:
                        self._frame = cur_img.copy()
                time.sleep(0.05)

    def get_latest_frame(self):
        with self._lock:
            if self._frame is None:
                return None
            return self._frame.copy()

    def stop(self) -> None:
        with self._state_lock:
            self._stop_unlocked()

    def _stop_unlocked(self) -> None:
        self._running = False
        thread = self._thread
        self._thread = None
        if thread is not None and thread.is_alive():
            thread.join(timeout=0.3)
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def set_camera_index(self, index: int) -> bool:
        with self._state_lock:
            self._stop_unlocked()
            self.index = index
            return self._start_unlocked()

    def get_camera_index(self) -> int:
        with self._state_lock:
            return self.index


_shared_camera = SharedCamera(index=0)


def ensure_camera_started() -> bool:
    return _shared_camera.start()


def set_camera_index(index: int) -> bool:
    return _shared_camera.set_camera_index(index)


def get_camera_index() -> int:
    return _shared_camera.get_camera_index()


def get_frame(timeout_seconds: float = 1.0):
    start = time.time()
    while time.time() - start < timeout_seconds:
        frame = _shared_camera.get_latest_frame()
        if frame is not None:
            return frame
        time.sleep(0.01)
    return None
