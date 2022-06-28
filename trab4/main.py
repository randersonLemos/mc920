import cv2
import time
import copy
import argparse
import itertools
import numpy as np


class Interpolation:
    @classmethod
    def nearneighbours(cls, w, h, ch, mat, width, height):
        w = int(w + 0.5) 
        h = int(h + 0.5) 

        if (w >= 0) and (h >= 0):
            if (w < width) and (h < height):
                return mat[h, w, ch]
        return 0

    @classmethod
    def bilinear(cls, w, h, ch, mat, width, height):
        x, y = int(w), int(h)
        dx = w - x
        dy = h - y
        try:
            return (1-dx)*(1-dy)*mat[y,x,ch] + \
                       dx*(1-dy)*mat[y,x+1,ch] + \
                          (1-dx)*(dy)*mat[y+1,x,ch] + \
                              dx*dy*mat[y+1,x+1,ch]
        except:
            return 0


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
    @classmethod
    def S(cls, scalex, scaley):
        T = np.matrix([[scalex, 0], [0, scaley]])
        return T



    def __init__(self):
        super().__init__()
        self._T = self.S
        self.MT = None


    def apply(self, scalex, scaley, img):
        if len(M.shape) == 3:
            height, width, channel = M.shape
        else:
            height, width = M.shape; channel = 1

        T = self._T(scalex, scaley)
        self.MT = self._apply(T, img, height, width, channel)

        return self.MT
         

    def _apply(self, T, M, height, width, channel):
        TI = T.I
        MT = np.zeros(M.shape).astype('uint8')
        product = itertools.product(range(height), range(width), range(channel))
        for het, wit, cht in product:
            xt = np.matrix([[wit], [het]])
            x = TI*xt

            wi, he = x.item(0,0), x.item(1,0); ch = cht
            px = self.inter_func(wi, he, ch, M, width, height)
            MT[het, wit, cht] = px

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
        if len(M.shape) == 3:
            height, width, channel = M.shape
        else:
            height, width = M.shape; channel = 1


        T = self._T(-degree)
        self.MT = self._apply(T, img, height, width, channel)
        return self.MT
         

    def _apply(self, T, M, height, width, channel):
        TI = T.I
        MT = np.zeros(M.shape).astype('uint8')
        product = itertools.product(range(height), range(width), range(channel))
        for het, wit, cht in product:
            xt = np.matrix([[wit], [het]])
            x = TI*xt

            wi, he = x.item(0,0), x.item(1,0); ch = cht
            px = self.inter_func(wi, he, ch, M, width, height)
            MT[het, wit, cht] = px

        return MT


inter_func = {}
inter_func['nearneighbours'] = Interpolation.nearneighbours
inter_func['bilinear'] = Interpolation.bilinear
inter_keys = inter_func.keys()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script para aplicacao de projecoes perspectiva e geometrica ')
    parser.add_argument('-imagem_entrada', required=True,               help='Imagem para aplicação da projecao selecionada')
    parser.add_argument('-e'             , required=False, type=float,  help='Fator de escala a ser aplicado na imagem')
    parser.add_argument('-d'             , required=False,              help='largura e altura')
    parser.add_argument('-a'             , required=False, type=float,  help='Angulo de rotacao em graus a ser aplicado na imagem')
    parser.add_argument('-m'             , required=False, help='Método de interpolacao. Opcoes: {}'.format(inter_keys))
    
    args = parser.parse_args()
    M = cv2.imread(args.imagem_entrada)

    inter_func = inter_func[args.m]
    Geometric.set_inter_func(inter_func)

    if args.e:
        scalex = args.e
        scaley = args.e
        rotation = 0
        sc = Scale()
        MT = sc.apply(scalex, scaley, M)

    elif args.d:
        largura, altura = map(int, args.d.split(','))
        height, width, _ = M.shape
        scalex = largura / width
        scaley = altura / height
        rotation = 0
        sc = Scale()
        MT = sc.apply(scalex, scaley, M)
 
    elif args.a:
        scalex = 1
        scaley = 1
        rotation = args.a
        rt = Rotation()
        MT = rt.apply(rotation, M)
    else:
        pass

    stem, ext = args.imagem_entrada.split('/')[-1].split('.')
    name = '{}_scax_{:06d}_scay_{:06d}_rot_{:06d}_int_{}.{}'.format(stem, int(scalex*1000), int(scaley*1000), int(rotation*1000), args.m, ext)
    cv2.imwrite('out' + '/' + name, MT)
