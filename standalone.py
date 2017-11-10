#!/bin/python
## imports ##

import datetime
import os
import subprocess
from time import sleep
import time
from multiprocessing import Process, Value
from flask import Flask,render_template, request, Markup, jsonify
photos_taken = Value('i',0)
montages_taken = Value('i',0)
prints_taken = Value('i',0)
contrast = Value('i',0)
saturation = Value('i',0)
brightness = Value('i',50)
flash = Value('i',0)
printing = Value('i',0)
remotesnap = Value('i',0)

def interpret_flashvalue(value):
    if value == 0:
        label = "off"
    elif value == 1:
        label = "on"
    elif value == 2:
        label = "auto"
    return label

def interpret_printingvalue(value):
    if value == 0:
        label = "manual"
    elif value == 1:
        label = "After every shot"
    return label

def flaskapp():
#    global photos_taken
#    global montages_taken
    #mesg = q.get()
    app = Flask(__name__)
    #q.put(["ofsnw"])

    def shutdown_server():
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()
    
    @app.route('/shutdown', methods=['GET'])
    def shutdown():
        shutdown_server()
        return 'Server shutting down...'
    
    @app.route("/button_pressed",methods=['POST'])
    def button_pressed():
        button = request.get_json('buttonid')
        #print(buttoni['buttonid'])
        if button['buttonid'] == 'contrast_pos':
            contrast.value += 1
            if contrast.value > 100:
                contrast.value = 100
        elif button['buttonid'] == 'contrast_neg':
            contrast.value -= 1
            if contrast.value < -100:
                contrast.value = -100
        elif button['buttonid'] == 'saturation_pos':
            saturation.value += 1
            if saturation.value > 100:
                saturation.value = 100
        elif button['buttonid'] == 'saturation_neg':
            saturation.value -= 1
            if saturation.value < -100:
                saturation.value = -100
        elif button['buttonid'] == 'brightness_pos':
            brightness.value += 1
            if brightness.value > 100:
                brightness.value = 100
        elif button['buttonid'] == 'brightness_neg':
            brightness.value -= 1
            if brightness.value < 0:
                brightness.value = 0
        elif button['buttonid'] == 'flash':
            flash.value += 1
            if flash.value > 2:
                flash.value = 0
        elif button['buttonid'] == 'printing':
            printing.value += 1
            if printing.value > 1:
                printing.value = 0
        elif button['buttonid'] == 'remotesnap':
            remotesnap.value = 1
        elif button['buttonid'] == 'printerstatus':
            subprocess.call(["cupsenable", "Canon_SELPHY_CP1200"])
        #seteffect('none')
        return ("success")

    @app.route("/background_process")
    def background_process():
        return jsonify(photos=photos_taken.value,montages=montages_taken.value,prints=prints_taken.value,contrast=contrast.value,saturation=saturation.value,brightness=brightness.value,flash=interpret_flashvalue(flash.value),printing=interpret_printingvalue(printing.value))

    @app.route("/stats",methods=['GET','POST'])
    def stats():
        if request.method == 'POST':
            pass
            #mesg = request.form
        mesg = subprocess.check_output(["lpstat", "-p", "Canon_SELPHY_CP1200"])
        #mesg = str(photos.value)+" & "+str(montages.value)
        data=['Booth Stats',"Stats",photos_taken.value,montages_taken.value,prints_taken.value,contrast.value,saturation.value,brightness.value,interpret_flashvalue(flash.value),interpret_printingvalue(printing.value),mesg]
        return render_template('template1.html',data=data)

    @app.route("/boothcontrol", methods=['GET','POST'])
    def boothcontrol():
        
        #output = subprocess.check_output(['sudo date -s "Oct 29 2017 13:00:00"'],shell=True)    
        #msg = output
        msg=""
        if request.method == 'POST':
            if request.form['action'] == 'Shutdown':
                subprocess.call(["sudo", "poweroff"])
            elif request.form['action'] == 'Terminate':
                subprocess.call(["sudo", "pkill", "python3"])
            elif request.form['action'] == 'Reboot':
                subprocess.call(["sudo", "reboot"])
            elif request.form['action'] == 'Clear Photo Gallery':
                subprocess.call(['mv -v ~/wfcamera/www/montages/* ~/wfcamera/montages_old/'],shell=True)
                subprocess.call(['mv -v ~/wfcamera/www/thumbnails/* ~/wfcamera/thumbnails_old/'],shell=True)
                msg = Markup('<div class="alert alert-success alert-dismissible fade show" role="alert"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>Photos cleared</div>')
            elif request.form['action'] == 'Sync Time':
                newdate = request.form['mytime']
                output = subprocess.call(['sudo date -s "'+newdate+'"'],shell=True)
                #msg = Markup('<div class="alert alert-success alert-dismissible fade show" role="alert"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>Time synced</div>')
            elif request.form['action'] == 'Enable AP Mode':
                subprocess.call(['sudo', 'bash', '~/Desktop/enable_ap.sh'],shell=True)
            elif request.form['action'] == 'Disable AP Mode':
                subprocess.call(['sudo', 'bash', '~/Desktop/disable_ap.sh'],shell=True)
            else:
                subprocess.call(['date'])
        data=['Booth Admin',"System",time.strftime("%b %d %Y %H:%M:%S",time.localtime()),msg]
        return render_template('panel.html',data=data)

    app.run(host='0.0.0.0',debug=False,use_reloader=False)

