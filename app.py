from flask import Flask, render_template, request, redirect, url_for
from bson.objectid import ObjectId
from pymongo import MongoClient
import os

host = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/my_app_db')
client = MongoClient(host=f"{host}?retryWrites=false")
db = client.get_default_database()
players = db.players
comments = db.comments

cart = db.cart
players.drop()
cart.drop()

app = Flask(__name__)

@app.route('/')
def index():
    """Show all players on the homepage."""
    return render_template('index.html', players=players.find())

@app.route('/players', methods=['POST'])
def submit_player():
    """Submit a new player."""
    player = {
        'title': request.form.get('title'),
        'description': request.form.get('description'),
        'images': request.form.get('images'),
        'rating': request.form.get('rating'),
        'price': request.form.get('price')

    }
    print(player)
    player_id = players.insert_one(player).inserted_id
    return redirect(url_for('show_player', player_id=player_id))

@app.route('/players/new')
def new_player():
    """Create a new player."""
    return render_template('new_player.html', player={}, title='New Player')

@app.route('/players/<player_id>')
def show_player(player_id):
    """Show a single player."""
    player = players.find_one({'_id': ObjectId(player_id)})
    player_comments = comments.find({'player_id': ObjectId(player_id)})
    return render_template('show_player.html', player=player, comments=player_comments)

@app.route('/players/<player_id>/edit')
def edit_player(player_id):
    """Show the edit form for a player."""
    player = players.find_one({'_id': ObjectId(player_id)})
    return render_template('edit_player.html', player=player, title='Edit Player')


@app.route('/players/<player_id>/delete', methods=['POST'])
def delete_player(player_id):
    """Delete one player."""
    players.delete_one({'_id': ObjectId(player_id)})
    return redirect(url_for('index'))

@app.route('/players/comments', methods=['POST'])
def comments_new():
    """Submit a new comment."""
    comment = {
        'title': request.form.get('title'),
        'content': request.form.get('content'),
        'player_id': ObjectId(request.form.get('player_id'))
    }
    print(comment)
    comment_id = comments.insert_one(comment).inserted_id
    return redirect(url_for('show_player', player_id=request.form.get('player_id')))

@app.route('/players/<comment_id>/delete', methods=['POST'])
def comments_delete(comment_id):
    """Delete a comment."""
    comments.delete_one({'_id': ObjectId(comment_id)})
    return redirect(url_for('show_player', player_id=request.form.get('player_id')))

@app.route('/players/<player_id>', methods=['POST'])
def update_player(player_id):
    """Submit a newly edited player."""
    updated_player = {
        'title': request.form.get('title'),
        'description': request.form.get('description'),
        'images': request.form.get('images').split(),
        'rating': request.form.get('rating'),
        'price': request.form.get('price')
    }
    players.update_one(
        {'_id': ObjectId(player_id)},
        {'$set': updated_player})
    return redirect(url_for('show_player', player_id=player_id))


"""
********** FOR BUILDING CART FUNCTION *********
"""

@app.route('/cart')
def show_cart():
    """Show cart."""
    carts = cart.find()

    return render_template('cart.html', cart=carts)

@app.route('/cart', methods=['POST'])
def add_to_cart():
    '''Submit new item to cart'''
    player = {
        'title': request.form.get('title'),
        "price": request.form.get('price')
    }

    add_item = cart.insert_one(item).inserted_id
    return redirect(url_for('show_cart', add_item=add_item))

@app.route('/cart/<item_id>/delete', methods=['POST'])
def remove_from_cart(item_id):
    '''Remove item from cart'''
    cart.delete_one({'_id': ObjectId(item_id)})

    return redirect(url_for('show_cart'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))
