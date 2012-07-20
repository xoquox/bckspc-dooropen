from flask import Flask, render_template, jsonify, request
from relais_client import RelaisClient
from flask.ext.sqlalchemy import SQLAlchemy

import time
import threading
import datetime
import settings
import syslog

enable_logging = True

syslog.openlog('dooropen')

def log(msg, ip):

    if enable_logging:
        
        msg = "[%s] %s" % (ip, msg)
        syslog.syslog( syslog.LOG_INFO, msg )


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://%s:%s@%s/%s' % (settings.mysql_user, settings.mysql_pass, settings.mysql_host, settings.mysql_name)
db = SQLAlchemy(app)


@app.route('/')
def page_main():
    return render_template('door.html')

@app.route('/verify', methods=["POST"])
def ajax_verify():

    if not 'password' in request.form or not 'type' in request.form:
        return "Password field missing", 200

    password = request.form.get('password')
    opentype = request.form.get('type')

    userid = db.session.execute("select id from users where active = 1 AND passwd = SHA2( CONCAT( salt, :pw ), 256 ) LIMIT 1", {'pw': password} ).scalar()
    if userid:

        db.session.execute("insert into log (type, userid, created) values(:type, :userid, NOW())", {'type': opentype, 'userid': userid })
        db.session.commit()


        pp = RelaisClient('webrelais.bckspc.de', 443, username=settings.relais_user, password=settings.relais_pass )

        if opentype == 'Open':
            
            # set door summer
            pp.setPort(2, 1)
            time.sleep(3)
            pp.setPort(2, 0)

            #open the door
            pp.setPort(0, 1)
            time.sleep(0.1)
            pp.setPort(0, 0)

        elif opentype == 'Close':

            #close the door
            pp.setPort(1, 1)
            time.sleep(0.1)
            pp.setPort(1, 0)

       # t = threading.Thread( target=execute )
       # t.start()
    
        return jsonify( response=True )

    else:
        return jsonify( response=False )

if __name__ == '__main__':
    app.debug = True
    app.run( host='0.0.0.0' )

