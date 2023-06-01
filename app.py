from bson import ObjectId
from pymongo.mongo_client import MongoClient
from flask import Flask, jsonify, request
import random
from werkzeug.security import generate_password_hash, check_password_hash
from config.config import API_KEY

app = Flask(__name__)

uri = "mongodb+srv://riza:Ty8Z0E2GsDriWiRL@winx.xqlnqmm.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri)

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


# app.config.from_object('config.config')
# # API anahtarını doğrulayan bir middleware
# def authenticate_api(func):
#     def wrapper(*args, **kwargs):
#         api_key = request.headers.get('API-Key')
#         if api_key == app.config['API_KEY']:
#             return func(*args, **kwargs)
#         else:
#             return jsonify({'error': 'Invalid API key'}), 401
#     return wrapper



db = client['winx']

# collection = db['users']

# document = {"name": "John", "age": 30}
# collection.insert_one(document)

# documents = [
#     {"name": "Alice", "age": 25},
#     {"name": "Bob", "age": 35}
# ]
# collection.insert_many(documents)

# #bütün belgeyi getirmek
# cursor = collection.find()
# for document in cursor:
#     print(document)

# # Belirli bir belgeyi getirmek
# document = collection.find_one({"name": "John"})
# print(document)


#FİLMLERİ GETİRME
@app.route('/api/films', methods=['GET'])
#@authenticate_api
def get_films():
    # MongoDB'den tüm filmleri/dizileri al ve JSON formatında dön
    films = db['films'].find()
    result = []
    for film in films:
        result.append({
            '_id' : str(film['_id']),  # ObjectId'i str olarak dönüştür
            'title': film['title'],
            'overview' : film['overview'],
            'release_date': film['release_date'],
            'genre': film['genre'],
            'poster_path' : film['poster_path'],
            'backdrop_path' : film['backdrop_path'],
            'imdb_rating' : film['imdb_rating'],
            'duration' : film['duration'],
            'credits' : film['credits'],
            'type' : film['type'],
            'vote_average' : film['vote_average'],
            'vote_count' : film['vote_count']
            # ...
        })
    return jsonify(result)


#rastgele film açma // BU TAMAM.
@app.route('/api/films/random', methods=['GET'])
#@authenticate_api
def get_random_film():
    film_cursor = db.films.aggregate([{ '$sample': { 'size': 1 } }])
    film = next(film_cursor, None)

    if film:
        film['_id'] = str(film['_id'])  # ObjectId'i stringe dönüştürme
        return jsonify(film)
    else:
        return jsonify({'message': 'No films found'})




#arama
@app.route('/api/search', methods=['GET'])
def search_films():
    query = request.args.get('query')
    # MongoDB'de arama yap
    results = db['films'].find({'title': {'$regex': query, '$options': 'i'}})
    films = []
    for film in results:
        films.append({
            'title': film['title'],
            'release_date': film['release_date'],
            'genre': film['genre']
            # ...
        })
    return jsonify(films)


#popüler içerikler
@app.route('/api/popular', methods=['GET'])
def get_popular_films():
    # MongoDB'de popüler filmleri al (örneğin, en çok izlenen veya en yüksek puan alan)
    films = db['films'].find().sort('views', -1).limit(10)
    result = []
    for film in films:
        result.append({
            'title': film['title'],
            'release_date': film['release_date'],
            'genre': film['genre']
            # ...
        })
    return jsonify(result)




#BU TAMAM CALISIYOR
#BİR FİLM GETİR.
@app.route('/api/films/<film_id>', methods=['GET'])
def get_film_details(film_id):
    film = db['films'].find_one({'_id': ObjectId(film_id)})
    if film:
        film['_id'] = str(film['_id'])  # ObjectId'i str olarak dönüştür
        return jsonify(film)
    else:
        return jsonify({'message': 'Film not found'})
    
# #Film detayları
# @app.route('/api/films/<film_id>', methods=['GET'])
# def get_film_details(film_id):
#     film = db['films'].find_one({'_id': ObjectId(film_id)})
#     if film:
#         return jsonify(film)
#     else:
#         return jsonify({'message': 'Film not found'})



