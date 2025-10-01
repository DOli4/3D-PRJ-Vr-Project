import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# List all collections
print("All collections:")
for collection in db.collections():
    print(f"- {collection.id}")

# Check interview-sessions collection
print("\nInterview sessions:")
sessions = db.collection('interview-sessions').stream()
for session in sessions:
    print(f"- Document ID: {session.id}")
    
    # Check subcollections
    subcollections = session.reference.collections()
    for subcol in subcollections:
        print(f"  - Subcollection: {subcol.id}")
        docs = subcol.stream()
        for doc in docs:
            print(f"    - Document: {doc.id}")