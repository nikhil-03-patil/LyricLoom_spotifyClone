# app.py
from os import abort
import os
from flask import Flask, render_template, request, redirect, send_from_directory ,session, jsonify ,url_for
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy
from flask import redirect, url_for
import matplotlib.pyplot as plt
import io
import base64
from base64 import *
import sqlite3
from datetime import datetime
from flask import abort

app = Flask(__name__, static_url_path='/static')
app = Flask(__name__)
app.secret_key = 'f5c2a34b9f9a4f6d87265e4ba6d48b4c'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///D:/Dnyaneshwari/Python/sqlite3/Database/users.db'
db = SQLAlchemy(app)
conn = sqlite3.connect('users.db')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
     
class MoodEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(1000), db.ForeignKey('user.id'), nullable=False)
    mood_type = db.Column(db.String(50), nullable=False)
    mood_count = db.Column(db.Integer, nullable=False)
   
    def __repr__(self):
        return f"MoodEntry(user_id={self.user_name}, mood_type='{self.mood_type}')"

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    song_name = db.Column(db.String(100), nullable=False)
    mood = db.Column(db.String(50), nullable=False)
    song_value = db.Column(db.BLOB, nullable=False)
    album_cover = db.Column(db.BLOB, nullable=False)
    create_date = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"Song(id={self.id}, song_name='{self.song_name}', mood='{self.mood}', " \
               f"create_date='{self.create_date}', active={self.active})"

class LikedSong(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Assuming a user ID is associated with each liked song
    user_name = db.Column(db.String(1000), db.ForeignKey('user.id'), nullable=False)
    song_name = db.Column(db.String(100), nullable=False)
    mood = db.Column(db.String(50), nullable=False)
    song_value = db.Column(db.BLOB, nullable=False)
    album_cover = db.Column(db.BLOB, nullable=False)

    def __repr__(self):
        return f"LikedSong(song_name='{self.song_name}', mood='{self.mood}')"

class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(1000), db.ForeignKey('user.id'), nullable=False)
    song_name = db.Column(db.String(100), nullable=False)
    mood = db.Column(db.String(50), nullable=False)
    song_value = db.Column(db.BLOB, nullable=False)
    album_cover = db.Column(db.BLOB, nullable=False)

    def __repr__(self):
        return f"Playlist(song_name='{self.song_name}', mood='{self.mood}')"

@app.route('/fetch_song', methods=['GET'])
def fetch_song():
    song_id = request.args.get('songId')  # Get the song ID from the request
    # Query the Song table to fetch data based on the song ID
    song = Song.query.filter_by(id=song_id).first()
    if song:
        # Convert the bytes fields to Base64 strings for JSON serialization
        song_value_base64 = base64.b64encode(song.song_value).decode('utf-8')
        album_cover_base64 = base64.b64encode(song.album_cover).decode('utf-8')

        # Create a new record in the LikedSong table with the fetched song data
        liked_song = LikedSong(
            user_name=session.get('email'),  # Assuming user name is stored in session
            song_name=song.song_name,
            mood=song.mood,
            song_value=base64.b64decode(song_value_base64),  # Decode Base64 string to bytes
            album_cover=base64.b64decode(album_cover_base64)
        )
        db.session.add(liked_song)
        db.session.commit()
        
        # Return a success response
        return jsonify({'success': True})
    else:
        # Return an error response if the song is not found
        return jsonify({'success': False, 'error': 'Song not found'})
# Define liked_songs_data as a global variable

# Endpoint to fetch liked songs
@app.route('/fetch_liked_songs', methods=['GET'])
def fetch_liked_songs():
    # Query the LikedSong table to fetch liked songs based on the current user
    user_name = session.get('email')  # Assuming user name is stored in session
    liked_songs = LikedSong.query.filter_by(user_name=user_name).all()
    
    # Convert the liked songs to a list of dictionaries for JSON serialization
    liked_songs_data = []
    for song in liked_songs:
        # Encode the album cover and song value to Base64 strings
        album_cover_base64 = base64.b64encode(song.album_cover).decode('utf-8')
        song_value_base64 = base64.b64encode(song.song_value).decode('utf-8')
        liked_songs_data.append({
            'id': song.id,
            'song_name': song.song_name,
            'mood': song.mood,
            'album_cover': album_cover_base64,
            'song_value': song_value_base64
        })
        
    return jsonify(liked_songs_data) 
