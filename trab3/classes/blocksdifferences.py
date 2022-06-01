from classes.abcpixels import ABCPixels

class BlocksDifferences(ABCPixels):
    def __init__(self, max_block_mse, max_block_num_per, block_dim):
        super().__init__()

        self.max_block_mse = max_block_mse
        self.max_block_num_per = max_block_num_per

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
        bcurrs  = self._get_blocks( self.brightness(frame) )
        blasts = self._get_blocks( self.brightness(self.last) )

        diffs = np.zeros( self.block_num )
        for idx, (bcurr, blast) in enumerate(zip(bcurrs, blasts)):
            diffs[idx] = ( ( ( bcurr - blast )**2 ) / 255**2 ).sum()

        import IPython; IPython.embed()


    def _get_blocks(self, frame):
        blocks = []
        inc = self.block_inc
        for h in range(self.block_num_height):
            for w in range(self.block_num_width):
                block = frame[h*inc : (h+1)*inc:, w*inc : (w+1)*inc]
                blocks.append(block)
        return blocks 


    def strategy_name(self):
        return 'Diferença entre blocos'


