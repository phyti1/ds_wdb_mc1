import pymysql
from app import app
import connector
from flask import jsonify
from flask import flash, request
from flaskext.mysql import MySQL


mysql = None

def init_flask(host, port, user, password, db):
    global mysql

    mysql = MySQL()
    app.config['MYSQL_DATABASE_HOST'] = host
    app.config['MYSQL_DATABASE_PORT'] = port
    app.config['MYSQL_DATABASE_USER'] = user
    app.config['MYSQL_DATABASE_PASSWORD'] = password
    app.config['MYSQL_DATABASE_DB'] = db
    mysql.init_app(app)
    
    return mysql

@app.errorhandler(404)
def showMessage(error=None):
    message = {
        'status': 404,
        'message': 'Record not found: ' + request.url,
    }
    respone = jsonify(message)
    respone.status_code = 404
    return respone


############################################################################################################
############################################# USER #########################################################
############################################################################################################

# get all users
@app.route('/user', methods=['GET'])
def get_users():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, name FROM user")
        users = cursor.fetchall()
        cursor.close() 
        conn.close() 
        respone = jsonify(users)
        respone.status_code = 200
        return respone
    except Exception as e:
        raise e

# get a specific user
@app.route('/user/<string:user_id>', methods=['GET'])
def get_specific_user(user_id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id, name FROM user WHERE user_id = %s", (user_id))
        user = cursor.fetchone()
        respone = jsonify(user)
        respone.status_code = 200
        return respone
    except Exception as e:
        raise e
    finally:
        cursor.close()
        conn.close()

# create a new user
@app.route('/user', methods=['POST'])
def create_user():
    try:
        _json = request.json
        _name = _json['name']
        if _name:
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            sqlQuery = "INSERT INTO user (name) VALUES(%s)"
            bindData = (_name)
            cursor.execute(sqlQuery, bindData)
            conn.commit()
            user_id = cursor.lastrowid
            response = jsonify(user_id)
            response.status_code = 200
            return response
        else:
            response = jsonify('Invalid request. Name is required.')
            response.status_code = 400
            return response
    except Exception as e:
        raise e
    finally:
        cursor.close()
        conn.close()

# update a user
@app.route('/user/<string:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        _json = request.json
        _name = _json['name']
        if _name:
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            sqlQuery = "UPDATE user SET name = %s WHERE user_id = %s"
            bindData = (_name, user_id)
            cursor.execute(sqlQuery, bindData)
            user = cursor.fetchall()
            conn.commit()
            respone = jsonify(user)
            respone.status_code = 200
            return respone
        else:
            response = jsonify('Invalid request. Name is required.')
            response.status_code = 400
            return response
    except Exception as e:
        raise e
    finally:
        cursor.close()
        conn.close()

# delete a user
@app.route('/user/<string:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user WHERE user_id =%s", (user_id))
        conn.commit()
        respone = jsonify('User deleted successfully!')
        respone.status_code = 200
        return respone
    except Exception as e:
        raise e
    finally:
        cursor.close()
        conn.close()

# get ratings of a specific user
@app.route('/user/<string:user_id>/ratings', methods=['GET'])
def get_ratings_from_user(user_id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT rating_id, movie_id, rating FROM rating WHERE user_id = %s", (user_id))
        ratings = cursor.fetchall()
        respone = jsonify(ratings)
        respone.status_code = 200
        return respone
    except Exception as e:
        raise e
    finally:
        cursor.close()
        conn.close()

# get all movies which a specific user rated
@app.route('/user/<string:user_id>/ratings/movies', methods=['GET'])
def get_movies_from_user(user_id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT movie_id, title, description, vote_average, vote_count, year FROM movies WHERE movie_id IN (SELECT movie_id FROM rating WHERE user_id = %s)", (user_id))
        ratings = cursor.fetchall()
        respone = jsonify(ratings)
        respone.status_code = 200
        return respone
    except Exception as e:
        raise e
    finally:
        cursor.close()
        conn.close()


############################################################################################################
############################################# MOVIE ########################################################
############################################################################################################

# get all movies matching params
@app.route('/movies', methods=['GET'])
def get_movies():
    try:
        args = request.args
        title = args.get('title')
        limit = args.get('limit')
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        sqlQuery = "SELECT movie_id, title, description, vote_average, vote_count, year FROM movies"
        bindData = []

        if title:
            sqlQuery += " WHERE title LIKE %s"
            bindData.append(title)

        if limit:
            sqlQuery += " LIMIT %s"
            bindData.append(limit)

        sqlQuery += " ORDER BY vote_average DESC"

        cursor.execute(sqlQuery, bindData)
        movies = cursor.fetchall()
        respone = jsonify(movies)
        respone.status_code = 200
        return respone
    except Exception as e:
        raise e
    finally:
        cursor.close()
        conn.close()

# get a specific movie
@app.route('/movie/<string:movie_id>', methods=['GET'])
def get_specific_movie(movie_id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT movie_id, title, description, vote_average, vote_count, year FROM user WHERE movie_id = %s", (movie_id))
        movie = cursor.fetchone()
        respone = jsonify(movie)
        respone.status_code = 200
        return respone
    except Exception as e:
        raise e
    finally:
        cursor.close()
        conn.close()

# create a new movie
@app.route('/movie', methods=['POST'])
def create_movie():
    try:
        _json = request.json
        _title = _json['title']
        _description = _json['description']
        _vote_average = _json['vote_average']
        _vote_count = _json['vote_count']
        _year = _json['year']

        if _title and _description and _vote_average and _vote_count and _year:
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            sqlQuery = "INSERT INTO movie (title, description, vote_average, vote_count, year) VALUES(%s)"
            bindData = (_title, _description, _vote_average, _vote_count, _year)
            cursor.execute(sqlQuery, bindData)
            conn.commit()
            movie_id = cursor.lastrowid
            response = jsonify(movie_id)
            response.status_code = 200
            return response
        else:
            response = jsonify('Invalid request. Title, description, vote_average, vote_count and year are required.')
            response.status_code = 400
            return response
    except Exception as e:
        raise e
    finally:
        cursor.close()
        conn.close()

# update a movie
@app.route('/movie/<string:movie_id>', methods=['PUT'])
def update_movie(movie_id):
    try:
        _json = request.json
        _title = _json['title']
        _description = _json['description']
        _vote_average = _json['vote_average']
        _vote_count = _json['vote_count']
        _year = _json['year']
        if _title and _description and _vote_average and _vote_count and _year:
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            sqlQuery = "UPDATE movie SET title = %s, description = %s, vote_average = %s, vote_count = %s, year = %s WHERE movie_id = %s"
            bindData = (_title, _description, _vote_average, _vote_count, _year, movie_id)
            cursor.execute(sqlQuery, bindData)
            user = cursor.fetchall()
            conn.commit()
            respone = jsonify(user)
            respone.status_code = 200
            return respone
        else:
            response = jsonify('Invalid request. Title, description, vote_average, vote_count and year are required.')
            response.status_code = 400
            return response
    except Exception as e:
        raise e
    finally:
        cursor.close()
        conn.close()

# delete a movie
@app.route('/movie/<string:movie_id>', methods=['DELETE'])
def delete_movie(movie_id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM movie WHERE movie_id = %s", (movie_id))
        conn.commit()
        respone = jsonify('Movie deleted successfully!')
        respone.status_code = 200
        return respone
    except Exception as e:
        raise e
    finally:
        cursor.close()
        conn.close()



if __name__ == "__main__":
    host, port, user, password, db = connector.get_credentials()
    init_flask(host, port, user, password, db)
    app.run()
