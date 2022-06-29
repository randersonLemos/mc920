import cv2
import time
import copy
import argparse
import itertools
import numpy as np


class Interpolation:
    @classmethod
    def nearneighbours(cls, w, h, ch, mat, width, height):
        x = int(w + 0.5) 
        y = int(h + 0.5) 

        if (x >= 0) and (x < width) \
            and (y >= 0) and (y < height):
                return mat[y, x, ch]
        return 0


    @classmethod
    def bilinear(cls, w, h, ch, mat, width, height):
        x, y = int(w), int(h)
        dx = w - x
        dy = h - y
        x1, y1 = x+1, y+1
        if     (x  >= 0) and (x  < width) \
           and (x1 >= 0) and (x1 < width) \
           and (y  >= 0) and (y  < height) \
           and (y1 >= 0) and (y1 < height):

            return (1-dx)*(1-dy)*mat[y,x,ch] + \
                       dx*(1-dy)*mat[y,x1,ch] + \
                          (1-dx)*(dy)*mat[y1,x,ch] + \
                              dx*dy*mat[y1,x1,ch]
        return 0

    
    @classmethod
    def P(cls, t):
        return t if t > 0 else 0


    @classmethod
    def R(cls, s):
        return 1/6*( cls.P(s+2)**3 -4*cls.P(s+1)**3 +6*cls.P(s)**3 -4*cls.P(s-1)**3 )


    @classmethod
    def bicubic(cls, w, h, ch, mat, width, height):
        x, y = int(w), int(h)
        dx = w - x
        dy = h - y

        px = 0
        for m in range(-1,3):
            for n in range(-1,3):
                xm, yn = x+m, y+n
                if ( xm >= 0 ) and ( xm < width ) \
                   and ( yn >= 0 ) and ( yn < height ):
                    a = mat[yn, xm, ch]
                    rx = cls.R(m-dx)
                    ry = cls.R(dy-n)
                    px += a*rx*ry
                else:
                    return 0
        return px


    @classmethod
    def L(cls, n, x, y, ch, dx, dy, mat, width, height):
        x_1 = x - 1
        x = x
        x1  = x + 1
        x2 = x + 2

        yn_2 = y + n - 2

        if ( x_1 >= 0 ) and ( x_1 < width ) \
            and ( x >= 0 ) and ( x < width ) \
            and ( x1 >= 0 ) and ( x1 < width ) \
            and ( x2 >= 0 ) and ( x2 < width ) \
            and ( yn_2 >= 0 ) and ( yn_2 < height):
                a = -dx*( dx-1 )*( dx-2 )*mat[ yn_2, x_1, ch ]
                b = ( dx+1 )*( dx-1 )*( dx-2 )*mat[ yn_2, x, ch ]
                c = -dx*( dx+1 )*( dx-2 )*mat[ yn_2, x1, ch ]
                d = dx*( dx+1 )*( dx-1 )*mat[ yn_2, x2, ch ]
                return ( a/6 )+( b/2 )+( c/2 )+( d/6 ) + 1e-9 # Valor adicionado apenas para usar os L's no if
                                                              # da função lagrange
        else:
            return 0


    @classmethod
    def lagrange(cls, w, h, ch, mat, width, height):
        x, y = int(w), int(h)
        dx = w - x
        dy = h - y

        L1 = cls.L(1, x, y, ch, dx, dy, mat, width, height)
        L2 = cls.L(2, x, y, ch, dx, dy, mat, width, height)
        L3 = cls.L(3, x, y, ch, dx, dy, mat, width, height)
        L4 = cls.L(4, x, y, ch, dx, dy, mat, width, height)

        if ( L1 == 0) or ( L2 == 0 ) or ( L3 == 0) or ( L4 == 0 ):
            return 0

        a = -dy*( dy-1 )*( dy-2 )*L1
        b = ( dy+1 )*( dy-1 )*( dy-2 )*L2
        c = -dy*( dy+1 )*( dy-2 )*L3
        d = dy*( dy+1 )*( dy-1 )*L4

        return ( a/6 )+( b/2 )+( c/2 )+( d/6 )
        

class Geometric:
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
inter_func['bicubic'] = Interpolation.bicubic
inter_func['lagrange'] = Interpolation.lagrange
inter_keys = inter_func.keys()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script para aplicacao de projecoes geometrica')
    parser.add_argument('-imagem_entrada', required=True,               help='Imagem para aplicação da projecao selecionada')
    parser.add_argument('-e'             , required=False, type=float,  help='Fator de escala a ser aplicado na imagem')
    parser.add_argument('-d'             , required=False,              help='largura e altura')
    parser.add_argument('-a'             , required=False, type=float,  help='Angulo de rotacao em graus a ser aplicado na imagem')
    parser.add_argument('-m'             , required=True, help='Método de interpolacao. Opcoes: {}'.format(inter_keys))
    
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
