import cv2

class ABCDifferences:
    def __init__(self):
        self.last = None

        self._all = {}
        
        self._violation = {}

        self.num_analyzed_frames = 0


    def analyze_frame(self, frame):
        raise NotImplemented


    def if_different(self, frame):
        raise NotImplemented


    def brightness(self, frame):
        if len(frame.shape) == 2:
            brightness = frame
        elif len(frame.shape) == 3:
            if frame.shape[2] == 3:
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) # Converte de BGR para HSV
                brightness = hsv[:,:,2]
        else:
            raise Exception('Frame must be of shape (A,B) or (A,B,3)')

        return brightness


    def suggested_stem(self, video_name):
        raise NotImplemented


    def get_all(self):
        raise NotImplemented


    def get_violation(self):
        raise NotImplemented
