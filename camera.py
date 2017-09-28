#!/bin/python
## imports ##
import RPi.GPIO as GPIO
from picamera import PiCamera, Color
from time import sleep
from time import time
from PIL import Image
from shutil import copyfile
import datetime
import os
import subprocess             
#import itertools
from itertools import cycle

## variables ##
selectedeffects = "none","negative","solarize","cartoon","sketch","colorbalance","emboss","film","watercolor","gpen","oilpaint","hatch","pastel","blur","saturation","washedout","posterise","colorpoint","deinterlace1","deinterlace2"
pin_camera_btn = 21 # pin that the button is attached to
countdowntimer = 6  # how many seconds to count down from
flashhertz = 5  #the maximum amount of times (x2) that the button will flash before taking the photo
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
buttonflag = False

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

    pad = Image.new('RGBA', (
        ((screen_w + 31) // 32) * 32,
        ((screen_h + 15) // 16) * 16,
        ),(color))
    o_id = camera.add_overlay(pad.tobytes(), size=(screen_w,screen_h))
    o_id.layer = layer

    if duration > 0:
        sleep(duration)
        camera.remove_overlay(o_id)
        return -1 # '-1' indicates there is no overlay
    else:
        return o_id # we have an overlay, and will need to remove it later

def setupGPIO():
    GPIO.setmode(GPIO.BCM)

 #   GPIO.setup(pin_camera_btn, GPIO.IN, pull_up_down=GPIO.PUD_UP) # assign GPIO pin 21 to our "take photo" button
    GPIO.setup(pin_camera_btn, GPIO.IN,pull_up_down=GPIO.PUD_UP) 
    GPIO.setup(led_pin, GPIO.OUT)
    GPIO.add_event_detect(pin_camera_btn, GPIO.FALLING, callback=my_callback, bouncetime=500)

def my_callback(channel):
    global buttonflag
    
    if buttonflag == False:
        camera.image_effect = next(cycleeffects)
        print("EFFECT: "+camera.image_effect) 
    else:
 #       buttonflag = True
         sleep(0)
  #  print(buttonflag)
        #TODO = start running main program

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

    for counter in range(countdowntimer,0,-1):
        camera.annotate_text = (messages[photo_number-1]+"\n..." + str(counter) + "...")

        #flashes faster as counter counts down
#        flashrate = int(((flashhertz-1)/(countdowntimer-1))*(-counter+1)+flashhertz)

        #print(flashrate)
        """
        for i in range(flashrate):
            GPIO.output(led_pin, True)
            sleep(0.1/flashrate)
            GPIO.output(led_pin, False)
            sleep(0.90/flashrate)
        """
        if counter > 3:
            for i in range(1):
                GPIO.output(led_pin, True)
                sleep(0.05)
                GPIO.output(led_pin, False)
                sleep(0.95)
        elif counter == 3:
            for i in range(2):
                GPIO.output(led_pin, True)
                sleep(0.05)
                GPIO.output(led_pin, False)
                sleep(0.45)
        elif counter ==2:
            for i in range(4):
                GPIO.output(led_pin, True)
                sleep(0.05)
                GPIO.output(led_pin, False)
                sleep(0.20)
        elif counter == 1:
            for i in range(1):
                GPIO.output(led_pin, True)
                sleep(1)
                GPIO.output(led_pin, False)
                


    #Take still
    camera.annotate_text = ''
 
    camera.start_preview(alpha = 0)
    camera.hflip = False
    camera.capture(REAL_PATH+'/temp/image%s.jpg' % photo_number)
    camera.hflip = True     
    camera.start_preview(alpha = 255)
   
    copyfile(REAL_PATH+'/temp/image%s.jpg' % photo_number,REAL_PATH+"/photos/"+filename)

    print("Photo (" + str(photo_number) + ") saved: " + filename)


def main():

    print("Starting main process")
    setupGPIO()
    background = make_solid('white',0,1)
#    GPIO.add_event_detect(pin_camera_btn, GPIO.FALLING, callback=my_callback, bouncetime=300)

    camera.start_preview()
#    background = overlay_image('/home/pi/instructions2.png',0,1)
    instruction_image = overlay_image(REAL_PATH+'/assets/instructions2.png',0,3,'RGBA')
    print("beginning loop")
    global buttonflag
    pinstatus = False
    start = time()
    while True:

#        func2()
        #Check to see if button is pushed
#        is_pressed = GPIO.wait_for_edge(pin_camera_btn, GPIO.FALLING, timeout=100)

        #Stay inside loop until button is pressed
#        if is_pressed is None:
        if buttonflag == False:
            
            #idleflash()
        #    t = threading.Timer(10,func2)
        #    t.start()
            
            if (time() - start) > 1:
                start = time()
                if pinstatus == True:
                    GPIO.output(led_pin, False)
                    pinstatus = False
                else:
                    GPIO.output(led_pin, True)
                    pinstatus = True
                #print(time() - start)                          
            
        #    for i in range(10):
        #        sleep(0.1)
        #    GPIO.output(led_pin, False)
        #    for i in range(10):
        #        sleep(0.1)          
            continue

        print("Taking photos!")
  #      GPIO.cleanup()
        remove_overlay(instruction_image)

  #      setupGPIO()

        sleep(2)

        filename_prefix = get_base_filename_for_images()

        for photo_number in range(1, total_pics + 1):
            #take all sets of photos
            taking_photo(photo_number, filename_prefix)
            
        wait_image =  overlay_image(REAL_PATH+'/assets/wait.png',0)

#        GPIO.remove_event_detect(pin_camera_btn)
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
        buttonflag = False
        print("reached end of main loop")
        #setupGPIO()



             
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
