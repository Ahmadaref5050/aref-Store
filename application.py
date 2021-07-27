from cs50 import SQL
from flask import Flask, redirect, render_template, request, session, flash
from flask_session import Session
from tempfile import mkdtemp

from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash

import datetime

app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response




# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///store.db")


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# login required function
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function



@app.route("/")
@login_required
def home():
    db.execute('delete from stocks where true')
    n1 = "لوح تقطيع"
    n2 = "حامل موبايل"

    d1 = "لوح تقطيع خضراوات و لحوم سمك 8 ملليمتر من أجود أنواع الخشب بلون بني"
    d2 = "مسند حامل للموبايل جميع الفئات بلون بني ومناسب لساعة أبل الذكية"

    db.execute("insert into stocks (name, price, description, image_file) values(?, 60, ?, 'static/1.jpg')", n1, d1)
    db.execute("insert into stocks (name, price, description, image_file) values(?, 120, ?, 'static/2.jpg')", n2, d2)

    stocks = db.execute("SELECT * FROM stocks")
    return render_template("home.html", stocks=stocks)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # admin
        if request.form.get('username') == 'admin' and request.form.get('password') == 'this is so secret':
            return redirect('/admin')
        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template('error.html', error='أدخل اسم المستخدم')

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template('error.html', error='أدخل كلمة المرور')
        # Query database for username
        rows = db.execute("SELECT * FROM usres WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template('error.html', error='كلمة المرور أو اسم المستخدم غير صحيح')

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        # useranme empty or hash IN JAVASCRIPT
        username = request.form.get('username')
        password = request.form.get('password')
        con_pass = request.form.get('confirmPassword')

        # username doesn't exist using db list of all users JAVASCRIPT
        usernames = []
        for i in range(len(db.execute('SELECT username FROM usres;'))):
            usernames.append(db.execute('SELECT username FROM usres;')[i]['username'])

        if not username:
            return render_template('error.html', error='أدخل اسم المستخدم')
        elif not password:
            return render_template('error.html', error='أدخل كلمة المرور')
        elif not con_pass:
            return render_template('error.html', error='أدخل تأكيد كلمة المرور بشكل صحيح')
        elif username in usernames:
            return render_template('error.html', error='اسم المستخدم موجود بالفعل سجل دخول اذا')
        elif password != con_pass:
            return render_template('error.html', error='أدخل تأكيد كلمة المرور بشكل صيحيح')
        else:
            # register the user
            db.execute('INSERT INTO usres (username, hash) VALUES (?, ?)', username, generate_password_hash(password))
            return redirect('/login')

@app.route('/buy', methods=['GET', 'POST'])
@login_required
def buy():
    if request.method == 'POST':
        if not request.form.get("username"):
            return render_template('error.html', error='must contain name')
        elif not request.form.get("stocksNum"):
            return render_template('error.html', error='please choose the number of stocks you want to buy')
        elif not request.form.get('phoneNumber'):
            return render_template('error.html', error='must contain phone number')
        elif not request.form.get('address'):
            return render_template('error.html', error='must contain the address')
        else:
            # get user_id
            user_id = session.get("user_id")

            # get Cleint Name
            clientName = request.form.get("username")

            # get stock name
            stock_id = request.form.get("stock_id")
            stockName = db.execute('SELECT name FROM stocks WHERE id=?', stock_id)[0]['name']

            # get number of stock
            stocks_num = request.form.get("stocksNum")

            # get total price
            total_price = int(stocks_num) * int(db.execute('SELECT price FROM stocks WHERE id=?', stock_id)[0]['price'])

            # get current date
            date = datetime.datetime.now().strftime("%x")

            # get client phone number
            phone = request.form.get('phoneNumber')

            # get client address
            address = request.form.get('address')
            # insert this deal into deasl
            db.execute("INSERT INTO deaslNew (clientName, stockName, stocks_num, total_price, date, user_id, phone, address, delivered) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", clientName, stockName, stocks_num, total_price, date, user_id, phone, address, False)
            return redirect("/deliver")

    if request.method == 'GET':
        stock = db.execute('SELECT * FROM STOCKS WHERE id=?', request.args.get('stock'))
        print(stock)
        return render_template('buy.html', stock=stock)



@app.route('/deliver', methods=['GET', 'POST'])
@login_required
def deliver():
    if request.method == 'GET':
        return render_template('deliver.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'GET':
        deals = db.execute('SELECT * FROM deaslNew WHERE delivered=False')
        return render_template('admin.html', deals=deals)
    else:
        db.execute('UPDATE deaslNew SET delivered=True WHERE id=?', request.form.get('deal_id'))
        # print(request.form.get('deal_id'))
        return redirect('/admin')