from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route('/contact.html')
def contact():
    return render_template('contact.html')

@app.route('/services.html')
def gallery():
    return render_template('services.html')

@app.route('/booking.html')
def booking():
    return render_template('booking.html')

if __name__ == '__main__':
    app.run(debug=True)