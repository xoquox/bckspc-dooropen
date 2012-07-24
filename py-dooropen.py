from flask import Flask, render_template, jsonify, request
from relais_client import RelaisClient
from flask.ext.sqlalchemy import SQLAlchemy

import threading
import datetime
import settings

from helpers import DoorOperation

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://%s:%s@%s/%s' % (settings.mysql_user, settings.mysql_pass, settings.mysql_host, settings.mysql_name)
db = SQLAlchemy(app)

lock = threading.Lock()


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

        if settings.logging:
            db.session.execute("insert into log (type, userid, created) values(:type, :userid, NOW())", {'type': opentype, 'userid': userid })
            db.session.commit()

        if opentype == 'Open':
            op_thread = DoorOperation( lock, True )
        elif opentype == 'Close':
            op_thread = DoorOperation( lock, False )

        op_thread.start()
        
    
        return jsonify( response=True )

    else:
        return jsonify( response=False )

if __name__ == '__main__':
    app.debug = True
    app.run( )

