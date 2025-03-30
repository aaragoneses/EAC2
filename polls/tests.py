from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth.models import User

class MySeleniumTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opts = Options()
        opts.add_argument("--headless")  # Activar modo headless
        cls.selenium = WebDriver(options=opts)
        cls.selenium.implicitly_wait(5)
        cls.live_server_url = 'http://0.0.0.0:8000'  # Sobrescribimos la URL del servidor

        # Crear superusuario inicial
        user = User.objects.create_user("isard", "isard@isardvdi.com", "pirineus")
        user.is_superuser = True
        user.is_staff = True
        user.save()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_create_and_verify_staff_user(self):
        # Accedemos al admin login
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/login/'))

        # Iniciar sesión como administrador
        username_input = self.selenium.find_element(By.NAME, "username")
        username_input.send_keys('isard')  # Usuario administrador
        password_input = self.selenium.find_element(By.NAME, "password")
        password_input.send_keys('pirineus')  # Contraseña administrador
        self.selenium.find_element(By.XPATH, '//input[@value="Log in"]').click()

        # Comprobar que estamos en el panel de administración
        self.assertEqual(self.selenium.title, "Site administration | Django site admin")

        # Ir a la sección de Usuarios
        self.selenium.find_element(By.LINK_TEXT, "Users").click()

        # Comprobar si el usuario ya existe
        existing_users = self.selenium.page_source
        if "aaragoneses" in existing_users:
            print("El usuario ya existe. Intentando iniciar sesión con el usuario existente.")
        else:
            # Crear un nuevo usuario
            self.selenium.find_element(By.LINK_TEXT, "ADD USER").click()
            new_username = self.selenium.find_element(By.NAME, "username")
            new_password = self.selenium.find_element(By.NAME, "password1")
            confirm_password = self.selenium.find_element(By.NAME, "password2")

            new_username.send_keys("aaragoneses")
            new_password.send_keys("101185-Ari")
            confirm_password.send_keys("101185-Ari")
            self.selenium.find_element(By.NAME, "_save").click()  # Guardar el usuario

            # Editar el usuario para añadir permisos de "staff"
            self.selenium.find_element(By.LINK_TEXT, "aaragoneses").click()
            is_staff_checkbox = self.selenium.find_element(By.NAME, "is_staff")
            if not is_staff_checkbox.is_selected():
                is_staff_checkbox.click()
            self.selenium.find_element(By.NAME, "_save").click()  # Guardar cambios

        # Cerrar sesión del administrador
        logout_form = WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.XPATH, '//form[@action="/admin/logout/"]')))
        logout_form.submit()  # Enviar el formulario de logout

        # Intentar iniciar sesión con el usuario
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/login/'))
        username_input = self.selenium.find_element(By.NAME, "username")
        username_input.send_keys('aaragoneses')
        password_input = self.selenium.find_element(By.NAME, "password")
        password_input.send_keys('101185-Ari')
        self.selenium.find_element(By.XPATH, '//input[@value="Log in"]').click()

        # Comprobar que el usuario "staff_user" puede acceder al panel
        self.assertEqual(self.selenium.title, "Site administration | Django site admin")
