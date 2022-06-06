import cv2
import time
import copy
import argparse
import itertools
import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Process


from classes.pixelsdifferences import PixelsDifferences
from classes.blocksdifferences import BlocksDifferences
from classes.histogramdifferences import HistogramDifferences
from classes.edgesdifferences import EdgesDifferences


VIDEO_DURACAO = 5 # SEGUNDOS


def main_pixels_differences(path, stem):
    mpnds = [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70] # max. pixel normalized distance
    mpnns = [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70] # max. pixel normalized number


    product = itertools.product(mpnds, mpnns)
    for mpnd, mpnn in product:
        cap = cv2.VideoCapture(path)
        pd = PixelsDifferences(max_pixel_norm_dist=mpnd, max_pixel_norm_nume=mpnn)

        while True:
            ret, frame = cap.read() # Captura frame por frame

            if ret == True:   
                #hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV) # Converte de BGR para HSV
                #value = hsv[:,:,2]
                #cv2.imshow('frame', value); cv2.waitKey(5) 
                pd.analyze_frame(frame)

            else:
                break


        print('---')
        print(pd.num_analyzed_frames)
        print(len(pd.get_violation()))

        
        frame_heigh = pd.height
        frame_width = pd.width
        if pd.get_violation():
            fps = int( len( pd.get_violation() ) / VIDEO_DURACAO ) + 1
            writer = cv2.VideoWriter('out/{}.{}'.format(pd.suggested_stem(stem), 'mp4')
                                     , cv2.VideoWriter_fourcc('M','J','P','G')
                                     , fps
                                     , (frame_width,frame_heigh)
                                    )
            keys = sorted( list( pd.get_violation().keys() ) )
            for key in keys:
                tup = pd.get_violation()[key]
                frame, num = tup
                writer.write(frame)

        
        fig, ax = plt.subplots( figsize=(8,5) )
        keys = sorted( list( pd.get_all().keys() ) )
        xs = []; ys = []
        for key in keys:
            tup = pd.get_all()[key]
            frame, num = tup
            xs.append(key)
            ys.append(num)

        ax.plot(xs, ys, 'bo')
        ax.axhline(y=mpnn, color='r')
        
        ax.set_ylim([-0.1, 1.1])

        title = ''
        title += 'RESUMO DE VÍDEO PELA ESTRATÉGIA: {}\n'.format(pd.strategy_name().upper())
        title += 'max. norm. dist. entre pixels (T1): {:0.2f}\n'.format( mpnd )
        title += 'max. norm. nume. de violações entre quadros (T2): {:0.2f}\n'.format( mpnn )
        title += 'eficiência de resumo: ({}-{})/{}={:0.2f}'.format(len(pd.get_all()),  len(pd.get_violation()), len(pd.get_all()), (len(pd.get_all()) - len(pd.get_violation()))/len(pd.get_all()) )
        ax.set_title(title)
        ax.set_xlabel('Número do quadro')
        ax.set_ylabel('Distancia T2')

        plt.tight_layout(pad=1.10)

        plt.savefig('out/{}.{}'.format(pd.suggested_stem(stem), 'png'))


def main_blocks_differences(path, stem):
    mbnds = [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70] # max. block normalized squared distance
    mbnns = [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70] # max. block normalized number


    product = itertools.product(mbnds, mbnns)
    for mbnd, mbnn in product:
        cap = cv2.VideoCapture(path)
        bd = BlocksDifferences(max_block_norm_dist=mbnd, max_block_norm_nume=mbnn, block_dim='8x8')
        
        while True:
            ret, frame = cap.read() # Captura frame por frame

            if ret == True:   
                #hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV) # Converte de BGR para HSV
                #value = hsv[:,:,2]
                #cv2.imshow('frame', value); cv2.waitKey(5) 
                bd.analyze_frame(frame)

            else:
                break


        print('---')
        print(bd.num_analyzed_frames)
        print(len(bd.get_violation()))


        frame_heigh = bd.height
        frame_width = bd.width
        if bd.get_violation():
            fps = int( len( bd.get_violation() ) / VIDEO_DURACAO ) + 1
            writer = cv2.VideoWriter('out/{}.{}'.format(bd.suggested_stem(stem), 'mp4'), cv2.VideoWriter_fourcc('M','J','P','G'), fps, (frame_width,frame_heigh))
            keys = sorted( list(bd.get_violation().keys() ) )
            for key in keys:
                tup = bd.get_violation()[key]
                frame, num = tup
                writer.write(frame)

        
        fig, ax = plt.subplots( figsize=(8,5) )
        keys = sorted( list( bd.get_all().keys() ) )
        xs = []; ys = []
        for key in keys:
            tup = bd.get_all()[key]
            frame, num = tup
            xs.append(key)
            ys.append(num)

        ax.plot(xs, ys, 'bo')
        ax.axhline(y=mbnn, color='r')
        
        ax.set_ylim([-0.1, 1.1])

        title = ''
        title += 'RESUMO DE VÍDEO PELA ESTRATÉGIA: {}\n'.format(bd.strategy_name().upper())
        title += 'max. norm. dist. entre blocos (T1): {:0.2f}\n'.format( mbnd )
        title += 'max. norm. nume. de violações entre quadros (T2): {:0.2f}\n'.format( mbnn )
        title += 'eficiência de resumo: ({}-{})/{}={:0.2f}'.format(len(bd.get_all()),  len(bd.get_violation()), len(bd.get_all()), ( len(bd.get_all()) - len(bd.get_violation()) )/len(bd.get_all()) )
        ax.set_title(title)
        ax.set_xlabel('Número do quadro')
        ax.set_ylabel('Distancia T2')

        plt.tight_layout(pad=1.10)

        plt.savefig('out/{}.{}'.format(bd.suggested_stem(stem), 'png'))


