import pymongo
from flask import Flask, request, Response, render_template, redirect, url_for
import json
from pymongo import MongoClient
from bson import Binary, Code
from bson.json_util import dumps

#client = MongoClient('localhost:27017')
client = MongoClient('mongodb', 27017)
db = client['movieFlixDB']
usersCollection = db['Users']
moviesCollection = db['Movies']

app = Flask(__name__)
loggedUser = {'name':'none','pass':'none','email':'none','category':'none'}


"""

Users & access controll V

"""
@app.route('/api/register', methods=['POST'])
def register_user():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    if name and password and email:
        exists = usersCollection.find_one({"email": email})
        if exists:
            data = {'info':f'A user with the email: {email} already exists'}
            js = json.dumps(data)
            return Response(js, status=405)
        else:
            if usersCollection.insert_one({'name':name, 'pass':password, 'email':email, 'category':'user'}):
                return redirect(url_for('login'))
            else:
                data = {'info':'Internal Server Error'}
                js = json.dumps(data)
                return Response(js, status=500)
    else:
        data = {'info':'Please provide a valid name, password and email in order to register'}
        js = json.dumps(data)
        return Response(js, status=400)


@app.route('/api/login', methods=['POST'])
def login_user():
    email = request.form['email']
    password = request.form['password']
    user = usersCollection.find_one({"email": email})
    global loggedUser 
    if user:
        if user['pass'] == password:
            loggedUser = user
            data = {'info':f"Welcone {loggedUser['name']}, Category: {loggedUser['category']}"}
            js = json.dumps(data)
            #return Response(js, status=200)
            return redirect(url_for('home'))
        else:
            data = {'info':'Wrong password, please try again'}
            js = json.dumps(data)
            return Response(js, status=401)
        
    else:
        data = {'info':'User not found. Try to register /register'}
        js = json.dumps(data)
        return Response(js, status=404)


@app.route('/api/logout')
def user_logout():
    global loggedUser
    loggedUser = {'name':'none','pass':'none','email':'none','category':'none'}
    return redirect(url_for('login'))

@app.route('/api/user/delete',methods=['GET'])
def delete_user():
    global loggedUser
    loggedUser = {'name':'none','pass':'none','email':'none','category':'none'}
    if usersCollection.delete_one({'email': loggedUser['email']}):
        return redirect(url_for('login'))
    else:
        return Response(json.dumps({'info':'Internal Server Error'}), status=500)


"""

User controlls by ADMINS V

"""

@app.route('/api/admin/change_category', methods=['UPDATE'])
def change_category():
    global loggedUser
    if loggedUser['category'] == 'admin':
        email = request.form['email']
        user = usersCollection.find_one({"email": email})
        if user:
            if usersCollection.update_one({'email': email}, {'$set':{'category': 'admin'}}):
                return Response(json.dumps({'info':'User elevated to admin'}), status=200)
            else:
                return Response(json.dumps({'info':'Internal Server Error'}), status=500)
        else:   
            return Response(json.dumps({'info':'User not found.'}), status=404)
    else:
        return Response(json.dumps({"info":"Only admins have access"}), status=403)

@app.route('/api/admin/delete_user', methods=['DELETE'])
def admin_delete_user():
    global loggedUser
    if loggedUser['category'] == 'admin':
        email = request.form['email']
        user = usersCollection.find_one({"email": email})
        if user:
            if user['category'] == 'admin':
                return Response(json.dumps({"info":"Admin accounts can't be deleted"}), status=405)
            else:
                if usersCollection.delete_one({'email': email}):
                    return Response(json.dumps({'info': 'User has been deleted'}), status=200)
                else:
                    return Response(json.dumps({'info':'Internal Server Error'}), status=500)
        else:   
            return Response(json.dumps({'info':'User not found.'}), status=404)
    else:
        return Response(json.dumps({"info":"Only admins have access"}), status=403)