#bu tamam..
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data['name']
    surname = data['surname']
    e_mail = data['e_mail']
    birth_date = data['birth_date']
    username = data['username']
    password = data['password']
    
    # Kullanıcının veritabanında mevcut olup olmadığını kontrol edin
    if db['users'].find_one({'username': username}):
        return jsonify({'message': 'Username already exists', 'response': 404})
    #e-mail için kontrol olabilir..
    # Şifreyi hashleyin ve kullanıcıyı veritabanına kaydedin
    hashed_password = generate_password_hash(password, method='sha256')
    user_id = db['users'].insert_one({
        'name': name,
        'surname': surname,
        'e_mail': e_mail,
        'birth_date': birth_date,
        'username': username,
        'password': hashed_password
    }).inserted_id
    
    return jsonify({'user_id': str(user_id), 'message': 'User registered successfully', 'response': 200})


# Kullanıcı girişi BU TAMAM
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    #data['_id'] = str(data['_id'])
    
    # Kullanıcının veritabanında mevcut olup olmadığını kontrol edin
    user = db['users'].find_one({'username': username})
    if not user:
        return jsonify({'message': 'Invalid username','response':404})
    
    # Şifreyi doğrulayın
    if not check_password_hash(user['password'], password):
        return jsonify({'message': 'Invalid password','response':404})
    
    return jsonify({'message': 'Login successful','response':200})


#kullanıcı bulma
@app.route('/api/user/<user_id>', methods=['GET'])
def get_user(user_id):
    # Kullanıcıyı ID'ye göre bulun
    user = db['users'].find_one({'_id': ObjectId(user_id)})
    if user:
        return jsonify({
            'user_id': str(user['_id']),
            'username': user['username'],
            'name': user['name'],
            'surname': user['surname'],
            'e_mail': user['e_mail'],
            'birth_date': user['birth_date'],
            'message': 'User found',
            'response': 200
        })
    else:
        return jsonify({'message': 'User not found', 'response': 404})




#Örnek korumalı bir rotaya erişim ??
@app.route('/api/protected', methods=['GET'])
def protected():
    # Kullanıcının kimlik doğrulamasını kontrol edin
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Unauthorized'})
    
    # Token'ı kontrol edin ve kullanıcıyı doğrulayın
    # Burada daha güvenli bir kimlik doğrulama yöntemi kullanabilirsiniz (ör. JWT)
    # Örneği basit tutmak için token'ı doğrudan kullanıcı adı olarak kabul edelim
    username = token
    
    # Kullanıcının veritabanında mevcut olup olmadığını kontrol edin
    user = db['users'].find_one({'username': username})
    if not user:
        return jsonify({'message': 'Invalid user'})
    
    return jsonify({'message': 'Protected resource'})



#puanlama
@app.route('/api/rate', methods=['POST'])
def rate_film():
    # İstekten gelen verileri al
    data = request.get_json()
    # MongoDB'de filmi puanla
    db['ratings'].insert_one(data)
    return jsonify({'message': 'Film rated'})


#profil görüntüleme
@app.route('/api/profile/<user_id>', methods=['GET'])
def get_profile(user_id):
    user = db['users'].find_one({'_id': ObjectId(user_id)})
    if user:
        return jsonify(user)
    else:
        return jsonify({'message': 'User not found'})

#profil düzenleme
@app.route('/api/profile/<user_id>', methods=['PUT'])
def update_profile(user_id):
    # İstekten gelen verileri al
    data = request.get_json()
    # MongoDB'de kullanıcı profili güncelle
    db['users'].update_one({'_id': ObjectId(user_id)}, {'$set': data})
    return jsonify({'message': 'Profile updated'})


#kategorizasyon
@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = db['categories'].find()
    result = []
    for category in categories:
        result.append({
            'name': category['name'],
            'description': category['description']
            # ...
        })
    return jsonify(result)



#film/dizi ekleme    # BU tamam
@app.route('/api/films/', methods=['POST'])
def add_film():
    # İstekten gelen verileri al
    data = request.get_json()
    # MongoDB'ye film/dizi ekle
    film_id = db['films'].insert_one(data).inserted_id
    return jsonify({'film_id': str(film_id)})




#film/dizi güncelleme # bu tamam
@app.route('/api/films/<film_id>', methods=['PUT'])
def update_film(film_id):
    # İstekten gelen verileri al
    data = request.get_json()
    # MongoDB'de film/dizi güncelle
    db['films'].update_one({'_id': ObjectId(film_id)}, {'$set': data})
    return jsonify({'message': 'Film updated'})



#film/dizi silme # bu tamam
@app.route('/api/films/<film_id>', methods=['DELETE'])
def delete_film(film_id):
    # MongoDB'den film/dizi sil
    db['films'].delete_one({'_id': ObjectId(film_id)})
    return jsonify({'message': 'Film deleted'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)