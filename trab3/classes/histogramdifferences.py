import cv2
import numpy as np
from classes.abcdifferences import ABCDifferences


class HistogramDifferences(ABCDifferences):
    def __init__(self, alpha):
        super().__init__()

        self.alpha = alpha

        self._diffs = {}

        self.stats = {}

        self.threshold = -1


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

        diff = abs( curr_norm - last_norm ).sum()

        self._diffs[self.num_analyzed_frames] = diff
        self._all  [self.num_analyzed_frames] = ( frame, diff ) 


    def histogram(self, frame):
        hist = np.zeros(256).astype('int')
        for idx in range(len(hist)):
            hist[idx] = (frame == idx).sum()

        return hist


    def get_violation(self):
        if not self.stats:
            mean = np.mean( list( self._diffs.values() ) )
            std  = np.std(  list( self._diffs.values() ) )

            self.stats['mean'] = mean
            self.stats['std']  = std

            self.threshold = mean + self.alpha*std
            for key in self._all:
                frame, diff = self._all[key]

                if diff > self.threshold:
                    self._violation[key] = ( frame, diff )

        return self._violation


    def get_all(self):
        return self._all


    def suggested_stem(self, video_name):
        stg = ''
        stg += video_name
        stg += '_histdiff'
        stg += '_alpha_{}'.format(self.alpha)
        stg += '_thres_{:1.3f}'.format(self.threshold)
        stg += '_nframe_{:05d}'.format(len(self._violation))
        return stg


    def strategy_name(self):
        return 'Diferença entre histogramas'
