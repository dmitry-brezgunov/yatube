import datetime as dt
from django.test import TestCase, Client
from django.utils.html import escape
from .models import Post, User

class IndexPageTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="test", email="test@test.com", password="test")
        self.post = Post.objects.create(text="You're talking about things I haven't done yet in the past tense. It's driving me crazy!", author=self.user)
        self.response_index = self.client.get('/')

    def testPageCodes(self):
        response_admin = self.client.get('/admin/')
        self.assertEqual(self.response_index.status_code, 200)
        self.assertEqual(response_admin.status_code, 302)

    def testIndexContext(self):
        self.assertIn('page', self.response_index.context)

    def testIndexTemplate(self):
        self.assertTemplateUsed(self.response_index, 'index.html')

    def testIndexPosts(self):
        self.assertEqual(len(self.response_index.context['page']), 1)
        self.assertIsInstance(self.response_index.context['page'][0], Post)
        self.assertEqual(self.response_index.context["page"][0].author, self.user)

    def testIndexContent(self):
        self.assertIn(escape("You're talking about things I haven't done yet in the past tense. It's driving me crazy!"), str(self.response_index.content))

    def testContextProcessor(self):
        self.assertIn('year', self.response_index.context)
        today = dt.datetime.today().year
        self.assertEqual(self.response_index.context['year'], today)
