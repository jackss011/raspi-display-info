import RPi.GPIO as GPIO
import OLED_Driver as OLED
from PIL import Image, ImageDraw, ImageFont
import time

t0 = time.time()

x=0
font = ImageFont.truetype('jaldi.ttf', 24)

def frame(draw: ImageDraw, delta):
    # global x
    # side = 16
    # draw.line([(x, 127/2), (x+side, 127/2)], fill = "WHITE", width = side)
    # x = (x + 1) % (127-side)

    draw.text((0, 12), '500Mbps', fill = "WHITE", font = font)


def cleanup():
    OLED.Clear_Screen()
    GPIO.cleanup()


def millis():
    return round((time.time() - t0) * 1000, 4)


def main():
    OLED.Device_Init()
    target_delta = 20

    while(True):
        t = millis()

        # frame begin
        image = Image.new("RGB", (OLED.WIDTH, OLED.HEIGHT), "BLACK")
        draw = ImageDraw.Draw(image)
        

        frame(draw, 100)
        # print(millis() - t)

        OLED.Display_Image(image)
        #frame end

        

        OLED.Delay(target_delta)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nClosed')
    finally: 
        cleanup()

