from bson import ObjectId
from pymongo.mongo_client import MongoClient
from flask import Flask, jsonify, request
import random
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import timedelta

app = Flask(__name__)

uri = "mongodb+srv://riza:Ty8Z0E2GsDriWiRL@winx.xqlnqmm.mongodb.net/?retryWrites=true&w=majority"

app.config['JSON_AS_ASCII'] = False
# Create a new client and connect to the server
client = MongoClient(uri)

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)




db = client['winx']

#FİLMLERİ GETİRME
@app.route('/api/films', methods=['GET'])
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






@app.route('/api/ids/<ids>', methods=['GET'])
def get_films_by_ids(ids):
    film_ids = ids.split(',')  # Gelen parametreleri virgülle ayrıştır

    results = []
    for film_id in film_ids:
        film_id = ObjectId(film_id)
        film = db['films'].find_one({'_id': film_id})
        if film:
            result = {
                '_id': str(film['_id']),  # ObjectId'i str olarak dönüştür
                'title': film['title'],
                'overview': film['overview'],
                'release_date': film['release_date'],
                'genre': film['genre'],
                'poster_path': film['poster_path'],
                'backdrop_path': film['backdrop_path'],
                'imdb_rating': film['imdb_rating'],
                'duration': film['duration'],
                'credits': film['credits'],
                'type': film['type'],
                'vote_average': film['vote_average'],
                'vote_count': film['vote_count']
                # ...
            }
            results.append(result)

    return jsonify(results)



#TV_SHOWLARI GETİRME
@app.route('/api/tvshows', methods=['GET'])
def get_tvshows():
    tvshows = db['tvshows'].find()
    result = []
    for tvshow in tvshows:
        result.append({
            '_id': str(tvshow['_id']),
            'title': tvshow['title'],
            'overview': tvshow['overview'],
            'release_date': tvshow['release_date'],
            'genre': tvshow['genre'],
            'poster_path': tvshow['poster_path'],
            'backdrop_path': tvshow['backdrop_path'],
            'imdb_rating': tvshow['imdb_rating'],
            'duration': tvshow['duration'],
            'credits': tvshow['credits'],
            'vote_average': tvshow['vote_average'],
            'vote_count': tvshow['vote_count'],
            'number_of_seasons' : tvshow['number_of_seasons'],
            'number_of_episodes' : tvshow['number_of_episodes']
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


# TV şovu detaylarını getirme
@app.route('/api/tvshows/<tvshow_id>', methods=['GET'])
def get_tvshow_details(tvshow_id):
    tvshow = db['tvshows'].find_one({'_id': ObjectId(tvshow_id)})
    if tvshow:
        tvshow['_id'] = str(tvshow['_id'])
        return jsonify(tvshow)
    else:
        return jsonify({'message': 'TV show not found'})


# arama
@app.route('/api/search', methods=['GET'])
def search_films():
    query = request.args.get('query')
    # MongoDB'de arama yap
    results = db['films'].find({'title': {'$regex': query, '$options': 'i'}})
    films = []
    for film in results:
        films.append({
            #'title': film['title'],
            'release_date': film['release_date'],
            #'genre': film['genre']
            # ...
        })
    return jsonify(films)


#popüler içerikler / films
@app.route('/api/films/popular', methods=['GET'])
def get_popular_films():
    # MongoDB'de popüler filmleri al (örneğin, en çok izlenen veya en yüksek puan alan)
    films = db['films'].find().sort('release_date', -1).limit(3)
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
            
        })
    return jsonify(result)

#popüler içerikler / tvshows
@app.route('/api/tvshows/popular', methods=['GET'])
def get_popular_tvshows():
    # MongoDB'de popüler dizi al (örneğin, en çok izlenen veya en yüksek puan alan)
    tvshows = db['tvshows'].find().sort('release_date', -1).limit(3)
    result = []
    for tvshow in tvshows:
        result.append({
            '_id': str(tvshow['_id']),
            'title': tvshow['title'],
            'overview': tvshow['overview'],
            'release_date': tvshow['release_date'],
            'genre': tvshow['genre'],
            'poster_path': tvshow['poster_path'],
            'backdrop_path': tvshow['backdrop_path'],
            'imdb_rating': tvshow['imdb_rating'],
            'duration': tvshow['duration'],
            'credits': tvshow['credits'],
            'vote_average': tvshow['vote_average'],
            'vote_count': tvshow['vote_count'],
            'number_of_seasons' : tvshow['number_of_seasons'],
            'number_of_episodes' : tvshow['number_of_episodes']
            
        })
    return jsonify(result)

@app.route('/api/films/top', methods=['GET'])
def get_top_films():
    # IMDB puanına göre filmleri sıralama işlemi
    top_films = db['films'].find().sort('imdb_rating', -1)  # Yüksek puana göre sıralama
    films = []
    for film in top_films:
        films.append({
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
            
        })
    return jsonify(films)

from datetime import datetime

@app.route('/api/films/upcoming', methods=['GET'])
def get_upcoming_films():
    # Yaklaşan filmleri sıralama işlemi
    upcoming_films = db['films'].find({'release_date': {'$gte': datetime.today()}}).sort('release_date', 1)  # Tarihe göre sıralama
    films = []
    for film in upcoming_films:
        films.append({
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
        })
    return jsonify(films)

