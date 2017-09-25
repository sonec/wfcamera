#!/bin/python
## imports ##
import RPi.GPIO as GPIO
from picamera import PiCamera, Color
from time import sleep
from PIL import Image
from shutil import copyfile
import datetime
import os
import subprocess             
#import itertools
from itertools import cycle

## variables ##
selectedeffects = "none","negative","cartoon","sketch","colorbalance","emboss","film","watercolor","gpen","oilpaint","hatch"
pin_camera_btn = 21 # pin that the button is attached to
led_pin = 17
camera = PiCamera()
camera.rotation = 270
camera.resolution= (640,512)
total_pics = 4
screen_w = 1280      # resolution of the photo booth display
screen_h = 1024
camera.hflip = True
camera.saturation = 70
#camera.annotate_background = Color('black')
camera.annotate_text_size = 60
REAL_PATH = os.path.dirname(os.path.realpath(__file__))
cycleeffects = cycle(selectedeffects)

def get_base_filename_for_images():
    """
    For each photo-capture cycle, a common base filename shall be used,
    based on the current timestamp.

    Example:
    ${ProjectRoot}/photos/2017-12-31_23-59-59

    The example above, will later result in:
    ${ProjectRoot}/photos/2017-12-31_23-59-59_1of4.png, being used as a filename.
    """
    base_filename = str(datetime.datetime.now()).split('.')[0]
    base_filename = base_filename.replace(' ', '_')
    base_filename = base_filename.replace(':', '-')
    return base_filename

def remove_overlay(overlay_id):
    """
    If there is an overlay, remove it
    """
    if overlay_id != -1:
        camera.remove_overlay(overlay_id)