# Endpoint to remove a song from the liked songs
@app.route('/remove_from_liked_songs', methods=['POST'])
def remove_from_liked_songs():
    global liked_songs_data  # Access the global liked_songs_data list

    # Get the song name from the request data
    song_name = request.json.get('songName')

    # Find the song in the liked songs data list
    for song in liked_songs_data:
        if song['song_name'] == song_name:
            # Remove the song from the liked songs data list
            liked_songs_data.remove(song)
            return jsonify({'success': True}), 200
    
    return jsonify({'success': False, 'error': 'Song not found'}), 404

@app.route('/fetch_song_details', methods=['GET'])
def fetch_song_details():
    song_id = request.args.get('songId')
    song = Song.query.get(song_id)
    if song:
        song_value_base64 = base64.b64encode(song.song_value).decode('utf-8')
        album_cover_base64 = base64.b64encode(song.album_cover).decode('utf-8')
        song_details = {
            'id': song.id,
            'song_name': song.song_name,
            'mood': song.mood,
            #'album_cover': base64.b64encode(song.album_cover).decode('utf-8'),
            #'song_value': base64.b64encode(song.song_value).decode('utf-8')
            'song_value':base64.b64decode(song_value_base64),  # Decode Base64 string to bytes
            'album_cover':base64.b64decode(album_cover_base64)
        }
        return jsonify({'success': True, 'songDetails': song_details})
    else:
        return jsonify({'success': False, 'error': 'Song not found'})


@app.route('/add_to_playlist', methods=['POST'])
def add_to_playlist():
    song_details = request.get_json()
    playlist_song = Playlist(
        user_name=session.get('email'),
        song_name=song_details['song_name'],
        mood=song_details['mood'],
        song_value=song_details['song_value'].encode('utf-8'),  # Encode back to bytes if necessary
        album_cover=song_details['album_cover'].encode('utf-8')  # Encode back to bytes if necessary
    )
    db.session.add(playlist_song)
    db.session.commit()
    return jsonify({'success': True})

# Convert file to binary data
def read_file_as_blob(file_path):
    with open(file_path, 'rb') as file:
        blob_data = file.read()
        print("Blob data:", blob_data)
    return blob_data


