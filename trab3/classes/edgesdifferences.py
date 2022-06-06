import cv2

from classes.abcdifferences import ABCDifferences


class EdgesDifferences(ABCDifferences):
    def __init__(self, max_edge_norm_diff):
        super().__init__()

        self.max_edge_norm_diff = max_edge_norm_diff


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

        bcurr = cv2.GaussianBlur(curr, (5,5), 0) # Reduce noise
        blast = cv2.GaussianBlur(last, (5,5), 0) # Reduce noise

        ccurr = cv2.Canny(image=bcurr, threshold1=100, threshold2=200) / 255
        clast = cv2.Canny(image=blast, threshold1=100, threshold2=200) / 255

        edge_diff = abs( ccurr.sum() - clast.sum() )
        edge_norm_diff = edge_diff / (self.height*self.width)

        if edge_norm_diff > self.max_edge_norm_diff:
           self._violation[self.num_analyzed_frames] = ( frame, edge_norm_diff  )
        self._all[self.num_analyzed_frames] = ( frame, edge_norm_diff )
        

    def get_violation(self):
        return self._violation


    def get_all(self):
       return self._all


    def suggested_stem(self, video_name):
        stg = ''
        stg += video_name
        stg += '_edgediff'
        stg += '_mpnd_{:.1f}%'.format(100*self.max_edge_norm_diff)
        stg += '_nframe_{:05d}'.format(len(self._violation))
        return stg


    def strategy_name(self):
        return 'Diferença entre bordas'

