#!/usr/bin/python3
## imports ##

import datetime
import os
import subprocess
#from time import sleep
import time
from multiprocessing import Process, Value
from flask import Flask,render_template, request, Markup, jsonify
from itertools import cycle

#set up information for web server first so it can be then handed off into its own process

#set up multiprocessing values so main loop and web interface can share data
#default values

# camera sensor res is 3280 x 2464
#27:23 resolution
#2892 x 2464
#2160 x 1840
#1080 x 960
#564 x 480

#settings
eventname = "The Wedding"
favcol = "#eeaaaa"
enable_effects = False
enable_customeffects = True
enable_printing = True
errorledflag = 0
printername = "Canon_SELPHY_CP1200"
image_resolution_w = 1080
image_resolution_h = 960
image_gap = 5
image_cutgap = 60
screen_w = 800      # resolution of the photo booth display
screen_h = 480
total_pics = 3
led_pin = 17
light_pin = 12
#flash pin is GPIO12!
pin_camera_btn = 21 # pin that the button is attached to
countdowntimer = 4  # how many seconds to count down from

projectpath = os.path.dirname(os.path.realpath(__file__))


watermark_path = '/assets/wedding_watermark.png'
instructions_path = '/assets/press.png'
wait_path = '/assets/done-stripes.png'
montages_path = '/www/montages/'
prints_path = "/www/prints/"
thumbnails_path = '/www/thumbnails/'
playback_path = '/www/thumbnails/'
messages = " Say Cheese! ", " Keep smiling! ", " Don't stop smiling ", " Make a funny face! ", " It's Selfie Time! ", " Smile! ", " Go Crazy! ", " Everyone move closer! ", " Bring it in! ", " Wacky! "


photos_taken = Value('i',0)
montages_taken = Value('i',0)
prints_taken = Value('i',0)
contrast = Value('i',0)
saturation = Value('i',0)
brightness = Value('i',50)
flash = Value('i',1)
printing = Value('i',1)
remotesnap = Value('i',0)
ledbrightness = Value('i',255)



cyshutter = cycle([0,240000,120000,60000,30000,15000,5000])
shutter = Value('i',next(cyshutter))

cyiso = cycle([0,100,200,320,400,500,640,800])
iso = Value('i',next(cyiso))

#flash. using custom torch interpretation

flashtuple = ('off','on','torch','auto','redeye','fillin')
printtuple = ('manual','after every shot')

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

def checkprintererror():
    global printing
    mesg = subprocess.check_output(["lpstat", "-p", printername])
    mesge = mesg.decode("utf-8")
    errsearch = mesge.find("Printer error")

    if errsearch == -1:
        errsearch = mesge.find("libusb")
        if errsearch == -1:
            return False
        else:
            if printing.value == 1:
                subprocess.call("cupsdisable "+printername+" --hold",shell=True)
                subprocess.call("cupsenable "+printername+" --release",shell=True)
            return True
    else:
        return True




