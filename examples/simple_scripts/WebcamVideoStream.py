from __future__ import print_function

import sys
from threading import Lock, Thread

import cv2
import time
from pyniryo.ned.vision.image_functions import show_img_and_check_close


class WebcamVideoStream:

    def __init__(self, src=0, name="WebcamVideoStream", display=False, nb_threads=None):
        self.name = name
        self.display = display
        self._frame = None

        self._lock = Lock()
        self._thread = None

        self._stopped = False
        self._should_stop = False
        self.timestamp_last_frame = time.time()

        self.last_read_timestamp = self.timestamp_last_frame
        self.fps_list = [0.0 for _ in range(30)]
        self._failed_read = 0

        self._stream = cv2.VideoCapture(src)
        if self._stream is None or not self._stream.isOpened():
            sys.exit(4)

        (self._grabbed, self._frame) = self._stream.read()
        # logger.debug("Camera Object created and launched")
        if nb_threads is not None:
            cv2.setNumThreads(nb_threads)
        # logger.info("OpenCV is using {} threads".format(cv2.getNumThreads()))

    def start(self):
        if self._thread is not None and self._thread.isAlive():
            print("Thread already started", file=sys.stderr)
            return
        self._thread = Thread(target=self.update, name=self.name, args=())
        self._thread.daemon = True
        self._thread.start()
        return self

    def _get_new_timestamp(self):
        self.timestamp_last_frame = time.time()

    def read(self):
        with self._lock:
            return self._frame.copy()

    def update(self):
        while not self._should_stop:
            (self._grabbed, frame_obtain) = self._stream.read()
            if not self._grabbed:
                self._failed_read += 1
                print("Video Capture Read Nothing", file=sys.stderr)
                if self._failed_read > 30:
                    self._should_stop = True
                    cv2.destroyWindow(self.name)
                continue
            self._get_new_timestamp()
            self._failed_read = 0
            with self._lock:
                self._frame = frame_obtain.copy()
            if self.display and show_img_and_check_close(self.name, self._frame):
                self._should_stop = True
                cv2.destroyWindow(self.name)
            time.sleep(max(0., 30E-03 - (time.time() - self.timestamp_last_frame)))
        self._stopped = True

    def stop(self):
        print("Stopping Webcam's Stream", file=sys.stderr)

        # del self.stream
        self._should_stop = True
