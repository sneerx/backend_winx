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


app.config.from_object('config.config')
# API anahtarını doğrulayan bir middleware
def authenticate_api(func):
    def wrapper(*args, **kwargs):
        api_key = request.headers.get('API-Key')
        if api_key == app.config['API_KEY']:
            return func(*args, **kwargs)
        else:
            return jsonify({'error': 'Invalid API key'}), 401
    return wrapper



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
@authenticate_api
def get_films():
    # MongoDB'den tüm filmleri/dizileri al ve JSON formatında dön
    films = db['films'].find()
    result = []
    for film in films:
        result.append({
            'title': film['title'],
            'release_date': film['release_date'],
            'genre': film['genre']
            # ...
        })
    return jsonify(result)


#rastgele film açma // BU TAMAM.
@app.route('/api/films/random', methods=['GET'])
@authenticate_api
def get_random_film():
    film_cursor = db.films.aggregate([{ '$sample': { 'size': 1 } }])
    film = next(film_cursor, None)

    if film:
        film['_id'] = str(film['_id'])  # ObjectId'i stringe dönüştürme
        return jsonify(film)
    else:
        return jsonify({'message': 'No films found'})



#izleme listesi oluşturma
@app.route('/api/watchlist', methods=['POST'])
def create_watchlist():
    # İstekten gelen verileri al
    data = request.get_json()
    # MongoDB'ye izleme listesi ekleyin
    watchlist_id = db['watchlists'].insert_one(data).inserted_id
    return jsonify({'watchlist_id': str(watchlist_id)})

@app.route('/api/watchlist/<watchlist_id>', methods=['PUT'])
def update_watchlist(watchlist_id):
    # İstekten gelen verileri al
    data = request.get_json()
    # MongoDB'de izleme listesini güncelle
    db['watchlists'].update_one({'_id': ObjectId(watchlist_id)}, {'$set': data})
    return jsonify({'message': 'Watchlist updated'})




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



#Film detayları
@app.route('/api/films/<film_id>', methods=['GET'])
def get_film_details(film_id):
    film = db['films'].find_one({'_id': ObjectId(film_id)})
    if film:
        return jsonify(film)
    else:
        return jsonify({'message': 'Film not found'})




#üye olma
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']
    
    # Kullanıcının veritabanında mevcut olup olmadığını kontrol edin
    if db['users'].find_one({'username': username}):
        return jsonify({'message': 'Username already exists'})
    
    # Şifreyi hashleyin ve kullanıcıyı veritabanına kaydedin
    hashed_password = generate_password_hash(password, method='sha256')
    user_id = db['users'].insert_one({'username': username, 'password': hashed_password}).inserted_id
    
    return jsonify({'user_id': str(user_id), 'message': 'User registered successfully'})


# Kullanıcı girişi
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    
    # Kullanıcının veritabanında mevcut olup olmadığını kontrol edin
    user = db['users'].find_one({'username': username})
    if not user:
        return jsonify({'message': 'Invalid username'})
    
    # Şifreyi doğrulayın
    if not check_password_hash(user['password'], password):
        return jsonify({'message': 'Invalid password'})
    
    return jsonify({'message': 'Login successful'})


#Örnek korumalı bir rotaya erişim
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




#favorileri ekleme
@app.route('/api/favorites', methods=['POST'])
def add_to_favorites():
    # İstekten gelen verileri al
    data = request.get_json()
    # MongoDB'ye favorilere ekle
    db['favorites'].insert_one(data)
    return jsonify({'message': 'Added to favorites'})





#favorilerden çıkarma
@app.route('/api/favorites/<favorite_id>', methods=['DELETE'])
def remove_from_favorites(favorite_id):
    # MongoDB'de favoriyi sil
    db['favorites'].delete_one({'_id': ObjectId(favorite_id)})
    return jsonify({'message': 'Removed from favorites'})


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


#film/dizi ekleme
@app.route('/api/films', methods=['POST'])
def add_film():
    # İstekten gelen verileri al
    data = request.get_json()
    # MongoDB'ye film/dizi ekle
    film_id = db['films'].insert_one(data).inserted_id
    return jsonify({'film_id': str(film_id)})


#film/dizi güncelleme
@app.route('/api/films/<film_id>', methods=['PUT'])
def update_film(film_id):
    # İstekten gelen verileri al
    data = request.get_json()
    # MongoDB'de film/dizi güncelle
    db['films'].update_one({'_id': ObjectId(film_id)}, {'$set': data})
    return jsonify({'message': 'Film updated'})



#film/dizi silme

@app.route('/api/films/<film_id>', methods=['DELETE'])
def delete_film(film_id):
    # MongoDB'den film/dizi sil
    db['films'].delete_one({'_id': ObjectId(film_id)})
    return jsonify({'message': 'Film deleted'})


if __name__ == '__main__':
    app.run(debug=True)