from flask import Flask, render_template, jsonify
from webrelais_client import RelaisClient
from flask.ext.sqlalchemy import SQLAlchemy

import time
import threading
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://user:pass@localhost/database'
db = SQLAlchemy(app)

door_pass = '123'

@app.route('/')
def page_main():
    return render_template('door.html')

@app.route('/verify/<password>', methods=["POST", "GET"])
def ajax_verify( password ):

    result = db.session.execute("select 1 from users where pass = SHA1( CONCAT( :pw, salt ) )", {'pw': password} ).fetchone()
    if result:

        def execute():
            pp = RelaisClient('10.1.20.6', 5000 )
            pp.setPort(3, 1)
            time.sleep(3)
            pp.setPort(3, 0)

        t = threading.Thread( target=execute )
        t.start()
    
        return jsonify( response=True )

    else:
        return jsonify( response=False )

if __name__ == '__main__':
    app.debug = True
    app.run( host='0.0.0.0' )

