# data_models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Author(db.Model):
    __tablename__ = 'author'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    date_of_death = db.Column(db.Date, nullable=True)
    
    # Define the string representation for the Author
    def __repr__(self):
        return f"<Author {self.name}>"
    
    def __str__(self):
        return self.name

class Book(db.Model):
    __tablename__ = 'book'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    publication_year = db.Column(db.Integer, nullable=False)
    
    # Foreign Key linking to Author table
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)
    author = db.relationship('Author', backref=db.backref('books', lazy=True))
    
    # Define the string representation for the Book
    def __repr__(self):
        return f"<Book {self.title}>"
    
    def __str__(self):
        return f"{self.title} by {self.author.name}"