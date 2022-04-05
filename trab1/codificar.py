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
    parser.add_argument('-imagem_entrada', required=True, help="Imagem utilizada para inserção de mensagem escondida")
    parser.add_argument('-texto_entrada',  required=True, help="Mensagem a ser escondida na imagem")
    parser.add_argument('-plano_bits',     required=True, type=int, help="Plano de bits: ou 0 ou 1 ou 2")

    args = parser.parse_args()
    imagem = args.imagem_entrada
    mat = cv2.imread(imagem)

    original = mat
    modified = copy.copy(mat)
    shape = original.shape

    with open(args.texto_entrada, 'r') as fh:
        texto = fh.read()

    plano_bits = args.plano_bits

    bytes_lst = word_to_byte(texto)
    bites = ''.join(bytes_lst)
    
    nrows, ncols, nchannels = shape

    if len(bytes_lst)*8 > nrows*ncols*nchannels:
        raise(Exception('Text is to long...'))
    
    positions = itertools.product(range(nrows), range(ncols), range(nchannels))

    for bit, position in zip(bites, positions):
        pixel = original[position]
        byte = int_to_byte(pixel)
        #print(byte, end=' ')    
        if plano_bits == 0:
            byte = byte[:-1] + bit
        elif plano_bits == 1:
            byte = byte[:-2] + bit + byte[-1]
        elif plano_bits == 2:
            byte = byte[:-3] + bit + byte[-2:]
        else:
            raise(Exception('Only 0, 1, and 2 are allowed for "plano_bits"'))

        #print(bit, '\n'+byte, end='\n---\n')    

        modified[position] = int(byte, 2)

    name = imagem.split('/')[-1].split('.')[0]
    name = 'out/{}m_plano{}.png'.format(name, plano_bits)
    cv2.imwrite(name, modified)
