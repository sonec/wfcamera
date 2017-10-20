from flask import Flask,render_template, request, Markup
import os, time

app = Flask(__name__)
#controlpanel = '<a href="#" class="btn btn-lg btn-block btn-danger">Shutdown</a><a href="#" class="btn btn-lg btn-block btn-warning">Reboot</a><a href="#" class="btn btn-lg btn-block btn-primary">Clear Photos</a>'

@app.route("/boothcontrol", methods=['GET','POST'])
def boothcontrol():
    msg = ""
    if request.method == 'POST':
        if request.form['action'] == 'Shutdown':
            os.system('sudo poweroff')
        elif request.form['action'] == 'Reboot':
            os.system('sudo reboot')
        elif request.form['action'] == 'Clear Photo Gallery':
            os.system('mv ~/wfcamera/www/montages/* ~/wfcamera/montages_old/')
            os.system('mv ~/wfcamera/www/thumbnails/* ~/wfcamera/thumbnails_old/')
            msg = Markup('<div class="alert alert-warning alert-dismissible fade show" role="alert"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>Photos cleared</div>')
        elif request.form['action'] == 'Sync Time':
            newdate = request.form['mytime']
            os.system('sudo date -s "'+newdate+'"')
            msg = Markup('<div class="alert alert-warning alert-dismissible fade show" role="alert"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>Time synced</div>')
        elif request.form['action'] == 'Enable AP Mode':
            os.system('sudo bash ~/Desktop/enable_ap.sh')
        elif request.form['action'] == 'Disable AP Mode':
            os.system('sudo bash ~/Desktop/disable_ap.sh')
        else:
            os.system('date')
    data=['Booth Controls','Photo Booth',time.strftime("%b %d %Y %H:%M:%S",time.localtime()),msg]
    return render_template('panel.html',data=data)
    
'''
@app.route("/reboot")
def reboot():
 os.system('sudo reboot')
 data=['Reboot','Photo Booth','Reboot']
 return render_template('template1.html',data=data)

@app.route("/shutdown")
def shutdown():
 os.system('sudo poweroff')
 data=['Shutdown','Photo Booth','Shutting Down']
 return render_template('template1.html',data=data)

@app.route("/clear")
def clear():
 os.system('mv ~/wfcamera/www/montages/* ~/wfcamera/montages_old/')
 os.system('mv ~/wfcamera/www/thumbnails/* ~/wfcamera/thumbnails_old/')
 data=['Clear','Photo Booth','Clear']
 return render_template('template1.html',data=data)
'''


    
if __name__ == "__main__":
 app.run(host='0.0.0.0',debug=True)