def flaskapp():
    app = Flask(__name__)

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
        if button['buttonid'] == 'contrast_pos':
            contrast.value += 1
            if contrast.value > 100: contrast.value = 100
        elif button['buttonid'] == 'contrast_neg':
            contrast.value -= 1
            if contrast.value < -100: contrast.value = -100
        elif button['buttonid'] == 'saturation_pos':
            saturation.value += 1
            if saturation.value > 100: saturation.value = 100
        elif button['buttonid'] == 'saturation_neg':
            saturation.value -= 1
            if saturation.value < -100: saturation.value = -100
        elif button['buttonid'] == 'brightness_pos':
            brightness.value += 1
            if brightness.value > 100: brightness.value = 100
        elif button['buttonid'] == 'brightness_neg':
            brightness.value -= 1
            if brightness.value < 0: brightness.value = 0
        elif button['buttonid'] == 'flash':
            flash.value += 1
            if flash.value > 2: flash.value = 0
        elif button['buttonid'] == 'iso':
          iso.value =  next(cyiso)
        elif button['buttonid'] == 'shutter':
            shutter.value = next(cyshutter)
        elif button['buttonid'] == 'printing':
            printing.value += 1
            if printing.value > 1: printing.value = 0
        elif button['buttonid'] == 'remotesnap':
            remotesnap.value = 1
        elif button['buttonid'] == 'resumeprinter':
            subprocess.call("cupsenable "+printername+" --release",shell=True)
        elif button['buttonid'] == 'disableprinter':
            subprocess.call("cupsdisable "+printername+" --hold",shell=True)
        elif button['buttonid'] == 'dumpprintqueue':
            subprocess.call("cancel -a "+printername,shell=True)
        elif button['buttonid'] == 'led_pos':
            ledbrightness.value += 1
            if ledbrightness.value > 255: ledbrightness.value = 255
        elif button['buttonid'] == 'led_neg':
            ledbrightness.value -= 1
            if ledbrightness.value < 0: ledbrightness.value = 0

        #customeffect('none')
        return ("success")

    @app.route("/sync_webinterface")
    def sync_webinterface():
        mesg = subprocess.check_output(["lpstat", "-p", printername])
        queue = subprocess.check_output(["lpstat", "-o"])
        return jsonify(photos=photos_taken.value,montages=montages_taken.value,prints=prints_taken.value,contrast=contrast.value,saturation=saturation.value,brightness=brightness.value,flash=flashtuple[flash.value],printing=printtuple[printing.value],mesg=mesg.decode("utf-8"),iso=iso.value,shutter=shutter.value,queue=queue.decode("utf-8"),ledbrightness=ledbrightness.value)

    @app.route("/stats",methods=['GET','POST'])
    def stats():
        if request.method == 'POST':
            pass
        return render_template('template1.html',data=["Booth stats",eventname])

    @app.route("/print",methods=['GET','POST'])
    def gallery():
        if request.method == 'POST':
            pass
        page = request.args.get('page',1,type=int)
        images = os.listdir(projectpath+thumbnails_path)
        return render_template('print.html',projectpath=projectpath,thumbnailpath=thumbnails_path,printpath=prints_path,images=images)


    @app.route("/boothcontrol", methods=['GET','POST'])
    def boothcontrol():
        msg = ""
        if request.method == 'POST':
            if request.form['action'] == 'Shutdown':
                subprocess.call(["sudo", "poweroff"])
            elif request.form['action'] == 'Terminate':
                subprocess.call(["sudo", "pkill", "python3"])
            elif request.form['action'] == 'Reboot':
                subprocess.call(["sudo", "reboot"])
            elif request.form['action'] == 'Clear Photo Gallery':
                thistime = str("_"+get_base_filename_for_images())

                subprocess.call("mkdir -p "+projectpath+"/archive/"+eventname+thistime+"/montages/",shell=True)
                subprocess.call("mkdir -p "+projectpath+"/archive/"+eventname+thistime+"/prints/",shell=True)
                subprocess.call("mkdir -p "+projectpath+"/archive/"+eventname+thistime+"/thumbnails/",shell=True)

                subprocess.call("mv -t "+projectpath+"/archive/"+eventname+thistime+"/montages/ "+projectpath+montages_path+"*",shell=True)
                subprocess.call("mv -t "+projectpath+"/archive/"+eventname+thistime+"/prints/ "+projectpath+prints_path+"*",shell=True)
                subprocess.call("mv -t "+projectpath+"/archive/"+eventname+thistime+"/thumbnails/ "+projectpath+thumbnails_path+"*",shell=True)
                
                subprocess.call("zip -j -r "+projectpath+"/www/archived/"+eventname+thistime+".zip "+projectpath+"/archive/"+eventname+thistime+"/montages/",shell=True)


                msg = Markup('<div class="alert alert-success alert-dismissible fade show" role="alert"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>Photos cleared</div>')
            elif request.form['action'] == 'Sync Time':
                newdate = request.form['mytime']
                output = subprocess.call(['sudo date -s "'+newdate+'"'],shell=True)
            else:
                subprocess.call(['date'])
        data=['Booth Admin',"System",time.strftime("%b %d %Y %H:%M:%S",time.localtime()),msg]
        return render_template('panel.html',data=data)

    app.run(host='0.0.0.0',debug=False,use_reloader=False)

p = Process(target=flaskapp)
p.start()

#end web server stuff
#--------------------------------------------------------------------------------------------------------------------------
#start initialising camera

        
import RPi.GPIO as GPIO
from picamera import PiCamera, Color
import random
from PIL import Image
from shutil import copyfile
import serial

try:
    serialMsg = serial.Serial("/dev/ttyACM0", 9600)
except:
    print("continuing without LED Arduino control")

## variables ##

selectedeffects = "none","negative","solarize","cartoon","sketch","emboss","film","watercolor","gpen","oilpaint","pastel","posterise"
cycleeffects = cycle(selectedeffects)

customeffects = "none","b&w","none","sepia"
cyclecustomeffects = cycle(customeffects)

