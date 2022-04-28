import cv2
import argparse
import numpy as np

class FloydSteinberg:
    def __init__(self):
        self.mask = np.array([
              [0   , 0   , 7/16]
            , [3/16, 5/16, 1/16]
        ])

        self._ref = (0, 1)


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
                    inc = (_r - self._ref[0] , _c - self._ref[1], )
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

    dotted = np.zeros((row, col, ))
    controller = np.zeros((row, col, ))

    for r in range(row):
        for c in range(col):
            if gray[r][c] < 128:
                controller[r][c] = 0
            
            else:
                controller[r][c] = 1

    for r in range(row):
        for c in range(col):
            if gray[r][c] < 128:
                dotted[r][c] = 0
            
            else:
                dotted[r][c] = 1

            error = gray[r][c] - dotted[r][c]*255
            
            for val, inc in fs:
                ir, ic = inc
                try:
                    gray[r + ir][c + ic] = gray[r + ir][c + ic] + val*error
                except IndexError:
                    pass

    cv2.imshow('gray', gray)
    cv2.imshow('controller', controller)
    cv2.imshow('dotted', dotted)
    cv2.waitKey(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script para aplicacao de tecnicas de pontilhado com difusao de erro')
    parser.add_argument('-imagem_entrada', required=True, help='Imagem (formato png) utilizada para aplicacao das tecnicas de pontilhado com difisao de erro')
    parser.add_argument('-color')

    args  = parser.parse_args()
    path = args.imagem_entrada

    color = cv2.imread(path)
    gray  = cv2.cvtColor(color, cv2.COLOR_BGR2GRAY)   

    fs = FloydSteinberg()
    apply_dotted(gray, fs)

    import IPython; IPython.embed()
