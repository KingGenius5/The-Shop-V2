from unittest import TestCase, main as unittest_main, mock
from app import app
from bson.objectid import ObjectId

player_id = ObjectId('5d55cffc4a3d4031f42827a3')
player = {
        "name": "Lebron",
        "price": "250",
        "img_url": "https://a.espncdn.com/combiner/i?img=/i/headshots/nba/players/full/1966.png"
}

player_form = {
        "name": player['name'],
        "price": player['price'],
        "img_url": player['img_url']
}


class PlayerTest(TestCase):

    def setUp(self):
        """Stuff to do before every test."""

        # Get the Flask test client
        self.client = app.test_client()

        # Show Flask errors that happen during tests
        app.config['TESTING'] = True

    def test_index(self):
        """Test the players homepage."""
        result = self.client.get('/')
        self.assertEqual(result.status, '200 OK')
        self.assertIn(b'The Shop', result.data)

    def test_new_player(self):
        """Test the new player creation page."""
        result = self.client.get('/player/new')
        self.assertEqual(result.status, '200 OK')
        self.assertIn(b'name', result.data)

    @mock.patch('pymongo.collection.Collection.find_one')
    def test_show_player(self, mock_find):
        """Test showing a single player."""
        mock_find.return_value = player

        result = self.client.get(f'/player/{player_id}')
        self.assertEqual(result.status, '200 OK')
        self.assertIn(b'Lebron', result.data)
        
    @mock.patch('pymongo.collection.Collection.find_one')
    def test_edit_player(self, mock_find):
        """Test editing a single player."""
        mock_find.return_value = player

        result = self.client.get(f'/player/edit/{player_id}')
        self.assertEqual(result.status, '200 OK')
        self.assertIn(b'Lebron', result.data)

    @mock.patch('pymongo.collection.Collection.insert_one')
    def test_submit_player(self, mock_insert):
        """Test submitting a new player."""
        result = self.client.post('/new_player', data=player_form)

        # After submitting, should redirect to that player's page
        self.assertEqual(result.status, '302 FOUND')
        mock_insert.assert_called_with(player)

    @mock.patch('pymongo.collection.Collection.update_one')
    def test_update_player(self, mock_update):
        result = self.client.post(f'/player/{player_id}', data=player_form)

        self.assertEqual(result.status, '302 FOUND')
        mock_update.assert_called_with({'_id': player_id}, {'$set': player})

    @mock.patch('pymongo.collection.Collection.delete_one')
    def test_delete_player(self, mock_delete):
        form_data = {'_method': 'DELETE'}
        result = self.client.post(f'/player/{player_id}/delete/', data=form_data)
        self.assertEqual(result.status, '302 FOUND')
        mock_delete.assert_called_with({'_id': player_id})

if __name__ == '__main__':
    unittest_main()