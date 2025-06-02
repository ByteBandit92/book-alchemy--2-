# app.py
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from data_models import db, Author, Book
from datetime import datetime
from flask_migrate import Migrate
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__)
load_dotenv()
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///library.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
db.init_app(app)
migrate = Migrate(app, db)

@app.route('/', methods=['GET'])
def home():
    """
    Home page route. Displays all books with optional search and sorting.
    Search can be by title or ISBN. Sorting by title, year, or author.
    """
    search = request.args.get('search', '')
    search_by = request.args.get('search_by', 'title')
    sort = request.args.get('sort', '')

    books_query = Book.query.join(Author)

    if search:
        if search_by == 'isbn':
            books_query = books_query.filter(Book.isbn.ilike(f'%{search}%'))
        else:
            books_query = books_query.filter(Book.title.ilike(f'%{search}%'))

    if sort == 'year_asc':
        books_query = books_query.order_by(Book.publication_year.asc())
    elif sort == 'year_desc':
        books_query = books_query.order_by(Book.publication_year.desc())
    elif sort == 'author_asc':
        books_query = books_query.order_by(Author.name.asc())
    elif sort == 'author_desc':
        books_query = books_query.order_by(Author.name.desc())
    else:
        books_query = books_query.order_by(Book.title.asc())

    books = books_query.all()
    return render_template('home.html', books=books, search=search, sort=sort, search_by=search_by)

@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    """
    Route to add a new author.
    Accepts POST request with form data:
    - name (str)
    - birth_date (optional, YYYY-MM-DD)
    - date_of_death (optional, YYYY-MM-DD)
    """
    if request.method == 'POST':
        name = request.form['name'].strip()

        try:
            birth_date_str = request.form.get('birth_date', '').strip()
            birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date() if birth_date_str else None

            date_of_death_str = request.form.get('date_of_death', '').strip()
            date_of_death = datetime.strptime(date_of_death_str, '%Y-%m-%d').date() if date_of_death_str else None

            author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)
            db.session.add(author)
            db.session.commit()
            flash(f"Author '{name}' added successfully!", "success")
            return redirect(url_for('home'))

        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.", "warning")
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f"Database error occurred while adding author: {e}", "danger")

    return render_template('add_author.html')

def is_valid_isbn(isbn):
    """
    Validates whether a given ISBN is valid (ISBN-10 or ISBN-13).
    Returns True if valid, False otherwise.
    """
    isbn = isbn.replace('-', '').replace(' ', '')

    if len(isbn) == 10:
        return is_valid_isbn10(isbn)
    elif len(isbn) == 13:
        return is_valid_isbn13(isbn)
    else:
        return False

def is_valid_isbn10(isbn):
    """
    Validates an ISBN-10 string.
    """
    if len(isbn) != 10:
        return False
    total = 0
    for i, char in enumerate(isbn):
        if char == 'X' and i == 9:
            value = 10
        elif char.isdigit():
            value = int(char)
        else:
            return False
        total += value * (10 - i)
    return total % 11 == 0

def is_valid_isbn13(isbn):
    """
    Validates an ISBN-13 string.
    """
    if len(isbn) != 13 or not isbn.isdigit():
        return False
    total = 0
    for i, char in enumerate(isbn):
        num = int(char)
        total += num if i % 2 == 0 else num * 3
    return total % 10 == 0

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    """
    Route to add a new book.
    Validates ISBN before saving. Requires:
    - isbn (str)
    - title (str)
    - publication_year (int)
    - author_id (int)
    """
    if request.method == 'POST':
        isbn = request.form['isbn']
        title = request.form['title']
        publication_year = request.form['publication_year']
        author_id = request.form['author_id']

        if not is_valid_isbn(isbn):
            error = "Invalid ISBN number."
            authors = Author.query.all()
            return render_template('add_book.html', authors=authors, error=error)

        try:
            book = Book(isbn=isbn, title=title, publication_year=publication_year, author_id=author_id)
            db.session.add(book)
            db.session.commit()
            flash(f"Book '{title}' added successfully!", "success")
            return redirect(url_for('home'))

        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f"Database error occurred while adding book: {e}", "danger")

    authors = Author.query.all()
    return render_template('add_book.html', authors=authors)

@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    """
    Route to delete a book by its ID.
    If the associated author has no more books, deletes the author too.
    """
    try:
        book = Book.query.get_or_404(book_id)
        author = book.author

        db.session.delete(book)
        db.session.commit()
        flash(f"Book '{book.title}' deleted successfully!", 'success')

        if not author.books:
            db.session.delete(author)
            db.session.commit()
            flash(f"Author '{author.name}' also deleted because they had no more books.", 'info')

    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f"Database error occurred while deleting book: {e}", "danger")

    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