@app.route('/api/tvshows/top', methods=['GET'])
def get_top_tvshows():
    # IMDB puanına göre TV şovlarını sıralama işlemi
    top_tvshows = db['tvshows'].find().sort('imdb_rating', -1)  # Yüksek puana göre sıralama
    tvshows = []
    for tvshow in top_tvshows:
        tvshows.append({
            '_id': str(tvshow['_id']),
            'title': tvshow['title'],
            'overview': tvshow['overview'],
            'release_date': tvshow['release_date'],
            'genre': tvshow['genre'],
            'poster_path': tvshow['poster_path'],
            'backdrop_path': tvshow['backdrop_path'],
            'imdb_rating': tvshow['imdb_rating'],
            'duration': tvshow['duration'],
            'credits': tvshow['credits'],
            'vote_average': tvshow['vote_average'],
            'vote_count': tvshow['vote_count'],
            'number_of_seasons' : tvshow['number_of_seasons'],
            'number_of_episodes' : tvshow['number_of_episodes']
            
        })
    return jsonify(tvshows)

@app.route('/api/tvshows/upcoming', methods=['GET'])
def get_upcoming_tvshows():
    # Yaklaşan TV şovlarını sıralama işlemi
    upcoming_tvshows = db['tvshows'].find({'release_date': {'$gte': datetime.today()}}).sort('release_date', 1)  # Tarihe göre sıralama
    tvshows = []
    for tvshow in upcoming_tvshows:
        tvshows.append({
            '_id': str(tvshow['_id']),
            'title': tvshow['title'],
            'overview': tvshow['overview'],
            'release_date': tvshow['release_date'],
            'genre': tvshow['genre'],
            'poster_path': tvshow['poster_path'],
            'backdrop_path': tvshow['backdrop_path'],
            'imdb_rating': tvshow['imdb_rating'],
            'duration': tvshow['duration'],
            'credits': tvshow['credits'],
            'vote_average': tvshow['vote_average'],
            'vote_count': tvshow['vote_count'],
            'number_of_seasons' : tvshow['number_of_seasons'],
            'number_of_episodes' : tvshow['number_of_episodes']
        })
    return jsonify(tvshows)





# MongoDB session configuration
app.config['SECRET_KEY'] = '31'
app.config['SESSION_TYPE'] = 'mongodb'
app.config['SESSION_MONGODB'] = MongoClient(uri)
app.config['SESSION_MONGODB_DB'] = 'winx'
app.config['SESSION_MONGODB_COLLECTION'] = 'sessions'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        self.password = user_data['password']

    @staticmethod
    def get(user_id):
        user_data = db['users'].find_one({'_id': user_id})
        if user_data:
            return User(user_data)
        return None


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data['name']
    email = data['email']
    username = data['username']
    password = data['password']

    if db['users'].find_one({'username': username}):
        return jsonify({'message': 'Username already exists', 'response': 404})

    hashed_password = generate_password_hash(password, method='sha256')
    user_id = db['users'].insert_one({
        'name': name,
        'email': email,
        'username': username,
        'password': hashed_password
    }).inserted_id

    return jsonify({'user_id': str(user_id), 'message': 'User registered successfully', 'response': 200})


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    user = db['users'].find_one({'username': username})
    if not user:
        return jsonify({'message': 'Invalid username', 'response': 404})

    if not check_password_hash(user['password'], password):
        return jsonify({'message': 'Invalid password', 'response': 404})

    user_obj = User(user)
    login_user(user_obj)

    token = jwt.encode({'user_id': user_obj.id}, app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({'message': 'Login successful', 'token': token, 'response': 200})



@app.route('/api/logout', methods=['POST',"GET"])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logout successful', 'response': 200})





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
            'email': user['email'],
            'vote_contents': user['vote_contents'],
            'message': 'User found',
            'response': 200
        })
    else:
        return jsonify({'message': 'User not found', 'response': 404})

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

@app.route('/api/users', methods=['GET'])
def get_users():
    users = db['users'].find()
    user_list = []
    for user in users:
        user_data = {
            'id': str(user['_id']),
            'username': user['username']
        }
        user_list.append(user_data)
    return jsonify({'users': user_list, 'response': 200})


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


# TV şovu ekleme
@app.route('/api/tvshows/', methods=['POST'])
def add_tvshow():
    data = request.get_json()
    tvshow_id = db['tvshows'].insert_one(data).inserted_id
    return jsonify({'tvshow_id': str(tvshow_id)})

# TV şovu güncelleme
@app.route('/api/tvshows/<tvshow_id>', methods=['PUT'])
def update_tvshow(tvshow_id):
    # İstekten gelen verileri al
    data = request.get_json()
    # MongoDB'de TV şovunu güncelle
    db['tvshows'].update_one({'_id': ObjectId(tvshow_id)}, {'$set': data})
    return jsonify({'message': 'TV show updated'})

# TV şovu silme
@app.route('/api/tvshows/<tvshow_id>', methods=['DELETE'])
def delete_tvshow(tvshow_id):
    db['tvshows'].delete_one({'_id': ObjectId(tvshow_id)})
    return jsonify({'message': 'TV show deleted'})



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True,threaded = True)