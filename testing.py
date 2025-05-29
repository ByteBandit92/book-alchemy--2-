from app import app, db
from data_models import Author
from datetime import datetime

# Ensure that the app is in the correct context
with app.app_context():
    try:
        # Correct the date format
        author = Author(
            name='John Steinbeck',
            birth_date=datetime.strptime('1902-02-27', '%Y-%m-%d').date(),
            date_of_death=None  # or use a datetime.date object for a death date
        )
        
        # Add to session and commit
        db.session.add(author)
        db.session.commit()
        
        print("Author added successfully.")
    except Exception as e:
        print(e)

