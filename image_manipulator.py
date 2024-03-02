from __future__ import print_function
import cv2 as cv
import os
from PIL import Image

png = './downloads/png'
jpg = './downloads/jpg'
jfif = './downloads/jfif'
webp = './downloads/webp'

class ImageConverter():
    def convert_from_png(self,png,jpg):
        files = os.listdir(png)
        for file in files:
            if file.endswith('.png'):
                png_path = os.path.join(png,file)
                img = Image.open(png_path).convert("RGB")
                jpgpath= os.path.join(jpg,file[:-4]+'.jpg')
                img.save(jpgpath,quality=95,optimize=True)

    def convert_from_jfif(self,jfif,jpg):
        files = os.listdir(jfif)
        for file in files:
            if file.endswith('.jfif'):
                jfif_path = os.path.join(jfif,file)
                img = Image.open(jfif_path).convert("RGB")
                jpgpath= os.path.join(jpg,file[:-5]+'.jpg')
                img.save(jpgpath,quality=95,optimize=True)

    def convert_from_webp(self,webp,jpg):
        files = os.listdir(webp)
        for file in files:
            if file.endswith('.webp'):
                webp_path = os.path.join(webp,file)
                img = Image.open(webp_path).convert("RGB")
                jpgpath= os.path.join(jpg,os.path.splitext(file)[0]+'.jpg')
                img.save(jpgpath,quality=95,optimize=True)

converter = ImageConverter()
converter.convert_from_png(png,jpg)
converter.convert_from_jfif(jfif,jpg)
converter.convert_from_jfif(webp,jpg)