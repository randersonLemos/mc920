import os
import cv2
import copy
import argparse
import itertools
import numpy as np
import matplotlib.pyplot as plt


def word_to_byte(text):
    lst = []
    for letter in text:
        lst.append('{:08b}'.format(ord(letter)))
    return lst


def int_to_byte(num):
    return '{:08b}'.format(num)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script para que mostra a imagem do plano de bits escolhido')
    parser.add_argument('-imagem_entrada', required=True, help="Imagem utilizada para inserção de mensagem escondida")
    parser.add_argument('-planos_bits',     required=True, help="Planos de bits: ou 0 ou 1 ou 2, ou combinações desses valores separados por ':'")

    args = parser.parse_args()
    imagem_entrada = args.imagem_entrada
    imagem = cv2.imread(imagem_entrada)
    planos_bits = args.planos_bits

    for plano_bits in planos_bits.split(':'):
        plano_bits = int(plano_bits)
        if plano_bits > 7:
            raise Exception('Variavel planos_bits pode ter valor máximo de 7')

        shape = imagem.shape
        nrows, ncols, nchannels = shape

        positions = itertools.product(range(nrows), range(ncols), range(nchannels))

        planos = np.zeros( (nrows, ncols, nchannels) )

        for position in positions:
            pixel = imagem[position]
            byte = int_to_byte(pixel)
            bit = byte[-1 -plano_bits]
            
            planos[position] = bit

        planos = planos*255

        try:
            os.mkdir('out')
        except FileExistsError:
            pass
            
        name = imagem_entrada.split('/')[-1].split('.')[0]
        name = 'out/{}'.format(name)
        cv2.imwrite('{}_plano_bits_{}_B.png'.format(name, plano_bits), planos[:, :, 0])
        cv2.imwrite('{}_plano_bits_{}_G.png'.format(name, plano_bits), planos[:, :, 1])
        cv2.imwrite('{}_plano_bits_{}_R.png'.format(name, plano_bits), planos[:, :, 2])
