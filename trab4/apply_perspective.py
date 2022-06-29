import cv2
import time
import copy
import argparse
import itertools
import numpy as np

if __name__ == '__main__':
    '''
    Aplique uma projeção perspectiva dos pontos (37, 51), (342, 42), (485, 467), (73, 380) para (0, 0), (511, 0),
    (511, 511), (0, 511) na imagem baboon perspectiva.png.
    '''

    #parser = argparse.ArgumentParser(description='Script para aplicacao de projecoes perspectiva')
    #parser.add_argument('-imagem_entrada', required=True,               help='Imagem para aplicação da projecao selecionada')
    #args = parser.parse_args()

    imagem_entrada = 'assets/baboon_perspectiva.png'

    M = cv2.imread(imagem_entrada)

    # Locate points of the documents
    # or object which you want to transform
    pts1 = np.float32([[37, 51], [342, 42],
                       [485, 467], [73, 380]])
    pts2 = np.float32([[0, 0], [511, 0],
                       [511, 511], [0, 511]])
     
    # Apply Perspective Transform Algorithm
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    result = cv2.warpPerspective(M, matrix, (512, 512))
    cv2.imwrite('out/baboon_perspectiva_result.png', result)
