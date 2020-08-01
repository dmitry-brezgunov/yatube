import tempfile
from django.test import TestCase, Client, override_settings
from django.core import mail
from django.core.cache import cache
from posts.models import User, Post, Group, Follow


class SignUpTest(TestCase):
    '''Тестирование регистрации пользователя'''
    def setUp(self):
        self.client = Client()

    def test_signup(self):
        response = self.client.get('/auth/signup/')
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/auth/signup/', {'username': 'testUser',
                                                      'email': 'test@user.com',
                                                      'password1': '*yxW$kE8',
                                                      'password2': '*yxW$kE8'})
        self.assertRedirects(response, '/auth/login/')
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject, 'Подтверждение регистрации Yatube')
        response = self.client.get('/testUser/')
        self.assertEqual(response.status_code, 200)


@override_settings(CACHES={
    'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}})
class PostsTest(TestCase):
    '''Тестирование публикаций'''
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testUser",
                                             email="test@user.com",
                                             password="*yxW$kE8",
                                             first_name="Test",
                                             last_name="User")

    def test_posts_unauth(self):
        response = self.client.get('/new/')
        self.assertRedirects(response, '/auth/login/?next=/new/')

    def test_posts_auth(self):
        self.client.login(username="testUser", password="*yxW$kE8")
        response = self.client.get('/new/')
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/new/', {'text': 'A test post'})
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
        response = self.client.post(
            '/testUser/1/edit/', {'text': 'An edited post'})
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


@override_settings(CACHES={
    'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}},
                   MEDIA_ROOT=tempfile.gettempdir())
class PostsImgTest(TestCase):
    '''Тестирование возможности добавления изображений к публикациям'''
    def setUp(self):
        self.client = Client()
        User.objects.create_user(username="testUser",
                                 email="test@user.com",
                                 password="*yxW$kE8",
                                 first_name="Test",
                                 last_name="User")
        self.group = Group.objects.create(title='Test Group',
                                          slug='testgroup',
                                          description='A test group')
        self.client.login(username="testUser", password="*yxW$kE8")

    def test_img_upload(self):
        with open('test-img.jpg', 'rb') as fp:
            self.client.post(
                '/new/', {'group': 1, 'text': 'Test post', 'image': fp, })
        response = self.client.get('/testUser/1/')
        self.assertContains(response, '<img class="card-img"', status_code=200)
        response = self.client.get('/')
        self.assertContains(response, '<img class="card-img"', status_code=200)
        response = self.client.get('/testUser/')
        self.assertContains(response, '<img class="card-img"', status_code=200)
        response = self.client.get('/group/testgroup/')
        self.assertContains(response, '<img class="card-img"', status_code=200)

    def test_file_upload(self):
        with open('test-file.txt', 'rb') as fp:
            response = self.client.post(
                '/new/', {'group': 1, 'text': 'Test post', 'image': fp, })
        self.assertFormError(response, 'form', 'image',
                             "Загрузите правильное изображение. "
                             "Файл, который вы загрузили, поврежден "
                             "или не является изображением.")


class CacheTest(TestCase):
    ''''Тестирование работы кеширования главной страницы'''
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testUser",
                                             email="test@user.com",
                                             password="*yxW$kE8",
                                             first_name="Test",
                                             last_name="User")
        self.client.login(username="testUser", password="*yxW$kE8")
        Post.objects.create(text='A test post', author=self.user)

    def test_index_cache(self):
        response = self.client.get('/')
        self.assertContains(response, 'A test post', status_code=200)
        self.client.post('/new/', {'text': 'A test post 2'})
        response = self.client.get('/')
        self.assertNotContains(response, 'A test post 2', status_code=200)
        cache.clear()
        response = self.client.get('/')
        self.assertContains(response, 'A test post 2', status_code=200)


class FollowTest(TestCase):
    '''Тестирование подписок'''
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username="testUser1",
                                              email="test1@user.com",
                                              password="*yxW$kE81",
                                              first_name="Test1",
                                              last_name="User1")
        self.user2 = User.objects.create_user(username="testUser2",
                                              email="test2@user.com",
                                              password="*yxW$kE82",
                                              first_name="Test2",
                                              last_name="User2")
        self.user3 = User.objects.create_user(username="testUser3",
                                              email="test3@user.com",
                                              password="*yxW$kE83",
                                              first_name="Test3",
                                              last_name="User3")

    def test_follow(self):
        self.client.login(username="testUser1", password="*yxW$kE81")
        response = self.client.get('/testUser2/follow')
        self.assertRedirects(response, '/testUser2/')
        follower = Follow.objects.get(user=self.user1, author=self.user2)
        self.assertIsNotNone(follower)
        response = self.client.get('/testUser2/unfollow')
        self.assertRedirects(response, '/testUser2/')
        follower = Follow.objects.filter(
            user=self.user1, author=self.user2).first()
        self.assertIsNone(follower)

    def test_follow_posts(self):
        self.client.login(username="testUser1", password="*yxW$kE81")
        self.client.get('/testUser2/follow')
        Post.objects.create(author=self.user2, text='A test post')
        response = self.client.get('/follow/')
        self.assertContains(response, 'A test post', status_code=200)
        self.client.login(username="testUser3", password="*yxW$kE83")
        response = self.client.get('/follow/')
        self.assertNotContains(response, 'A test post', status_code=200)


class CommentsTest(TestCase):
    '''Тестирование комментариев'''
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username="testUser1",
                                              email="test1@user.com",
                                              password="*yxW$kE81",
                                              first_name="Test1",
                                              last_name="User1")
        Post.objects.create(author=self.user1, text='A test post')

    def test_comments(self):
        response = self.client.get('/testUser1/1/comment/')
        self.assertRedirects(
            response, '/auth/login/?next=/testUser1/1/comment/')
        self.client.login(username="testUser1", password="*yxW$kE81")
        response = self.client.post(
            '/testUser1/1/comment/', {'text': 'A test comment'})
        self.assertRedirects(response, '/testUser1/1/')
        response = self.client.get('/testUser1/1/')
        self.assertContains(response, 'A test comment', status_code=200)
