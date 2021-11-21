from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
import hashlib
import random

app = Flask(__name__)
app.secret_key = "#12345#"


@app.route("/")
def index():
    session['attempts'] = 0
    session['random'] = random.randint(3, 10)
    return render_template('index.html')

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        conn = sqlite3.connect("admin_login.db")
        username = request.form.get("uname")
        password = request.form.get("pwd")
        password = hashlib.md5(password.encode()).hexdigest()
        cursor = conn.execute("SELECT username FROM login WHERE username=? AND password=?", (username, password))
        for row in cursor:
            if row[0] == username:
                conn.close()
                return render_template('success_admin.html')
        conn.close()
        session['attempts'] += 1
        if session['attempts'] == session['random']:
            session['attempts'] = 0
            session['random'] = random.randint(3, 10)
            return render_template('security.html')
        flash('Check Your Username and Password')
        return redirect('admin')
    return render_template('admin.html')

@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        conn = sqlite3.connect("user_login.db")
        username = request.form.get("uname")
        password = request.form.get("pwd")
        password = hashlib.md5(password.encode()).hexdigest()
        cursor = conn.execute("SELECT username FROM login WHERE username=? AND password=?", (username, password))
        for row in cursor:
            if row[0] == username:
                conn.close()
                return render_template('success_user.html')
        conn.close()
        session['attempts'] += 1
        if session['attempts'] == session['random']:
            session['attempts'] = 0
            session['random'] = random.randint(3, 10)
            return render_template('security.html')
        flash('Check Your Username and Password', 'error')
        return redirect('signin')   
    return render_template('signin.html')

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        conn = sqlite3.connect("user_login.db")
        first_name = request.form.get("first_name").title()
        last_name = request.form.get("last_name").title()
        uname = request.form.get("uname")
        date_ = request.form.get("date_")
        pwd = request.form.get("pwd")
        pwd = hashlib.md5(pwd.encode()).hexdigest()
        cpwd = request.form.get("cpwd")
        cpwd = hashlib.md5(cpwd.encode()).hexdigest()
        security_question = request.form.get("security_question")
        security_answer = request.form.get("security_answer").lower()
        security_answer = hashlib.md5(security_answer.encode()).hexdigest()
        if cpwd != pwd:
            conn.close()
            flash('Passwords does not match')
            return redirect('signup')
        data = (first_name, last_name, uname, date_, pwd, security_question, security_answer)
        conn.execute("INSERT INTO login (firstname,lastname,username,dob,password,securityquestion,securityanswer) VALUES (?,?,?,?,?,?,?)", data)
        conn.commit()
        conn.close()
        flash("Successfully Registered", 'registration')
        return redirect('signin')
    return render_template('signup.html')

@app.route("/password", methods=["GET", "POST"])
def password():
    if request.method == "POST":
        conn = sqlite3.connect("user_login.db")
        uname = request.form.get("uname")
        security_question = request.form.get("security_question")
        security_answer = request.form.get("security_answer").lower()
        security_answer = hashlib.md5(security_answer.encode()).hexdigest()
        pwd = request.form.get("pwd")
        pwd = hashlib.md5(pwd.encode()).hexdigest()
        cpwd = request.form.get("cpwd")
        cpwd = hashlib.md5(cpwd.encode()).hexdigest()
        if cpwd != pwd:
            conn.close()
            flash('Passwords does not match')
            return redirect('password')
        data = (pwd, uname, security_question, security_answer)
        cursor = conn.execute("UPDATE login SET password=? WHERE username=? AND securityquestion=? AND securityanswer=?", data)
        if not cursor:
            conn.close()
            flash('Incorrect Username or Security Question or Security Answer')
            return redirect('password')
        conn.commit()
        conn.close()
        flash("Password Updated successfully", 'registration')
        return redirect('signin')
    return render_template('password.html')


if __name__ == '__main__':
    app.run(debug=True)