camera = PiCamera()
camera.start_preview()
camera.flash_mode = 'auto'
camera.iso = 0
camera.rotation = 00
camera.hflip = True
camera.annotate_text_size = 60
camera.shutter_speed = 0
camera.resolution = (image_resolution_w,image_resolution_h)
camera.preview.resolution=(screen_w,screen_h)
#camera.framerate = 45

buttonflag = False

def led( col="#ffffff",t=0):
    h = col.lstrip('#')
    mesg = str(int(h[0:2], 16))+","+str(int(h[2:4], 16))+","+str(int(h[4:6],16))+","+str(t)
    encodemsg = mesg.encode()
    try:
        serialMsg.write(encodemsg)
    except:
        print("no serial connection")
    finally:
        print(mesg)
        #return mesg

def hsb( h=0,s=0,b=0,t=0):
    mesg = str(int(h))+","+str(int(s))+","+str(int(b))+","+str(int(t))
    encodemsg = mesg.encode()
    try:
        serialMsg.write(encodemsg)
    except:
            print("no serial connection")
    finally:
        print(mesg)
        #return mesg

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
        time.sleep(duration)
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
        time.sleep(duration)
        camera.remove_overlay(o_id)
        return -1 # '-1' indicates there is no overlay
    else:
        return o_id # we have an overlay, and will need to remove it later

def setupGPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin_camera_btn, GPIO.IN,pull_up_down=GPIO.PUD_UP) 
    GPIO.setup(led_pin, GPIO.OUT)
    #need to disable this ?
    GPIO.setup(light_pin, GPIO.OUT)
    GPIO.add_event_detect(pin_camera_btn, GPIO.FALLING, callback=buttoncallback, bouncetime=300)

def customeffect(effect='none'):
    #sets custom effects based on camera tweaks
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
       print("CUSTOM EFFECT: "+effect)


def buttoncallback(channel):
    global buttonflag
#    global enable_effects
    if buttonflag == True:
        if enable_effects == True:
            if enable_customeffects == True:
                neweffect = next(cycleeffects)
                customeffect(neweffect)
            else:
                camera.image_effect = next(cycleeffects)
                print("EFFECT: "+camera.image_effect)
        else:
            print("no filter")
        pass     
    else:
        buttonflag = True

def flashrate(num=1,pin=led_pin):
    #flashes the led a certain amount of times over a second. higher numbers are faster
    #improve this so negative values won't happen
    for i in range(num):
        GPIO.output(pin, True)
        time.sleep(0.05)
        GPIO.output(pin, False)
        time.sleep((1/num)-0.05)
    
def taking_photo(photo_number, filename_prefix):
    """
    This function captures the photo
    """
    global messages
    #get filename to use
    filename = filename_prefix + '_' + str(photo_number) + 'of'+ str(total_pics)+'.jpg'

    #countdown from n, and display countdown on screen

    if photo_number == total_pics:
        camera.annotate_text = "Last one!"
    else:
        camera.annotate_text = random.choice(messages)

    for counter in range(countdowntimer,0,-1):
        #camera.annotate_text = (messages[photo_number-1]+"\nPhoto "+str(photo_number)+" of "+str(total_pics)+"\n..." + str(counter) + "...")

        if counter > 4:
            countoverlay5 = overlay_image(projectpath+'/assets/p5.png',0,3,'RGBA',False)
            flashrate(1)

            remove_overlay(countoverlay5) 
        if counter == 4:
            countoverlay4 = overlay_image(projectpath+'/assets/p4.png',0,4,'RGBA',False)
            flashrate(2)
 
        elif counter == 3:
            #led("#ffffff",1)
            hsb(0,0,ledbrightness.value,20);
            countoverlay3 = overlay_image(projectpath+'/assets/p3.png',0,5,'RGBA',False)
            remove_overlay(countoverlay4)
            flashrate(3)

        elif counter == 2:
            
            countoverlay2 = overlay_image(projectpath+'/assets/p2.png',0,6,'RGBA',False)
            remove_overlay(countoverlay3)
            flashrate(4)

        elif counter == 1:
            
            countoverlay1 = overlay_image(projectpath+'/assets/p1.png',0,7,'RGBA',False)
            camera.annotate_text = ''
            remove_overlay(countoverlay2)
            for i in range(1):
                GPIO.output(led_pin, True)
                #time.sleep(0.5)
                #turns on light if flash is set to torch
                if flash.value == 2:
                    GPIO.output(light_pin, True)
                hsb(0,0,0,0);
                time.sleep(1)
            countoverlay1.alpha = 0
            remove_overlay(countoverlay1)

    #Take still
    #led("#000000",0)
    GPIO.output(led_pin, False)

    #blank preview while image flipping happens

    #camera.flash_mode = "auto"
    if flashtuple[flash.value] == "torch":
        camera.flash_mode = "off"
    else: camera.flash_mode = flashtuple[flash.value]
    
    camera.iso = iso.value
    camera.shutter_speed = shutter.value
    
    camera.preview.alpha = 0
    camera.hflip = False
    print('ISO: '+str(camera.iso)+'\n Shutter: '+str(camera.exposure_speed)+'\nFlash:'+camera.flash_mode)
    camera.capture(projectpath+'/temp/image%s.jpg' % photo_number)
    if flashtuple[flash.value] == "torch":
        GPIO.output(light_pin, False)
    camera.hflip = True

    #remove_overlay(countoverlay1)
    global photos_taken
    photos_taken.value +=1
    overlay_image(projectpath+'/temp/image%s.jpg' % photo_number,4,4,'RGB',True)
    
    camera.preview.alpha = 255

    #copyfile(projectpath+'/temp/image%s.jpg' % photo_number,projectpath+"/photos/"+filename)

    print("Photo (" + str(photo_number) + ") saved: " + filename)


