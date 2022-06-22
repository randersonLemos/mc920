import cv2
import time
import copy
import argparse
import itertools
import numpy as np


class Interpolation:
    @classmethod
    def nearnighbours(cls, w, h):
        w = int(w + 0.5) 
        h = int(h + 0.5) 
        return w, h

class Projection:
    def apply(self, T, M):
        raise NotImplemented


class Geometric(Projection):
    pass


class Scale(Geometric):
    def __init__(self):
        self._T = np.matrix([[1,0], [0,1]])
        self.MT = None


    def apply(self, scale, img):
        T = scale*self._T
        self.MT = self._apply(T, img)
        return self.MT
         

    def _apply(self, T, M):
        try:
            height, width, channel = M.shape
        except:
            height, width = M.shape; channel = 1

        TI = T.I
        MT = np.zeros(M.shape).astype('uint8')
        product = itertools.product(range(height), range(width), range(channel))
        for het, wit, cht in product:
            xt = np.matrix([[wit], [het]])
            x = TI*xt
            wi, he = Interpolation.nearnighbours(x.item(0,0), x.item(1,0)); ch = cht
            try:
                MT[het, wit, cht] = M[he, wi, ch]
            except:
                pass

        return MT


class Rotation(Geometric):
    pass



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script para aplicacao de projecoes perspectiva e geometrica ')
    parser.add_argument('-imagem_entrada', required=True, help='Imagem para aplicação da projecao selecionada')
    parser.add_argument('-e'             , required=True, help='Fator de escala a ser aplicado na imagem')
    
    args = parser.parse_args()

    M = cv2.imread(args.imagem_entrada)
    scale = float(args.e)

    sc = Scale()
    MT = sc.apply(scale, M)
