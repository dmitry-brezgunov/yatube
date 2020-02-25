from django.test import TestCase, Client
from django.core import mail
from posts.models import User, Post

class SignUpTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_signup(self):
        response = self.client.get('/auth/signup/')
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/auth/signup/', {'username':'testUser', 'email':'test@user.com', 'password1':'*yxW$kE8', 'password2':'*yxW$kE8'})
        self.assertRedirects(response, '/auth/login/')
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Подтверждение регистрации Yatube')
        response = self.client.get('/testUser/')
        self.assertEqual(response.status_code, 200)

class PostsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testUser", email="test@user.com", password="*yxW$kE8", first_name="Test", last_name="User")

    def test_posts_unauth(self):
        response = self.client.get('/new/')
        self.assertRedirects(response, '/auth/login/?next=/new/')

    def test_posts_auth(self):
        self.client.login(username="testUser", password="*yxW$kE8")
        response = self.client.get('/new/')
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/new/', {'text':'A test post'})
        self.assertRedirects(response, '/')
        response = self.client.get('/')
        self.assertEqual(response.context["page"][0].text, 'A test post')
        response = self.client.get('/testUser/')
        self.assertEqual(response.context["page"][0].text, 'A test post')
        response = self.client.get('/testUser/1/')
        self.assertEqual(response.context["post"].text, 'A test post')

    def test_posts_edit(self):
        self.client.login(username="testUser", password="*yxW$kE8")
        Post.objects.create(text="A test post", author=self.user)
        response = self.client.get('/testUser/1/edit/')
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/testUser/1/edit/', {'text':'An edited post'})
        self.assertRedirects(response, '/testUser/1/')
        response = self.client.get('/')
        self.assertEqual(response.context["page"][0].text, 'An edited post')
        response = self.client.get('/testUser/')
        self.assertEqual(response.context["page"][0].text, 'An edited post')
        response = self.client.get('/testUser/1/')
        self.assertEqual(response.context["post"].text, 'An edited post')

class Code404Error(TestCase):
    def test_404_error(self):
        client = Client()
        response = client.get('/404/')
        self.assertEqual(response.status_code, 404)
