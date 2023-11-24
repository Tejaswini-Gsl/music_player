import pymongo
from pymongo import MongoClient
import gridfs

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['sonic_bilss']  # Replace with your database name
fs = gridfs.GridFS(db)

# # Read and store an audio file as binary data
with open(r'D:\vs\test\songs\rama-rama.mp3', 'rb') as audio_file:
     audio_data = audio_file.read()
     file_id= fs.put(audio_data, filename='Manasa rama')  # Store the binary data
     db.songs.insert_one({'_id': file_id, 'song_name': 'Manasa','artist_id': ['rahul', 'chinmayi'],'genre': 'mass','runtime': '4:20','album': 'kushi'})
# f_id = db.fs.files.find_one({'filename': "rama-rama.mp3"})
# data = fs.get(f_id['_id']).read()
# out = r'C:\Users\harik\Downloads\audio1.mp3'
# output = open(out, 'wb')
# output.write(data)
# output.close()
# print("Download compleate")
client.close()