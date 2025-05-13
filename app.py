from datetime import datetime, timedelta, date
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookings.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
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
def gallery():
    return render_template('services.html')

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        timeslot = request.form['timeslot']
        selected_date = request.form['date']
        selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()

        # Check if slot is available for that day
        existing = Booking.query.filter_by(timeslot=timeslot, date=selected_date_obj).first()
        if not existing:
            booking = Booking(name=name, email=email, timeslot=timeslot, date=selected_date_obj)
            db.session.add(booking)
            db.session.commit()
            return redirect(url_for('booking'))

    # Get selected date from query param or default to today
    selected_date = request.args.get('date', date.today().isoformat())
    selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()

    all_slots = generate_time_slots()
    booked = [b.timeslot for b in Booking.query.filter_by(date=selected_date_obj).all()]
    available_slots = [slot for slot in all_slots if slot not in booked]

    days = get_next_5_days()
    return render_template('booking.html',
                        slots=available_slots,
                        selected_date=selected_date,
                        days=days)

@app.route('/booking_admin')
def booking_admin():
    return render_template('booking_admin.html')

if __name__ == '__main__':
    app.run(debug=True)