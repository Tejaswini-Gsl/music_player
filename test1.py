from flask import Flask, render_template, request, redirect, session,send_file,Response,jsonify, url_for
import pymongo
from bson import ObjectId
from datetime import datetime, timedelta
from gridfs import GridFS
import io
import sub_email

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
    admin = db['admin']
    songs = db['songs']
    payments = db['payment_info']
    ratings = db['song_rating']
    artists = db['artist']
    playlist_db = db['playlist']
    gridfs = GridFS(db)
except:
    print("ERROR - cannot connect to db")

slide_images = ["playlist1.jpg", "playlist2.jpg", "playlist3.jpg"]
genres_list= songs.distinct('genre')
all_genres = [genre.strip() for genres in genres_list for genre in genres.split(',')]
genres = list(set(all_genres))
@app.route('/')   # done
def index():
    is_logged_in = 'username' in session
    return render_template('sp1.html', is_logged_in=is_logged_in, slide_images=slide_images,genres=genres)

@app.route('/playlist')   # done
def playlist():
    is_logged_in = 'username' in session
    return render_template('playlist.html', is_logged_in=is_logged_in)

@app.route('/register', methods=['GET', 'POST'])
def register():          # done
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
                'user_gender': gender,
                'membership': 'no membership'
            }
            
            users.insert_one(user)


            session['user_id'] = str(user_id)
            return render_template('login.html')
        else:
            return render_template('register.html')
    except Exception as e:
        print(e)

@app.route('/logout')  # done
def logout():
    try:
        session.pop('username', None)
        session.pop('user_id',None)
        return render_template('sp1.html', is_logged_in=False, slide_images=slide_images,genres=genres)
    except Exception as ex:
        print(ex)

@app.route('/login', methods=['GET', 'POST'])  # done
def login():
    try:
        if request.method == "POST":
            username = request.form['username']
            password = request.form['password']
            selected_users =  request.form.get('selected_users')
            # # Process the selected users as needed (e.g., print, save to a database, etc.)
            print("Selected Users:", selected_users)
            if selected_users == 'admin':
                admin_value = admin.find_one({'admin_name': username, 'admin_password': password})
                user_all = list(users.find())
                if admin_value:
                    print(admin_value)
                    session['username'] = username
                    session['user_id'] = str(admin['_id'])
                    return render_template('admin_user.html', is_logged_in=True,is_admin=True,users=user_all)
                else:
                    return render_template('error.html',message='not a admin')
            
            else:
                user = users.find_one({'user_name': username, 'user_password': password})
                
                if user:
                    session['username'] = username
                    session['user_id'] = str(user['_id'])
                    sub_email.check(user['_id'])
                    return render_template('sp1.html', is_logged_in=True, slide_images=slide_images,genres=genres)
                else:
                    return render_template('register.html')
        else:
            return render_template('login.html')
    except Exception as e:
        print(e)

@app.route('/payment', methods=['GET', 'POST'])  # done
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
                    return render_template('sp1.html', is_logged_in=is_logged_in, slide_images=slide_images, payment_successful=True, show_as_index=True,genres=genres)
                else:
                    return render_template('sp1.html', is_logged_in=is_logged_in, slide_images=slide_images, payment_successful=True,genres=genres)
                # return render_template('sp1.html', is_logged_in=True, slide_images=slide_images,payment_successful=True)

        return render_template('payment.html', is_logged_in='username' in session)
    except Exception as ex:
        print(ex)

def update_user(amount,registration_date):  # need to add de registered 
    try:
        user_id = session.get('user_id')
        if amount == '45':
            membership = 'year'
            end_date = registration_date +  timedelta(days=365)
        elif amount == '20':
            membership = 'month'
            end_date = registration_date + timedelta(days=30)
        # elif amount == '-':
        #     membership = 'no membership'
        #     end_date = registration_date 

        else:
            membership = 'no membership'
            end_date = registration_date


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