p = Process(target=flaskapp)
p.start()

        
import RPi.GPIO as GPIO
from picamera import PiCamera, Color

from PIL import Image
from shutil import copyfile

#import itertools
from itertools import cycle


REAL_PATH = os.path.dirname(os.path.realpath(__file__))

#turn screen flashing on or not
screenflash = True
## variables ##
#selectedeffects = "none","negative","solarize","cartoon","sketch","emboss","film","watercolor","gpen","oilpaint","pastel","posterise"
selectedeffects = "none","b&w","none","sepia"
led_pin = 17
light_pin = 12
#flash pin is GPIO12!
pin_camera_btn = 21 # pin that the button is attached to
countdowntimer = 4  # how many seconds to count down from
camera = PiCamera()
camera.flash_mode = 'off'
camera.rotation = 00
camera.resolution= (1520,960)
camera.hflip = True
camera.annotate_text_size = 120
total_pics = 4
screen_w = 800      # resolution of the photo booth display
screen_h = 480

#flashhertz = 5  #the maximum amount of times (x2) that the button will flash before taking the photo
#camera.annotate_background = Color('black')

#child_conn, parent_conn = Pipe([False])

cycleeffects = cycle(selectedeffects)
buttonflag = False



    


def updatecount():
    #q.put(photos_taken,montages_taken)
    #print(photos_taken,montages_taken)
    #parent_conn.send(str(photos_taken)+" & "+str(montages_taken))
    pass

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


def overlay_image(image_path, duration=0, layer=3,mode='RGB',mirror=False):
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
    o_id = camera.add_overlay(pad.tobytes(), size=img.size,hflip=mirror)
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
    GPIO.setup(light_pin, GPIO.OUT)
    GPIO.add_event_detect(pin_camera_btn, GPIO.FALLING, callback=my_callback, bouncetime=300)

def seteffect(effect='none'):
    camera.brightness = brightness.value
    
    if effect == "sepia":
        camera.color_effects = (98, 148)
        camera.contrast = 20
        camera.saturation = -80
    elif effect == "b&w":
        camera.color_effects = None
        camera.contrast = 20
        camera.saturation = -100

    else:
        camera.saturation = saturation.value
        camera.contrast = contrast.value
        camera.color_effects = None
    if buttonflag == True:
        print("EFFECT: "+effect)


def my_callback(channel):
    global buttonflag

    if buttonflag == True:
#        camera.image_effect = next(cycleeffects)
#        print("EFFECT: "+camera.image_effect)
#         print("no filter")
        neweffect = next(cycleeffects)
        seteffect(neweffect)
         
    else:
        buttonflag = True
  #  print(buttonflag)
        #TODO = start running main program
    
def taking_photo(photo_number, filename_prefix):
    """
    This function captures the photo
    """
    global screenflash
    #get filename to use
    filename = filename_prefix + '_' + str(photo_number) + 'of'+ str(total_pics)+'.jpg'

    #countdown from n, and display countdown on screen

    messages = " Say Cheese! ", " Let's do it again! ", " Keep smiling! ", " Final one! "
    camera.annotate_text = messages[photo_number-1]
    #sleep(0)

    for counter in range(countdowntimer,0,-1):
        camera.annotate_text = (messages[photo_number-1]+"\nPhoto "+str(photo_number)+" of "+str(total_pics)+"\n..." + str(counter) + "...")

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
        if counter > 5:
            for i in range(1):
                GPIO.output(led_pin, True)
                sleep(0.05)
                GPIO.output(led_pin, False)
                sleep(0.95)
        elif counter > 3:
            for i in range(2):
                GPIO.output(led_pin, True)
                sleep(0.05)
                GPIO.output(led_pin, False)
                sleep(0.45)
        elif counter > 1:
            for i in range(4):
                GPIO.output(led_pin, True)
                sleep(0.05)
                GPIO.output(led_pin, False)
                sleep(0.20)
        elif counter == 1:
            for i in range(1):
                GPIO.output(led_pin, True)
                sleep(0.5)
                GPIO.output(light_pin, False)
                sleep(0.5)
                
                


    #Take still
    camera.annotate_text = ''
    GPIO.output(led_pin, False)
    if screenflash ==True:
        camera.start_preview(alpha = 0)
    camera.flash_mode = interpret_flashvalue(flash.value)
    camera.hflip = False
    camera.capture(REAL_PATH+'/temp/image%s.jpg' % photo_number)
    camera.hflip = True
    GPIO.output(light_pin, True)
    if screenflash == True:
        camera.start_preview(alpha = 255)
    global photos_taken
    photos_taken.value +=1
    #updatecount()
    overlay_image(REAL_PATH+'/temp/image%s.jpg' % photo_number,4,4,'RGB',True)
    
    copyfile(REAL_PATH+'/temp/image%s.jpg' % photo_number,REAL_PATH+"/photos/"+filename)

    print("Photo (" + str(photo_number) + ") saved: " + filename)


