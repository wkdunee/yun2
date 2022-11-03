#!/usr/bin/python3
from email import message
from pickle import NONE
from xml.etree.ElementTree import Comment
from flask import Flask, request, render_template, make_response, redirect, url_for, session, g
import sqlite3
import hashlib
import os
import time, random
import os #운영체제에서 제공되는 여러 기능을 파이썬에서 수행할 수 있게 해줌.
from flask import Flask, flash, request, redirect
from flask import url_for, render_template
from werkzeug.utils import secure_filename
#from xss_stored import xss_stored_page, xss_stored_api
from util import get_root_dir
from db_helper import db_helper
from db_models import db_models
from middlewares import require_api_key

app = Flask(__name__)


app.secret_key = os.urandom(32)
DATABASE = "database.db"
MAXRESETCOUNT = 5

app.db_helper = db_helper
app.db_models = db_models

def makeBackupcode():
    return random.randrange(100)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def main():
    return render_template('main.html')

@app.route('/main_success/<userid>')
def index(userid):
    return render_template('main_success.html', userid=userid)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        userid = request.form.get("userid")
        userpasswd = request.form.get("userpasswd")

        conn = get_db()
        cur = conn.cursor()
        user = cur.execute("SELECT * FROM user WHERE userid = '%s' and userpasswd = '%s'"%(userid, userpasswd)).fetchone()        
        if user:
            session['userid'] = user['userid']
            session['userpasswd'] = user['userpasswd']
            return redirect(url_for('index', userid=userid)) #userid=userid

        return "<script>alert('잘못된 아이디 또는 패스워드입니다.');history.back(-1);</script>"

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        userid = request.form.get("userid")
        userpasswd = request.form.get("userpasswd")
        name = request.form.get("name")
        email = request.form.get("email")
        birth = request.form.get("birth")

        conn = get_db()
        cur = conn.cursor()
        user = cur.execute('SELECT * FROM user WHERE userid = ?', (userid,)).fetchone()
        
        if user:
            return "<script>alert('이미 존재하는 아이디입니다.');history.back(-1);</script>";
        user = cur.execute('SELECT * FROM user WHERE email = ?', (email,)).fetchone()
        if user:
            return "<script>alert('이미 존재하는 이메일입니다.');history.back(-1);</script>";

        sql = "INSERT INTO user(userid, userpasswd, name, email, birth) VALUES (?, ?, ?, ?, ?)"
        cur.execute(sql, (userid, userpasswd, name, email, birth))
        conn.commit()
        return render_template("index.html", msg=f"<b>회원가입에 성공하였습니다.</b><br/>")

@app.route('/list', methods=['GET', 'POST'])
def list():
    conn = get_db()
    cur = conn.cursor()
    if request.method == 'GET':
        rows = cur.execute("SELECT * FROM brdwrite")
        
        return render_template('list.html',rows=rows)
    else:
        no = request.form.get("no")
        title = request.form.get("title")
        write = request.form.get("write")
        regdate = request.form.get("regdate")
        count = request.form.get("count")
       

        cur.execute("SELECT * FROM brdwrite WHERE no = ?", (no,)).fetchall()
        conn.commit()
        return render_template("list.html")


@app.route('/write', methods=['GET', 'POST'])
def write():
    conn = get_db()
    cur = conn.cursor()
    if request.method == 'GET':
        userid = request.form.get("userid")
        rows = cur.execute("SELECT * FROM user WHERE userid = ?", (userid,)).fetchall()
        return render_template('write.html',rows=rows)
    else:
        writer = request.form.get("writer")
        title = request.form.get("title")
        context = request.form.get("context")

     #   if brdcontext:
     #       brdcontext = cur.execute("SELECT * FROM brdcontext")

        sql = "INSERT INTO brdwrite(writer, title, context) VALUES (?, ?, ?)"
        cur.execute(sql, (writer, title, context))
        conn.commit()
        
        return render_template('write.html')

