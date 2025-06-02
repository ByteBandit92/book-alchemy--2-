from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Author(db.Model):
    """
    Author model representing an author in the library.
    """
    __tablename__ = 'author'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=True)  # Made nullable to avoid form issues
    date_of_death = db.Column(db.Date, nullable=True)

    def __repr__(self):
        return f"<Author {self.name}>"

    def __str__(self):
        return self.name

class Book(db.Model):
    """
    Book model representing a book in the library.
    """
    __tablename__ = 'book'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    publication_year = db.Column(db.Integer, nullable=False)

    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)
    author = db.relationship('Author', backref=db.backref('books', lazy=True))

    def __repr__(self):
        return f"<Book {self.title}>"

    def __str__(self):
        return f"{self.title} by {self.author.name}"
