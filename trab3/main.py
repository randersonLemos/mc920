import cv2
import time
import copy
import argparse
import numpy as np
from multiprocessing import Process


class ABCPixels:
    def __init__(self):
        self.last = None

        self.violation = []

        self.num_analyzed_frames = 0


    def analyze_frame(self, frame):
        self.num_analyzed_frames += 1
        if self.last is None:
            self.last = frame
            self.height = frame.shape[0]
            self.width  = frame.shape[1]
            return

        self.is_different(frame)


    def if_different(self, frame):
        raise NotImplemented


    def brightness(self, frame):
        if len(frame.shape) == 2:
            brightness = frame
        elif len(frame.shape) == 3:
            if frame.shape[2] == 3:
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) # Converte de BGR para HSV
                brightness = hsv[:,:2]
        else:
            raise Exception('Frame must be of shape (A,B) or (A,B,3)')

        return brightness
 
    
class PixelsDifferences(ABCPixels):
    def __init__(self, max_pixel_distance, max_pixel_num_per):
        super().__init__()

        self.max_pixel_distance = max_pixel_distance
        self.max_pixel_num_per = max_pixel_num_per


    def is_different(self, frame):
        diff = self.brightness(frame) - self.brightness(self.last)
        viol = diff > self.max_pixel_distance
        nume = viol.sum()

        max_pixel_num = int(self.max_pixel_num_per*self.height*self.width)
        if nume > max_pixel_num:
            self.violation.append(( frame, nume  )
                          )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script para busca de mudanças abruptas em videos ')
    parser.add_argument('-video_entrada', required=True, help='Video que se deseja buscas mudancas abruptas')

    args  = parser.parse_args()
    path = args.video_entrada

    cap = cv2.VideoCapture(path)

    pd = PixelsDifferences(max_pixel_distance=20, max_pixel_num_per=0.01)

    while True:
        ret, frame = cap.read() # Captura frame por frame

        if ret == True:   
            #hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV) # Converte de BGR para HSV
            #value = hsv[:,:,2]
            #cv2.imshow('frame', value); cv2.waitKey(5) 
            pd.analyze_frame(frame)

        else:
            break


    print('---')
    print(pd.num_analyzed_frames)
    print(len(pd.violation))
    
    frame_heigh = pd.height
    frame_width = pd.width
    if pd.violation:
        fps = 10
        writer = cv2.VideoWriter('out/frame.mp4',cv2.VideoWriter_fourcc('M','J','P','G'), 30, (frame_width,frame_heigh))
        for tup in pd.violation:
            frame, num = tup
            writer.write(frame)
