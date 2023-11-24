from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
import stripe

app = Flask(__name__)
app.secret_key = 'secret key'

client = MongoClient('mongodb://localhost:27017/')
db = client['sonicbliss']
users = db['users']
admins = db['admins']
songs = db['songs']
payments = db['payments']
artists = db['artists']

stripe.api_key = 'your stripe api key'

@app.route('/')
def index():
    if 'user' in session:
        user = users.find_one({'username': session['user']})
        if user['is_member']:
            return render_template('index.html', songs=songs.find(), user=user)
        else:
            return redirect(url_for('subscribe'))
    else:
        return render_template('index.html', songs=songs.find())

@app.route('/register', methods=['POST'])
def register():
    users.insert_one({'username': request.form['username'],
                       'password': request.form['password'],
                       'age': request.form['age'],
                       'gender': request.form['gender'],
                       'music_preferences': request.form['music_preferences'],
                       'is_member': False})
    session['user'] = request.form['username']
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    user = users.find_one({'username': request.form['username']})
    if user and user['password'] == request.form['password']:
        session['user'] = request.form['username']
        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

@app.route('/subscribe')
def subscribe():
    user = users.find_one({'username': session['user']})
    return render_template('subscribe.html', user=user)

@app.route('/subscribe', methods=['POST'])
def subscribe_post():
    user = users.find_one({'username': session['user']})
    try:
        charge = stripe.Charge.create(
            amount=500,
            currency='usd',
            description='Subscription',
            source=request.form['stripeToken']
        )
        users.update_one({'username': session['user']}, {'$set': {'is_member': True}})
        payments.insert_one({'user_id': user['_id'],
                             'payment_id': charge.id,
                             'amount': 500,
                             'card_details': charge.source.last4,
                             'payment_date': charge.created})
        return redirect(url_for('index'))
    except:
        return redirect(url_for('subscribe'))

@app.route('/cancel')
def cancel():
    users.update_one({'username': session['user']}, {'$set': {'is_member': False}})
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)