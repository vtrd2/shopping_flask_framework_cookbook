import os, time
from my_app import app, db
import unittest
import tempfile
import coverage

cov = coverage.coverage(
    source = '../cap_10',
    omit = [
        '/venv/lib/site-packages/*',
        'app_tests.py'
    ],
)

cov.start()

class CatalogTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.test_db_file = tempfile.mkstemp()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + self.test_db_file
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        os.close(self.db_fd)
        os.remove(self.test_db_file)

    def test_home(self):
        rv = self.app.get('/en/home')
        self.assertEqual(rv.status_code, 200)
    
    def test_products(self):
        'Test Products list page'
        rv = self.app.get('/en/products')
        self.assertEqual(rv.status_code, 200)
        # print(rv.data.decode('utf-8'))
        # self.assertTrue('No Previous Page' in rv.data.decode("utf-8"))
        # self.assertTrue('No Next Page' in rv.data.decode("utf-8"))

    # def test_create_category(self):
    #     "Test creation of new category"
    #     rv = self.app.get('/en/category-create')
    #     self.assertEqual(rv.status_code, 200)

    #     rv = self.app.post('/en/category-create')
    #     self.assertEqual(rv.status_code, 200)
    #     self.assertTrue('This field is required.' in rv.data.decode("utf-8"))

    #     rv = self.app.get('/en/categories')
    #     self.assertEqual(rv.status_code, 200)
    #     self.assertFalse('Phones' in rv.data.decode('utf-8'))

    #     rv = self.app.post('/en/category-create', data={
    #         'name': 'Phones'
    #     })
    #     self.assertEqual(rv.status_code, 302)

    #     rv = self.app.get('/en/categories')
    #     self.assertEqual(rv.status_code, 200)
    #     self.assertTrue('Phones' in rv.data.decode("utf-8"))

    #     rv = self.app.get('/en/category/1')
    #     self.assertEqual(rv.status_code, 200)
    #     self.assertTrue('Phones' in rv.data.decode("utf-8"))
    
    def test_create_product(self):
        "Test creation of new product"
        rv = self.app.get('/en/product-create')
        self.assertEqual(rv.status_code, 200)

        rv = self.app.post('/en/product-create')
        self.assertEqual(rv.status_code, 200)
        self.assertTrue('This field is required.' in rv.data.decode("utf-8"))

        rv = self.app.post('/en/category-create', data={
            'name': 'Phones'
        })
        self.assertEqual(rv.status_code, 302)

        rv = self.app.post('/en/product-create', data={
            'name': 'iPhone 5',
            'price': 549.49,
            'company': 'Apple',
            'category': 1,
            'image': tempfile.NamedTemporaryFile()
        })
        self.assertEqual(rv.status_code, 302)

        rv = self.app.get('/en/products')
        self.assertEqual(rv.status_code, 200)
        self.assertTrue('iPhone 5' in rv.data.decode("utf-8"))
    
    def test_search_product(self):
        "Test searching product"
        rv = self.app.post('/en/category-create', data={
            'name': 'Phones',
        })
        self.assertEqual(rv.status_code, 302)

        rv = self.app.post('/en/product-create', data={
            'name': 'iPhone 5',
            'price': 549.49,
            'company': 'Apple',
            'category': 1,
            'image': tempfile.NamedTemporaryFile()
        })
        self.assertEqual(rv.status_code, 302)

        rv = self.app.post('/en/product-create', data={
            'name': 'Galaxy S5',
            'price': 549.49,
            'company': 'Samsung',
            'category': 1,
            'image': tempfile.NamedTemporaryFile()
        })
        self.assertEqual(rv.status_code, 302)

        self.app.get('/')

        rv = self.app.get('/en/product-search?name=iPhone')
        self.assertEqual(rv.status_code, 200)
        self.assertTrue('iPhone 5' in rv.data.decode('utf-8'))
        self.assertFalse('Galaxy S5' in rv.data.decode('utf-8'))

        rv = self.app.get('/en/product-search?name=iPhone 6')
        self.assertEqual(rv.status_code, 200)
        self.assertFalse('iPhone 6' in rv.data.decode("utf-8"))

if __name__ == '__main__':
    try:
        unittest.main()
    finally:
        # pass
        cov.stop()
        cov.save()
        cov.report()
        cov.html_report(directory = 'coverage')
        cov.erase()