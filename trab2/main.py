import cv2
import time
import copy
import argparse
import numpy as np
from multiprocessing import Process


class FloydSteinberg:
    name = 'FloydSteinberg'

    mask = np.array([
          [0, 0, 7]
        , [3, 5, 1]
    ]) / 16
    
    ref = (0, 1)


class StevensonArce:
    name = 'StevensonArce'

    mask = np.array([
          [ 0,  0,  0,  0,  0, 32,  0]
        , [12,  0, 26,  0, 30,  0, 16]
        , [ 0, 12,  0, 26,  0, 12,  0]
        , [ 5,  0, 12,  0, 12,  0,  5]
    ]) / 200
    ref = (0, 3)


class Burkers:
    name = 'Burkers'

    mask = np.array([
          [ 0,  0,  0,  8,  4]
        , [ 2,  4,  8,  4,  2]
    ]) / 32

    ref = (0, 2)


class Sierra:
    name = 'Sierra'


    mask = np.array([
          [ 0,  0,  0,  5,  3]
        , [ 2,  4,  5,  4,  3]
        , [ 0,  2,  3,  2,  0]
    ]) / 32

    ref = (0, 2)


class Stucki:
    name = 'Stucki'

    mask = np.array([
          [ 0,  0,  0,  8,  4]
        , [ 2,  4,  8,  4,  2]
        , [ 1,  2,  4,  2,  1]
    ]) / 42

    ref = (0, 2)


class Jarvis:
    name = 'Jarvis'

    mask = np.array([
          [ 0,  0,  0,  7,  5]
        , [ 3,  5,  7,  5,  3] 
        , [ 1,  3,  5,  3,  1] 
    ]) / 48

    ref = (0, 2)


class Mask:
    def __init__(self, mask):
        self.name = mask.name
        self.mask = mask.mask
        self.ref = mask.ref


    def __iter__(self):
        self._r = 0
        self._c = -1 
        return self


    def __next__(self):
        mask = self.mask
        row, col = mask.shape
        _r = self._r; _c = self._c

        _c += 1
        if _c == col:
            _r += 1 
            _c = _c % col

        while True:
            if _r < row:
                val = mask[_r][_c]

                if val:
                    self._r = _r
                    self._c = _c
                    inc = (_r - self.ref[0] , _c - self.ref[1], )
                    return val, inc

                _c += 1
                if _c == col:
                    _r += 1 
                    _c = _c % col

            else:
                break

        raise StopIteration

            
def apply_dotted(gray, dotted_mask):
    row, col = gray.shape
    
    original = copy.copy(gray)
    dotted   = np.zeros((row, col, ))
    control  = np.zeros((row, col, ))

    for r in range(row):
        for c in range(col):
            if gray[r][c] < 128:
                control[r][c] = 0
            
            else:
                control[r][c] = 1

    for r in range(row):
        for c in range(col):
            if gray[r][c] < 128:
                dotted[r][c] = 0
            
            else:
                dotted[r][c] = 1

            error = gray[r][c] - dotted[r][c]*255
            
            for val, inc in dotted_mask:
                ir, ic = inc
                try:
                    gray[r + ir][c + ic] = gray[r + ir][c + ic] + val*error
                except IndexError:
                    pass

    original = (    original).astype('uint8')
    control  = ( control*255).astype('uint8')
    dotted   = (  dotted*255).astype('uint8')
    return original, control, dotted


def handle_grayscale_image(gray, mask):
    start = time.time()
    original, control, dotted = apply_dotted(gray, mask)
    print('GRAY', mask.name, time.time() - start)
    
    cv2.imwrite('./out/{}.png'.format(name), original)
    cv2.imwrite('./out/{}_control.png'.format(name) , control)
    cv2.imwrite('./out/{}_{}.png'.format(name,mask.name.lower()) , dotted)


def handle_bgr_images(bgr, mask):
    start = time.time()
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    v = hsv[:, :, 2]

    original, control, dotted = apply_dotted(v, mask)

    hsv[:, :, 2] = original
    original  = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    hsv[:, :, 2] = control
    control= cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    hsv[:, :, 2] = dotted
    dotted = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    print('COLOR', mask.name, time.time() - start)

    cv2.imwrite('./out/c{}.png'.format(name), original)
    cv2.imwrite('./out/c{}_control.png'.format(name) , control)
    cv2.imwrite('./out/c{}_{}.png'.format(name,mask.name.lower()) , dotted)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script para aplicacao de tecnicas de pontilhado com difusao de erro')
    parser.add_argument('-imagem_entrada', required=True, help='Imagem (formato png) utilizada para aplicacao das tecnicas de pontilhado com difisao de erro')
    parser.add_argument('-color')

    args  = parser.parse_args()
    path = args.imagem_entrada
    name = path.split('/')[-1].split('.')[0]

    bgr = cv2.imread(path)
    gray  = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)   

    masks = []
    masks.append(Mask(FloydSteinberg))
    masks.append(Mask(StevensonArce))
    masks.append(Mask(Burkers))
    masks.append(Mask(Sierra))
    masks.append(Mask(Stucki))
    masks.append(Mask(Jarvis))

    ### IMAGEM EM ESCALA DE CINZA
    for mask in masks:
        Process( target=handle_grayscale_image, args=( gray, mask,) ).start()

    ### IMAGEM EM BGR
    for mask in masks:
        Process( target=handle_bgr_images, args=( bgr, mask,) ).start()