def main():
#    global photos_taken
    
#    app.run(host='0.0.0.0',debug=True)
    print("Starting main process")
    setupGPIO()
    background = make_solid('black',0,1)

    print("beginning loop")
    #led("000000",0)
    hsb(0,0,0,10)
    #led(favcol,1)
    hsb(random.randint(0,359),random.randint(0,255),ledbrightness.value,10)

    customeffect("none")
    global buttonflag
    global errorledflag
    pinstatus = False
    start = time.time()
    timeout_timer = time.time()
    attracttime = time.time()
    instruction_image = overlay_image(projectpath+instructions_path,0,3,'RGB')
    watermark = Image.open(projectpath+watermark_path)

    while True:
        #print(random.choice(os.listdir(projectpath+'/www/montages/')))
        #Check to see if button is pushed
#        is_pressed = GPIO.wait_for_edge(pin_camera_btn, GPIO.FALLING, timeout=100)

        #Stay inside loop until button is pressed
#        if is_pressed is None:
        if remotesnap.value == True:
            remotesnap.value = 0
            buttonflag = True
            
        if buttonflag == False:
            if (time.time() - timeout_timer) < 0.1:
                #led(favcol,1)
                pass
                
            if (time.time() - timeout_timer) < 10:
                pass

            elif (time.time() - timeout_timer) > 10:
                
                if (time.time() - attracttime) > 3:
                    attracttime = time.time()
                    #change screen at 3 sec interval
                    remove_overlay(instruction_image)
                    #camera.annotate_text = "Press button to start taking photos!"
                    
                    try:
                        #if len(os.listdir(projectpath+playback_path)):
                        instruction_image = overlay_image(projectpath+playback_path+random.choice(os.listdir(projectpath+playback_path)),0,3,'RGB')
                    except:
                        instruction_image = overlay_image(projectpath+instructions_path,0,3,'RGB')
                pass

            if (time.time() - timeout_timer) > 15.8:
                #reset time
                timeout_timer = time.time()
                attracttime = time.time()
                remove_overlay(instruction_image)
                instruction_image = overlay_image(projectpath+instructions_path,0,3,'RGB')
                camera.annotate_text = ""
                #led("#000000",1)
                if checkprintererror() == False:
                    hsb(random.randint(0,359),random.randint(0,255),ledbrightness.value,100)

                pass
            
            
            

            
            customeffect("none")
            #cycle LED on and off every second while idle
            if (time.time() - start) > 1:
                start = time.time()

                
                if pinstatus == True:
                    GPIO.output(led_pin, False)
                    pinstatus = False
                    #led("#000000",1)
                    #led(favcol,1)
                    #hsb(random.randint(0,359),random.randint(0,255),ledbrightness.value,10)
                    if checkprintererror() == True:
                        print("printer error")
                        if errorledflag == 0:
                            hsb(0,255,ledbrightness.value,1)
                            errorledflag = 1
                        else:
                            hsb(0,255,0,1)
                            errorledflag = 0

                else:
                    GPIO.output(led_pin, True)
                    pinstatus = True
                    

        
            continue

        print("Taking photos!")
  #      GPIO.cleanup()
        #led("#000000",1)
        #hsb(0,0,0,10)
        remove_overlay(instruction_image)
        countoverlayready = overlay_image(projectpath+'/assets/p5.png',0,3,'RGBA',False)
  #      setupGPIO()
        #warm up camera?
        time.sleep(2)
        remove_overlay(countoverlayready)
        filename_prefix = get_base_filename_for_images()

        for photo_number in range(1, total_pics + 1):
            #take all sets of photos
            taking_photo(photo_number, filename_prefix)
            
        wait_image =  overlay_image(projectpath+wait_path,0)