def overlay_image(image_path, duration=0, layer=3,mode='RGB'):
    """
    Add an overlay (and sleep for an optional duration).
    If sleep duration is not supplied, then overlay will need to be removed later.
    This function returns an overlay id, which can be used to remove_overlay(id).
    """

    # Load the arbitrarily sized image
    img = Image.open(image_path)
    # Create an image padded to the required size with
    # mode 'RGB'
    pad = Image.new('RGBA', (
        ((img.size[0] + 31) // 32) * 32,
        ((img.size[1] + 15) // 16) * 16,
        ))
    # Paste the original image into the padded one
    pad.paste(img, (0, 0))

    # Add the overlay with the padded image as the source,
    # but the original image's dimensions
    o_id = camera.add_overlay(pad.tobytes(), size=img.size)
    o_id.layer = layer

    if duration > 0:
        sleep(duration)
        camera.remove_overlay(o_id)
        return -1 # '-1' indicates there is no overlay
    else:
        return o_id # we have an overlay, and will need to remove it later

 
def make_solid(color='white', duration=0, layer=3,):
    """
    Add an overlay (and sleep for an optional duration).
    If sleep duration is not supplied, then overlay will need to be removed later.
    This function returns an overlay id, which can be used to remove_overlay(id).
    """
    # Create an image padded to the required size with
    # mode 'RGB'
    pad = Image.new('RGBA', (
        ((1280 + 31) // 32) * 32,
        ((1024 + 15) // 16) * 16,
        ),(color))
    # Paste the original image into the padded one
    #pad.paste(img, (0, 0))

    # Add the overlay with the padded image as the source,
    # but the original image's dimensions
    o_id = camera.add_overlay(pad.tobytes(), size=(1280,1024))
    o_id.layer = layer

    if duration > 0:
        sleep(duration)
        camera.remove_overlay(o_id)
        return -1 # '-1' indicates there is no overlay
    else:
        return o_id # we have an overlay, and will need to remove it later


def setupGPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin_camera_btn, GPIO.IN, pull_up_down=GPIO.PUD_UP) # assign GPIO pin 21 to our "take photo" button
    GPIO.setup(led_pin, GPIO.OUT)

def my_callback(channel):
    camera.image_effect = next(cycleeffects)
    print("EFFECT: "+camera.image_effect) 
"""
def count_down(i):

    #display a "count down" on screen, starting from 5
    #TODO make LED buttons flash faster
    # 1 sec period- off
    # 0.4 sec period - 0.25 period
    # 0.3 sec period - 
    # 0.2 sec period - 
    # 0.1 sec period - on

    messages = " Say Cheese! ", " Again! ", " Once more! ", " Last one! "
    camera.annotate_text = messages[i]
    sleep(1)

    for counter in range(1,0,-1):
        camera.annotate_text = (messages[i]+"\n..." + str(counter) + "...")
        sleep(1)
    camera.annotate_text = ''
"""

def taking_photo(photo_number, filename_prefix):
    """
    This function captures the photo
    """

    #get filename to use
    filename = filename_prefix + '_' + str(photo_number) + 'of'+ str(total_pics)+'.jpg'

    #countdown from 3, and display countdown on screen

    messages = " Say Cheese! ", " Again... ", " ...and another! ", " Final one! "
    camera.annotate_text = messages[photo_number-1]
    sleep(0)

    for counter in range(4,0,-1):
        camera.annotate_text = (messages[photo_number-1]+"\n..." + str(counter) + "...")



        if counter == 4:
            for i in range(1):
                GPIO.output(led_pin, True)
                sleep(0.5)
                GPIO.output(led_pin, False)
                sleep(0.5)
                
        if counter == 3:
            for i in range(2):
                GPIO.output(led_pin, True)
                sleep(0.25)
                GPIO.output(led_pin, False)
                sleep(0.25)
                
        if counter == 2:
            for i in range(10):
                GPIO.output(led_pin, True)
                sleep(0.05)
                GPIO.output(led_pin, False)
                sleep(0.05)
        if counter == 1:
            for i in range(20):
                GPIO.output(led_pin, True)
                sleep(0.025)
                GPIO.output(led_pin, False)
                sleep(0.025)
                
                
        #flashrate = 
            """
        for i in range(counter):
            GPIO.output(led_pin, True)
            sleep(1/counter)
            GPIO.output(led_pin, False)
            sleep(1/counter)
            """
        #sleep(1)


    #Take still
    camera.annotate_text = ''


#    flash.alpha = 255
    camera.hflip = False
    camera.start_preview(alpha = 0)
    camera.capture(REAL_PATH+'/temp/image%s.jpg' % photo_number)
    camera.start_preview(alpha = 255)
    camera.hflip = True    
    copyfile(REAL_PATH+'/temp/image%s.jpg' % photo_number,REAL_PATH+"/photos/"+filename)
    #camera.capture(filename)

#    flash.alpha = 0
#    sleep(0.18)
                
    #camera.hflip = False
    #camera.capture(filename)
    #camera.capture('/home/pi/Desktop/Captures/image%s.jpg' % photo_number)
    #camera.hflip = True
    
    print("Photo (" + str(photo_number) + ") saved: " + filename)
    


def main():

    print("Starting main process")
    setupGPIO()
    background = make_solid('white',0,1)
    camera.start_preview()
#    background = overlay_image('/home/pi/instructions2.png',0,1)
    instruction_image = overlay_image(REAL_PATH+'/assets/instructions2.png',0,3,'RGBA')
#    flash = make_solid('white',0)
#    flash.alpha = 0
   
    while True:
        #Check to see if button is pushed
        is_pressed = GPIO.wait_for_edge(pin_camera_btn, GPIO.FALLING, timeout=100)

        #Stay inside loop until button is pressed
        if is_pressed is None:
        #TODO flash button LED on and off every second
            GPIO.output(led_pin, True)
         #   delay(1)
         #   GPIO.output(led_pin, False)
         #   delay(1)


            
            continue

        print("Taking photos!")
        GPIO.cleanup()

        remove_overlay(instruction_image)

        setupGPIO()
        sleep(2)
        GPIO.add_event_detect(pin_camera_btn, GPIO.FALLING, callback=my_callback, bouncetime=300)

        filename_prefix = get_base_filename_for_images()

        for photo_number in range(1, total_pics + 1):

            #
            #prep_for_photo_screen(photo_number)
            #
            taking_photo(photo_number, filename_prefix)
        """
                #TODO turn LED strips on
                for i in range(4):
                        print("photo "+ i+"...")
                        count_down(i)

#                        flash.alpha = 255
                        camera.hflip = False
                        camera.capture(REAL_PATH+'/temp/image%s.jpg' % i)
                        camera.hflip = True
#                        flash.alpha = 0
                        sleep(0.18)
        """
                
        #TODO turn LED strips off
        #TODO turn button LED off
#        remove_overlay(flash)
        wait_image =  overlay_image(REAL_PATH+'/assets/wait.png',0)

        GPIO.remove_event_detect(pin_camera_btn)
        print("Processing photos")
        subprocess.call("sudo " + REAL_PATH+"/photoassemble",shell="True")        
        
        copyfile(REAL_PATH+"/temp/temp_montage_framed.jpg",REAL_PATH+"/montages/"+filename_prefix+"_montage.jpg")
        copyfile(REAL_PATH+"/temp/temp_montage_thumbnail.jpg",REAL_PATH+"/thumbnails/"+filename_prefix+"_thumbnail.jpg")
        print("Processing complete")

        remove_overlay(wait_image)

        #Playback
        prev_overlay = False
        
        for photo_number in range(1, total_pics + 1):
            filename = REAL_PATH+"/photos/"+filename_prefix + '_' + str(photo_number) + 'of'+ str(total_pics)+'.jpg'
            this_overlay = overlay_image(filename, False, 3+total_pics)
            # The idea here, is only remove the previous overlay after a new overlay is added.
            if prev_overlay:
                remove_overlay(prev_overlay)
            sleep(2)
            prev_overlay = this_overlay
        remove_overlay(prev_overlay)

        overlay_image(REAL_PATH+'/temp/temp_montage_framed.jpg',10)

        
        camera.image_effect = 'none'
        cycleeffects = cycle(selectedeffects)
        
        #TODO - PRINT commands here
        
        instruction_image = overlay_image(REAL_PATH+'/assets/instructions2.png',0,3,'RGBA')

        print("reached end of main loop")
        #setupGPIO()
        #TODO make button LED flash again



             
if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        print("Exiting")

    except Exception as exception:
        print("unexpected error: ", str(exception))

    finally:
        #camera.remove_overlay(o)
        #camera.stop_preview()
        GPIO.cleanup()
