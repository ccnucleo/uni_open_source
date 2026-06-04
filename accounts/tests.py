from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class AjustesViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = "testuser"
        self.email = "testuser@uni.edu.pe"
        self.password = "original_password123"
        self.user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password
        )
        
    def test_anonymous_redirect(self):
        """Un usuario anónimo debe ser redirigido al login al intentar acceder a ajustes."""
        response = self.client.get(reverse('ajustes'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('accounts:login'), response.url)
        
    def test_logged_in_access(self):
        """Un usuario autenticado debe poder acceder a ajustes y ver el formulario."""
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('ajustes'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/pages/profile/ajustes.html')
        self.assertIn('password_form', response.context)
        
    def test_change_password_validation_errors(self):
        """Validar que un cambio de contraseña inválido retorne errores y mantenga la página."""
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(reverse('ajustes'), {
            'action': 'change_password',
            'old_password': 'wrong_password',
            'new_password1': 'short',
            'new_password2': 'short'
        })
        self.assertEqual(response.status_code, 200)
        form = response.context['password_form']
        self.assertFalse(form.is_valid())
        
    def test_change_password_success(self):
        """Validar que el cambio de contraseña exitoso actualice el hash de sesión y redireccione."""
        self.client.login(username=self.username, password=self.password)
        new_pass = "new_secure_password_123!"
        response = self.client.post(reverse('ajustes'), {
            'action': 'change_password',
            'old_password': self.password,
            'new_password1': new_pass,
            'new_password2': new_pass
        })
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_pass))
        
    def test_delete_account(self):
        """Validar que el borrado de cuenta elimine físicamente al usuario de la base de datos y redireccione."""
        self.client.login(username=self.username, password=self.password)
        user_id = self.user.id
        response = self.client.post(reverse('ajustes'), {
            'action': 'delete_account'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))
        self.assertFalse(User.objects.filter(id=user_id).exists())
