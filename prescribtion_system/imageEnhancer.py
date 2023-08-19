from PIL import Image, ImageEnhance
from PIL import Image, ImageFilter

def imageEnhance(img):
    enc_img = img.filter(ImageFilter.DETAIL)
    return enc_img