#        GPIO.remove_event_detect(pin_camera_btn)
        print("Processing photos")

        print("saving watermarked montage image")
        list_im = ['image1.jpg','image2.jpg','image3.jpg']
        watermarked_image_strip = Image.new('RGB',((image_resolution_w),(total_pics*(image_resolution_h+image_gap)+watermark.height)),'white')
        imgs = [Image.open(projectpath+"/temp/"+i) for i in list_im]
        for j in range(0,total_pics):
            watermarked_image_strip.paste(imgs[j], (0,j*(image_resolution_h+image_gap)))
        watermarked_image_strip.paste(watermark,(0,total_pics*(image_resolution_h+image_gap)))
        watermarked_image_strip.save(projectpath+'/temp/temp_pil.jpg')
        
        print("saving horizontal thumbnail")
        horizontal_layout_thumbnail = Image.new('RGB',((total_pics*(image_resolution_w+image_gap),image_resolution_h)),'white')
        for j in range(0,total_pics):
            horizontal_layout_thumbnail.paste(imgs[j], (j*(image_resolution_w+image_gap),0))
        horizontal_layout_thumbnail.thumbnail((screen_w-20,screen_h-20))
        horizontal_layout_thumbnail.save(projectpath+'/temp/temp_s.jpg')

        print("saving print image")
        printable_image = Image.new('RGB',(watermarked_image_strip.width*2+image_cutgap,watermarked_image_strip.height),'white')
        printable_image.paste(watermarked_image_strip,(0,0))
        printable_image.paste(watermarked_image_strip,(watermarked_image_strip.width+image_cutgap,0))
        printable_image.save(projectpath+'/temp/temp_pil2.jpg')
        

        if printing.value == 1:
            subprocess.call(["sudo lp -d "+ printername +" "+projectpath+"/temp/temp_pil2.jpg"],shell=True)
            print("Printing photo")
            camera.annotate_text = "Printing..."
            prints_taken.value +=1

        print("copying temp files to directories")
        copyfile(projectpath+"/temp/temp_s.jpg",projectpath+thumbnails_path+filename_prefix+"_m.jpg")
        copyfile(projectpath+"/temp/temp_pil.jpg",projectpath+montages_path+filename_prefix+"_m.jpg")        
        copyfile(projectpath+"/temp/temp_pil2.jpg",projectpath+prints_path+filename_prefix+"_m.jpg")
        global montages_taken
        montages_taken.value +=1
        print("Processing complete")
        #global photos_taken
        print("Photos Taken: ",photos_taken.value) 
        print("Montages Taken: ",montages_taken.value)
        remove_overlay(wait_image)
        hsb(random.randint(0,359),random.randint(0,255),ledbrightness.value,10)
        #Playback
        prev_overlay = False
        """
        for photo_number in range(1, total_pics + 1):
            filename = projectpath+"/photos/"+filename_prefix + '_' + str(photo_number) + 'of'+ str(total_pics)+'.jpg'
            this_overlay = overlay_image(filename, False, 3+total_pics)
            # The idea here, is only remove the previous overlay after a new overlay is added.
            if prev_overlay:
                remove_overlay(prev_overlay)
            time.sleep(2)
            prev_overlay = this_overlay
        remove_overlay(prev_overlay)
        """

        #overlay_image(projectpath+'/temp/temp_m.jpg',15)
        overlay_image(projectpath+'/temp/temp_s.jpg',15)
        #overlay_image(projectpath+'/assets/download2.png',10)

        camera.annotate_text =""
        camera.image_effect = 'none'
        cycleeffects = cycle(selectedeffects)
        customeffect("none")
        cyclecustomeffects = cycle(customeffects)
        
        instruction_image = overlay_image(projectpath+instructions_path,0,3,'RGBA')
        remotesnap.value = 0
        buttonflag = False
        print("Ready for next photo")
        timeout_timer = time.time()
        attracttime = time.time()
        #setupGPIO()
             
if __name__ == "__main__":

    try:
        main()
        p.join()
        
    except KeyboardInterrupt:
        print("Exiting")

    except Exception as exception:
        print("unexpected error: ", str(exception))

    finally:
        camera.stop_preview()
        GPIO.cleanup()
