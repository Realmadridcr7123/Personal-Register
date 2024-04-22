from flask import Flask, render_template, request, flash, redirect, url_for
from flask_migrate import Migrate, upgrade
from models import db, User, seed_data
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# Konfigurera databas-URI från miljövariabel
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URI_LOCAL")
# Alternativt: Använd en SQLite-databas direkt
# app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///name.db"

# Ange en hemlig nyckel för att hantera sessions
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Initiera databasen i applikationen
db.init_app(app)

# Initiera migrering för databasmodellerna
migrate = Migrate(app, db)

@app.route("/")
def home_page():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register_new_user():
    if request.method == "POST":
        # Hämta användarens information från formuläret
        name = request.form.get('name')
        age = request.form.get('age', type=int)
        email = request.form.get('email')
        username = request.form.get('username')
        phone = request.form.get('phone')
        country = request.form.get('country')

        # Kontrollera om e-post eller användarnamn redan existerar i databasen
        email_exist = User.query.filter_by(email=email).first()
        username_exist = User.query.filter_by(username=username).first()

        if email_exist or username_exist:
            # Visa meddelande om användarnamn eller e-post redan existerar
            flash('Username or email already exist!')
        else:
            # Skapa en ny användare och lägg till i databasen
            new_user = User(name=name, age=age, email=email, username=username, phone=phone, country=country)
            db.session.add(new_user)
            db.session.commit()
            # Visa bekräftelsemeddelande för att användaren har skapats
            flash('User created! Welcome!')
    
    return render_template('register_user.html')

@app.route("/allusers")
def all_users():
    # Hämta söktermen och sortering från URL-parametrar
    q = request.args.get('q', '')
    sort_column = request.args.get('sort_column', 'id')
    sort_order = request.args.get('sort_order', 'desc')
    page = request.args.get('page', 1, type=int)

    # Filtrera användare baserat på söktermen
    users = User.query.filter(
        User.name.like("%" + q + "%") |
        User.email.like("%" + q + "%") |
        User.age.like("%" + q + "%") |
        User.username.like("%" + q + "%") |
        User.phone.like("%" + q + "%")
    )

    # Ange vilken kolumn som ska sorteras och i vilken ordning
    if sort_column == 'name':
        sort_by = User.name
    elif sort_column == 'age':
        sort_by = User.age
    elif sort_column == 'username':
        sort_by = User.username
    elif sort_column == 'phone':
        sort_by = User.phone
    elif sort_column == 'email':
        sort_by = User.email
    elif sort_column == 'country':  
        sort_by = User.country
    else:
        sort_by = User.id

    # Välj sorteringsordning (stigande eller fallande)
    if sort_order == 'asc':
        sort_by = sort_by.asc()
    elif sort_order == 'desc':
        sort_by = sort_by.desc()
    
    # Sortera användare enligt vald kolumn och ordning
    users = users.order_by(sort_by)  

    # Paginera användare baserat på sidnummer och antal per sida
    pa_obj = users.paginate(page=page, per_page=10, error_out=True)

    return render_template(
        'users.html', 
        list_of_users=pa_obj.items, 
        q=q, 
        sort_order=sort_order, 
        sort_column=sort_column,
        pagination=pa_obj,
        page=page,
        nr_pages=pa_obj.pages,
        has_next=pa_obj.has_next,
        has_prev=pa_obj.has_prev
    )

@app.route("/user/<int:user_id>")
def user_page(user_id):
    # Hämta en användares detaljerade sida baserat på användar-ID
    user = User.query.filter_by(id=user_id).first()
    return render_template('user_page.html', user=user)

@app.route("/user/goto", methods=["GET", "POST"])
def goto_user():
    if request.method == "POST":
        # Hämta användar-ID från formuläret och omdirigera till användarens sida
        user_id = request.form.get('user_id', type=int)
        return redirect(url_for('user_page', user_id=user_id))
    return render_template('goto.html')

if __name__ == "__main__":
    # Uppgradera databasen och fyll med testdata
    with app.app_context():
        upgrade()
        seed_data()
    # Starta Flask-appen i debug-läge
    app.run(debug=True)
