from flask import Flask,render_template, request, Markup
import subprocess, time

app = Flask(__name__)
#controlpanel = '<a href="#" class="btn btn-lg btn-block btn-danger">Shutdown</a><a href="#" class="btn btn-lg btn-block btn-warning">Reboot</a><a href="#" class="btn btn-lg btn-block btn-primary">Clear Photos</a>'

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

@app.route("/boothcontrol", methods=['GET','POST'])
def boothcontrol():
        
    msg = ""
    if request.method == 'POST':
        if request.form['action'] == 'Shutdown':
            subprocess.call(["sudo", "poweroff"])
        elif request.form['action'] == 'Reboot':
            subprocess.call(["sudo", "reboot"])
        elif request.form['action'] == 'Clear Photo Gallery':
            subprocess.call(['mv','~/wfcamera/www/montages/*', '~/wfcamera/montages_old/'],shell=True)
            subprocess.call(['mv','~/wfcamera/www/thumbnails/*', '~/wfcamera/thumbnails_old/'],shell=True)
            msg = Markup('<div class="alert alert-success alert-dismissible fade show" role="alert"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>Photos cleared</div>')
        elif request.form['action'] == 'Sync Time':
            newdate = request.form['mytime']
            subprocess.call(['sudo', 'date', '-s', '"'+newdate+'"'])
            msg = Markup('<div class="alert alert-success alert-dismissible fade show" role="alert"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>Time synced</div>')
        elif request.form['action'] == 'Enable AP Mode':
            subprocess.call(['sudo', 'bash', '~/Desktop/enable_ap.sh'],shell=True)
        elif request.form['action'] == 'Disable AP Mode':
            subprocess.call(['sudo', 'bash', '~/Desktop/disable_ap.sh'],shell=True)
        else:
            subprocess.call(['date'])
    data=['Booth Controls','Photo Booth Admin',time.strftime("%b %d %Y %H:%M:%S",time.localtime()),msg]
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
