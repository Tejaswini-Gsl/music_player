from flask import Flask, render_template, request, redirect, session,send_file,Response,jsonify
import pymongo
from bson import ObjectId
from datetime import datetime, timedelta
from gridfs import GridFS
import io

app = Flask(__name__)
app.secret_key = 'some secret key'

try:
    mongo = pymongo.MongoClient(
        host="localhost",
        port=27017,
        serverSelectionTimeoutMS=1000
    )
    db = mongo.sonic_bilss
    mongo.server_info()
    users = db['user']
    admins = db['admins']
    songs = db['songs']
    payments = db['payment_info']
    ratings = db['song_rating']
    artists = db['artist']
    playlist = db['playlist']
    gridfs = GridFS(db)
except:
    print("ERROR - cannot connect to db")

slide_images = ["playlist1.jpg", "playlist2.jpg", "playlist3.jpg"]

@app.route('/')
def index():
    is_logged_in = 'username' in session
    return render_template('sp1.html', is_logged_in=is_logged_in, slide_images=slide_images)

@app.route('/playlist')
def playlist():
    is_logged_in = 'username' in session
    return render_template('playlist.html', is_logged_in=is_logged_in)

@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if request.method == "POST":
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            age = request.form['age']
            gender = request.form['gender']
            user_id = ObjectId()
            user = {
                '_id' : user_id,
                'user_name': username,
                'user_password': password,
                'user_email': email,
                'user_age': age,
                'user_gender': gender
            }
            
            users.insert_one(user)


            session['user_id'] = str(user_id)
            return render_template('login.html')
        else:
            return render_template('register.html')
    except Exception as e:
        print(e)

@app.route('/logout')
def logout():
    try:
        session.pop('username', None)
        session.pop('user_id',None)
        return render_template('sp1.html', is_logged_in=False, slide_images=slide_images)
    except Exception as ex:
        print(ex)

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == "POST":
            username = request.form['username']
            password = request.form['password']
            user = users.find_one({'user_name': username, 'user_password': password})
            
            if user:
                session['username'] = username
                session['user_id'] = str(user['_id'])
                return render_template('sp1.html', is_logged_in=True, slide_images=slide_images)
            else:
                return render_template('register.html')
        else:
            return render_template('login.html')
    except Exception as e:
        print(e)

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    try:
        if request.method == 'POST':
            # payment_method = request.form['payment_method']
            amount = request.form['amount']
            cardnumber = request.form['cardnumber']
            expiry = request.form['expiry']
            cvv = request.form['cvv']
            payment_id = ObjectId()

            username = session.get('username')
            user_id = session.get('user_id')
            registration_date = datetime.utcnow()
            if username:
                # Update payment information in MongoDB for the logged-in user
                payment_info = {
                    '_id': payment_id,
                    'user_id': ObjectId(user_id),
                    'card_number': cardnumber,
                    'expiry': expiry,
                    'cvv': cvv,
                    'amount': amount,
                    'date': registration_date
                }
                payments.insert_one(payment_info)
                # flash("Payment Successful!", category='success')
                update_user(amount,registration_date)

                referring_page = request.referrer
                is_logged_in = 'user_id' in session

                if referring_page and 'login' in referring_page:
                    return render_template('sp1.html', is_logged_in=is_logged_in, slide_images=slide_images, payment_successful=True, show_as_index=True)
                else:
                    return render_template('sp1.html', is_logged_in=is_logged_in, slide_images=slide_images, payment_successful=True)
                # return render_template('sp1.html', is_logged_in=True, slide_images=slide_images,payment_successful=True)

        return render_template('payment.html', is_logged_in='username' in session)
    except Exception as ex:
        print(ex)

def update_user(amount,registration_date):
    try:
        user_id = session.get('user_id')
        if amount == '45':
            membership = 'year'
            end_date = registration_date +  timedelta(days=365)
        elif amount == '20':
            membership = 'month'
            end_date = registration_date + timedelta(days=30)
        else:
            membership = 'no membership'
        users.update_one(
                    {'_id': ObjectId(user_id)},
                    {
                        '$set': {
                            'membership': membership,
                            'start_date': registration_date,
                            'end_date': end_date
                        }
                    }
                )
                # Fetch the updated user's document
        updated_user = users.find_one({'_id': ObjectId(user_id)})
        print("User updated:", updated_user)
        # return redirect('/')
    except Exception as ex:
        print(ex)



@app.route('/music', methods=['POST'])
def search_music():
    
    search_query = request.form['song']
    print(search_query)
    is_logged_in = 'username' in session
    # # is_logged_in = 'user_id' in session 

    # user = users.find_one({'_id': ObjectId(session.get('user_id'))})
    # current_date = datetime.utcnow()
    # user_membership = user.get('membership')
    # membership_end_date = user.get('end_date')
    # valid_membership = user_membership and user_membership != 'no membership'
 
        
    # if not is_logged_in or not valid_membership:
    #     return render_template('sp1.html', is_logged_in=is_logged_in, slide_images=slide_images, message="You must be logged in with a valid membership to access songs.")
    # elif current_date > membership_end_date:
    #     return render_template('sp1.html', is_logged_in=is_logged_in, slide_images=slide_images, message="Your membership has expired. Please renew to access songs.")

    if search_query:
    # Search for the song details in the 'songs' collection
        song_details = list(songs.find({'song_name': {'$regex': search_query, '$options': 'i'}}))
        print(type(song_details))
        # If the song is found, get its details
        if len(song_details) > 0:
            # Get the song_id for fetching ratings
            song_id = song_details[0]['song_name']
            print(song_id)
            
            # Fetch ratings from the 'song_rating' collection
           

            song_details[0]['avg_rating'] = find_rating(song_id)

        
        # Return both the song details and the average rating
        return render_template('music.html', songs=song_details,is_logged_in=is_logged_in,has_membership= True)
    else:
        # If the song is not found, return an appropriate message
        return render_template('music.html', message="Song not found",is_logged_in=is_logged_in,has_membership= True)

    # return render_template('player.html', music_files=music_files,music_id= music_files[0]['_id'])



