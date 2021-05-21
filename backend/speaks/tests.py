from urllib.parse import urlencode

from django.test import TestCase
from django.urls import reverse
from django.conf import settings

from .models import Speak
from accounts.models import User

# Create your tests here.
class TestSpeakModel(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test_user1", 
            email='test_email1@user.com',
            password="test_password1",
        )
        self.speak = Speak.objects.create(
            content="This is a speak created by test_user1",
            user=self.user
        )
    
    def test_str(self):
        self.assertEqual(self.speak.__str__() ,self.speak.content)

    def test_excerpted_content(self):
        self.assertEqual(self.speak.excerpted_content() ,self.speak.content[:20])


class TestSpeakCreateView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_user1', 
            email='test_email1@user.com',
            password='test_password1',
        )
        self.client.force_login(self.user)
    
    def get(self):
        return self.client.get(reverse('speaks:speak_create'))
    
    def post(self, post_data={}):
        return self.client.post(reverse('speaks:speak_create'), post_data)

    def test_simple_get(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'speaks/speak_create.html')
    
    def test_get_by_logouted_user(self):
        self.client.logout()
        response = self.get()
        params = urlencode({'next':reverse('speaks:speak_create')})
        expected_url = f'{reverse(settings.LOGIN_URL)}?{params}'
        self.assertRedirects(response, expected_url)

    def test_simple_post(self):
        records = Speak.objects.all().count()

        response = self.post({
            'content': 'test_simple_post'
        })
        self.assertRedirects(response, reverse('accounts:home'))

        self.assertEqual(Speak.objects.all().last().content, 'test_simple_post')
        self.assertEqual(Speak.objects.all().count(), records+1)

    def test_post_by_logouted_user(self):
        records = Speak.objects.all().count()

        self.client.logout()
        response = self.post({
            'content': 'test_post_by_logouted_user'
        })
        params = urlencode({'next':reverse('speaks:speak_create')})
        expected_url = f'{reverse(settings.LOGIN_URL)}?{params}'
        self.assertRedirects(response, expected_url)

        self.assertEqual(Speak.objects.all().count(), records)

    def test_post_with_missing_content(self):
        records = Speak.objects.all().count()

        response = self.post({
            'content': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'speaks/speak_create.html')
        self.assertTrue(response.context['form'].errors['content'])

        self.assertEqual(Speak.objects.all().count(), records)

    def test_post_with_too_long_content(self):
        records = Speak.objects.all().count()

        response = self.post({
            'content': 'test_post_with_too_long_content/test_post_with_too_long_content/test_post_with_too_long_content/test_post_with_too_long_content/test_post_with_too_long_content/'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'speaks/speak_create.html')
        self.assertTrue(response.context['form'].errors['content'])

        self.assertEqual(Speak.objects.all().count(), records)


class TestSpeakDeleteView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_user1', 
            email='test_email1@user.com',
            password='test_password1',
        )
        self.client.force_login(self.user)

    def create_speak(self, content: str):
        self.speak = Speak.objects.create(
            content=content,
            user=self.user
        )
        return self.speak

    def get(self, pk: int):
        return self.client.get(reverse('speaks:speak_delete', args=[pk]))
    
    def post(self, pk: int, post_data={}):
        return self.client.post(reverse('speaks:speak_delete', args=[pk]), post_data)

    def test_get_succeeds(self):
        speak = self.create_speak(content='test_get_succeeds')

        response = self.get(speak.id)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'speaks/speak_delete.html')
    
    def test_get_fails_by_logouted_user(self):
        speak = self.create_speak(content='test_get_fails_by_logouted_user')
        self.client.logout()
        response = self.get(speak.id)
        params = urlencode({'next':reverse('speaks:speak_delete', args=[speak.id])})
        expected_url = f'{reverse(settings.LOGIN_URL)}?{params}'
        self.assertRedirects(response, expected_url)

    def test_post_succeeds(self):
        speak = self.create_speak(content='test_post_succeeds')

        response = self.post(speak.id)
        self.assertRedirects(response, reverse('accounts:home'))

        self.assertEqual(Speak.objects.filter(content='test_post_succeeds').count(), 0)

    def test_post_fails_by_logouted_user(self):
        speak = self.create_speak(content='test_post_fails_by_logouted_user')

        self.client.logout()
        response = self.post(speak.id)
        params = urlencode({'next':reverse('speaks:speak_delete', args=[speak.id])})
        expected_url = f'{reverse(settings.LOGIN_URL)}?{params}'
        self.assertRedirects(response, expected_url)

        self.assertEqual(Speak.objects.filter(content='test_post_fails_by_logouted_user').count(), 1)

    def test_post_fails_by_unauthorized_user(self):
        speak = self.create_speak(content='test_post_fails_by_unauthorized_user')
        self.client.logout()
        self.user = User.objects.create_user(
            username='test_user2', 
            email='test_email2@user.com',
            password='test_password2',
        )
        self.client.force_login(self.user)

        response = self.post(speak.id)
        self.assertEqual(response.status_code, 404)

        self.assertEqual(Speak.objects.filter(content='test_post_fails_by_unauthorized_user').count(), 1)


