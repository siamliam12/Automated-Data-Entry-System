from __future__ import print_function
import cv2 as cv
from matplotlib import pyplot as plt

path = './downloads/png/web_prescription_big.png'
src = cv.imread(path)
if src is None:
    print('Could not find or open the image file: ',path)
    exit(0)

denoising = cv.fastNlMeansDenoisingColored(src,None,0,1,6,10)
src = cv.cvtColor(denoising, cv.COLOR_BGR2GRAY)
contrasted = cv.equalizeHist(src)
_,thres = cv.threshold(contrasted,0,255,cv.THRESH_BINARY|cv.THRESH_OTSU)
