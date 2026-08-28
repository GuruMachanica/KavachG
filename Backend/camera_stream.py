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
        self._is_hardware = False

    def start(self) -> bool:
        with self._state_lock:
            return self._start_unlocked()

    def _start_unlocked(self) -> bool:
        if self._running and self._thread and self._thread.is_alive():
            return True

        self._running = True
        self._thread = threading.Thread(target=self._reader, daemon=True)
        self._thread.start()
        return True

    def _reader(self) -> None:
        # 1. Attempt to open hardware camera with CAP_DSHOW on Windows
        cap = None
        try:
            if sys.platform.startswith("win"):
                cap = cv2.VideoCapture(self.index, cv2.CAP_DSHOW)
            else:
                cap = cv2.VideoCapture(self.index)
        except Exception:
            cap = None

        if cap is not None and cap.isOpened():
            # Test first frame
            ok, test_frame = cap.read()
            if ok and test_frame is not None:
                self.cap = cap
                self._is_hardware = True
                print(f"[CAMERA ENGINE] Live Hardware Camera {self.index} successfully connected ({test_frame.shape[1]}x{test_frame.shape[0]})")
            else:
                cap.release()
                self.cap = None
                self._is_hardware = False
        else:
            self.cap = None
            self._is_hardware = False

        # Find sample factory assets for fallback when no hardware cam is available
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        sample_1 = os.path.join(base_dir, "Frontend", "assets", "cctv_factory_1.jpg")
        sample_2 = os.path.join(base_dir, "Frontend", "assets", "cctv_factory_2.jpg")

        fallback_img = None
        if os.path.exists(sample_1):
            fallback_img = cv2.imread(sample_1)
        elif os.path.exists(sample_2):
            fallback_img = cv2.imread(sample_2)

        while self._running:
            if self._is_hardware and self.cap is not None and self.cap.isOpened():
                ok, frame = self.cap.read()
                if ok and frame is not None:
                    with self._lock:
                        self._frame = frame
                else:
                    time.sleep(0.02)
            else:
                # Simulated optical CCTV feed loop
                if fallback_img is not None:
                    cur_path = sample_2 if (self.index % 2 == 1 and os.path.exists(sample_2)) else sample_1
                    cur_img = cv2.imread(cur_path) if os.path.exists(cur_path) else fallback_img
                    with self._lock:
                        self._frame = cur_img.copy() if cur_img is not None else None
                time.sleep(0.04)

        if self.cap is not None:
            self.cap.release()
            self.cap = None

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
            thread.join(timeout=0.4)
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
    ensure_camera_started()
    start = time.time()
    while time.time() - start < timeout_seconds:
        frame = _shared_camera.get_latest_frame()
        if frame is not None:
            return frame
        time.sleep(0.01)
    return None
