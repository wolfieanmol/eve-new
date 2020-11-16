from captcha.image import ImageCaptcha
import random


class Captcha(object):
    def __init__(self):
        self.path = '/home/wolfie_anmol/bot11/captcha1.jpg'

    def captcha(self):
        image_captcha = ImageCaptcha(300, 150)
        # no1 = random.randint(2, 10)
        # no2 = random.randint(2, 10)
        # ans = no1 * no2
        img_txt = ' '.join(random.choices('abcdefhjkmnprstuvwxyz', k=4))
        ans = img_txt.replace(' ', '')
        image = image_captcha.generate_image(img_txt)
        image.save(self.path)
        return ans