def check_logged_in_membership(user_id):   # done
    try:
        print ("user_id",user_id)
        user = users.find_one({'_id': ObjectId(session.get('user_id'))})
        if user_id:
            current_date = datetime.utcnow()
            user_membership = user.get('membership')
            membership_end_date = user.get('end_date')
            print(membership_end_date)
            valid_membership = user_membership and user_membership != 'no membership'
            if not valid_membership or current_date > membership_end_date:
                has_membership = False
                return (has_membership)
            else:
                has_membership = True
                return(has_membership)
    
        else:
             has_membership = False
             return(has_membership)

    except Exception as ex:
        print(ex)


@app.route('/genre_music_search/<filename>') # done
def search_genre_music(filename):     # done 
    search_query = filename
    print(search_query)
    is_logged_in = 'username' in session
    user_id = 'user_id' in session
    has_membership = check_logged_in_membership(user_id)
    print("has_membership",has_membership)
    if search_query:
    # Search for the song details in the 'songs' collection
        song_details = list(songs.find({'genre': {'$regex': search_query, '$options': 'i'}}))
        print(type(song_details))
        print(song_details)
        # If the song is found, get its details
        if len(song_details) > 0:
            pipeline = [
        {
            '$match': {
                'genre': {'$regex': search_query, '$options': 'i'}
            }
        },
        {
            '$lookup': {
                'from': 'artist',
                'localField': 'artist_id',
                'foreignField': '_id',
                'as': 'artists'
            }
        },
        {
            '$addFields': {
                'artist_name': '$artists.artist_name'
            }
        },
        {
            '$lookup': {
                'from': 'song_rating',
                'localField': '_id',
                'foreignField': 'song_id',
                'as': 'ratings'
            }
        },
        {
            '$addFields': {
                'avg_rating': {
                    '$avg': '$ratings.song_rating'
                }
            }
        }
       
    ]

            result = list(songs.aggregate(pipeline))
            print("result:",result)
            
        return render_template('music.html', songs=result,is_logged_in=is_logged_in,has_membership=has_membership,is_playlist= True)
    else:
        # If the song is not found, return an appropriate message
        return render_template('music.html', message="Song not found",is_logged_in=is_logged_in,has_membership= has_membership,is_playlist= True)


@app.route('/music', methods=['POST'])
def search_music():      # done 
    search_query = request.form['song']
    print(search_query)
    song_details = list(songs.find({'song_name': {'$regex': search_query, '$options': 'i'}}))
    is_logged_in = 'username' in session
    user_id = 'user_id' in session
    has_membership = check_logged_in_membership(user_id)
    if len(song_details) > 0:
    
        # has_membership = check_logged_in_membership(user_id)
        print("has_membership",has_membership)
        if search_query:
        # Search for the song details in the 'songs' collection
            # song_details = list(songs.find({'song_name': {'$regex': search_query, '$options': 'i'}}))
            print(song_details)
            # If the song is found, get its details
            
            pipeline = [
            {
                '$match': {
                    'song_name': {'$regex': search_query, '$options': 'i'}
                }
            },
            {
                '$lookup': {
                    'from': 'artist',
                    'localField': 'artist_id',
                    'foreignField': '_id',
                    'as': 'artists'
                }
            },
            {
                '$addFields': {
                    'artist_name': '$artists.artist_name'
                }
            },
            {
                '$lookup': {
                    'from': 'song_rating',
                    'localField': '_id',
                    'foreignField': 'song_id',
                    'as': 'ratings'
                }
            },
            {
                '$addFields': {
                    'avg_rating': {
                        '$avg': '$ratings.song_rating'
                    }
                }
            }
        
        ]

            result = list(songs.aggregate(pipeline))
            print("result:",result)
            
        return render_template('music.html', songs=result,is_logged_in=is_logged_in,has_membership=has_membership,is_playlist= True)
    else:
        # If the song is not found, return an appropriate message
        return render_template('music.html', message="Song not found",is_logged_in=is_logged_in,has_membership= has_membership,is_playlist= True)

    # return render_template('player.html', music_files=music_files,music_id= music_files[0]['_id'])