# Insert data into the Song table
# @app.route('/insert_song',methods=['GET', 'POST'])
# def insert_data():
#     try:
#         # List of song data with file paths
#         song_data = [
#             {
#                 'song_name': 'Kal Ho Naa Ho',
#                 'mood': 'Sad',
#                 'song_file_path': 'D:/Dnyaneshwari/Python/test/static/songs/KalHoNaaHo.mp3',
#                 'album_cover_file_path': 'D:/Dnyaneshwari/Python/test/static/images/KalHoNaaHo.jpg'
#             },
#             {
#                 'song_name': 'Kamli',
#                 'mood': 'Dancing',
#                 'song_file_path': 'D:/Dnyaneshwari/Python/test/static/songs/Kamli.mp3',
#                 'album_cover_file_path': 'D:/Dnyaneshwari/Python/test/static/images/Kamli.jpeg'
#             },
#             {
#                 'song_name': 'KhudaJaane',
#                 'mood': 'Happy',
#                 'song_file_path': 'D:/Dnyaneshwari/Python/test/static/songs/KhudaJaane.mp3',
#                 'album_cover_file_path': 'D:/Dnyaneshwari/Python/test/static/images/KhudaJaane.jpeg'
#             },
#             {
#                 'song_name': 'Heeriye',
#                 'mood': 'Romantic',
#                 'song_file_path': 'D:/Dnyaneshwari/Python/test/static/songs/Heeriye.mp3',
#                 'album_cover_file_path': 'D:/Dnyaneshwari/Python/test/static/images/Heeriye.jpg'
#             },
#             {
#                 'song_name': 'ChikniChameli',
#                 'mood': 'Dancing',
#                 'song_file_path': 'D:/Dnyaneshwari/Python/test/static/songs/ChikniChameli.mp3',
#                 'album_cover_file_path': 'D:/Dnyaneshwari/Python/test/static/images/ChikniChameli.jpg'
#             },
#             {
#                 'song_name': 'Hamari Adhuri Kahani',
#                 'mood': 'Sad',
#                 'song_file_path': 'D:/Dnyaneshwari/Python/test/static/songs/HamariAdhuriKahani.mp3',
#                 'album_cover_file_path': 'D:/Dnyaneshwari/Python/test/static/images/HamariAdhuriKahani.jpg'
#             },
#             {
#                 'song_name': 'Pehli Nazar Mein',
#                 'mood': 'Lofi',
#                 'song_file_path': 'D:/Dnyaneshwari/Python/test/static/songs/PehliNazarMein.mp3',
#                 'album_cover_file_path': 'D:/Dnyaneshwari/Python/test/static/images/PehliNazarMein.jpg'
#             },
#             {
#                 'song_name': 'Jeene Laga Hoon',
#                 'mood': 'Lofi',
#                 'song_file_path': 'D:/Dnyaneshwari/Python/test/static/songs/JeeneLagaHoon.mp3',
#                 'album_cover_file_path': 'D:/Dnyaneshwari/Python/test/static/images/JeeneLagaHoon.jpg'
#             },
#             # Add more song data as needed
#         ]

#         for data in song_data:
#             # Read the MP3 file and image file as BLOBs
#             song_value_blob = read_file_as_blob(data['song_file_path'])
#             album_cover_blob = read_file_as_blob(data['album_cover_file_path'])

#             # Create a new Song instance with the provided data
#             new_song = Song(
#                 song_name=data['song_name'],
#                 mood=data['mood'],
#                 song_value=song_value_blob,
#                 album_cover=album_cover_blob,
#                 create_date=datetime.utcnow(),
#                 active=True
#             )

#             # Add the new song to the database session
#             db.session.add(new_song)

#         # Commit all changes to the database session
#         db.session.commit()

#         return jsonify({'status': 'success', 'message': 'Data inserted successfully!'})
#     except Exception as e:
#         # Rollback changes if an error occurs
#         db.session.rollback()
#         return jsonify({'status': 'error', 'message': f'Error: {str(e)}'})
with app.app_context():
    db.create_all()
    
@app.route('/view_song', methods=['POST'])
def view_song():
    # Query the database to retrieve song data
    # songs = Song.query.all()  # Assuming Song is your SQLAlchemy model
    # for song in songs:
    #         # Convert album_cover to base64
    #     album_cover_base64 = base64.b64encode(song.album_cover).decode('utf-8')
    #     song.album_cover = album_cover_base64

    #     # Convert song_value to base64
    #     song_value_base64 = base64.b64encode(song.song_value).decode('utf-8')
    #     song.song_value = song_value_base64


    # # Render HTML template with the retrieved song data
    # return render_template('index.html', songs=songs)
    if request.method == 'POST':
        mood = request.json['mood']
        # Query the database to retrieve song data based on the mood
        songs = Song.query.filter_by(mood=mood).all()
        song_data = []
        for song in songs:
            album_cover_base64 = base64.b64encode(song.album_cover).decode('utf-8')
            song.album_cover = album_cover_base64
            song_value_base64 = base64.b64encode(song.song_value).decode('utf-8')
            song.song_value = song_value_base64
            song_data.append({
                'album_cover': album_cover_base64,
                'song_name': song.song_name,
                'mood': song.mood,
                'song_value': song_value_base64
            })

        return jsonify({'songs': song_data})

