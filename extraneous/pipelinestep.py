from dataclasses import dataclass
class PipelineStep:
    type:str

@dataclass 
class blurMedian(PipelineStep):
    max:int
    min:int
    step:int

    def __call__(self, ___):
        pass
    

@dataclass
class blurGauss(PipelineStep):
    width_max:int
    width_min:int
    width_step:int
    height_max:int
    height_min:int
    height_step:int

    def __call__(self, ___):
        pass


@dataclass
class blur(PipelineStep):
    width_max:int
    width_min:int
    width_step:int
    height_max:int
    height_min:int
    height_step:int

    def __call__(self, ___):
        pass


@dataclass
class bilateralBlur(PipelineStep):
    d_min:int
    d_max:int
    d_step:int
    sigmaColor_min:float
    sigmaColor_max:float
    sigmaColor_step:float
    sigmaSpace_min:float
    sigmaSpace_max:float
    sigmaSpace_step:float

    def __call__(self, ___):
        pass

@dataclass
class colorConv(PipelineStep):
    type:str
    def __call__(self, ___):
        pass


@dataclass
class binThresh(PipelineStep):
    min:int
    max:int
    step:int
    def __call__(self, ___):
        return list(range(self.min,self.max,self.step))

        


@dataclass
class adaptiveThres(PipelineStep):
    adaptiveType: str
    type: str
    block_min: int
    block_max:int
    block_step:int
    c_min:int
    c_max:int
    c_step:int

    def __call__(self, ___):
        pass



@dataclass
class otsuComplex(PipelineStep):
    def __call__(self, ___):
        # use Otsu's method to find the thresholds for hue and saturation

        thresh_h = threshold_otsu(image_hsv[:, :, 0])

        thresh_s = threshold_otsu(image_hsv[:, :, 1])
 
        # mask the image to get determine which pixels with hue and saturation above their thresholds

        mask_h = image_hsv[:, :, 1] > thresh_h

        mask_s = image_hsv[:, :, 1] > thresh_s
 
        # combine the masks with an OR so any pixel above either threshold counts as foreground

        np_mask = np.logical_or(mask_h, mask_s)
 
        # apply morphological transforms

        for mt in self.morph_transform:

            np_mask = mt(np_mask)

        return np_mask 


@dataclass
class blobDetector(PipelineStep):
    minArea_min:int
    minArea_max:int
    minArea_step:int

    minCirc_step:float

    def __call__(self, ___):
        pass
