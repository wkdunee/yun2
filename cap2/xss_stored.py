from email import message
from flask import Flask, request, render_template, make_response, redirect, url_for, session, g
import time, random
import sqlite3
from db_helper import db_helper


DATABASE = "database.db"


def makeBackupcode():
    return random.randrange(100)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def xss_stored_page(request, app):
    messages = app.db_helper.execute_read('SELECT * FROM messages', {})
    messages = list(map(lambda it: it[0], messages))

    return render_template('xss-stored.html', messages=messages)




def xss_stored_api(request, app):
    messages = request.form.get("messages")
    
    conn = get_db()
    cur = conn.cursor()
    
    request = "INSERT INTO messages(messages) VALUES (?)"
    cur.execute(request, (messages))
    conn.commit()

    return xss_stored_page(request, app)