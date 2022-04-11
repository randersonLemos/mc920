import os
import cv2
import copy
import argparse
import itertools
import matplotlib.pyplot as plt


def word_to_byte(text):
    lst = []
    for letter in text:
        lst.append('{:08b}'.format(ord(letter)))
    return lst


def int_to_byte(num):
    return '{:08b}'.format(num)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script para inserção de mensagem escondida em images (Esteganografia)')
    parser.add_argument('-imagem_entrada', required=True, help="Imagem utilizada para inserção de mensagem a ser escondida")
    parser.add_argument('-texto_entrada',  required=True, help="Mensagem a ser escondida na imagem")
    parser.add_argument('-planos_bits',    required=True, help="Planos de bits: ou 0 ou 1 ou 2, ou combinações desses valores separados por ':'")

    args = parser.parse_args()
    imagem_entrada = args.imagem_entrada
    imagem = cv2.imread(imagem_entrada)

    planos_bits = sorted(list(map(int, args.planos_bits.split(':')))) # Começar sempre do plano de bits menos significativo

    with open(args.texto_entrada, 'r') as fh:
        texto = fh.read()

    bytes = word_to_byte(texto) # Lista de bytes
    bites = ''.join(bytes) # Sequência de bits
    
    shape = imagem.shape
    nrows, ncols, nchannels = shape
    nplanos = len(planos_bits)

    if len(bytes)*8 > nrows*ncols*nchannels*nplanos:
        raise(Exception('Text is to long...'))
    
    cartesian = itertools.product(range(nrows), range(ncols), range(nchannels), range(nplanos))

    for bit, (row, col, channel, plano_bits) in zip(bites, cartesian):
        position = (row, col, channel)
        pixel = imagem[position]
        byte = int_to_byte(pixel) # Pega valor do pixel em representação de bits
        #print(byte, end=' ')    
        if plano_bits == 0:
            byte = byte[:-1] + bit
        elif plano_bits == 1:
            byte = byte[:-2] + bit + byte[-1]
        elif plano_bits == 2:
            byte = byte[:-3] + bit + byte[-2:]
        else:
            raise(Exception('Apenas 0, 1, e 2 são permitidos para "planos_bits"'))

        #print(bit, '\n'+byte, end='\n---\n')    

        imagem[position] = int(byte, 2)

    try:
        os.mkdir('out')
    except FileExistsError:
        pass

    name = imagem_entrada.split('/')[-1].split('.')[0]
    name = 'out/{}m_plano{}.png'.format(name, ''.join(map(str, planos_bits)))
    cv2.imwrite(name, imagem)