def main():
#    global photos_taken
    
#    app.run(host='0.0.0.0',debug=True)
    print("Starting main process")
    setupGPIO()
    background = make_solid('black',0,1)
#    GPIO.add_event_detect(pin_camera_btn, GPIO.FALLING, callback=my_callback, bouncetime=300)
    GPIO.output(light_pin, True)
    camera.start_preview()
    camera.preview.window = (0,0,760,480)
#    background = overlay_image('/home/pi/instructions2.png',0,1)
    instruction_image = overlay_image(REAL_PATH+'/assets/instructions3.png',0,3,'RGBA')
    print("beginning loop")
    seteffect("none")
    global buttonflag
    pinstatus = False
    start = time.time()
    while True:

#        func2()
        #Check to see if button is pushed
#        is_pressed = GPIO.wait_for_edge(pin_camera_btn, GPIO.FALLING, timeout=100)

        #Stay inside loop until button is pressed
#        if is_pressed is None:
        if remotesnap.value == True:
            remotesnap.value = 0
            buttonflag = True
        if buttonflag == False:
            
            #idleflash()
        #    t = threading.Timer(10,func2)
        #    t.start()
            
            seteffect("none")
            if (time.time() - start) > 1:
                start = time.time()
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
            
        wait_image =  overlay_image(REAL_PATH+'/assets/wait2.png',0)

#        GPIO.remove_event_detect(pin_camera_btn)
        print("Processing photos")
        subprocess.call("sudo " + REAL_PATH+"/photoassemble",shell=True)        
        
        #subprocess.call(["montage", REAL_PATH+"/temp/image*.jpg", "-tile", "2x2", "-geometry", "+10+10", REAL_PATH+"/temp/temp_montage_four.jpg"],shell=True)
        #subprocess.call(["convert", REAL_PATH+"/temp/temp_montage_four.jpg", "-resize", "256x256", REAL_PATH+"/temp/temp_montage_thumbnail.jpg"],shell=True)
        #subprocess.call(["montage", REAL_PATH+"/temp/temp_montage_four.jpg", REAL_PATH+"/assets/photobooth_label.jpg", "-tile", "2x1", "-geometry +5+5", REAL_PATH+"/temp/temp_montage_framed.jpg"],shell=True)
        #copyfile(REAL_PATH+"/temp/temp_montage_framed.jpg",REAL_PATH+"/www/montages/"+filename_prefix+"_montage.jpg")

        if printing.value == 1:
            subprocess.call(["lp -d CANON_SELPHY_CP1200 "+REAL_PATH+"/temp/temp_mvp.jpg"],shell=True)
            prints_taken.value +=1
        subprocess.call(["sudo " + REAL_PATH+"/webassemble"],shell=True)        
            
        copyfile(REAL_PATH+"/temp/temp_mt.jpg",REAL_PATH+"/www/thumbnails/"+filename_prefix+"_m.jpg")
        copyfile(REAL_PATH+"/temp/temp_mw.jpg",REAL_PATH+"/www/montages/"+filename_prefix+"_m.jpg")        
        copyfile(REAL_PATH+"/temp/temp_mvp.jpg",REAL_PATH+"/www/prints/"+filename_prefix+"_m.jpg")
        global montages_taken
        montages_taken.value +=1
        #updatecount()
        print("Processing complete")
        #global photos_taken
        print("Photos Taken: ",photos_taken.value) 
        print("Montages Taken: ",montages_taken.value)
        remove_overlay(wait_image)

        #Playback
        prev_overlay = False
        """
        for photo_number in range(1, total_pics + 1):
            filename = REAL_PATH+"/photos/"+filename_prefix + '_' + str(photo_number) + 'of'+ str(total_pics)+'.jpg'
            this_overlay = overlay_image(filename, False, 3+total_pics)
            # The idea here, is only remove the previous overlay after a new overlay is added.
            if prev_overlay:
                remove_overlay(prev_overlay)
            sleep(2)
            prev_overlay = this_overlay
        remove_overlay(prev_overlay)
        """

        overlay_image(REAL_PATH+'/temp/temp_mw.jpg',10)
        overlay_image(REAL_PATH+'/assets/download2.png',10)

        
#        camera.image_effect = 'none'
        cycleeffects = cycle(selectedeffects)
        seteffect("none")
        #TODO - PRINT commands here
        
        instruction_image = overlay_image(REAL_PATH+'/assets/instructions3.png',0,3,'RGBA')
        remotesnap.value = 0
        buttonflag = False
        print("Ready for next photo")
        #setupGPIO()



             
if __name__ == "__main__":
    #q = Queue()
    
    try:
        
        #p = Process(target=flaskapp,args=(q))
        #p = Process(target=flaskapp)
        #p.start()
        updatecount()
        #print(q.get())
        main()
        p.join()
        
    except KeyboardInterrupt:
        print("Exiting")

    except Exception as exception:
        print("unexpected error: ", str(exception))

    finally:
        camera.stop_preview()
        GPIO.cleanup()
