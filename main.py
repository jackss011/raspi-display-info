import os
import requests
import time
import socket
from math import floor
from dotenv import load_dotenv
import RPi.GPIO as GPIO
import OLED_Driver as OLED
from PIL import Image, ImageDraw, ImageFont
import urllib3
urllib3.disable_warnings()



def retrieve_ip():
    ip = None
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


def retrieve_cpu_temp():
    with open('/sys/class/thermal/thermal_zone0/temp', mode='r') as file:
        return round(int(file.read()) / 1000)


def system_info():
    return dict(ip=retrieve_ip(), cpu_temp=retrieve_cpu_temp())



def unifi_login(usr, key):
    r = s.post(url_unifi + '/api/login', verify=False, json=dict(username=usr, password=key, remeber=True, strict=True))
    return r.status_code == 200


def unifi_valid_get(response):
    if response.status_code != 200:
        print(f"ERROR in get: {response.url}")
        return False

    return True


def unifi_get_stat(stat):
    r = s.get(url_unifi_stat + '/' + stat, verify=False)

    if not unifi_valid_get(r):
        return False
    
    return r.json()['data']


def unifi_info():
    info = dict()

    data = unifi_get_stat('health')
    if data:
        subs = { sub['subsystem'] : sub for sub in data if sub.get('subsystem') in ['wlan', 'lan']}

        wlan = subs.get('wlan')
        info['wlan_status'] = wlan.get('status')
        info['wlan_users'] = wlan.get('num_user')

        lan = subs.get('lan')
        info['lan_status'] = lan.get('status')
        info['lan_users'] = lan.get('num_user')

    data = unifi_get_stat('sysinfo')
    if data and len(data) > 0:
        sys = data[0]
        uptime = sys.get('uptime')
        info['uptime'] = floor(uptime / 3600)
    
    return info



def blank_image():
    image = Image.new("RGB", (OLED.WIDTH, OLED.HEIGHT), "BLACK")
    draw = ImageDraw.Draw(image)
    return (image, draw)


def draw_data(image, draw, data):

    def draw_text(xy, text, fill, font, anchor):
        draw.text(xy, text, fill=fill, font=font, anchor=anchor)
        l = font.getlength(text)
        return (xy[0] + l, xy[0] - l)

    margin_v = 5
    margin_h = 3
    color_detail = '#4D4D4D'

    # IP address
    draw.text((image.width - margin_h, margin_v), data['ip'], fill='WHITE', font=font_ip, anchor="ra")
    
    # Up time
    uptime_h = data['uptime']
    d = str(floor(uptime_h / 24)).zfill(3)
    h = str(uptime_h % 24).zfill(2)

    uptime_y = image.height - margin_v - 28
    l, r = draw_text((image.width - margin_h, uptime_y), 'h', fill=color_detail, font=font_detail, anchor="rs")
    l, r = draw_text((r - 2, uptime_y), h, fill='WHITE', font=font_time, anchor="rs")
    l, r = draw_text((r - 5, uptime_y), 'd', fill=color_detail, font=font_detail, anchor="rs")
    l, r = draw_text((r - 2, uptime_y), d, fill='WHITE', font=font_time, anchor="rs")
  
    # Devices wan
    lan_users = str(data['lan_users'])
    wlan_users = str(data['wlan_users'])

    devices_y = image.height - margin_v

    l, r = draw_text((image.width - margin_h, devices_y), 'lan', fill=color_detail, font=font_detail, anchor="rs")
    l, r = draw_text((r - 4, devices_y), lan_users, fill='WHITE', font=font_ip, anchor="rs")
    # draw.ellipse([(r - 4 - 6, devices_y - 2), (r - 4, devices_y - 2 - 6)], fill='GREEN')
    
    l, r = draw_text((margin_h, devices_y), wlan_users, fill='WHITE', font=font_ip, anchor="ls")
    l, r = draw_text((l + 4, devices_y), 'wifi', fill=color_detail, font=font_detail, anchor="ls")


    # CPU Temp
    temp_y = 62
    l, r = draw_text((image.width - margin_h, temp_y), '°C', fill=color_detail, font=font_temp, anchor="rs")
    l, r = draw_text((r - 4, temp_y), str(data['cpu_temp']), fill='WHITE', font=font_temp, anchor="rs")

    

    
last_data = None

def data_changed(new_data):
    if last_data == None:
        return True

    for (k, v) in new_data.items():
        if last_data.get(k) != v:
            return True

    return False


def loop():
    global last_data

    image, draw = blank_image()

    view_data = { **system_info(), **unifi_info() }
    
    if data_changed(view_data):
        print(view_data)
        draw_data(image, draw, view_data)
        OLED.Display_Image(image)

    last_data = view_data
    time.sleep(REFRESH_RATE)


REFRESH_RATE = 10


if __name__ == '__main__':
    try:
        load_dotenv()
        addr = os.getenv('INFO_ADDR')
        port = os.getenv('INFO_PORT')
        usr = os.getenv('INFO_USR')
        key = os.getenv('INFO_KEY')

        url_unifi = f"https://{addr}:{port}"
        url_unifi_stat = f"{url_unifi}/api/s/default/stat"

        s = requests.Session()

        font_ip = ImageFont.truetype('manrope.ttf', 20)
        font_detail = ImageFont.truetype('manrope.ttf', 16)
        font_time = ImageFont.truetype('manrope.ttf', 22)
        font_temp = ImageFont.truetype('manrope.ttf', 26)

        unifi_login(usr, key)
        OLED.Device_Init()

        while(True):
            loop()

    except KeyboardInterrupt:
        print('\nClosed')

    finally: 
        OLED.Clear_Screen()
        GPIO.cleanup()
