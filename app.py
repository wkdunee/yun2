#!/usr/bin/python3
from pickle import NONE
from flask import Flask, request, render_template, make_response, redirect, url_for, session, g
import sqlite3
import hashlib
import os
import time, random
import os
from flask import Flask, flash, request, redirect
from flask import url_for, render_template
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.urandom(32)
DATABASE = "database.db"

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

@app.route('/main_success')
def index():
    return render_template('main_success.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        userid = request.form.get("userid")
        userpasswd = request.form.get("userpasswd")

        conn = get_db()
        cur = conn.cursor()
        user = cur.execute('SELECT * FROM user WHERE userid = ? and userpasswd = ?', (userid, userpasswd)).fetchone()
        
        if user:
            session['userid'] = user['userid']
            session['userpasswd'] = user['userpasswd']
            return redirect(url_for('index', userid=userid))

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

app.run(host='0.0.0.0', port=8000)