@app.route('/update_mood', methods=['POST'])
def update_mood():
    if request.method == 'POST':
        # Get the mood type from the request JSON data
        mood_type = request.json.get('mood_type')  # Update this line to use 'mood_type'
        
        # Check if the user has already entered the same mood type today
        existing_entry = MoodEntry.query.filter_by(user_name=session.get('email'), mood_type=mood_type).first()
        if existing_entry:
            # If the entry already exists, increment the mood_count
            existing_entry.mood_count += 1
        else:
            # If it doesn't exist, create a new entry
            new_entry = MoodEntry(user_name=session.get('email'), mood_type=mood_type, mood_count=1)
            db.session.add(new_entry)
        
        # Commit the changes to the database
        db.session.commit()
        
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Invalid request method'})
@app.route('/')
def registration():
    return render_template('registration.html')

@app.route('/register', methods=['POST'])
def register():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    password = request.form['password']
    
    # Check if the email is already registered
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return "Email already exists. Please use a different email."

    # Create a new user
    new_user = User(first_name=first_name, last_name=last_name, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()
    session['email'] = email
    session['first_name'] = first_name
    session['last_name'] = last_name
    # return 'Registration successful!' 
    return redirect('/login')

# @app.route('/index')
# def index():
#     if 'email' in session:
#         return render_template('index.html', email=session['email'])
#     else:
#         return redirect(url_for('login'))  # Redirect to the login route
@app.route('/index')
def index():
    if 'email' in session:
        email = session['email']
        # Fetch songs data from the database
        songs = Song.query.all()
        for song in songs:
            # Convert album_cover to base64
            album_cover_base64 = base64.b64encode(song.album_cover).decode('utf-8')
            song.album_cover = album_cover_base64

            # Convert song_value to base64
            song_value_base64 = base64.b64encode(song.song_value).decode('utf-8')
            song.song_value = song_value_base64

        return render_template('index.html', email=email, songs=songs)
    else:
        return redirect(url_for('login'))

@app.route('/artist/<artist_id>')
def get_artist_songs(artist_id):
    return jsonify(artists.get(artist_id, {'songs': []}))

@app.route('/login',methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Query the database for the user
        user = User.query.filter_by(email=email).first()

        if user and user.password == password:
            # User authenticated successfully
            session['email'] = email 
            # Store username in session
            session['first_name'] = user.first_name  # Store first name in session
            session['last_name'] = user.last_name
            return redirect(url_for('index', email=email))  # Pass email as parameter to index route

        else:
            # Authentication failed
            return render_template('login.html', error='Invalid email or password')

    return render_template('login.html')

@app.route('/playlist')
def playlist():
    user_info = {
        'first_name': session.get('first_name'),
        'last_name': session.get('last_name'),
        'email': session.get('email')
    }
    return render_template('playlist_page.html',user_info=user_info)  


@app.route('/mymedia')
def mymedia():
    return render_template('mymedia.html')

@app.route('/index2')
def index2():
    return render_template('index2.html')

@app.route('/account')
def account():
    # Get user information from session
    user_email = session.get('email')
    user_info = {
        'first_name': session.get('first_name'),
        'last_name': session.get('last_name'),
        'email': user_email
    }
    
    # Query the database to retrieve mood entries for the current user
    mood_entries = MoodEntry.query.filter_by(user_name=user_email).all()
    
    # Process the data to create a bar chart
    mood_types = [entry.mood_type for entry in mood_entries]
    mood_counts = [entry.mood_count for entry in mood_entries]
    
    plt.bar(mood_types, mood_counts)
    plt.xlabel('Mood Type')
    plt.ylabel('Mood Count')
    plt.title('Mood Entry Bar Chart')
    
    # Save the chart as an image
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    chart_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    # Render the HTML page with the chart and user information
    return render_template('account.html', user_info=user_info, chart_url=chart_url)
    




@app.route('/play_song/<int:song_id>')
def play_song(song_id):
    # Fetch the song details based on the song_id
    # Replace the below code with your logic to fetch song details
    song_details = {
        'album_cover_url': 'url_to_album_cover',
        'audio_url': 'url_to_audio_file',
        'song_name': 'Song Name'
    }
    return jsonify(song_details)
# Ignore favicon requests
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    app.run(debug=True)
