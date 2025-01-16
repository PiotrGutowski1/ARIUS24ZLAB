# -*- coding: utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from datetime import datetime, time

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Dozwolone przedmioty
DOZWOLONE_PRZEDMIOTY = ["matematyka", "fizyka", "chemia", "historia", "WoS", "biologia", "geografia"]

# Tabela nauczycieli
class Nauczyciel(db.Model):
    __tablename__ = 'nauczyciele'

    id_nauczyciela = db.Column(db.Integer, primary_key=True)
    imie = db.Column(db.String(50), nullable=False)
    nazwisko = db.Column(db.String(50), nullable=False)
    prowadzone_przedmioty = db.Column(db.String(255), nullable=False)  # Lista przedmiotów jako tekst oddzielony przecinkami
    opis = db.Column(db.Text)
    ocena_nauczyciela = db.Column(db.Float, nullable=False)
    numer_telefonu = db.Column(db.String(15), nullable=False)
    stawka = db.Column(db.Integer, nullable=False)
    waluta = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

    # Relacje
    lekcje = db.relationship('Lekcja', back_populates='nauczyciel', cascade='all, delete-orphan')
    kalendarz = db.relationship('KalendarzNauczyciela', back_populates='nauczyciel', cascade='all, delete-orphan')

    @validates('ocena_nauczyciela')
    def validate_ocena(self, key, value):
        """Walidacja wartości oceny nauczyciela (od 0.0 do 5.0)."""
        if value < 0.0 or value > 5.0:
            raise ValueError("Ocena nauczyciela musi być liczbą rzeczywistą z przedziału 0.0-5.0.")
        return value

    @validates('prowadzone_przedmioty')
    def validate_prowadzone_przedmioty(self, key, value):
        przedmioty = [p.strip() for p in value.split(',')]
        for przedmiot in przedmioty:
            if przedmiot not in DOZWOLONE_PRZEDMIOTY:
                raise ValueError(f"Nieprawidłowy przedmiot: {przedmiot}")
        return value

# Tabela studentów
class Student(db.Model):
    __tablename__ = 'studenci'

    id_studenta = db.Column(db.Integer, primary_key=True)
    imie = db.Column(db.String(50), nullable=False)
    nazwisko = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

    # Relacje
    lekcje = db.relationship('Lekcja', back_populates='student', cascade='all, delete-orphan')

# Tabela lekcji
class Lekcja(db.Model):
    __tablename__ = 'lekcje'

    id_lekcji = db.Column(db.Integer, primary_key=True)
    id_nauczyciela = db.Column(db.Integer, db.ForeignKey('nauczyciele.id_nauczyciela'), nullable=False)
    id_studenta = db.Column(db.Integer, db.ForeignKey('studenci.id_studenta'), nullable=False)
    id_przedmiotu = db.Column(db.Integer, db.ForeignKey('lista_przedmiotow.id'), nullable=False)
    data_lekcji = db.Column(db.Date, nullable=False)

    # Relacje
    nauczyciel = db.relationship('Nauczyciel', back_populates='lekcje')
    student = db.relationship('Student', back_populates='lekcje')
    przedmiot = db.relationship('Przedmiot', back_populates='lekcje')

# Tabela kalendarza nauczycieli
class KalendarzNauczyciela(db.Model):
    __tablename__ = 'kalendarz_nauczycieli'

    id = db.Column(db.Integer, primary_key=True)
    id_nauczyciela = db.Column(db.Integer, db.ForeignKey('nauczyciele.id_nauczyciela'), nullable=False)
    dostepny_od = db.Column(db.Time, nullable=False)
    dostepny_do = db.Column(db.Time, nullable=False)

    # Relacje
    nauczyciel = db.relationship('Nauczyciel', back_populates='kalendarz')

