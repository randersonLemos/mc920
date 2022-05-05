import cv2
import time
import copy
import argparse
import numpy as np
from multiprocessing import Process


###
# Classes das mascaras das tecnicas de meios-tons
# por difusao de erro consideradas do trabalho.
# Essas mascaras sao passadas para a classe Mask
# que contem toda a logica de obtacao dos valores
# corretos das mascaras
###


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
    """ Classe responsavel por abstrair a logica de utlizacao
    das mascaras das tecnicas de meios-tons por difusao de erro
    consideradas. Essa classe e um iterador, de modo que basta
    fazer um laco de repeticao nela para recuperar os valores
    junto com a posicao relativa de onde esses pesos sao aplicados
    na imagem original.
    """


    def __init__(self, mask):
        self.name = mask.name
        self.mask = mask.mask
        self.ref = mask.ref


    def __iter__(self):
        self._r = 0
        self._c = -1 
        return self


    def __next__(self):
        """ Metodo que encapsula a logica de recuperacao de valores
        e de posicao relativas a serem utilizadas na imagem original
        para difusao do erro
        """

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
    """ Funcao que aplica as tecnicas de meios-tons
    sobre imagens monocromatica (de apenas um canal)
    Parametros de entrada:
        gray : imagem monocromatica
        dotted_mask : objeto da class Mask
    """

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

    original = (    original).astype('uint8') # Imagem original
    control  = ( control*255).astype('uint8') # Imagem em meio-tom (controle) apenas aplicando o limiar 128
    dotted   = (  dotted*255).astype('uint8') # Imagem em meio-tom por difusao de erro
    return original, control, dotted


def apply_dotted_zigzag(gray, dotted_mask):
    """ Funcao que aplica as tecnicas de meios-tons
    sobre imagens monocromatica (de apenas um canal)
    Parametros de entrada:
        gray : imagem monocromatica
        dotted_mask : objeto da class Mask
    """

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
        rangecol = range(col) # Da esquerda para direita
        if r%2 == 1:
            rangecol = reversed(rangecol) # Da direita para esquerda

        for c in rangecol:
            if gray[r][c] < 128:
                dotted[r][c] = 0
            
            else:
                dotted[r][c] = 1

            error = gray[r][c] - dotted[r][c]*255
            
            for val, inc in dotted_mask:
                ir, ic = inc # Valores de incremento corretos para o caminho da esquerda para direita

                if r%2 == 1: # Para o caminho da direita para esquerda, a mascara precisa ser espelha.
                             # Para alcancar esse efeito basta usar o negativo desses valores
                    ir = -ir
                    ic = -ic

                try:
                    gray[r + ir][c + ic] = gray[r + ir][c + ic] + val*error
                except IndexError:
                    pass

    original = (    original).astype('uint8') # Imagem original
    control  = ( control*255).astype('uint8') # Imagem em meio-tom (controle) apenas aplicando o limiar 128
    dotted   = (  dotted*255).astype('uint8') # Imagem em meio-tom por difusao de erro
    return original, control, dotted


def handle_grayscale_image(gray, mask):
    """ Funcao responsavel por fazer todo processo de 
    aplicacao das tecnicas de meios-tons por difusao
    de erro sobre imagens monocromaticas
    """

    ### DEFAULT PATH ###
    start = time.time()
    original, control, dotted = apply_dotted(copy.copy(gray), mask)
    print('GRAY', mask.name, time.time() - start)
    
    cv2.imwrite('./out/{}.png'.format(name), original)
    cv2.imwrite('./out/{}_control.png'.format(name) , control)
    cv2.imwrite('./out/{}_{}.png'.format(name,mask.name.lower()) , dotted)

    
    ### ZIGZAG PATH ###
    start = time.time()
    original, control, dotted = apply_dotted_zigzag(copy.copy(gray), mask)
    print('GRAY', mask.name, time.time() - start)
    
    cv2.imwrite('./out/z{}.png'.format(name), original)
    cv2.imwrite('./out/z{}_control.png'.format(name) , control)
    cv2.imwrite('./out/z{}_{}.png'.format(name,mask.name.lower()) , dotted)


def handle_bgr_images(bgr, mask):
    """ Funcao responsavel por fazer todo o processo de
    aplicacao das tecnicas de meios-tons por difusao de
    erro sobre imagens coloridas
    """

    ### DEFAULT PATH ###
    start = time.time()
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV) # Converte de BGR para HSV
    v = hsv[:, :, 2] # Pegando apenas o canal associado a intencidade luminosa

    original, control, dotted = apply_dotted(copy.copy(v), mask) # Aplicando tecnica de meio-tom

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


    ### ZIGZAG PATH ###
    start = time.time()
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV) # Converte de BGR para HSV
    v = hsv[:, :, 2] # Pegando apenas o canal associado a intencidade luminosa

    original, control, dotted = apply_dotted_zigzag(copy.copy(v), mask) # Aplicando tecnica de meio-tom

    hsv[:, :, 2] = original
    original  = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    hsv[:, :, 2] = control
    control= cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    hsv[:, :, 2] = dotted
    dotted = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    print('COLOR', mask.name, time.time() - start)

    cv2.imwrite('./out/cz{}.png'.format(name), original)
    cv2.imwrite('./out/cz{}_control.png'.format(name) , control)
    cv2.imwrite('./out/cz{}_{}.png'.format(name,mask.name.lower()) , dotted)


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
