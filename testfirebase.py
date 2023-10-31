import firebase_admin
from firebase_admin import credentials, db

# Check firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {'databaseURL': 'https://faceproject-b3c27-default-rtdb.firebaseio.com'})
handle = db.reference('User')
a = handle.get()
print(a[1]['time'])