"""

Movie controlls by ADMINS V

"""
@app.route('/api/admin/add_movie', methods=['POST'])
def add_movie():
    global loggedUser
    if loggedUser['category'] == 'admin':
        try:
            data = json.loads(request.form['data'])
        except:
            return Response(json.dumps({'info':'Please provide at least a title and an actor(actors) in a json format'}), status=400)
        if ("title" in data) and ("actors" in data):
            if not("year" in data):
                data["year"] = 0
            if moviesCollection.insert_one(data):
                return Response(json.dumps({'info': 'Movie has been added!'}), status=200)
            else:
                return Response(json.dumps({'info':'Internal Server Error'}), status=500)
        else:
            return Response(json.dumps({'info':'Please provide at least a title and an actor(actors)'}), status=400)
    else:
        return Response(json.dumps({"info":"Only admins have access"}), status=403)

@app.route('/api/admin/delete_movie', methods=['DELETE'])
def delete_movie():
    global loggedUser
    if loggedUser['category'] == 'admin':
        title = request.form['title']
        if title:
            movie = moviesCollection.find_one({"year": {"$exists": "true"}, "$and": [{"title": title}]}, sort = [('year', 1)])
            print(movie)
            if movie:
                if moviesCollection.delete_one({'title': title, 'year': movie['year']}):
                    return Response(json.dumps({'info': 'Movie has been deleted!'}), status=200)
                else:
                    return Response(json.dumps({'info':'Internal Server Error'}), status=500)
            else:
                return Response(json.dumps({'info':f'There is no movie with the title {title}'}), status=404)  
        else:
            return Response(json.dumps({'info':'Please provide at a title'}), status=400)
    else:
        return Response(json.dumps({"info":"Only admins have access"}), status=403)
#UPDATE a movie
#Post request with a json containing all the values to be changed an a current-title (the movie to title we want to update)
@app.route('/api/admin/update_movie', methods=['UPDATE'])
def update_movie():
    global loggedUser
    if loggedUser['category'] == 'admin':
        try:
            data = json.loads(request.form['data'])
        except:
            return Response(json.dumps({'info':'Please provide at least a current-title'}), status=400)
        if data['current-title']:
            title = data['current-title']
            if moviesCollection.find_one({'title': title}):
                del data['current-title']
                if moviesCollection.update_one({'title': title}, {'$set': data}):
                    return Response(json.dumps({'info': 'Movie has been Updated!'}), status=200)
                else:
                    return Response(json.dumps({'info':'Internal Server Error'}), status=500)
            else:
                return Response(json.dumps({'info':f'There is no movie with the title {title}'}), status=404)  
        else:
            return Response(json.dumps({'info':'Please provide a current-title'}), status=400)
    else:
        return Response(json.dumps({"info":"Only admins have access"}), status=403)

@app.route('/api/admin/delete_comment', methods=['DELETE'])
def admin_delete_comment():
    global loggedUser
    if loggedUser['category'] == 'admin':
        title = request.form['title']
        email = request.form['email']
        movie = moviesCollection.find_one({'title': title})
        if moviesCollection.update({'_id': movie['_id']}, {'$pull': {'comments':{'email': email}}}) :
            if usersCollection.update({'email': email}, {'$pull': {'comments':{'title': title}}}):
                return Response(json.dumps({'info': 'comment has been deleted!'}), status=200)
            else:
                return Response(json.dumps({'info':'Internal Server Error'}), status=500)
        else:
            return Response(json.dumps({'info':'Internal Server Error'}), status=500)
    else:
        return Response(json.dumps({"info":"Only admins have access"}), status=403)

"""

All the user actions V

"""
@app.route('/api/movie/search', methods=['GET'])
def movie_search():
    global loggedUser
    if loggedUser['category'] != 'none':
        title = request.args.get('title')
        year = request.args.get('year')
        actor = request.args.get('actor')
        movies = ''
        if title:
            movies = moviesCollection.find({'title': title})
        elif year:
            movies = moviesCollection.find({'year': int(year)})
        elif actor:
            movies = moviesCollection.find({'actors': {'$all': [actor]}})
        if movies != '' and movies.count() != 0:
            return Response(dumps(movies), status=200)
        else:
            return Response(json.dumps({"info":"No results"}), status=404)
    else:
        return Response(json.dumps({"info":"Login in to view this page"}), status=403)

