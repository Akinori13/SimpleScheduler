import re
from time import sleep

from django.test import TestCase
from django.conf import settings
from django.core import mail
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse

from .models import User, Profile
from .forms import CustomUserCreationForm


# Create your tests here.
class TestSignup(TestCase):
    def setUp(self):
        pass    

    def get(self, url=reverse('accounts:signup'), params={}):
        return self.client.get(url, params)

    def post(self, post_data={}):
        return self.client.post(reverse('accounts:signup'), post_data)

    def test_get_succeeds(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/signup.html')
        self.assertTrue(isinstance(response.context['form'], CustomUserCreationForm))
    
    def test_post_succeeds(self):
        response = self.post({
            'username': 'test_post_succeeds',
            'email': 'test@user.com',
            'password1': 'test_password',
            'password2': 'test_password',
        })
        self.assertRedirects(response, reverse('accounts:signup_done'))
        url=re.search(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-]+', mail.outbox[0].body).group()
        response = self.get(url=url)
        self.assertTemplateUsed(response, 'registration/signup_complete.html')
        self.assertEqual(User.objects.filter(username='test_post_succeeds').count(), 1)

    def test_post_fails_with_password_mismatch(self):
        response = self.post({
            'username': 'test_post_fails_with_password_mismatch',
            'email': 'test@user.com',
            'password1': 'test_password1',
            'password2': 'test_password2',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/signup.html')
        self.assertTrue(response.context['form'].errors['password2'])
        self.assertEqual(User.objects.filter(username='test_post_fails_with_password_mismatch').count(), 0)
    
    def test_post_fails_with_too_short_password(self):
        response = self.post({
            'username': 'test_post_fails_with_too_short_password',
            'email': 'test@user.com',
            'password1': 'test',
            'password2': 'test',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/signup.html')
        self.assertContains(response, 'このパスワードは短すぎます。')
        self.assertEqual(User.objects.filter(username='test_post_fails_with_too_short_password').count(), 0)

    def test_post_fails_with_missing_password(self):
        response = self.post({
            'username': 'test_post_fails_with_missing_password',
            'email': 'test@user.com',
            'password1': '',
            'password2': '',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/signup.html')
        self.assertTrue(response.context['form'].errors['password1'])
        self.assertEqual(User.objects.filter(username='test_post_fails_with_missing_password').count(), 0)


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

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class SeleniumTests(StaticLiveServerTestCase):
    def setUp(self):
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@user.com',
            password='test_password'
        )

        options = webdriver.ChromeOptions()
        self.chrome = webdriver.Remote(
            command_executor='http://selenium:4444/wd/hub',
            desired_capabilities=DesiredCapabilities.CHROME,
            options=options
        )
        self.chrome.implicitly_wait(10)
    
    def test_login(self):
        self.chrome.get('http://nginx:80/accounts/login/')
        
        # self.chrome.find_element_by_id("id_username").send_keys('testuser')
        # self.chrome.find_element_by_id("id_password").send_keys('test_password')
        
        # self.chrome.find_element_by_id("submit").click()
        
        sleep(10)
        
    def tearDown(self):
        self.chrome.quit()
