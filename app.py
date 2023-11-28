from flask import Flask, render_template, request, url_for, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from datetime import date

app = Flask(__name__)

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "password"
app.config["MYSQL_DB"] = "hotel"

mysql = MySQL(app)

app_info = {'Full_Name': '', 'Email': ''}
booking = {'check_in': '', 'check_out': '', 'adults': '', 'children': '', 'days': ''}
prices = {1: '', 2: '', 3: ''}

def check_book(r, i=0):
    room_id = r[i]['Room_ID']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM Bookings WHERE Room_ID = %s AND ((Check_in <= %s AND Check_out < %s) OR (Check_in < %s AND Check_out >= %s))", (room_id, booking['check_in'], booking['check_in'], booking['check_out'], booking['check_out']),)
    b = cursor.fetchone()
    if b:
        if i == len(r) - 1:
            return 'No'
        return check_book(r, i+1)
    else:
        cursor.execute("SELECT * FROM Users WHERE Full_Name = %s AND Email = %s", (app_info['Full_Name'], app_info['Email']),)
        user_row = cursor.fetchone()
        user_id = user_row['User_ID']
        return ('Yes', room_id, user_id)
    

@app.route("/")
def logout():
    app_info['Full_Name'] = ''
    app_info['Email'] = ''
    return render_template("index.html")

@app.route("/booked")
def booked_to_logged_in():
    return render_template('logged_in.html', msg = app_info['Full_Name'])

@app.route('/confirm1')
def get_booking_summary1():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM Rooms WHERE Room_Type = 'Standard' AND is_booked = 0")
    rooms = cursor.fetchall()
    ans = check_book(rooms)
    print(ans[0])
    if ans[0] == 'Yes':
        cursor.execute("INSERT INTO Bookings VALUES (NULL, %s, %s, %s, %s, %s, %s, %s)", (booking['check_in'], booking['check_out'], ans[1], ans[2], booking['adults'], booking['children'], prices[1].split('$')[1]),)
        mysql.connection.commit()
        cursor.execute("SELECT * FROM Rooms WHERE Room_ID = %s", (ans[1],),)
        room_num_s = cursor.fetchone()
        room_num = room_num_s['Room_Number']
        return render_template('booked.html', fname=app_info['Full_Name'], cin=booking['check_in'], cou=booking['check_out'], rtype='Standard', rnum=room_num)
    elif ans == 'No':
        flash("Sorry! Standard Rooms Unavailable.")
        return render_template('rooms.html')
    else:
        return -1
    

@app.route('/confirm2')
def get_booking_summary2():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM Rooms WHERE Room_Type = 'Deluxe' AND is_booked = 0")
    rooms = cursor.fetchall()
    ans = check_book(rooms)
    if ans[0] == 'Yes':
        cursor.execute("INSERT INTO Bookings VALUES (NULL, %s, %s, %s, %s, %s, %s, %s)", (booking['check_in'], booking['check_out'], ans[1], ans[2], booking['adults'], booking['children'], prices[2].split('$')[1]),)
        mysql.connection.commit()
        cursor.execute("SELECT * FROM Rooms WHERE Room_ID = %s", (ans[1],),)
        room_num_s = cursor.fetchone()
        room_num = room_num_s['Room_Number']
        return render_template('booked.html', fname=app_info['Full_Name'], cin=booking['check_in'], cou=booking['check_out'], rtype='Deluxe', rnum=room_num)
    elif ans == 'No':
        flash("Sorry! Deluxe Rooms Unavailable.")
        return render_template('rooms.html')
    else:
        return -1
    

@app.route('/confirm3')
def get_booking_summary3():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM Rooms WHERE Room_Type = 'Suite' AND is_booked = 0")
    rooms = cursor.fetchall()
    ans = check_book(rooms)
    print(ans[0])
    if ans[0] == 'Yes':
        cursor.execute("INSERT INTO Bookings VALUES (NULL, %s, %s, %s, %s, %s, %s, %s)", (booking['check_in'], booking['check_out'], ans[1], ans[2], booking['adults'], booking['children'], prices[3].split('$')[1]),)
        mysql.connection.commit()
        cursor.execute("SELECT * FROM Rooms WHERE Room_ID = %s", (ans[1],),)
        room_num_s = cursor.fetchone()
        room_num = room_num_s['Room_Number']
        return render_template('booked.html', fname=app_info['Full_Name'], cin=booking['check_in'], cou=booking['check_out'], rtype='Suite', rnum=room_num)
    elif ans == 'No':
        flash("Sorry! Suite Rooms Unavailable.")
        return render_template('rooms.html')
    else:
        return -1

