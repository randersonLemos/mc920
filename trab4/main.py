import cv2
import time
import copy
import argparse
import itertools
import numpy as np


class Interpolation:
    @classmethod
    def nearneighbours(cls, w, h):
        w = int(w + 0.5) 
        h = int(h + 0.5) 
        return w, h


class Projection:
    def apply(self, T, M):
        raise NotImplemented


class Geometric(Projection):
    @classmethod
    def set_inter_func(cls, inter_func):
        cls.inter_func = inter_func


    def __init__(self):
        if not hasattr(self, 'inter_func'):
            raise Exception('inter_func method must be set!')


class Scale(Geometric):
    def __init__(self):
        super().__init__()
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
            wi, he = self.inter_func(x.item(0,0), x.item(1,0)); ch = cht

            if (wi >= 0) and (he >= 0):
                if (wi < width) and (he < height):
                    MT[het, wit, cht] = M[he, wi, ch]

        return MT


class Rotation(Geometric):
    @classmethod
    def R(cls, degree):
        cs = np.cos(degree*np.pi/180)
        sn = np.sin(degree*np.pi/180)
        T = np.matrix([[cs, -sn], [sn, cs]])
        return T


    def __init__(self):
        super().__init__()
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
            wi, he = self.inter_func(x.item(0,0), x.item(1,0)); ch = cht
            
            if (wi >= 0) and (he >= 0):
                if (wi < width) and (he < height):
                    MT[het, wit, cht] = M[he, wi, ch]

        return MT


inter_func = {}
inter_func['nearneighbours'] = Interpolation.nearneighbours
inter_keys = inter_func.keys()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script para aplicacao de projecoes perspectiva e geometrica ')
    parser.add_argument('-imagem_entrada', required=True,  help='Imagem para aplicação da projecao selecionada')
    parser.add_argument('-e'             , required=False, type=float, default=1, help='Fator de escala a ser aplicado na imagem')
    parser.add_argument('-a'             , required=False, type=float, default=0, help='Angulo de rotacao em graus a ser aplicado na imagem')
    parser.add_argument('-m'             , required=False, help='Método de interpolacao. Opcoes: {}'.format(inter_keys))
    
    args = parser.parse_args()

    M = cv2.imread(args.imagem_entrada)

    inter_func = inter_func[args.m]
    Geometric.set_inter_func(inter_func)

    sc = Scale()
    rt = Rotation()
    MT = rt.apply(args.a, sc.apply(args.e, M))

    stem, ext = args.imagem_entrada.split('/')[-1].split('.')
    name = '{}_sca_{:06d}_rot_{:06d}_int_{}.{}'.format(stem, int(args.e*1000), int(args.a*1000), args.m, ext)
    cv2.imwrite('out' + '/' + name, MT)
