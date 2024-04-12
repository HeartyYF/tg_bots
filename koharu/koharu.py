from PIL import Image, ImageDraw, ImageFont
import io

font_size = 128
half_size = int(font_size/2)

def GenerateImage(text: str):
    bg = Image.open('koharu_swimsuit.png')
    txt_im = Image.new('RGBA', (font_size, font_size), (255, 255, 255, 0))


    font = ImageFont.truetype('simhei.ttf', font_size)

    draw = ImageDraw.Draw(txt_im)

    draw.text((0, 0), text, font=font, fill='black')
    txt_im = txt_im.rotate(25, expand=True, resample=Image.Resampling.BICUBIC)

    txt_im_size = txt_im.size[0]
    half_txt_size = int(txt_im_size/2)

    box_field = (125-half_txt_size, 125-half_txt_size, 125+half_txt_size, 125+half_txt_size)

    bg.paste(txt_im, box_field, txt_im)

    img_byte_arr = io.BytesIO()
    bg.save(img_byte_arr, format='WEBP')
    img_byte_arr = img_byte_arr.getvalue()
    
    return img_byte_arr