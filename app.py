from datetime import datetime, timedelta, date
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO
import pyotp, qrcode, base64
import secret


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookings.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.secret_key = secret.app_pass
TOTP_SECRET = secret.totp_pass

app.permanent_session_lifetime = timedelta(minutes=10)  

@app.before_request
def make_session_permanent():
    session.permanent = True

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    nummerplade = db.Column(db.String(7), nullable=False)
    telefon = db.Column(db.String(11), nullable=False)
    timeslot = db.Column(db.String(20), nullable=False)
    date = db.Column(db.Date, nullable=False)

with app.app_context():
    db.create_all()

def generate_time_slots(start='08:00', end='16:00', interval_minutes=60):
    slots = []
    current = datetime.strptime(start, '%H:%M')
    end_time = datetime.strptime(end, '%H:%M')

    while current < end_time:
        slots.append(current.strftime('%H:%M'))
        current += timedelta(minutes=interval_minutes)

    return slots

def get_next_5_days():
    today = date.today()
    return [today + timedelta(days=i) for i in range(5)]

def get_available_slots():
    days = get_next_5_days()
    slots = generate_time_slots()

    slots_by_day = {}
    for day in days:
        available = []
        for time in slots:
            if not Booking.query.filter_by(date=day, timeslot=time).first():
                available.append((day, time)) 
        if available:
            slots_by_day[day.strftime('%A, %d %b')] = available
    return slots_by_day

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        try:
            name = request.form['name']
            email = request.form['email']
            nummerplade = request.form['nummerplade']
            telefon = request.form['telefon']
            selection = request.form['datetime_slot']

            selected_date_str, timeslot = selection.split('|')
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()

            booking = Booking(
                name=name,
                email=email,
                nummerplade=nummerplade,
                telefon=telefon,
                timeslot=timeslot,
                date=selected_date
            )
            db.session.add(booking)
            db.session.commit()

            flash("Din booking blev gennemført!", "success")
            return redirect(url_for('booking'))

        except Exception as e:
            flash("Noget gik galt. Prøv venligst igen.", "error")
            return redirect(url_for('booking'))

    days = get_next_5_days()
    slots = generate_time_slots()

    slots_by_day = {}
    for day in days:
        available = []
        for time in slots:
            if not Booking.query.filter_by(date=day, timeslot=time).first():
                value = f"{day.isoformat()}|{time}"
                available.append((value, time))
        if available:
            slots_by_day[day.strftime('%A, %d %b')] = available

    return render_template('booking.html', slots_by_day=slots_by_day)


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['password'] == secret.admin_pass:
            session['2fa'] = True
            return redirect(url_for('admin_2fa'))
    return render_template('admin_login.html')

@app.route('/admin_2fa', methods=['GET', 'POST'])
def admin_2fa():
    if not session.get('2fa'):
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        if pyotp.TOTP(TOTP_SECRET).verify(request.form['code']):
            session['admin'] = True
            session.pop('2fa')
            return redirect(url_for('booking_admin'))
    return render_template('admin_2fa.html')

@app.route('/admin_2fa_setup')
def admin_2fa_setup():
    totp = pyotp.TOTP(TOTP_SECRET)
    uri = totp.provisioning_uri(name='Booking Admin', issuer_name='LC-AutoEl Teknik')

    img = qrcode.make(uri)
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render_template('admin_2fa_setup.html', qr_code=qr_base64, secret=TOTP_SECRET)

@app.route('/booking_admin')
def booking_admin():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    available_slots = get_available_slots()
    bookings = Booking.query.order_by(Booking.date).all()
    return render_template('booking_admin.html', bookings=bookings, available_slots=available_slots)

if __name__ == '__main__':
    app.run(debug=True)