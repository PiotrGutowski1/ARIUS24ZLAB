from flask import Flask, jsonify, request
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
    prowadzone_przedmioty = db.Column(db.String(255), nullable=False)
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


    lekcje = db.relationship('Lekcja', back_populates='student', cascade='all, delete-orphan')

class Lekcja(db.Model):
    __tablename__ = 'lekcje'

    id_lekcji = db.Column(db.Integer, primary_key=True)
    id_nauczyciela = db.Column(db.Integer, db.ForeignKey('nauczyciele.id_nauczyciela'), nullable=False)
    id_studenta = db.Column(db.Integer, db.ForeignKey('studenci.id_studenta'), nullable=False)
    id_przedmiotu = db.Column(db.Integer, db.ForeignKey('lista_przedmiotow.id'), nullable=False)
    data_lekcji = db.Column(db.DateTime, nullable=False)

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
        db.drop_all()
        db.create_all()
        print("Baza danych została zainicjalizowana.")
def populate_data():
    with app.app_context():
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
            Nauczyciel(imie="Piotr", nazwisko="Zielinski", prowadzone_przedmioty="historia", opis="Historyk z powołania", ocena_nauczyciela=4.7, numer_telefonu="456789123", stawka=45, waluta="PLN", email="piotr.zielinski@example.com"),
            Nauczyciel(imie="Katarzyna", nazwisko="Wisniewska", prowadzone_przedmioty="matematyka,biologia", opis="Entuzjastka matematyki i biologii", ocena_nauczyciela=4.9, numer_telefonu="321654987", stawka=55, waluta="PLN", email="katarzyna.wisniewska@example.com"),
            Nauczyciel(imie="Tadeusz", nazwisko="Lewandowski", prowadzone_przedmioty="fizyka,chemia", opis="Zrozumienie to klucz", ocena_nauczyciela=4.6, numer_telefonu="789123456", stawka=65, waluta="PLN", email="michal.lewandowski@example.com"),
        ]
        db.session.add_all(nauczyciele)
        db.session.commit()

        # Dodawanie studentów
        studenci = [
            Student(imie="Oliwia", nazwisko="Kwiatkowska", email="oliwia.kwiatkowska@example.com"),
            Student(imie="Jakub", nazwisko="Kaminski", email="jakub.kaminski@example.com"),
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
            (5, 2, 1, datetime(2024, 12, 4, 10, 0)),  
            (5, 2, 2, datetime(2024, 12, 9, 11, 0)),
            (1, 1, 1, datetime(2024, 12, 9, 12, 0)),
            (1, 1, 2, datetime(2024, 12, 9, 13, 0)),
            (1, 1, 1, datetime(2024, 12, 10, 14, 0)),
            (3, 2, 2, datetime(2024, 12, 10, 15, 0)),
            (1, 4, 2, datetime(2024, 12, 10, 16, 0)),
            (5, 2, 2, datetime(2024, 12, 11, 10, 0)),
            (3, 2, 2, datetime(2024, 12, 11, 11, 0)),
            (2, 5, 1, datetime(2024, 12, 12, 12, 0)),
            (4, 3, 2, datetime(2024, 12, 12, 13, 0)),
            (1, 1, 2, datetime(2024, 12, 13, 14, 0)),
            (5, 4, 1, datetime(2024, 12, 14, 15, 0)),
            (1, 4, 3, datetime(2024, 12, 14, 16, 0)),
            (1, 4, 2, datetime(2024, 12, 14, 17, 0)),
            (5, 4, 2, datetime(2024, 12, 16, 18, 0)),
        ]
        for id_przedmiotu, id_nauczyciela, id_studenta, data in lekcje:
            db.session.add(Lekcja(id_przedmiotu=id_przedmiotu, id_nauczyciela=id_nauczyciela, id_studenta=id_studenta, data_lekcji=data))

        db.session.commit()


populate_data()



# 1. Lista nauczycieli
@app.route('/teacher-list', methods=['GET'])
def get_teacher_list():
    nauczyciele = Nauczyciel.query.all()
    response = [
        {
            'id_nauczyciela': nauczyciel.id_nauczyciela,
            'imie': nauczyciel.imie,
            'nazwisko': nauczyciel.nazwisko,
            'przedmioty': nauczyciel.prowadzone_przedmioty
        }
        for nauczyciel in nauczyciele
    ]
    return jsonify(response), 200

# 2. Szczegóły nauczyciela
@app.route('/teacher-details/<int:id_nauczyciela>', methods=['GET'])
def get_teacher_details(id_nauczyciela):
    nauczyciel = Nauczyciel.query.filter_by(id_nauczyciela=id_nauczyciela).first()
    if not nauczyciel:
        return jsonify({'error': 'Nie znaleziono nauczyciela'}), 404

    response = {
        'id_nauczyciela': nauczyciel.id_nauczyciela,
        'imie': nauczyciel.imie,
        'nazwisko': nauczyciel.nazwisko,
        'opis': nauczyciel.opis,
        'przedmioty': nauczyciel.prowadzone_przedmioty,
        'ocena': nauczyciel.ocena_nauczyciela,
        'numer_telefonu': nauczyciel.numer_telefonu,
        'stawka': nauczyciel.stawka,
        'waluta': nauczyciel.waluta,
        'email': nauczyciel.email
    }
    return jsonify(response), 200


