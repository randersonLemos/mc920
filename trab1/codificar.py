import cv2
import copy
import itertools
import matplotlib.pyplot as plt

class Codificar:
    pass


def char_to_bytes(char):
    return '{:08b}'.format(ord(char))


def int_to_bytes(num):
    return '{:08b}'.format(num)



if __name__ == '__main__':
    oimg = cv2.imread('./png/watch.png')
    mimg = copy.copy(oimg) 
    shape = oimg.shape

    with open('texto_entrada.txt', 'r') as fh:
        txt = fh.read()

    bytess = []
    for ch in txt:
        bytess.append(char_to_bytes(ch))

    bites = ''.join(bytess)
    
    nrows, ncols, nchannels = shape

    if len(bytess)*8 > nrows*ncols*nchannels:
        raise(Exception('Text is to long...'))
    
    positions = itertools.product(range(nrows), range(ncols), range(nchannels))

    for bit, position in zip(bites, positions):
        pixel = oimg[position]
        byte = int_to_bytes(pixel)
        byte = byte[:-1] + bit
        mimg[position] = int(byte, 2)

    cv2.imshow('oimg', oimg)
    cv2.imshow('mimg', mimg)
    cv2.waitKey(0)


    for position in positions:
        pixel = mimg[position]


    import IPython; IPython.embed()
    
