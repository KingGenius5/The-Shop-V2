from flask import Flask, render_template, request, redirect, url_for
from bson.objectid import ObjectId
from pymongo import MongoClient
import os

host = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/my_app_db')
client = MongoClient(host=f"{host}?retryWrites=false")
db = client.get_default_database()
players = db.players
comments = db.comments

carst = db.carts
players.drop()
carts.drop()

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

@app.route('/players/<player_id>/add', methods=['POST'])
def add_to_cart(player_id):
    if carts.find_one({'_id': ObjectId(player_id)}):
        carts.update_one(
            {'_id': ObjectId(player_id)},
            {'$inc': {'quantity': int(1)}}
        )
    else:
        carts.insert_one(
            {**players.find_one({'_id': ObjectId(player_id)}), **{'quantity': 1}})

    return redirect(url_for('show_cart'))

@app.route('/cart')
def show_cart():
    """Show cart."""
    cart = carts.find()
    # This will display all products by looping through the database
    total_price = list(carts.find({}))
    total = 0
    for i in range(len(total_price)):
        total += total_price[i]["price"]*total_price[i]["quantity"]
        round(float(total), 2)

    return render_template('cart.html', carts=cart, total=total)


@app.route('/carts/<cart_id>/delete', methods=['POST'])
def remove_from_cart(cart_id):
    # This will delete a product by using an id as a parameter
    """Remove one product from cart"""
    cart_item  = carts.find_one({'_id': ObjectId(cart_id)})
    carts.update_one(
        {'_id': ObjectId(cart_id)},
        {'$inc': {'quantity': -int(1)}}
    )

    if cart_item['quantity']==1:
        carts.remove({'_id': ObjectId(cart_id)})

    return redirect(url_for('show_cart'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))