@app.route('/login_page')
def get_login_page():
    return render_template('login.html', error_message='')

@app.route('/register_page')
def get_reg_page():
    return render_template('register.html', error_message='')


@app.route("/login", methods=["GET", "POST"])
def login():
    email = request.form['email']
    password = request.form['passw']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
            "SELECT * FROM Users WHERE Email = % s AND Password = % s",
            (
                email,
                password,
            ),
        )
    account = cursor.fetchone()
    if account:
        cursor.execute(
            "SELECT Full_Name FROM Users WHERE Email = % s AND Password = % s",
            (
                email,
                password,
            ),
        )
        msg = cursor.fetchone()
        full_name = msg.get('Full_Name')
        print(full_name, type(full_name))
        print(email, type(email))
        app_info['Full_Name'] = full_name
        app_info['Email'] = email
        return render_template('logged_in.html', msg = full_name)
    else:
        return render_template('login.html', error_message='Invalid Email or Password!')
    
@app.route("/rooms", methods=["GET", "POST"])
def show_rooms():
    if app_info["Full_Name"] == '' and app_info["Email"] == '':
        flash("You need to login first!")
        return render_template('index.html')
    else:
        check_in_date = request.form['chc_in']
        check_out_date = request.form['chc_out']
        adult = request.form['adult']
        children = request.form['children']
        check_in = list(map(int, check_in_date.split('-')))
        check_out = list(map(int, check_out_date.split('-')))
        cid = date(check_in[0], check_in[1], check_in[2])
        cod = date(check_out[0], check_out[1], check_out[2])
        if cid >= cod:
            flash("You cannot check-out before check-in!")
            return render_template('logged_in.html', msg=app_info['Full_Name'])
        days = (cod-cid).days

        booking['check_in'] = check_in_date
        booking['check_out'] = check_out_date
        booking['adults'] = adult
        booking['children'] = children
        booking['days'] = days

        price1 = '$' + str(days * 80)
        price2 = '$' + str(days * 170)
        price3 = '$' + str(days * 265)

        prices[1] = price1
        prices[2] = price2
        prices[3] = price3

        return render_template('rooms.html', msg = app_info['Full_Name'], price1=price1, price2=price2, price3=price3)
        


@app.route("/register", methods=["GET", "POST"])
def register():
    fname = request.form['fname']
    email = request.form['email']
    phone = request.form['phone']
    dob = request.form['dob']
    add = request.form['add']
    pin = request.form['pin']
    city = request.form['city']
    id_t = request.form['id_type']
    id_num = request.form['id_no']
    password = request.form['passw']
    cpassw = request.form['cpassw']

    if len(phone) != 10:
        return render_template('register.html', error_message='Invalid Phone!')
    
    if len(pin) == 6:
        pass
    else:
        return render_template('register.html', error_message='Invalid Pin Code!')
    
    if password == cpassw:
        pass
    else:
        return render_template('register.html', error_message='Passwords do not match!')
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM Users WHERE Email = % s AND Password = % s", (email, password))
    account = cursor.fetchone()

    if account:
        return render_template('register.html', error_message='Account Already Exists!')
    elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return render_template('register.html', error_message='Invalid Email!')
    else:
         cursor.execute(
                "INSERT INTO Users VALUES (NULL, % s, % s, % s, % s, % s, % s, % s, % s, % s, %s)",(fname, email, phone, dob, add, pin, city, id_t, id_num, password),
            )
         mysql.connection.commit()
         flash("Account Created!")
         return render_template('index.html')
    

@app.route('/bookings')
def bookings():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM Users WHERE Full_Name = %s AND Email = %s", (app_info['Full_Name'], app_info['Email']),)
    user_row = cursor.fetchone()
    user_id = user_row['User_ID']
    cursor.execute("SELECT * FROM Bookings WHERE User_ID = %s", (user_id,),)
    data_parser = cursor.fetchall()
    headings = tuple(data_parser[0].keys())
    data = get_table_data(data_parser)
    return render_template('bookings.html', msg = app_info['Full_Name'],headings = headings, data = data)

def get_table_data(data):
    formated_data = [(i['Booking_ID'], '-'.join(map(str, [i['Check_in'].day, i['Check_in'].month, i['Check_in'].year])),'-'.join(map(str, [i['Check_out'].day, i['Check_out'].month, i['Check_out'].year])), i['Room_ID'], i['User_ID'], i['Adults'], i['Children'], f"${i['Bill']}") for i in data]

    return tuple(map(tuple, formated_data))


if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.run(debug=True)