from flask import Flask, request, render_template, flash, redirect, url_for, session, logging
from wtforms import Form, StringField, validators

app = Flask(__name__)
app.secret_key = "super secret key"


Addresses = [
    {
        'name': 'Gizmo',
        'address': '1234 Corgi Ct.',
        'city': 'Denver',
        'state': 'CO',
        'zip_code': '80123',
    },
    {
        'name': 'Rusty',
        'address': '5678 Dog Dr.',
        'city': 'Golden',
        'state': 'CO',
        'zip_code': '80401',
    },
    {
        'name': 'Jeff',
        'address': '91011 Bark Pl.',
        'city': 'Englewood',
        'state': 'CO',
        'zip_code': '80110',
    },
]

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/addresses')
def addresses():
    return render_template('addresses.html', addresses=Addresses)

class NewAddress(Form):
    name = StringField(u'Name', validators=[validators.Length(min=1, max=50)])
    address  = StringField(u'Address', validators=[validators.input_required()])
    city  = StringField(u'City', validators=[validators.input_required()])
    state  = StringField(u'State', validators=[validators.Length(min=2, max=2)])
    zip_code  = StringField(u'Zip Code', validators=[validators.input_required()])

@app.route('/new-address', methods=['GET', 'POST'])
def new_address():
    form = NewAddress(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        address = form.address.data
        city = form.city.data
        state = form.state.data
        zip_code = form.zip_code.data
        Addresses.append({
            "name": name.encode("utf-8"),
            "address": address.encode("utf-8"),
            "city": city.encode("utf-8"),
            "state": state.encode("utf-8"),
            "zip_code": zip_code.encode("utf-8")})
        flash('Your address book has been updated', 'success')

        redirect(url_for('addresses'))
    return render_template('new-address.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
