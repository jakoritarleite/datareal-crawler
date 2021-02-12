from PIL import Image
from io import BytesIO, StringIO

baseheight = 400

def resize_image(raw_image: bytes):
    rawIO = BytesIO(raw_image)
    rawIO.seek(0)

    imgIO = BytesIO()
    image = Image.open(rawIO).convert('RGB')

    weigth = image.size[0]
    height = image.size[1]

    hpercent = (baseheight / float(height))
    wsize = int((float(weigth) * float(hpercent)))

    image.resize((wsize, baseheight), Image.ANTIALIAS)
    image.save(imgIO, 'JPEG')
    imgIO.seek(0)

    return imgIO