@app.route('/music_search/<filename>')
def search_music_direct(filename):
    output = list(songs.find({'song_name':filename}))
    is_logged_in = 'username' in session
    # is_logged_in = 'user_id' in session 

    user = users.find_one({'_id': ObjectId(session.get('user_id'))})
    current_date = datetime.utcnow()
    user_membership = user.get('membership')
    membership_end_date = user.get('end_date')
    valid_membership = user_membership and user_membership != 'no membership'
 
        
    if not is_logged_in or not valid_membership:
        return render_template('sp1.html', is_logged_in=is_logged_in, slide_images=slide_images, message="You must be logged in with a valid membership to access songs.")
    elif current_date > membership_end_date:
        return render_template('sp1.html', is_logged_in=is_logged_in, slide_images=slide_images, message="Your membership has expired. Please renew to access songs.")

    if len(output) > 0:
            # Get the song_id for fetching ratings
            song_id = output[0]['song_name']

            output[0]['avg_rating'] = find_rating(song_id)
    return render_template('music.html', songs=output,is_logged_in=is_logged_in,has_membership= True)


def find_rating(song_id):
    ratings = list(db.song_rating.find({'song_id': song_id}))
    print(ratings)
            # Calculate the average rating
    avg_rating = 0
    num_ratings = len(ratings)
    if num_ratings > 0:
        total_rating = sum([rating['song_rating'] for rating in ratings])
                
        avg_rating = total_rating //num_ratings
    return(avg_rating)


@app.route('/stream_music/<filename>')
def stream_music(filename):
    try:
    
        print("session",session)
        is_logged_in = 'username' in session
        # is_logged_in = 'user_id' in session 
        user_id = 'user_id' in session
        print ("user_id",user_id)
        user = users.find_one({'_id': ObjectId(session.get('user_id'))})
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        if is_logged_in:
            current_date = datetime.utcnow()
            user_membership = user.get('membership')
            membership_end_date = user.get('end_date')
            print(membership_end_date)
            valid_membership = user_membership and user_membership != 'no membership'
            if not valid_membership or current_date > membership_end_date:
                return render_template('/', is_logged_in=is_logged_in, message="You must be logged in with a valid membership to access songs.")
            else:
                file = gridfs.find_one({'filename': filename})
                return Response(
                file.read(),
                mimetype=file.content_type,
                headers={'Content-Disposition': f'attachment; filename={filename}'} 
            )
        else:
            return render_template('login.html')





      

       
        # if not is_logged_in or not valid_membership:
        #     print("yes")
        #     return render_template('sp1.html', is_logged_in=is_logged_in, slide_images=slide_images, message="You must be logged in with a valid membership to access songs.")
        # elif current_date > membership_end_date:
        #     return render_template('sp1.html', is_logged_in=is_logged_in, slide_images=slide_images, message="Your membership has expired. Please renew to access songs.")
        
        # else:
        #     file = gridfs.find_one({'filename': filename})
        #     return Response(
        #         file.read(),
        #         mimetype=file.content_type,
        #         headers={'Content-Disposition': f'attachment; filename={filename}'} 
        #     )
    except Exception as ex:
        print(ex)
#     return send_file(
#         io.BytesIO(file.read()),
#         mimetype='audio/mp3',
#         as_attachment=True,
#         download_name=f'{file.filename}'
#     )

# @app.route('/artist/<artist_id>')
# def artist_profile(artist_id):
#     # Fetch artist details from MongoDB
#     artist = artist.find_one({'artist_name': artist_id})

#     if artist:
#         return render_template('artist_profile.html', artist=artist)
#     else:
#         return 'Artist not found', 404
    
@app.route('/artist/<artist_id>')
def artist_profile(artist_id):
    # Fetch artist details from MongoDB
    print("######################")
    print (artist_id)
    artist_name = db.artist.find_one({'artist_name': artist_id})
   
    is_logged_in = 'username' in session
    if artist_name:
        # Fetch songs associated with the artist
        songs_info = songs.find({'artist_id': artist_id})
        song_values = list(songs_info)
        print(song_values[0])
        return render_template('artist.html',is_logged_in=is_logged_in, artist_info=artist_name,song_values= song_values)
    else:
        return 'Artist not found', 404

@app.route('/rate_song/<song_name>/<int:rating>', methods=['POST'])
def rate_song(song_name, rating):
    # Check if the song has an existing rating
    
    username = session.get('username')
    existing_rating = ratings.find_one({'song_id': song_name,'user_id': username})

    if existing_rating:
        # If a previous rating exists, update it
        ratings.update_one(
            {'song_id': song_name,'user_id': username},
            {'$set': {'song_rating': rating}}
        )
    else:
        # If no previous rating exists, insert a new document
        ratings.insert_one({
            'user_id': username,
            'song_id': song_name,
            'song_rating': rating
        })

    # Optionally, you can send a response to the client
    return 'Rating saved successfully', 200


if __name__ == '__main__':
    app.run(port=5000, debug=True)
