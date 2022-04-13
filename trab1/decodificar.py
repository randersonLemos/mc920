import cv2
import copy
import argparse
import itertools
from collections import deque
import matplotlib.pyplot as plt


def word_to_byte(text): # Converte uma string na lista de bytes correspondente
    lst = []
    for letter in text:
        lst.append('{:08b}'.format(ord(letter)))
    return lst


def int_to_byte(num): # Converte um inteiro na sua representação em bytes correspondente
                      # Estamos assumindo que o inteiro pertence ao intervalo [0, 255] 
                      # Para caber apenas em um byte
    return '{:08b}'.format(num)


def grouper(n, iterable, fillvalue=None): # Agrupa valores de n em n
                                          # Utilizado para organizar a sequencia de bits da
                                          # mensagem escondida na imagem
    "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return itertools.zip_longest(fillvalue=fillvalue, *args)



EFM = '!@#FIM#@!' # End of Message


EFMBITS = ''.join(word_to_byte(EFM))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script para recuperação de mensagem escondida em images (Esteganografia)')
    parser.add_argument('-imagem_entrada', required=True, help="Imagem com mensagem escondida")
    parser.add_argument('-planos_bits',    required=True, help="Planos de bits: ou 0 ou 1 ou 2, ou combinações desses valores separados por ':'")

    args = parser.parse_args()
    imagem_entrada = args.imagem_entrada
    imagem = cv2.imread(imagem_entrada)
    planos_bits = sorted(list(map(int, args.planos_bits.split(':')))) # Começar sempre do plano de bits menos significativo

    shape = imagem.shape

    nrows, ncols, nchannels = shape
    nplanos = len(planos_bits)
    
    cartesian = itertools.product(planos_bits, range(nrows), range(ncols), range(nchannels))

    queue = deque(maxlen=len(EFMBITS)) # Deque utilizado como janela móvel da sequencia de bits. 
                                       # Possui o tamanho do código de fim de mensagem
                                       # Assim, quando a sequencia de bits do fim de mensagem for 
                                       # alcançado, ele estará integralmene no deque e sua identifi
                                       # cação será realizada facilmente

    bits= [] # Sequencia de bits da mensagem escondida no deque

    for (plano_bits, row, col, channel) in cartesian: # Varrendo a imagem
        position = (row, col, channel)

        pixel = imagem[position]

        byte = int_to_byte(pixel)

        if plano_bits == 0: # Recuperando os bits da mensagem escondida
            bit = byte[-1]
        elif plano_bits == 1:
            bit = byte[-2]
        elif plano_bits == 2:
            bit = byte[-3]
        else:
            raise(Exception('Apenas 0, 1, and 2 são permitidos para "plano_bits"'))

        queue.append(bit)

        if len(queue) == len(EFMBITS):
            if ''.join(queue) == EFMBITS: # Verifica se chegou no final de mensagem
                break

            bits.append(queue.popleft())

    message = ''    
    for byte in grouper(8, bits): # Agrupando a sequencia de bits em uma lista de bytes
                                  # Varrendo essa lista de bites
        message += chr(int(''.join(byte), 2)) # montando mensagem
    
    name = imagem_entrada.split('/')[-1].split('.')[0]
    name = 'out/{}.txt'.format(name)
    with open(name, 'w') as fh:
        fh.write(message)