@app.template_global(name='zip')
def _zip(*args, **kwargs): #to not overwrite builtin zip in globals
    return __builtins__.zip(*args, **kwargs)


@app.route('/music_search/<filename>') # done
def search_music_direct(filename):
    output = list(songs.find({'_id':ObjectId(filename)}))  
    print("Output:",output)
    is_logged_in = 'username' in session
    user_id = 'user_id' in session 
    has_membership = check_logged_in_membership(user_id)
    print("has_membership",has_membership)

    if len(output) > 0:
            # Get the song_id for fetching ratings
            artist_id = output[0]['artist_id']
            # print(artist_id)
            artist_names = []
            for artist_id in artist_id:
                artist_details = artists.find_one({'_id': ObjectId(artist_id)})
                if artist_details:
                    artist_names.append(artist_details['artist_name'])
    
            output[0]['artist_name'] = artist_names

            song_id = output[0]['_id']

            output[0]['avg_rating'] = find_rating(song_id)
    return render_template('music.html', songs=output,is_logged_in=is_logged_in,has_membership= has_membership,is_playlist= True)


from bson import Regex
import re


@app.route('/stream_music/<filename>')   # done
def stream_music(filename):
    try: 
        output = list(songs.find({'_id':ObjectId(filename)}))  
        # print("stream_output:",output)
        music_filename = output[0]['song_name']
        # Convert the filename to a case-insensitive regular expression
        filename_regex = Regex(f'^{re.escape(music_filename)}$', 'i')
        # print(music_filename)
        file = gridfs.find_one({'filename': filename_regex}) 
        return send_file(
        io.BytesIO(file.read()),
        mimetype='audio/mp3',
        as_attachment=True,
        download_name=f'{file.filename}'
    )
        # return Response(
        #         file.read(),
        #         mimetype=file.content_type,
        #         headers={'Content-Disposition': f'attachment; filename={filename}'} 
        #     )

    except Exception as ex:
        print(ex)




@app.route('/create_playlist', methods=['GET', 'POST'])   # done 
def create_playlist():
    is_logged_in = 'username' in session
    user_id = 'user_id' in session
    has_membership = check_logged_in_membership(user_id)

    if user_id and has_membership:
        playlists = list(db.playlist.find({'user_id': ObjectId(session.get('user_id'))}))

        if request.method == 'POST':
            new_playlist_name = request.form.get('playlistName')
            action = request.form.get('action')

            # Check if the playlist name already exists
            existing_playlist = db.playlist.find_one({'playlist_name': new_playlist_name, 'user_id': ObjectId(session.get('user_id'))})

            
            # Playlist name is unique, insert the new playlist
            if action == 'add':
                if existing_playlist:
                # Playlist name already exists, ask the user to create a playlist with a new name
                    error_message = "Playlist name already exists. Please choose a different name."
                    return render_template("playlist.html", is_logged_in=is_logged_in, has_membership=has_membership, playlists=playlists, error_message=error_message)

                db.playlist.insert_one({'playlist_name': new_playlist_name, 'user_id': ObjectId(session.get('user_id')),'songs_list':[]})
            
                 # Refresh the playlists after adding the new playlist
                playlists = list(db.playlist.find({'user_id': ObjectId(session.get('user_id'))}))
            
                return render_template("playlist.html", is_logged_in=is_logged_in, has_membership=has_membership, playlists=playlists)
            
            elif action == 'remove':
                db.playlist.delete_many({'playlist_name': new_playlist_name, 'user_id': ObjectId(session.get('user_id'))})
                playlists = list(db.playlist.find({'user_id': ObjectId(session.get('user_id'))}))
            
                return render_template("playlist.html", is_logged_in=is_logged_in, has_membership=has_membership, playlists=playlists)

        return render_template("playlist.html", is_logged_in=is_logged_in, playlists=playlists, has_membership=has_membership)

    return render_template('login.html')


