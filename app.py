from flask import Flask, render_template, request, redirect, url_for, session
from database import get_database
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'


# routes
@app.route('/')
@app.route('/index')
def index():
    if 'username' in session:
        return redirect(url_for('home'))
    return render_template('index.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/recovery')
def recovery():
    return render_template('recovery.html')


@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'username' in session:
        db = get_database()
        users = db.execute('SELECT * FROM users WHERE username = ?', (session['username'],)).fetchall()
        for user in users:
            userid = user['id']
            expenses = db.execute('SELECT * FROM expense where userid = ?', (userid,)).fetchall()
            return render_template('home.html', expenses=expenses, name=user['name'])
    return redirect(url_for('index'))


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    pw = request.form['password']
    db = get_database()
    user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchall()
    db.close()
    if user:
        for use in user:
            if check_password_hash(use['password'], pw):
                session['username'] = username
                return redirect(url_for('home'))
    else:
        return redirect(url_for('signup'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    name = request.form['name']
    username = request.form['username']
    pw = request.form['password']
    password = generate_password_hash(pw)
    db = get_database()
    db.execute('INSERT INTO users (name, username, password) VALUES (?, ?, ?)', (name, username, password))
    db.commit()
    db.close()
    return redirect(url_for('index'))


@app.route('/add_expense', methods=['POST'])
def add_expense():
    data = request.form['expense']
    price = request.form['price']
    created = date.today().isoformat()
    db = get_database()
    users = db.execute('SELECT * FROM users WHERE username = ?', (session['username'],)).fetchall()
    for user in users:
        userid = user['id']
        db.execute('insert into expense (userid, data, price, created) VALUES (? ,? ,? ,?)',
                   (userid, data, price, created))
        db.commit()
        db.close()
    return redirect(url_for('home'))


@app.route('/delete_expense/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    db = get_database()
    db.execute('delete from expense where _id = ?', (expense_id,))
    db.commit()
    db.close()
    return redirect(url_for('home'))


@app.route('/chart/<string:name>', methods=['GET', 'POST'])
def chart(name):
    if 'username' in session:
        db = get_database()
        lab = []
        data = []
        users = db.execute('SELECT * FROM users WHERE username = ?', (session['username'],)).fetchall()
        for user in users:
            userid = user['id']
            labels = db.execute('SELECT data FROM expense where userid = ?', (userid, )).fetchall()
            values = db.execute('SELECT price FROM expense where userid = ?', (userid, )).fetchall()
            for label in labels:
                lab.append(label['data'])
            for value in values:
                data.append(value['price'])
            return render_template('chart.html', labels=lab, values=data, name=name)
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