@app.route('/read', methods=['GET', 'POST'])
def read():
    if request.method == 'GET':
        return render_template('read.html')
    else:
        no = request.form.get("no")
        title = request.form.get("title")
        write = request.form.get("write")
        regdate = request.form.get("regdate")
        count = request.form.get("count")

        conn = get_db()
        cur = conn.cursor()
        sql = 'SELECT * FROM brdwrite WHERE no,'
        cur.execute(sql,(no, title, write, regdate, count))

        conn.commit()
        return render_template("read.html")

"""
@app.route('/writecomment', methods=['GET', 'POST'])
def writecomment():
    if request.method == 'GET':
        return render_template('write.html')
    else:
        writer = request.form.get("writer")
        comment = request.form.get("comment")

        conn = get_db()
        cur = conn.cursor()

     #   if brdcontext:
     #       brdcontext = cur.execute("SELECT * FROM brdcontext")

        sql = "INSERT INTO brdcomment(writer, title, context) VALUES (?, ?, ?)"
        cur.execute(sql, (writer, comment))
        conn.commit()
        
        return render_template("write.html")
"""
"""
@app.route('/downfile')
def down_page():
	files = os.listdir("./uploads")
	return render_template('filedown.html',files=files)

#파일 다운로드 처리
@app.route('/fileDown', methods = ['GET', 'POST'])
def down_file():
	if request.method == 'POST':
		sw=0
		files = os.listdir("./uploads")
		for x in files:
			if(x==request.form['file']):
				sw=1

		path = "./uploads/" 
		return send_file(path + request.form['file'],
				attachment_filename = request.form['file'],
				as_attachment=True)
"""

#@app.route('/upload', methods=['GET', 'POST'])
#def upload():
#    return render_template("upload.html")

def xss_stored_page(request, app):
    messages = app.db_helper.execute_read('SELECT * FROM messages', {})
    print(messages)
    xss_message = []
    for i in messages:
        xss_message.append(i[0])

    return render_template('xss_stored.html', messages=xss_message)


def xss_stored_api(request, app):
    message = request.form['message']
    result = app.db_helper.execute_write('INSERT INTO messages (message) VALUES (:msg)', { 'msg': message })

    return xss_stored_page(request, app)

@app.route('/xss_stored', methods=['GET', 'POST'])
def xss_stored():
    if request.method == 'GET':
        return xss_stored_page(request, app)

    return xss_stored_api(request, app) 

@app.route('/forgot_userpasswd', methods=['GET', 'POST'])
def forgot_userpasswd():
    if request.method == 'GET':
        return render_template('forgot.html')
    else:
        userid = request.form.get("userid")
        newuserpasswd = request.form.get("newuserpasswd")
        backupCode = request.form.get("backupCode", type=int)

        conn = get_db()
        cur = conn.cursor()
        user = cur.execute('SELECT * FROM user WHERE id = ?', (userid,)).fetchone()
        if user:
            if user['resetCount'] == MAXRESETCOUNT:
                return "<script>alert('reset Count Exceed.');history.back(-1);</script>"
            
            if user['backupCode'] == backupCode:
                newbackupCode = makeBackupcode()
                updateSQL = "UPDATE user set pw = ?, backupCode = ?, resetCount = 0 where idx = ?"
                cur.execute(updateSQL, (hashlib.sha256(newuserpasswd.encode()).hexdigest(), newbackupCode, str(user['idx'])))
                msg = f"<b>userpasswd Change Success.</b><br/>New BackupCode : {newbackupCode}"

            else:
                updateSQL = "UPDATE user set resetCount = resetCount+1 where idx = ?"
                cur.execute(updateSQL, (str(user['idx'])))
                msg = f"Wrong BackupCode !<br/><b>Left Count : </b> {(MAXRESETCOUNT-1)-user['resetCount']}"
            conn.commit()
            return render_template("index.html", msg=msg)
        return "<script>alert('User Not Found.');history.back(-1);</script>";


@app.route('/user/<int:useridx>')
def users(useridx):
    conn = get_db()
    cur = conn.cursor()
    user = cur.execute('SELECT * FROM user WHERE idx = ?;', [str(useridx)]).fetchone()
    
    if user:
        return render_template('user.html', user=user)
    return "<script>alert('User Not Found.');history.back(-1);</script>";
app.run(host='0.0.0.0', port=8080)
