# app.py
from flask import Flask, render_template, request, redirect, url_for,flash
from data_models import db, Author, Book
from datetime import datetime
from flask_migrate import Migrate


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'AS98778998797SDSD79SD897DSSD879DS'
db.init_app(app)
migrate = Migrate(app, db)

# Home route to display all books
@app.route('/')
def home():
    search_query = request.args.get('search')
    if search_query:
        books = Book.query.filter(Book.title.ilike(f'%{search_query}%')).all()
        if not books:
            flash('No books found matching your search.')
    else:
        books = Book.query.all()
    return render_template('home.html', books=books)

# Route to add an author
@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        name = request.form['name']
        birth_date = datetime.strptime(request.form['birth_date'], '%Y-%m-%d')
        date_of_death = request.form.get('date_of_death', None)
        if date_of_death:
            date_of_death = datetime.strptime(date_of_death, '%Y-%m-%d')
        
        author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)
        db.session.add(author)
        db.session.commit()
        return redirect(url_for('add_author'))  # Redirect to the same page for another author
        
    return render_template('add_author.html')


# Route to add a book
@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        isbn = request.form['isbn']
        title = request.form['title']
        publication_year = request.form['publication_year']
        author_id = request.form['author_id']
        
        book = Book(isbn=isbn, title=title, publication_year=publication_year, author_id=author_id)
        db.session.add(book)
        db.session.commit()
        return redirect(url_for('home'))
    
    authors = Author.query.all()
    return render_template('add_book.html', authors=authors)

@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    author = book.author

    db.session.delete(book)
    db.session.commit()
    flash(f"Book '{book.title}' deleted successfully!", 'success')

    if not author.books:
        db.session.delete(author)
        db.session.commit()
        flash(f"Author '{author.name}' also deleted because they had no more books.", 'info')

    return redirect(url_for('home'))
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)