@app.route('/playlist_search/<filename>')  # done
def search_playlist(filename):
    is_logged_in = 'username' in session
    user_id = 'user_id' in session
    has_membership = check_logged_in_membership(user_id)
     # output = list(songs.find({'song_name':filename}))
    print("has_membership",has_membership)
    print(filename)
    # print(list(db.playlist.find({'playlist_name': filename})))
    pipeline = [
        {
            '$match': {'playlist_name': filename} 
        }, 
        {
           '$lookup': {
               'from': 'songs',
               'localField': 'songs_list',
               'foreignField': '_id', #need to change as '_id'
               'as': 'song_details'
            }
        },
        {
            '$unwind': '$song_details'
        },
        {
            '$project': { 
                'song_name': '$song_details.song_name',
                'artist_id': '$song_details.artist_id',
                'genre': '$song_details.genre',
                'runtime': '$song_details.runtime',
                'album': '$song_details.album',
                '_id': '$song_details._id',
                'playlist': '$name'
            }
        }
    ]
    
    results = db.playlist.aggregate(pipeline)
    print(results)
    output = list(results)
    print("whole output",output)

   
    return render_template('music.html', songs=output,is_logged_in=is_logged_in,has_membership= has_membership,is_playlist= False)



@app.route('/add_to_playlist_modal/<song_name>', methods=['GET','POST']) # no changes required only song_id input -- done
def add_to_playlist_modal(song_name):

    playlists = list(db.playlist.find({'user_id': ObjectId(session.get('user_id'))}))

    return render_template('add_to_playlist_modal.html', song_name=song_name, playlists=playlists,is_logged_in='user_id' in session)


@app.route('/manage_playlist/<song_name>', methods=['POST'])   # no changes required only song_id input -- done 
def manage_playlist(song_name):
    playlist_name = request.form.get('playlist_name')
    action = request.form.get('action')
    song_name= ObjectId(song_name)
    # print(playlist_name)
    # print(action)
    # print(song_name)
    # Check if the user is logged in
    if 'user_id' not in session:
        return render_template('error.html', message='User not logged in')

    user_id = ObjectId(session.get('user_id'))

    # Check if the playlist exists and is owned by the user
    playlist_query = {'playlist_name': playlist_name, 'user_id': user_id}
    playlist = db.playlist.find_one(playlist_query)

    if not playlist:
        # Playlist doesn't exist or is not owned by the user, handle accordingly
        return render_template('error.html', message='Playlist not found or not owned by the user')

    # Check if the song already exists in the playlist
    if action == 'add' and song_name in playlist['songs_list']:
        # Song already exists in the playlist, handle accordingly
        return render_template('error.html', message=f"song is already in the playlist")

    if action == 'remove' and song_name not in playlist['songs_list']:
        # Song doesn't exist in the playlist, handle accordingly
        return render_template('error.html', message=f"song is not in the playlist")

    # Your logic for adding or removing a song from the playlist
    if action == 'add':
        # Add song to the playlist
        # print(f"Adding '{song_name}' to playlist '{playlist_name}'")
        db.playlist.update_one(
            playlist_query,
            {'$push': {'songs_list': song_name}}
        )
    elif action == 'remove':
        # Remove song from the playlist
        # print(f"Removing '{song_name}' from playlist '{playlist_name}'")
        db.playlist.update_one(
            playlist_query,
            {'$pull': {'songs_list': song_name}}
        )
    # return redirect(url_for('search_music'))
    return render_template('sp1.html',is_logged_in='user_id' in session,slide_images=slide_images,genres=genres)
       
    
