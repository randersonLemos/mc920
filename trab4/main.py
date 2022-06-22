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
    @classmethod
    def R(cls, degree):
        cs = np.cos(degree*np.pi/180)
        sn = np.sin(degree*np.pi/180)
        T = np.matrix([[cs, -sn], [sn, cs]])
        return T


    def __init__(self):
        self._T = self.R
        self.MT = None


    def apply(self, degree, img):
        T = self._T(-degree)
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



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script para aplicacao de projecoes perspectiva e geometrica ')
    parser.add_argument('-imagem_entrada', required=True,  help='Imagem para aplicação da projecao selecionada')
    parser.add_argument('-e'             , required=False, help='Fator de escala a ser aplicado na imagem')
    parser.add_argument('-a'             , required=False, help='Angulo de rotacao em graus a ser aplicado na imagem')
    
    args = parser.parse_args()

    M = cv2.imread(args.imagem_entrada)

    if args.e:
        scale = float(args.e)
        sc = Scale()
        MT = sc.apply(scale, M)

    elif args.a:
        angle = float(args.a)
        rt = Rotation()
        MT = rt.apply(angle, M)

    cv2.imshow('MT', MT); cv2.waitKey()
