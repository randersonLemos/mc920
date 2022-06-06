from classes.abcdifferences import ABCDifferences

class PixelsDifferences(ABCDifferences):
    def __init__(self, max_pixel_norm_dist, max_pixel_norm_nume):
        super().__init__()

        self.max_pixel_norm_dist = max_pixel_norm_dist
        self.max_pixel_norm_nume = max_pixel_norm_nume


    def analyze_frame(self, frame):
        self.num_analyzed_frames += 1
        if self.last is None:
            self.last = frame
            self.height = frame.shape[0]
            self.width  = frame.shape[1]
            return

        self.is_different(frame)

        self.last = frame


    def is_different(self, frame):
        curr = ( self.brightness(frame) ).astype('int')
        last = ( self.brightness(self.last) ).astype('int')

        pixel_norm_dist = abs(curr - last) / 255
        viol = pixel_norm_dist > self.max_pixel_norm_dist

        pixel_nume = viol.sum()
        pixel_norm_nume = pixel_nume / (self.height*self.width)

        if pixel_norm_nume > self.max_pixel_norm_nume:
            self.violation[self.num_analyzed_frames] = ( frame, pixel_norm_nume  )
        self.all[self.num_analyzed_frames] = ( frame, pixel_norm_nume  )


    def suggested_stem(self, video_name):
        stg = ''
        stg += video_name
        stg += '_pixeldiff'
        stg += '_mpnd_{}%'.format(int(100*self.max_pixel_norm_dist))
        stg += '_mpnn_{}%'.format(int(100*self.max_pixel_norm_nume))
        stg += '_nframe_{:05d}'.format(len(self.violation))
        return stg


    def strategy_name(self):
        return 'Diferença entre pixels'