@app.route('/artist/<artist_id>')    # done
def artist_profile(artist_id):
    # Fetch artist details from MongoDB
    print (artist_id)
    artist_details = db.artist.find_one({'_id': ObjectId(artist_id)})  
   
    is_logged_in = 'username' in session
    if artist_details:
        # Fetch songs associated with the artist
        songs_info = songs.find({'artist_id': ObjectId(artist_id)}) 
        song_values = list(songs_info)
        # print(song_values[0])
        return render_template('artist.html',is_logged_in=is_logged_in, artist_info=artist_details,song_values= song_values)
    else:
        return 'Artist not found', 404

@app.route('/rate_song/<song_id>/<int:rating>', methods=['POST'])
def rate_song(song_id, rating):   # need to change song_name to song_id -- done
   
    
    # username = session.get('username')
    existing_rating = ratings.find_one({'song_id': ObjectId(song_id),'user_id': ObjectId(session.get('user_id'))})  # need to change song_name to song_id 

    if existing_rating:
        # If a previous rating exists, update it
        ratings.update_one(
            {'song_id':ObjectId(song_id),'user_id': ObjectId(session.get('user_id'))},  # need to change song_id value in rating db too 
            {'$set': {'song_rating': rating}}
        )
    else:
        # If no previous rating exists, insert a new document
        ratings.insert_one({            
            'user_id': ObjectId(session.get('user_id')),
            'song_id': ObjectId(song_id),          # need to change song_id value in rating db too 
            'song_rating': rating
        })

    return 'Rating saved successfully', 200

def find_rating(song_id):    # need to change the song_id  
    ratings = list(db.song_rating.find({'song_id': song_id})) # need to change the song_id  objectid(song_id)
    print(ratings)
            # Calculate the average rating
    avg_rating = 0
    num_ratings = len(ratings)
    if num_ratings > 0:
        total_rating = sum([rating['song_rating'] for rating in ratings])
                
        avg_rating = total_rating //num_ratings
    return(avg_rating)

def find_artist_names(artist_id):    # need to change the song_id 
    print("arstist_id:",artist_id)
    artist_names = []
    for artist_id in artist_id:
        artist_details = artists.find_one({'_id': ObjectId(artist_id)})
        if artist_details:
            artist_names.append(artist_details['artist_name'])
    return(artist_names)

@app.route('/admin_song')    
def admin_songs():
    songs = list(db.songs.find())
    return render_template('admin_song.html', songs=songs,is_admin=True)

@app.route('/admin_artist')    
def admin_artist():

    artists = list(db.artist.find())
    return render_template('admin_artist.html', artists=artists,is_admin=True)
@app.route('/admin_user')    
def admin_user():
    users = list(db.user.find())
    return render_template('admin_user.html', users=users,is_admin=True)


@app.route('/admin_edit/<filename>/<values>', methods=['GET','POST'])
def admin_edit(filename,values):
    # user_values = values.split(',')
    print(values)
    if filename == 'a_user':
        labels_user = ['user_name', 'user_email', 'user_password','user_gender','user_age']  # Replace with your dynamic labels
        labels= labels_user
        heading = 'EDIT USER'
        
    elif filename == 'a_artist':
        labels_artist = ['artist_name', 'age', 'gender','artist_description']  # Replace with your dynamic labels
        labels= labels_artist
        heading = 'EDIT ARTIST'
    elif filename == 'a_song':
        labels_song = ['song_name', 'genre', 'runtime','album','artist_id']  # Replace with your dynamic labels
        labels= labels_song
        heading = 'EDIT SONG'

    if request.method == 'POST':
        if filename == 'a_user':
            form_data = {label: request.form.get(label) for label in labels}
            update_query = {
                '$set': form_data
                                    }
            # print(form_data)
            users.update_one({'_id': ObjectId(values)}, update_query)
            return(admin_user())
        
        elif filename == 'a_artist':
            form_data = {label: request.form.get(label) for label in labels[1:]}
            update_query = {
                '$set': form_data
                                    }
            db.artist.update_one({'_id': ObjectId(values)}, update_query)
            return(admin_artist())
        elif filename == 'a_song':
            form_data = {label: request.form.get(label) for label in labels[1:]}
            update_query = {
                '$set': form_data
                                    }
            db.songs.update_one({'_id': ObjectId(values)}, update_query)
            return(admin_songs())

            # print(audio_file)
        # Do something with the data

        

    return render_template('admin_add.html', labels=labels,is_admin=True, is_edit  = True,values= values,heading=heading)

