from flask import Flask, request, render_template, flash, redirect, url_for, session, logging
from data import Addresses

app = Flask(__name__)

Addresses = Addresses()

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/addresses')
def addresses():
    return render_template('addresses.html', addresses=Addresses)

@app.route('/address/<string:id>')
def address(id):
    return render_template('address.html', id=id)

if __name__ == '__main__':
    app.run(debug=True)
