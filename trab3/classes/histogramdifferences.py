import cv2
import numpy as np
from classes.abcpixels import ABCPixels


class HistogramDifferences(ABCPixels):
    def __init__(self, max_threshold, alpha):
        super().__init__()

        self.max_threshold = max_threshold
        self.alpha = alpha


    def analyze_frame(self, frame):
        self.num_analyzed_frames += 1
        if self.last is None:
            self.last = frame
            self.height = frame.shape[0]
            self.width  = frame.shape[1]
            return

        self.is_different(frame)

        self.last = frame


    def is_different(self, frame):
        curr = self.brightness(frame)
        last = self.brightness(self.last)

        curr = self.histogram(curr)
        last = self.histogram(last)

        curr_norm = curr / curr.sum()
        last_norm = last / last.sum()

        diff = abs( curr_norm - last_norm ) 

        mean = diff.mean()
        std = diff.std()

        threshold = mean + self.alpha*std
        if threshold > self.max_threshold:
            self.violation[self.num_analyzed_frames] = ( frame, threshold)
        self.all[self.num_analyzed_frames] = ( frame, threshold)




    def histogram(self, frame):
        hist = np.zeros(256).astype('int')
        for idx in range(len(hist)):
            hist[idx] = (frame == idx).sum()

        return hist


