
import unittest
import flask_unittest
import main
import testing.mysqld


class MainTests(flask_unittest.ClientTestCase):
    # Assign the `Flask` app object
    app = main.app

    def setUp(self, client):
        # Perform set up before each test, using client
        self.mysqld = testing.mysqld.Mysqld(my_cnf={'skip-networking': None})

    def test_404(self, client):
        rv = client.get('/does_not_exist')
        self.assertEqual(rv.status_code, 404)

    def test_foo_with_client(self, client):
        rv = client.get('/user')
        self.assertInResponse(bytes('{"message":"Hello, World!"}', 'utf8'), rv)
        #self.assertInResponse(rv, 'hello world!')

    def tearDown(self, client):
        # Perform tear down after each test, using client
        self.mysqld.stop()


if __name__ == '__main__':
    unittest.main()
