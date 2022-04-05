import cv2
import copy
import argparse
import itertools
from collections import deque
import matplotlib.pyplot as plt


def word_to_byte(text):
    lst = []
    for letter in text:
        lst.append('{:08b}'.format(ord(letter)))
    return lst


def int_to_byte(num):
    return '{:08b}'.format(num)


def grouper(n, iterable, fillvalue=None):
    "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return itertools.zip_longest(fillvalue=fillvalue, *args)


EFM = '@#FIM#@' # End of Message

EFMBITS = ''.join(word_to_byte(EFM))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script para recuperação de mensagem escondida em images (Esteganografia)')
    parser.add_argument('-imagem_entrada', required=True, help="Imagem com mensagem escondida")
    parser.add_argument('-plano_bits',   required=True, type=int, help="Plano de bits: ou 0 ou 1 ou 2")

    args = parser.parse_args()
    imagem = args.imagem_entrada
    mat = cv2.imread(imagem)
    plano_bits = args.plano_bits

    modified = mat
    shape = modified.shape

    nrows, ncols, nchannels = shape
    
    positions = itertools.product(range(nrows), range(ncols), range(nchannels))

    queue = deque(maxlen=len(EFMBITS))
    bits= []

    for position in positions:
        pixel = modified[position]
        byte = int_to_byte(pixel)
        if plano_bits == 0:
            bit = byte[-1]
        elif plano_bits == 1:
            bit = byte[-2]
        elif plano_bits == 2:
            bit = byte[-3]
        else:
            raise(Exception('Only 0, 1, and 2 are allowed for "plano_bits"'))

        queue.append(bit)

        if len(queue) == len(EFMBITS):
            if ''.join(queue) == EFMBITS:
                break

            bits.append(queue.popleft())
    message = ''    
    for byte in grouper(8, bits):
        message += chr(int(''.join(byte), 2))
    
    name = imagem.split('/')[-1].split('.')[0]
    name = 'out/{}.txt'.format(name)
    with open(name, 'w') as fh:
        fh.write(message)