# 3. Zarezerwowanie lekcji
@app.route("/book-lesson", methods=["POST"])
def book_lesson():
    """Endpoint do rezerwowania lekcji.
    Sprawdza, czy wybrana data i godzina są dostępne."""
    data = request.get_json()

    # Pobieranie parametrów
    id_studenta = data.get("id_studenta")
    id_nauczyciela = data.get("id_nauczyciela")
    data_lekcji = data.get("data_lekcji") 

    # Walidacja parametrów
    if not all([id_studenta, id_nauczyciela, data_lekcji]):
        return jsonify({"error": "Brak wymaganych parametrów"}), 400

    try:
        # Konwersja daty i godziny
        data_lekcji = datetime.strptime(data_lekcji, "%Y-%m-%d %H:%M")
    except ValueError:
        return jsonify({"error": "Nieprawidłowy format daty i godziny"}), 400

    # Sprawdzenie, czy termin jest już zajęty
    zajeta_lekcja = Lekcja.query.filter_by(
        id_nauczyciela=id_nauczyciela,
        data_lekcji=data_lekcji
    ).first()

    if zajeta_lekcja:
        return jsonify({"error": "Termin jest już zajęty"}), 409

    # Dodanie nowej lekcji
    nowa_lekcja = Lekcja(
        id_nauczyciela=id_nauczyciela,
        id_studenta=id_studenta,
        id_przedmiotu=1,  
        data_lekcji=data_lekcji
    )
    db.session.add(nowa_lekcja)
    db.session.commit()

    return jsonify({"message": "Lekcja została zarezerwowana"}), 201


# 4. Dodawanie nauczyciela
@app.route('/add-teacher', methods=['POST'])
def add_teacher():
    data = request.get_json()

    required_fields = ['imie', 'nazwisko', 'prowadzone_przedmioty', 'opis', 'ocena_nauczyciela','numer_telefonu','stawka', 'waluta', 'email', 'id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f"Brak wymaganego pola: {field}"}), 400

    # Pobranie istniejącego kalendarza
    kalendarz = KalendarzNauczyciela.query.get(data['id'])
    if not kalendarz:
        return jsonify({'error': 'Nie znaleziono kalendarza o podanym id'}), 404

    # Tworzenie nowego nauczyciela
    nowy_nauczyciel = Nauczyciel(
        imie=data['imie'],
        nazwisko=data['nazwisko'],
        prowadzone_przedmioty=data['prowadzone_przedmioty'],
        opis=data['opis'],
        ocena_nauczyciela=data['ocena_nauczyciela'], 
        numer_telefonu=data['numer_telefonu'],
        stawka=data['stawka'],
        waluta=data['waluta'],
        email=data['email']
    )

    # Powiązanie nauczyciela z kalendarzem
    kalendarz.nauczyciel = nowy_nauczyciel

    # Zapis do bazy danych
    db.session.add(nowy_nauczyciel)
    db.session.commit()

    return jsonify({
        'message': 'Nauczyciel został dodany',
        'id_nauczyciela': nowy_nauczyciel.id_nauczyciela
    }), 201


#5. Pobranie informacji o lekcjach studenta w danym przedziale
@app.route("/get-lessons", methods=["GET"])
def get_lessons():
    # Pobranie parametrów z zapytania
    id_studenta = request.args.get("id_studenta", type=int)
    data_poczatkowa = request.args.get("data_początkowa")
    data_koncowa = request.args.get("data_końcowa")

    # Walidacja wymaganych parametrów
    if not id_studenta or not data_poczatkowa or not data_koncowa:
        return "", 400  # Zwraca pustą odpowiedź z kodem 400 (Bad Request)

    try:
        # Konwersja dat na obiekt datetime
        data_poczatkowa = datetime.strptime(data_poczatkowa, "%Y-%m-%d %H:%M")
        data_koncowa = datetime.strptime(data_koncowa, "%Y-%m-%d %H:%M")
    except ValueError:
        return "", 400  # Błąd parsowania daty, zwraca pustą odpowiedź

    # Sprawdzenie, czy student istnieje
    student = Student.query.get(id_studenta)
    if not student:
        return "", 404  # Brak studenta, zwraca pustą odpowiedź z kodem 404 (Not Found)

    # Pobieranie lekcji dla studenta w danym przedziale czasowym
    lekcje = (
        Lekcja.query
        .filter(Lekcja.id_studenta == id_studenta)
        .filter(Lekcja.data_lekcji >= data_poczatkowa)
        .filter(Lekcja.data_lekcji <= data_koncowa)
        .all()
    )

    # Jeśli brak wyników, zwracamy pustą odpowiedź z kodem 200
    if not lekcje:
        return "", 200

    # Konwersja wyników na JSON
    lekcje_json = [
        {
            "id_lekcji": lekcja.id_lekcji,
            "id_nauczyciela": lekcja.id_nauczyciela,
            "imie nauczyciela": lekcja.nauczyciel.imie,
            "nazwisko nauczyciela": lekcja.nauczyciel.nazwisko,
            "id_studenta": lekcja.id_studenta,
            "data_lekcji": lekcja.data_lekcji.strftime("%Y-%m-%d %H:%M"),
            "id_przedmiotu": lekcja.id_przedmiotu,
            "przedmiotu": lekcja.przedmiot.nazwa_przedmiotu
        }
        for lekcja in lekcje
    ]

    return jsonify(lekcje_json), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
