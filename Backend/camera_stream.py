import sys
import threading
import time

import cv2


class SharedCamera:
    def __init__(self, index: int = 0):
        self.index = index
        self.cap = None
        self._frame = None
        self._running = False
        self._lock = threading.Lock()
        self._thread = None

    def start(self) -> bool:
        if self._running and self.cap is not None and self.cap.isOpened():
            return True

        backend = cv2.CAP_DSHOW if sys.platform.startswith("win") else None
        self.cap = (
            cv2.VideoCapture(self.index, backend)
            if backend is not None
            else cv2.VideoCapture(self.index)
        )

        if not self.cap.isOpened():
            self.cap = None
            return False

        self._running = True
        self._thread = threading.Thread(target=self._reader, daemon=True)
        self._thread.start()
        return True

    def _reader(self) -> None:
        while self._running and self.cap is not None:
            ok, frame = self.cap.read()
            if ok:
                with self._lock:
                    self._frame = frame
            else:
                time.sleep(0.02)

    def get_latest_frame(self):
        with self._lock:
            if self._frame is None:
                return None
            return self._frame.copy()

    def stop(self) -> None:
        self._running = False
        if self.cap is not None:
            self.cap.release()
            self.cap = None


_shared_camera = SharedCamera(index=0)


def ensure_camera_started() -> bool:
    return _shared_camera.start()


def get_frame(timeout_seconds: float = 1.0):
    start = time.time()
    while time.time() - start < timeout_seconds:
        frame = _shared_camera.get_latest_frame()
        if frame is not None:
            return frame
        time.sleep(0.01)
    return None