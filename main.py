import urllib
import urllib2
from urlparse import urlparse
from flask import Flask, request, render_template, flash, redirect, url_for, session, logging
from wtforms import Form, StringField, validators
import xml.etree.ElementTree as xml
from config import api_info

app = Flask(__name__)
app.secret_key = "super secret key"

USPS_SHIPPING_ENDPOINT = 'http://production.shippingapis.com/ShippingAPI.dll'
API_ZIP_LOOKUP = '?API=CityStateLookup&'

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

def build_api_zip_lookup_element(user, zip_code):
    zip_lookup_request = xml.Element('CityStateLookupRequest', {'USERID': user})
    zip_node = xml.SubElement(zip_lookup_request, 'ZipCode', {'ID': '0'})
    zip5_node = xml.SubElement(zip_node, 'Zip5')
    zip5_node.text = zip_code

    return zip_lookup_request

def build_url_usps_zip_lookup(user, zip_code):
    xml_doc = build_api_zip_lookup_element(user, zip_code)
    call = USPS_SHIPPING_ENDPOINT + API_ZIP_LOOKUP + urllib.urlencode({'XML': xml.tostring(xml_doc)})

    return call

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

        return redirect(url_for('addresses'))
    return render_template('new-address.html', form=form)

class ZipCodeLookup(Form):
    zip_code  = StringField(u'Zip Code', validators=[validators.Length(min=5, max=5)])

@app.route('/zip-lookup', methods=['GET', 'POST'])
def zip_code_lookup():
    zip_lookup = ZipCodeLookup(request.form)
    if request.method == 'POST' and zip_lookup.validate():
        zip_code = zip_lookup.zip_code.data
        zip_code = build_url_usps_zip_lookup(api_info['API_USERNAME'], zip_code)
        zip_code = urllib.urlopen(zip_code).read()

        zip_text = xml.fromstring(zip_code).find('ZipCode').find('Zip5').text
        city_text = xml.fromstring(zip_code).find('ZipCode').find('City').text
        state_text = xml.fromstring(zip_code).find('ZipCode').find('State').text

        flash('Zip Code %s is %s, %s' % (zip_text, city_text, state_text), 'success')

        return redirect(url_for('new_address'))
    return render_template('ziplookup.html', zip_lookup=zip_lookup)

@app.route('/delete_address/<string:name>', methods=['POST'])
def delete_address(name):
    if request.method == 'POST':
        for address in Addresses:
            if address['name'] == name:
                Addresses.remove(address)

        flash('Address deleted', 'success')

        return redirect(url_for('addresses'))

if __name__ == '__main__':
    app.run(debug=True)