def main_histog_differences(path, stem):
    alphas = [3, 4, 5, 6] # max. block normalized squared distance

    for alpha in alphas:
        cap = cv2.VideoCapture(path)
        hd = HistogramDifferences(alpha=alpha)
        
        while True:
            ret, frame = cap.read() # Captura frame por frame

            if ret == True:   
                #hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV) # Converte de BGR para HSV
                #value = hsv[:,:,2]
                #cv2.imshow('frame', value); cv2.waitKey(5) 
                hd.analyze_frame(frame)

            else:
                break

        print('---')
        print(hd.num_analyzed_frames)
        print( len( hd.get_violation() ) )

        frame_heigh = hd.height
        frame_width = hd.width
        if hd.get_violation():
            fps = int( len( hd.get_violation() ) / VIDEO_DURACAO ) + 1
            writer = cv2.VideoWriter('out/{}.{}'.format(hd.suggested_stem(stem), 'mp4')
                                     , cv2.VideoWriter_fourcc('M','J','P','G')
                                     , fps
                                     , (frame_width,frame_heigh)
                                    )

            keys = sorted( list( hd.get_violation().keys() ) )
            for key in keys:
                tup = hd.get_violation()[key]
                frame, num = tup
                writer.write(frame)

        fig, ax = plt.subplots( figsize=(8,5) )
        keys = sorted( list( hd.get_all().keys() ) )
        xs = []; ys = []
        for key in keys:
            tup = hd.get_all()[key]
            frame, num = tup
            xs.append(key)
            ys.append(num)

        ax.plot(xs, ys, 'bo')
        ax.axhline(y=hd.threshold, color='r')
        
        #ax.set_ylim([-0.1, 1.1])

        title = ''
        title += 'RESUMO DE VÍDEO PELA ESTRATÉGIA: {}\n'.format(hd.strategy_name().upper())
        title += 'alpha: {:0.2f}\n'.format( alpha )
        title += 'threshold: {:0.2f}\n'.format( hd.threshold )
        title += 'eficiência de resumo: ({}-{})/{}={:0.2f}'.format( len(hd.get_all()),  len(hd.get_violation()), len(hd.get_all()), ( len(hd.get_all()) - len(hd.get_violation()) )/len(hd.get_all()) )
        ax.set_title(title)
        ax.set_xlabel('Número do quadro')
        ax.set_ylabel('Distancia T2')

        plt.tight_layout(pad=1.10)

        plt.savefig('out/{}.{}'.format(hd.suggested_stem(stem), 'png'))
        

def main_edges_differences(path, stem):
    mends = [0.010, 0.015, 0.020, 0.025, 0.030, 0.035] # max. edge normalized difference

    for mend in mends:
        cap = cv2.VideoCapture(path)
        ed = EdgesDifferences(max_edge_norm_diff=mend)

        while True:
            ret, frame = cap.read() # Captura frame por frame

            if ret == True:   
                #hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV) # Converte de BGR para HSV
                #value = hsv[:,:,2]
                #cv2.imshow('frame', value); cv2.waitKey(5) 
                ed.analyze_frame(frame)

            else:
                break


        print('---')
        print(ed.num_analyzed_frames)
        print( len( ed.get_violation() ) )

        frame_heigh = ed.height
        frame_width = ed.width
        if ed.get_violation():
            fps = int( len( ed.get_violation() ) / VIDEO_DURACAO ) + 1
            writer = cv2.VideoWriter('out/{}.{}'.format(ed.suggested_stem(stem), 'mp4'),cv2.VideoWriter_fourcc('M','J','P','G'), fps, (frame_width,frame_heigh))
            keys = sorted( list( ed.get_violation().keys() ) )
            for key in keys:
                tup = ed.get_violation()[key]
                frame, num = tup
                writer.write(frame)

        
        fig, ax = plt.subplots( figsize=(8,5) )
        keys = sorted( list( ed.get_all().keys() ) )
        xs = []; ys = []
        for key in keys:
            tup = ed.get_all()[key]
            frame, num = tup
            xs.append(key)
            ys.append(num)

        ax.plot(xs, ys, 'bo')
        ax.axhline(y=mend, color='r')
        #
        ax.set_ylim([-0.01, 0.11])

        title = ''
        title += 'RESUMO DE VÍDEO PELA ESTRATÉGIA: {}\n'.format(ed.strategy_name().upper())
        title += 'max. norm. dife. entre bordas: {:0.3f}\n'.format( mend)
        title += 'eficiência de resumo: ({}-{})/{}={:0.2f}'.format(len(ed.get_all()),  len(ed.get_violation()), len(ed.get_all()), ( len(ed.get_all()) - len(ed.get_violation()) )/len(ed.get_all()) )
        ax.set_title(title)
        ax.set_xlabel('Número do quadro')
        ax.set_ylabel('Diferença entre bordas')

        plt.tight_layout(pad=1.10)

        plt.savefig('out/{}.{}'.format(ed.suggested_stem(stem), 'png'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script para busca de mudanças abruptas em videos ')
    parser.add_argument('-video_entrada', required=True, help='Video que se deseja buscas mudancas abruptas')

    args  = parser.parse_args()

    path = args.video_entrada
    name = path.split('/')[-1]
    stem = name[:-4]

    main_pixels_differences(path, stem)
    main_blocks_differences(path, stem)
    main_histog_differences(path, stem)
    main_edges_differences(path, stem)


