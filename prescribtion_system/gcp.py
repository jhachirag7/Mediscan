import os
from google.cloud import vision
from .google_vision_ai import VisionAI
from .google_vision_ai import prepare_image_local,prepare_image_web,draw_boundary,draw_boundary_normalized

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "mediscan_key.json"

client =vision.ImageAnnotatorClient()

def gcp(image_file_path):
    image = prepare_image_local(image_file_path)
    va= VisionAI(client,image)
    textlst=[]
    texts= va.text_detection()
    for i,j in texts:
        lst=i.split()
        for k in lst:
            textlst.append(k)
    return textlst