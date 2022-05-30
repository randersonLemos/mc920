import cv2
import time
import copy
import argparse
import itertools
import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Process


class ABCPixels:
    def __init__(self):
        self.last = None

        self.all = {}
        
        self.violation = {}

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
                brightness = hsv[:,:,2]
        else:
            raise Exception('Frame must be of shape (A,B) or (A,B,3)')

        return brightness


    def suggested_stem(self, video_name):
        raise NotImplemented

 
    
class PixelsDifferences(ABCPixels):
    def __init__(self, max_pixel_distance, max_pixel_num_per):
        super().__init__()

        self.max_pixel_distance = max_pixel_distance
        self.max_pixel_num_per = max_pixel_num_per


    def is_different(self, frame):
        left  = self.brightness(frame) 
        right = self.brightness(self.last)

        diff = left - right

        viol = diff > self.max_pixel_distance

        nume = viol.sum()

        max_pixel_num = int(self.max_pixel_num_per*self.height*self.width)

        if nume > max_pixel_num:
            self.violation[self.num_analyzed_frames] = ( frame, nume  )
        self.all[self.num_analyzed_frames] = ( frame, nume  )


    def suggested_stem(self, video_name):
        stg = ''
        stg += video_name
        stg += '_mpd_{}'.format(self.max_pixel_distance)
        stg += '_mpnp_{}%'.format(int(100*self.max_pixel_num_per))
        stg += '_nframe_{:05d}'.format(len(self.violation))
        return stg


    def strategy_name(self):
        return 'Diferença entre pixels'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script para busca de mudanças abruptas em videos ')
    parser.add_argument('-video_entrada', required=True, help='Video que se deseja buscas mudancas abruptas')

    args  = parser.parse_args()
    path = args.video_entrada

    name = path.split('/')[-1]
    stem = name[:-4]
    suffix = name[-3:]



    mpds = [50, 150, 250] # max_pixel_distances
    mpps = [0.10, 0.20, 0.30, 0.40, 0.50, 0.60] # max_pixel_num_per


    product = itertools.product(mpds, mpps)
    for mpd, mpp in product:
        cap = cv2.VideoCapture(path)
        pd = PixelsDifferences(max_pixel_distance=mpd, max_pixel_num_per=mpp)

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
            writer = cv2.VideoWriter('out/{}.{}'.format(pd.suggested_stem(stem), suffix),cv2.VideoWriter_fourcc('M','J','P','G'), 30, (frame_width,frame_heigh))
            keys = sorted( list( pd.violation.keys() ) )
            for key in keys:
                tup = pd.violation[key]
                frame, num = tup
                writer.write(frame)

        
        fig, ax = plt.subplots(figsize=(8,5))
        keys = sorted( list( pd.all.keys() ) )
        xs = []; ys = []
        ymin = 999999999
        ymax = 0
        for key in keys:
            tup = pd.all[key]
            frame, num = tup
            xs.append(key)
            ys.append(num)

            if ymin > num:
                ymin = num
            if ymax < num:
                ymax = num

        ax.plot(xs, ys)
        T2 = mpp*pd.height*pd.width
        ax.axhline(y=T2, color='r')
        
        if ymin > T2:
            ymin = T2
        if ymax < T2:
            ymax = T2

        interval = ymax - ymin
        pad = interval*0.05
        ax.set_ylim([ymin-pad, ymax+pad])

        title = ''
        title += 'DISTÂNCIA ENTRE QUADROS PARA A ESTRATÉGIA: {}\n'.format(pd.strategy_name().upper())
        title += 'max. dist. entre pixels (T1): {}\n'.format(mpd)
        title += 'max. de violações por quadro (T2): {} ({}%)\n'.format(int(T2), int(100*mpp))
        ax.set_title(title)
        ax.set_xlabel('Número do quadro')
        ax.set_ylabel('Distancia T2')

        plt.tight_layout(pad=1.10)

        plt.savefig('out/{}.{}'.format(pd.suggested_stem(stem), 'png'))
