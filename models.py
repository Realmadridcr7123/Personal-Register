from flask_sqlalchemy import SQLAlchemy
from faker import Faker
import random

# Skapa en SQLAlchemy-instans för att hantera databasanslutning och modellhantering
db = SQLAlchemy()

# Skapa en användarmodell som ärver från db.Model
class User(db.Model):
    # Definiera kolumnerna i användartabellen
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    email = db.Column(db.String(128), unique=True)
    username = db.Column(db.String(128), unique=True)
    phone = db.Column(db.String(128))
    country = db.Column(db.String(100))

# Funktion för att fylla databasen med testdata
def seed_data():
    # Skapa en Faker-instans för att generera falsk data
    faker = Faker()
    # Loopa tills det finns minst 100 användare i databasen
    while User.query.count() < 100:
        # Generera slumpmässig data för varje användare
        new_name = faker.name()
        new_age = random.randint(20, 80)
        new_email = faker.email()
        new_username = faker.user_name()
        new_phone = str(random.randint(10000000, 99999999))
        new_country = faker.country() 
        
        # Skapa en ny användare med den genererade datan
        new_user = User(name=new_name, age=new_age, email=new_email, username=new_username, phone=new_phone, country=new_country)
        # Lägg till den nya användaren i sessionen för databasen
        db.session.add(new_user)
        # Utför commit för att spara ändringar i databasen
        db.session.commit()