class TestSpeakUpdateView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_user1', 
            email='test_email1@user.com',
            password='test_password1',
        )
        self.client.force_login(self.user)

    def create_speak(self, content: str):
        self.speak = Speak.objects.create(
            content=content,
            user=self.user
        )
        return self.speak

    def get(self, pk: int):
        return self.client.get(reverse('speaks:speak_update', args=[pk]))
    
    def post(self, pk: int, post_data={}):
        return self.client.post(reverse('speaks:speak_update', args=[pk]), post_data)

    def test_get_succeeds(self):
        speak = self.create_speak(content='test_get_succeeds')

        response = self.get(speak.id)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'speaks/speak_update.html')
    
    def test_get_fails_by_logouted_user(self):
        speak = self.create_speak(content='test_get_fails_by_logouted_user')
        self.client.logout()
        response = self.get(speak.id)
        params = urlencode({'next':reverse('speaks:speak_update', args=[speak.id])})
        expected_url = f'{reverse(settings.LOGIN_URL)}?{params}'
        self.assertRedirects(response, expected_url)

    def test_post_succeeds(self):
        speak = self.create_speak(content='test_post_succeeds')

        response = self.post(
            speak.id, 
            {'content': 'test_post_succeeds_updated'}
        )
        self.assertRedirects(response, reverse('accounts:home'))

        self.assertEqual(Speak.objects.filter(content='test_post_succeeds_updated').count(), 1)

    def test_post_fails_with_blank_content(self):
        speak = self.create_speak(content='test_post_fails_with_blank_content')

        response = self.post(
            speak.id,
            {'content': ''}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'speaks/speak_update.html')
        self.assertTrue(response.context['form'].errors['content'])

        self.assertEqual(Speak.objects.filter(content='test_post_fails_with_blank_content').count(), 1)

    def test_post_fails_by_logouted_user(self):
        speak = self.create_speak(content='test_post_fails_by_logouted_user')

        self.client.logout()
        response = self.post(
            speak.id,
            {'content': 'test_post_fails_by_logouted_user_updated'}
        )
        params = urlencode({'next':reverse('speaks:speak_update', args=[speak.id])})
        expected_url = f'{reverse(settings.LOGIN_URL)}?{params}'
        self.assertRedirects(response, expected_url)

        self.assertEqual(Speak.objects.filter(content='test_post_fails_by_logouted_user').count(), 1)

    def test_post_fails_by_unauthorized_user(self):
        speak = self.create_speak(content='test_post_fails_by_unauthorized_user')
        self.client.logout()
        self.user = User.objects.create_user(
            username='test_user2', 
            email='test_email2@user.com',
            password='test_password2',
        )
        self.client.force_login(self.user)

        response = self.post(
            speak.id,
            {'content': 'test_post_fails_by_unauthorized_user_updated'}
        )
        self.assertEqual(response.status_code, 404)

        self.assertEqual(Speak.objects.filter(content='test_post_fails_by_unauthorized_user').count(), 1)

