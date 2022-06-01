import cv2
import numpy as np
from classes.abcpixels import ABCPixels

class BlocksDifferences(ABCPixels):
    def __init__(self, max_block_norm_dist, max_block_norm_nume, block_dim):
        super().__init__()
            
        self.max_block_norm_dist = max_block_norm_dist
        self.max_block_norm_nume = max_block_norm_nume

        if block_dim not in ['8x8', '16x16']:
            raise ValueError('Parameter block_dim must be 8x8 or 16x16')

        self.block_dim = block_dim

        if block_dim == '8x8':
            self.block_inc = 8
        else:
            self.block_inc = 16


    def analyze_frame(self, frame):
        self.num_analyzed_frames += 1
        if self.last is None:
            self.last = frame

            self.height = frame.shape[0]
            self.width  = frame.shape[1]

            self.block_num_height = int(self.height / self.block_inc)
            self.block_num_width  = int(self.width  / self.block_inc)
            self.block_num = self.block_num_height*self.block_num_width
            return

        self.is_different(frame)

        self.last = frame
    

    def is_different(self, frame):
        bcurrs  = self._get_blocks( self.brightness(frame).astype('int') )
        blasts = self._get_blocks( self.brightness(self.last).astype('int') )

        diffs = np.zeros( self.block_num )
        for idx, (bcurr, blast) in enumerate(zip(bcurrs, blasts)):
            diffs[idx] = ( ( ( bcurr - blast )**2 ) / 255**2 ).sum()

        viols = np.zeros( self.block_num )
        for idx, diff in enumerate(diffs):
            viols[idx] = diff > self.max_block_norm_dist

        block_nume = viols.sum()
        block_norm_nume = block_nume / self.block_num

        if block_norm_nume > self.max_block_norm_nume:
            self.violation[self.num_analyzed_frames] = ( frame, block_norm_nume) 
        self.all[self.num_analyzed_frames] = ( frame, block_norm_nume )


    def _get_blocks(self, frame):
        blocks = []
        inc = self.block_inc
        for h in range(self.block_num_height):
            for w in range(self.block_num_width):
                block = frame[h*inc : (h+1)*inc:, w*inc : (w+1)*inc]
                blocks.append(block)
        return blocks 


    def suggested_stem(self, video_name):
        stg = ''
        stg += video_name
        stg += '_blockdiff'
        stg += '_mbnd_{}%'.format(int(100*self.max_block_norm_dist))
        stg += '_mbnn_{}%'.format(int(100*self.max_block_norm_nume))
        stg += '_nframe_{:05d}'.format(len(self.violation))
        return stg


    def strategy_name(self):
        return 'Diferença entre blocos'


