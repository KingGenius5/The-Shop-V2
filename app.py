from flask import Flask, render_template, redirect, url_for, request
from pymongo import MongoClient
from bson.objectid import ObjectId
from functools import reduce
import os

app = Flask(__name__)

host = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/my_app_db')
client = MongoClient(host=f"{host}?retryWrites=false")
db = client.get_default_database()

#drop function in python helps remove rows based on labels/tags rather than numeric indexing, this will be great for our cart
players_collection = db.players
players_collection.drop()
carts = db.carts
carts.drop()


db.players.insert_many([{'player_name': 'Lebron James', 'charity': 'Lebron James Foundation', 'pledge': 250, 'image': 'http://ih.constantcontact.com/fs054/1107137834319/img/72.jpg?a=1109948824771'},
                        {'player_name': 'Serge Ibaka', 'charity': 'Serge Ibaka Foundation', 'pledge': 150, 'image': 'https://pbs.twimg.com/profile_images/570015235500838912/s49_Or4n_400x400.jpeg'},
                        {'player_name': 'Cena John', 'charity': 'What Foundation', 'pledge': 170, 'image': 'https://pbs.twimg.com/profile_images/570015235500838912/s49_Or4n_400x400.jpeg'},
                        ])

@app.route('/')
def index():
    """Return homepage."""
    return render_template('index.html', players=players_collection.find())

'''

@app.route('/new')
def new_player():
    """Return new player creation page."""
    return render_template('new_player.html')

@app.route('/new', methods=['POST'])
def create_player():
    """Make a new player according to user's specifications."""
    player = {
        'name': request.form.get('name'),
        'price': request.form.get('price'),
        'img_url': request.form.get('img_url')
    }
    player_id = players_collection.insert_one(player).inserted_id
    return redirect(url_for('show_player', player_id=player_id))

@app.route('/player/<player_id>')
def show_player(player_id):
    """Show a single player."""
    player = players_collection.find_one({'_id': ObjectId(player_id)})
    return render_template('show_player.html', player=player)

@app.route('/cans')
def player_index():
    """Show all players."""
    return render_template('player_index.html', players=players_collection.find())

@app.route('/edit/<player_id>', methods=['POST'])
def update_player(player_id):
    """Edit page for a player."""
    new_player = {
        'name': request.form.get('name'),
        'price': request.form.get('price'),
        'img_url': request.form.get('img_url')
    }
    players_collection.update_one(
        {'_id': ObjectId(player_id)},
        {'$set': new_player}
    )
    return redirect(url_for('show_player', player_id=player_id))

@app.route('/edit/<player_id>', methods=['GET'])
def edit_player(player_id):
    """Page to submit an edit on a player."""
    player = players_collection.find_one({'_id': ObjectId(player_id)})
    return render_template('edit_player.html', player=player)

@app.route('/delete/<player_id>', methods=['POST'])
def delete_player(player_id):
    """Delete a player."""
    players_collection.delete_one({'_id': ObjectId(player_id)})
    return redirect(url_for('index'))

'''

"""
********** FOR BUILDING CART FUNCTION *********
"""

@app.route('/player/<player_id>/add', methods=['POST'])
def add_to_cart(player_id):
    if carts.find_one({'_id': ObjectId(player_id)}):
        carts.update_one(
            {'_id': ObjectId(player_id)},
            {'$inc': {'quantity': int(1)}}
        )
    else:
        carts.insert_one(
            {**players_collection.find_one({'_id': ObjectId(player_id)}), **{'quantity': 1}})

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
