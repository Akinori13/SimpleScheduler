from django.test import TestCase
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse

from .models import User, Profile
from .forms import CustomUserCreationForm


# Create your tests here.
class TestUserCreate(TestCase):
    def setUp(self):
        pass    

    def get(self, params={}):
        return self.client.get(reverse('accounts:signup'), params)

    def post(self, post_data={}):
        return self.client.post(reverse('accounts:signup'), post_data)

    def test_get(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/signup.html')
        self.assertTrue(isinstance(response.context['form'], CustomUserCreationForm))
    
    def test_post(self):
        response = self.post({
            'username': 'testuser',
            'email': 'test@user.com',
            'password1': 'test_password',
            'password2': 'test_password',
        })

        self.assertRedirects(response, reverse('accounts:home'))

        users = User.objects.filter(username='testuser',)
        self.assertEqual(users.count(), 1)

    def test_post_with_password_mismatch(self):
        response = self.post({
            'username': 'testuser',
            'email': 'test@user.com',
            'password1': 'test_password1',
            'password2': 'test_password2',
        })

        # Check that the page remains
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/signup.html')

        # Check that the form has a error
        self.assertTrue(response.context['form'].errors['password2'])

        # Checkou that the user wasn't created
        users = User.objects.filter(username='testuser',)
        self.assertEqual(users.count(), 0)
    
    def test_post_with_too_short_password(self):
        response = self.post({
            'username': 'testuser',
            'email': 'test@user.com',
            'password1': 'test',
            'password2': 'test',
        })

        # Check that the page remains
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/signup.html')

        # Check that the form has a error
        self.assertContains(response, 'このパスワードは短すぎます。')

        # Checkou that the user wasn't created
        users = User.objects.filter(username='testuser',)
        self.assertEqual(users.count(), 0)

    def test_post_with_missing_password(self):
        response = self.post({
            'username': 'testuser',
            'email': 'test@user.com',
            'password1': '',
            'password2': '',
        })

        # Check that the page remains
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/signup.html')

        # Check that the form has a error
        self.assertTrue(response.context['form'].errors['password1'])

        # Checkou that the user wasn't created
        users = User.objects.filter(username='testuser',)
        self.assertEqual(users.count(), 0)


class TestLogin(TestCase):
    def setUp(self):
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@user.com',
            password='test_password'
        )
    
    def get(self, params={}):
        return self.client.get(reverse('accounts:login'), params)

    def post(self, post_data={}):
        return self.client.post(reverse('accounts:login'), post_data)
    
    def test_get(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')
        self.assertTrue(isinstance(response.context['form'], AuthenticationForm))
    
    def test_login(self):
        response = self.post({
            'username': 'testuser',
            'password': 'test_password'
        })
        self.assertRedirects(response, reverse(settings.LOGIN_REDIRECT_URL))

    def test_login_with_password_mismatch(self):
        response = self.post({
            'username': 'testuser',
            'password': 'test_password1'
        })
        self.assertTrue(response.context['form'].non_field_errors)

    def test_login_with_password_missing(self):
        response = self.post({
            'username': 'testuser',
            'password': ''
        })
        self.assertTrue(response.context['form'].non_field_errors)
    
    def test_login_with_username_mismatch(self):
        response = self.post({
            'username': 'testuser2',
            'password': 'test_password1'
        })
        self.assertTrue(response.context['form'].non_field_errors)

    def test_login_with_username_missing(self):
        response = self.post({
            'username': '',
            'password': 'test_password1'
        })
        self.assertTrue(response.context['form'].non_field_errors)


class TestLogout(TestCase):
    def setUp(self):
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@user.com',
            password='test_password'
        )
        self.client.login(username='testuser', password='test_password')
    
    def get(self, params={}):
        return self.client.get(reverse('accounts:logout'), params)

    def test_logout(self):
        response = self.get()
        self.assertRedirects(response, reverse(settings.LOGOUT_REDIRECT_URL))


class TestHome(TestCase):
    def setUp(self):
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@user.com',
            password='test_password'
        )
        self.client.login(username='testuser', password='test_password')
    
    def get(self, params={}):
        return self.client.get(reverse('accounts:home'), params)
    
    def test_get(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/home.html')


class TestProfile(TestCase):
    def setUp(self):
        User.objects.create_user(
            username='testuser2',
            email='test@user.com',
            password='test_password',
        )
        self.test_user = User.objects.get(username='testuser2')
        self.client.force_login(self.test_user)
    
    def test_profile_is_created_when_user_is_created(self):
        self.assertTrue(Profile.objects.filter(user=self.test_user).exists())

    def test_profile_view(self):
        response = self.client.get(reverse('accounts:profile_detail', args=[self.test_user.profile.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')
        self.assertContains(response, self.test_user.profile.user.username)
    
    def test_profile_update_view(self):
        response = self.client.post(
                reverse('accounts:profile_update', args=[self.test_user.profile.id]), 
                {
                    'text': 'HelloWorldTest'
                }
            )
        self.assertRedirects(response, reverse('accounts:profile_detail', args=[self.test_user.profile.id]))

        self.test_user = User.objects.get(username='testuser2')
        self.assertEqual(self.test_user.profile.text, 'HelloWorldTest')
