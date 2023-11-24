from flask import Flask, render_template, request, redirect, url_for, session
import pymongo

# app = Flask(__name__)
# app.secret_key = 'some secret key'

# client = pymongo.MongoClient('mongodb://localhost:27017/')
# db = client['sonicbliss']
# users = db['users']
# admins = db['admins']
# songs = db['songs']
# payments = db['payments']
# ratings = db['ratings']
# artists = db['artists']
# playlist = db['playlist']

app=Flask(__name__)
is_logged_in = False

try:
   mongo = pymongo.MongoClient(
      host="localhost",
      port= 27017,
      serverSelectionTimeoutMS = 1000
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
except:
   print("ERROR - cannot connect to db")

slide_images = ["playlist1.jpg", "playlist2.jpg", "playlist3.jpg"]
logged_in_users = set()

@app.route('/')
def index():
    return render_template('sp1.html',is_logged_in = is_logged_in,slide_images=slide_images )

@app.route('/register', methods=['GET','POST'])
def register():
    try:
        if request.method == "POST":
        
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            age = request.form['age']
            gender = request.form['gender']
            # music_preferences = request.form['music_preferences']
            # user = {'username': username, 'password': password, 'email': email, 'age': age, 'gender': gender, 'music_preferences': music_preferences}
            user = {'user_name': username, 'user_password': password, 'user_email': email, 'user_age': age, 'user_gender': gender}
            users.insert_one(user)
            return render_template('login.html')
            # return redirect(url_for('static', filename='login.html'))
        else:
            return render_template('register.html')
    except Exception as e:
        print (e)


@app.route('/logout')
def logout():
    try :
        global is_logged_in
        is_logged_in = False
        logged_in_users.clear()
        return render_template('sp1.html',is_logged_in = is_logged_in,slide_images=slide_images )
    except Exception as ex:
        print(ex)

@app.route('/login', methods=['GET','POST'])
def login():
    try:
        if request.method == "POST":
            global is_logged_in
            username = request.form['username']
            password = request.form['password']
            user = users.find_one({'user_name': username, 'user_password': password})
            
            if user:
                print("hello")
                is_logged_in = not is_logged_in
                print(is_logged_in)
                logged_in_users.add(username)
                print(logged_in_users)
                # session['username'] = username
                # print(session['username'])
                return render_template('sp1.html', is_logged_in=is_logged_in,slide_images=slide_images)
            else:
                return render_template('register.html')
        else:
            return render_template('login.html')
            
    # except Exception as e:
    #     return 'Invalid username or password'
        
    except Exception as e:
        print (e)



# @app.route('/home')
# def home():
#     if 'username' in session:
#         user = users.find_one({'username': session['username']})
#         return render_template('home.html', user=user)
#     return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(port=5000,debug=True)


@app.route('/avg_rating/<filename>')
def avg_rating(filename):
    # search_query = request.form['song']
    # print(search_query)
    # print(search_query)
    # music_files = songs.find({'song_name': {'$regex': f'.*{search_query}.*', '$options': 'i'}})
    
    # output = songs.find({'song_name': {'$regex': search_query, '$options': 'i'}})
    pipeline = [
            {
                '$match': {
                    'song_id': filename  # Assuming 'song_id' is the identifier for songs in song_rating
                }
            },
            {
                '$group': {
                    '_id': '$song_id',
                    'average_rating': {'$avg': '$song_rating'}
                }
            },
            {
                '$set': {
                    'average_rating': {'$toInt': '$average_rating'}  # Convert average rating to integer
                }
            }
        ]
    avg_rating = list(ratings.aggregate(pipeline))
    print(avg_rating[0])
    # artist_names = [output.artist_id for out in output]
    # print(artist_names)
    # # play_song= stream_music(music_files['song_name'])
    # print(output.artist_id)
    # print(output['artist_id'])
    return Response('music.html',avg_rating=avg_rating[0] if avg_rating else 0)


# @app.route('/music', methods=['POST'])
# def search_music():
#     search_query = request.form['song']
#     # print(search_query)
#     print(search_query)
#     # music_files = songs.find({'song_name': {'$regex': f'.*{search_query}.*', '$options': 'i'}})
    
#     output = songs.find({'song_name': {'$regex': search_query, '$options': 'i'}})
    
#     # artist_names = [output.artist_id for out in output]
#     # print(artist_names)
#     # # play_song= stream_music(music_files['song_name'])
#     # print(output.artist_id)
#     # print(output['artist_id'])
#     return render_template('music.html', songs=output)



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