# Tabela listy przedmiotów
class Przedmiot(db.Model):
    __tablename__ = 'lista_przedmiotow'

    id = db.Column(db.Integer, primary_key=True)
    nazwa_przedmiotu = db.Column(db.String(50), nullable=False, unique=True)

    # Relacje
    lekcje = db.relationship('Lekcja', back_populates='przedmiot', cascade='all, delete-orphan')

    @validates('nazwa_przedmiotu')
    def validate_nazwa_przedmiotu(self, key, value):
        if value not in DOZWOLONE_PRZEDMIOTY:
            raise ValueError(f"Nieprawidłowy przedmiot: {value}")
        return value

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Baza danych została zainicjalizowana.")
def populate_data():
    with app.app_context():
        db.drop_all()
        db.create_all()
        # Dodawanie przedmiotów
        przedmioty = ["matematyka", "fizyka", "chemia", "historia", "biologia"]
        for nazwa in przedmioty:
            # Sprawdzenie, czy przedmiot już istnieje
            if not db.session.query(Przedmiot).filter_by(nazwa_przedmiotu=nazwa).first():
                db.session.add(Przedmiot(nazwa_przedmiotu=nazwa))
            else:
                print(f"Przedmiot '{nazwa}' już istnieje.")
        db.session.commit()

        # Dodawanie nauczycieli
        nauczyciele = [
            Nauczyciel(imie="Jan", nazwisko="Kowalski", prowadzone_przedmioty="matematyka,fizyka", opis="Specjalista w naukach ścisłych", ocena_nauczyciela=4.8, numer_telefonu="123456789", stawka=50, waluta="PLN", email="jan.kowalski@example.com"),
            Nauczyciel(imie="Anna", nazwisko="Nowak", prowadzone_przedmioty="chemia,biologia", opis="Pasja do nauczania", ocena_nauczyciela=4.5, numer_telefonu="987654321", stawka=60, waluta="PLN", email="anna.nowak@example.com"),
            Nauczyciel(imie="Piotr", nazwisko="Zieliński", prowadzone_przedmioty="historia", opis="Historyk z powołania", ocena_nauczyciela=4.7, numer_telefonu="456789123", stawka=45, waluta="PLN", email="piotr.zielinski@example.com"),
            Nauczyciel(imie="Katarzyna", nazwisko="Wiśniewska", prowadzone_przedmioty="matematyka,biologia", opis="Entuzjastka matematyki i biologii", ocena_nauczyciela=4.9, numer_telefonu="321654987", stawka=55, waluta="PLN", email="katarzyna.wisniewska@example.com"),
            Nauczyciel(imie="Michał", nazwisko="Lewandowski", prowadzone_przedmioty="fizyka,chemia", opis="Zrozumienie to klucz", ocena_nauczyciela=4.6, numer_telefonu="789123456", stawka=65, waluta="PLN", email="michal.lewandowski@example.com"),
        ]
        db.session.add_all(nauczyciele)
        db.session.commit()

        # Dodawanie studentów
        studenci = [
            Student(imie="Oliwia", nazwisko="Kwiatkowska", email="oliwia.kwiatkowska@example.com"),
            Student(imie="Jakub", nazwisko="Kamiński", email="jakub.kaminski@example.com"),
            Student(imie="Zuzanna", nazwisko="Wójcik", email="zuzanna.wojcik@example.com"),
        ]
        db.session.add_all(studenci)
        db.session.commit()

        # Dodawanie kalendarzy nauczycieli
        grafiki = [
            (1, time(9, 0), time(17, 0)),
            (2, time(8, 0), time(16, 0)),
            (3, time(14, 0), time(20, 0)),
            (4, time(8, 0), time(13, 0)),
        ]
        for id_nauczyciela, od, do in grafiki:
            db.session.add(KalendarzNauczyciela(id_nauczyciela=id_nauczyciela, dostepny_od=od, dostepny_do=do))

        db.session.commit()

        # Dodawanie lekcji
        lekcje = [
            (5, 2, 1, datetime(2024, 12, 4)),
            (5, 2, 2, datetime(2024, 12, 9)),
            (1, 1, 1, datetime(2024, 12, 9)),
            (1, 1, 2, datetime(2024, 12, 9)),
            (1, 1, 1, datetime(2024, 12, 10)),
            (3, 2, 2, datetime(2024, 12, 10)),
            (1, 4, 2, datetime(2024, 12, 10)),
            (5, 2, 2, datetime(2024, 12, 11)),
            (3, 2, 2, datetime(2024, 12, 11)),
            (2, 5, 1, datetime(2024, 12, 12)),
            (4, 3, 2, datetime(2024, 12, 12)),
            (1, 1, 2, datetime(2024, 12, 13)),
            (5, 4, 1, datetime(2024, 12, 14)),
            (1, 4, 3, datetime(2024, 12, 14)),
            (1, 4, 2, datetime(2024, 12, 14)),
            (5, 4, 2, datetime(2024, 12, 16)),
        ]
        for id_przedmiotu, id_nauczyciela, id_studenta, data in lekcje:
            db.session.add(Lekcja(id_przedmiotu=id_przedmiotu, id_nauczyciela=id_nauczyciela, id_studenta=id_studenta, data_lekcji=data))

        db.session.commit()