@app.route('/admin_delete/<string:filename>/<file_id>/<song_name>')
def admin_delete(filename,file_id,song_name):
    print(filename)
    if filename == 'a_user':
        print("hello")
        db.user.delete_one({"_id":ObjectId(file_id)})
        return(admin_user())

    elif filename == 'a_artist':
        db.artist.delete_one({"_id":ObjectId(file_id)})

        return(admin_artist())

        
    elif filename == 'a_song':
        filename_regex = Regex(f'^{re.escape(song_name)}$', 'i')
        file_to_delete = gridfs.find_one({'filename': filename_regex})
        if file_to_delete:
            gridfs.delete(file_to_delete._id)
        db.songs.delete_one({"_id":ObjectId(file_id)})

        return(admin_songs())



    return render_template('error.html')

@app.route('/admin_add/<filename>', methods=['GET','POST'])
def admin_add(filename):

    if filename == 'a_user':
        labels_user = ['user_name', 'user_email', 'user_password','user_gender','user_age']  # Replace with your dynamic labels
        labels= labels_user
        heading = 'NEW USER'
    elif filename == 'a_artist':
        labels_artist = ['artist_name', 'age', 'gender','artist_description']  # Replace with your dynamic labels
        labels= labels_artist
        heading = 'NEW ARTIST'
    elif filename == 'a_song':
        labels_song = ['song_name', 'genre', 'runtime','album','artist_id','upload_song']  # Replace with your dynamic labels
        labels= labels_song
        heading = 'NEW SONG'
    if request.method == 'POST':
        if filename == 'a_user':
            form_data = {label: request.form.get(label) for label in labels}
            users.insert_one(form_data)
            return(admin_user())
        elif filename == 'a_artist':
            form_data = {label: request.form.get(label) for label in labels}
            db.artist.insert_one(form_data)
            return(admin_artist())
        elif filename == 'a_song':
            form_data = {
                label: [ObjectId(value) for value in request.form.getlist(label)] if label == 'artist_id' else request.form.get(label)
                                for label in labels[:-1]
                                }           
            audio_file = request.files['audioFile']
            file_id = gridfs.put(audio_file, filename=request.form.get('song_name'))
            db.songs.insert_one(form_data)
            return(admin_songs())

            # print(audio_file)
        # Do something with the data

        

    return render_template('admin_add.html', labels=labels,is_admin=True,heading=heading)

@app.route('/update_prof', methods=['GET','POST'])
def update_prof():
    print("triggered")
    user_id = ObjectId(session.get('user_id'))
    updated_user = users.find_one({'_id': user_id})
    start_date = updated_user['start_date']
    end_date= updated_user['end_date']
    membership = updated_user['membership']
    days_until_expiry = (end_date - datetime.utcnow()).days

    if request.method == 'POST':
            if request.form.get("membership") == "Yes":
                membership = "no membership"
                start_date = datetime.utcnow()
                end_date = datetime.utcnow()

            update_query = {
                '$set':{
                    "user_name": request.form['name'],
                    "user_email": request.form['email'],
                    "membership": membership,
                    "start_date": start_date,
                    "end_date":end_date,
                }
                                    }
            print("updatingg........")
            users.update_one({'_id': user_id}, update_query)
            return render_template('error.html',message="user got updated")

    return render_template('update_prof.html', users=updated_user,is_logged_in=True,days_until_expiry=days_until_expiry)


if __name__ == '__main__':
    app.run(port=5000, debug=True)
