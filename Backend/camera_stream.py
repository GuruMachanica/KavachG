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

        # Find sample factory assets for fallback when no hardware cam is available (Cloud / Docker)
        import numpy as np
        search_paths = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), "../..", "Frontend", "assets")),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Frontend", "assets")),
            os.path.abspath(os.path.join(os.getcwd(), "Frontend", "assets")),
            os.path.abspath(os.path.join(os.getcwd(), "..", "Frontend", "assets")),
            "/app/Frontend/assets"
        ]

        sample_1, sample_2 = None, None
        for sp in search_paths:
            s1 = os.path.join(sp, "cctv_factory_1.jpg")
            s2 = os.path.join(sp, "cctv_factory_2.jpg")
            if os.path.exists(s1):
                sample_1, sample_2 = s1, s2
                break

        fallback_img = None
        if sample_1 and os.path.exists(sample_1):
            fallback_img = cv2.imread(sample_1)

        if fallback_img is None:
            # Generate clean synthetic industrial frame
            fallback_img = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.rectangle(fallback_img, (0, 0), (640, 480), (8, 14, 22), -1)
            cv2.putText(fallback_img, "KAVACHG CLOUD OPTICAL CCTV", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 240, 255), 2)
            cv2.putText(fallback_img, "SECTOR ALPHA - DIRECT VISION", (30, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 229, 163), 1)

        while self._running:
            if self._is_hardware and self.cap is not None and self.cap.isOpened():
                ok, frame = self.cap.read()
                if ok and frame is not None:
                    with self._lock:
                        self._frame = frame
                else:
                    time.sleep(0.02)
            else:
                # Simulated optical CCTV feed loop with live timestamp
                cur_path = sample_2 if (self.index % 2 == 1 and sample_2 and os.path.exists(sample_2)) else sample_1
                cur_img = cv2.imread(cur_path) if (cur_path and os.path.exists(cur_path)) else fallback_img.copy()
                if cur_img is not None:
                    frame_copy = cur_img.copy()
                    ts = time.strftime("%Y-%m-%d %H:%M:%S")
                    cv2.putText(frame_copy, f"CAM {self.index:02d} | {ts} | FPS: 30.0", (16, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 240, 255), 1, cv2.LINE_AA)
                    with self._lock:
                        self._frame = frame_copy
                time.sleep(0.033)


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