@app.route('/api/movie/add_rating', methods=['POST'])
def add_rating():
    global loggedUser
    if loggedUser['category'] != 'none':
        title = request.form['title']
        rating = request.form['rating']
        if title and rating:
            if moviesCollection.update_one({'title': title}, {'$addToSet':{'ratings': {'email': loggedUser['email'], 'rating': int(rating)}}}):
                if usersCollection.update_one({'email': loggedUser['email']}, {'$addToSet':{'ratings': {'title': title, 'rating': int(rating)}}}):
                    return Response(json.dumps({'info': 'Rating added!'}), status=200)
                else:
                    return Response(json.dumps({'info':'Internal Server Error'}), status=500)
            else:
                return Response(json.dumps({'info':'Internal Server Error'}), status=500)      
        else:
            return Response(json.dumps({"info":"Provide a title and a rating"}), status=404)
    else:
        return Response(json.dumps({"info":"Login in to view this page"}), status=403)

@app.route('/api/movie/delete_rating', methods=['DELETE'])
def delete_rating():
    global loggedUser
    if loggedUser['category'] != 'none':
        title = request.form['title']
        if title :
            if moviesCollection.update_one({'title': title}, {'$pull':{'ratings': {'email': loggedUser['email']}}}):
                if usersCollection.update_one({'email': loggedUser['email']}, {'$pull':{'ratings': {'title': title}}}):
                    return Response(json.dumps({'info': 'Rating deleted!'}), status=200)
                else:
                    return Response(json.dumps({'info':'Internal Server Error'}), status=500)
            else:
                return Response(json.dumps({'info':'Internal Server Error'}), status=500)      
        else:
            return Response(json.dumps({"info":"Provide a title"}), status=404)
    else:
        return Response(json.dumps({"info":"Login in to view this page"}), status=403)

@app.route('/api/movie/add_comment', methods=['POST'])
def add_comment():
    global loggedUser
    if loggedUser['category'] != 'none':
        title = request.form['title']
        comment = request.form['comment']
        if title and comment:
            if moviesCollection.update_one({'title': title}, {'$addToSet':{'comments': {'email': loggedUser['email'], 'text': comment}}}):
                if usersCollection.update_one({'email': loggedUser['email']}, {'$addToSet':{'comments': {'title': title, 'text': comment}}}):
                    return Response(json.dumps({'info': 'Comment added!'}), status=200)
                else:
                    return Response(json.dumps({'info':'Internal Server Error'}), status=500)
            else:
                return Response(json.dumps({'info':'Internal Server Error'}), status=500)      
        else:
            return Response(json.dumps({"info":"Provide a title and a comment"}), status=404)
    else:
        return Response(json.dumps({"info":"Login in to view this page"}), status=403)

@app.route('/api/movie/delete_comment', methods=['DELETE'])
def delete_comment():
    global loggedUser
    if loggedUser['category'] != 'none':
        title = request.form['title']
        comment = request.form['comment']
        if title and comment:
            if moviesCollection.update_one({'title': title}, {'$pull':{'comments': {'email': loggedUser['email'], 'text': comment}}}):
                if usersCollection.update_one({'email': loggedUser['email']}, {'$pull':{'comments': {'title': title, 'text': comment}}}):
                    return Response(json.dumps({'info': 'Comment deleted!'}), status=200)
                else:
                    return Response(json.dumps({'info':'Internal Server Error'}), status=500)
            else:
                return Response(json.dumps({'info':'Internal Server Error'}), status=500)      
        else:
            return Response(json.dumps({"info":"Provide a title and a comment"}), status=404)
    else:
        return Response(json.dumps({"info":"Login in to view this page"}), status=403)

#Used to get all the comments and all the rating of a user
@app.route('/api/user/data', methods=['GET'])
def get_user_data():
    global loggedUser
    if loggedUser['category'] != 'none':
        loggedUser = usersCollection.find_one({'email': loggedUser['email']})
        return Response(dumps(loggedUser), status=200)
    else:
        return Response(json.dumps({"info":"Login in to view this page"}), status=403)

"""

Handling all the routes that return views V

"""
@app.route('/')
def home():
    global loggedUser
    if loggedUser['category'] == 'none':
        return redirect(url_for('login'))
    else:
        return render_template("index.html", loggedUser = loggedUser)

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/register')
def register():
    return render_template("register.html")

@app.route('/admin')
def admin():
    global loggedUser
    if loggedUser['category'] == 'admin':
        return render_template("dashboard.html")
    else:
        return redirect(url_for('home'))
    


if __name__=='__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)