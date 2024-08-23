from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.models import App
from unittest.mock import patch
import os
from django.conf import settings
from django.forms.models import model_to_dict


class AppManagerTestCase(TestCase):
    def setUp(self):
        # Create test users
        self.username = 'testuser'
        self.password = 'testpass123'
        self.user = User.objects.create_user(username=self.username, password=self.password)

        self.other_user = User.objects.create_user(username='otheruser', password='otherpass123')

        # Create a test APK file
        self.apk_content = b'Fake APK content'
        self.apk_file_path = SimpleUploadedFile("WhatsApp.apk", self.apk_content,
                                           content_type="application/vnd.android.package-archive")

    def test_user_register(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'newpass123',
            'password2': 'newpass123',
        })
        self.assertEqual(response.status_code, 302)  # Expecting a redirect after successful registration
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_user_login(self):
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': self.password,
        })
        self.assertEqual(response.status_code, 302)  # Expecting a redirect after successful login
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_app_add(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(reverse('app_add'), {
            'name': 'Test App',
            'apk_file_path': self.apk_file_path,
        })
        self.assertEqual(response.status_code, 302)  # Expecting a redirect after successful upload
        self.assertTrue(App.objects.filter(name='Test App').exists())

    def test_app_edit(self):
        self.client.login(username=self.username, password=self.password)

        # Create dummy files
        dummy_apk = SimpleUploadedFile("test_app.apk", b"file_content",
                                       content_type="application/vnd.android.package-archive")
        dummy_screenshot = SimpleUploadedFile("test_screenshot.png", b"file_content", content_type="image/png")

        # Create the App with all required fields
        app = App.objects.create(
            name='Original App',
            uploaded_by=self.user,
            apk_file_path=dummy_apk,
            first_screen_screenshot_path=dummy_screenshot,
            second_screen_screenshot_path=dummy_screenshot
        )

        # Prepare data for edit
        data = {
            'name': 'Updated App',
            # We're not changing the files, so we don't include them in the POST data
        }

        # Post the updated data
        response = self.client.post(reverse('app_edit', kwargs={'pk': app.pk}), data=data)

        if response.status_code != 302:
            print("Response content:", response.content.decode())
            print("Form errors:",
                  response.context['form'].errors if 'form' in response.context else "No form in context")

        self.assertEqual(response.status_code, 302)  # Expecting a redirect after successful edit
        app.refresh_from_db()
        self.assertEqual(app.name, 'Updated App')

    def test_list_apps(self):
        # Log in the test user
        self.client.login(username=self.username, password=self.password)

        # Create some apps for the logged-in user
        App.objects.create(name='User App 1', uploaded_by=self.user)
        App.objects.create(name='User App 2', uploaded_by=self.user)

        # Create an app for another user
        App.objects.create(name='Other User App', uploaded_by=self.other_user)

        # Get the app list page
        response = self.client.get(reverse('app_list'))

        # Check that the response is successful
        self.assertEqual(response.status_code, 200)

        # Check that the user's apps are in the context
        self.assertContains(response, 'User App 1')
        self.assertContains(response, 'User App 2')

        # Check that the other user's app is not in the context
        self.assertNotContains(response, 'Other User App')

        # Check that the correct number of apps is passed to the template
        self.assertEqual(len(response.context['apps']), 2)

    def test_delete_apk(self):
        self.client.login(username=self.username, password=self.password)
        app = App.objects.create(name='App to Delete', uploaded_by=self.user)
        response = self.client.post(reverse('app_delete', kwargs={'pk': app.pk}))
        self.assertEqual(response.status_code, 302)  # Expecting a redirect after successful deletion
        self.assertFalse(App.objects.filter(pk=app.pk).exists())

    def tearDown(self):
        # Clean up any files created during tests
        for app in App.objects.all():
            if app.apk_file_path:
                app.apk_file_path.delete()


class AppiumTestCase(TestCase):
    def setUp(self):
        self.username = 'testuser'
        self.password = 'testpass123'
        self.user = User.objects.create_user(username=self.username, password=self.password)

        # Path to a real APK file in your project
        apk_path = os.path.join(settings.BASE_DIR, 'test_resources', 'WhatsApp.apk')
        with open(apk_path, 'rb') as apk_file_path:
            self.apk_content = apk_file_path.read()
        self.apk_file_path = SimpleUploadedFile("WhatsApp.apk", self.apk_content,
                                           content_type="application/vnd.android.package-archive")

    @patch('apps.views.call_command')
    def test_run_appium_test(self, mock_call_command):
        mock_call_command.return_value = ('success', 'Test completed successfully')
        self.client.login(username=self.username, password=self.password)
        app = App.objects.create(name='Test App', uploaded_by=self.user)
        response = self.client.get(reverse('run_appium_test', kwargs={'app_id': app.pk}))
        self.assertEqual(response.status_code, 302)  # Expecting a redirect after test run
        mock_call_command.assert_called_once_with('run_appium_test', app.pk, return_output=True)
