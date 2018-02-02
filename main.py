import urllib
import urllib2
from urlparse import urlparse
from flask import Flask, request, render_template, flash, redirect, url_for, session, logging
from wtforms import Form, StringField, validators
import xml.etree.ElementTree as xml



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
    print 'xml_doc pasre ', urllib.urlencode({'XML': xml.tostring(xml_doc)})

    call = USPS_SHIPPING_ENDPOINT + API_ZIP_LOOKUP + urllib.urlencode({'XML': xml.tostring(xml_doc)})
    print 'call ', call
    return call

test_response = build_url_usps_zip_lookup(API_USERNAME, '80110')

print 'test_response ', urllib.urlopen(test_response).read()

@app.route('/')
def index():
    print 'test_response: ' + str(test_response)
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