populate_data()

# Funkcje
from sqlalchemy import func

from sqlalchemy import func

def f1():
    with app.app_context():
        query = db.session.query(Lekcja.id_studenta).\
            join(KalendarzNauczyciela, KalendarzNauczyciela.id_nauczyciela == Lekcja.id_nauczyciela).\
            filter(KalendarzNauczyciela.dostepny_od <= time(17, 0)).\
            join(Student, Student.id_studenta == Lekcja.id_studenta).\
            filter(func.strftime('%w', Lekcja.data_lekcji) <= '4').\
            distinct()

        print(f"Liczba studentów w dni powszednie: {query.count()}")



def f2():
    with app.app_context():
        query = db.session.query(Lekcja.id_nauczyciela).\
            filter(func.strftime('%w', Lekcja.data_lekcji).in_(['6', '7'])).\
            distinct()
        print(f"Liczba nauczycieli z lekcjami w weekendy: {query.count()}")


def f3():
    with app.app_context():
        query = db.session.query(
            Lekcja.id_studenta,
            db.func.count(Lekcja.id_lekcji).label('count')
        ).group_by(Lekcja.id_studenta).order_by(db.desc('count')).first()

        if query:
            student_id = query[0]
            liczba_lekcji = query[1]

            student = db.session.get(Student, student_id)

            if student:
                print(f"Student z największą liczbą lekcji ({liczba_lekcji} lekcji):")
                print(f"Imię: {student.imie}")
                print(f"Nazwisko: {student.nazwisko}")
                print(f"Adres email: {student.email}")
            else:
                print("Nie znaleziono studenta.")
        else:
            print("Brak studentów w bazie danych.")



def f4():
    with app.app_context():
        query = db.session.query(Przedmiot.nazwa_przedmiotu, db.func.count(Lekcja.id_lekcji).label('count')).\
            join(Lekcja).\
            group_by(Przedmiot.id).\
            order_by(db.desc('count')).first()
        print(f"Najczęściej wybierany przedmiot: {query[0]} ({query[1]} lekcji)")

def f5():
    with app.app_context():
        query = db.session.query(Lekcja).join(Przedmiot).filter(Przedmiot.nazwa_przedmiotu == "matematyka").count()
        print(f"Liczba lekcji z matematyki: {query}")

def f6():
    with app.app_context():
        query = db.session.query(Lekcja).filter(func.strftime('%w', Lekcja.data_lekcji) == '3').count()
        print(f"Liczba lekcji w środy: {query}")


from datetime import datetime

from datetime import date

def f7(id_nauczyciela, dzien):
    with app.app_context():
        if isinstance(dzien, datetime):
            dzien = dzien.date()

        query = db.session.query(Lekcja).filter(
            Lekcja.id_nauczyciela == id_nauczyciela,
            Lekcja.data_lekcji == dzien
        ).all()

        if query:
            print(f"Lekcje dla nauczyciela {id_nauczyciela} w dniu {dzien}:")
            for lekcja in query:
                print(f" - Lekcja ID: {lekcja.id_lekcji}, Przedmiot: {lekcja.przedmiot.nazwa_przedmiotu}, Student ID: {lekcja.id_studenta}")
        else:
            print(f"Brak lekcji dla nauczyciela {id_nauczyciela} w dniu {dzien}.")


with app.app_context():
    f1()
    f2()
    f3()
    f4()
    f5()
    f6()
    f7(4, date(2024, 12, 14))
