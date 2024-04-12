#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/clear', methods=['DELETE'])
def clear_session():
    session['page_views'] = None
    session['user_id'] = None
    return {}, 204

@app.route('/articles', methods=['GET'])
def index_article():
    articles = [article.to_dict() for article in Article.query.all()]
    return jsonify(articles), 200

@app.route('/articles/<int:id>', methods=['GET'])
def show_article(id):
    session['page_views'] = 0 if not session.get('page_views') else session.get('page_views')
    session['page_views'] += 1

    if session['page_views'] <= 3:
        article = Article.query.filter(Article.id == id).first()
        return jsonify(article.to_dict()), 200

    return {'message': 'Maximum pageview limit reached'}, 401

@app.route('/login', methods=['POST'])
def login():
    username = request.get_json().get('username')
    user = User.query.filter_by(username=username).first()
    if user:
        session['user_id'] = user.id
        return jsonify(user.to_dict()), 200
    else:
        return {'error': 'Invalid username'}, 401

@app.route('/logout', methods=['DELETE'])
def logout():
    session.pop('user_id', None)
    return {}, 204

@app.route('/check_session', methods=['GET'])
def check_session():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return jsonify(user.to_dict()), 200
    else:
        return {}, 401

if __name__ == '__main__':
    app.run(port=5555, debug=True)
