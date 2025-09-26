import os
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

BASE_URL = os.environ.get("APP_BASE_URL", "http://localhost:5000")

@pytest.fixture
def browser():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # correr sin interfaz gráfica
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()

def wait_for(browser, locator, timeout=5):
    """Espera explícita para encontrar elementos"""
    return WebDriverWait(browser, timeout).until(
        EC.presence_of_element_located(locator)
    )

def js_click(browser, element):
    """Forzar clic con JavaScript (evita intercepts)"""
    browser.execute_script("arguments[0].scrollIntoView(true);", element)
    browser.execute_script("arguments[0].click();", element)

def test_crear_y_ver_nota(browser):
    browser.get(BASE_URL + "/")

    # Completar formulario
    titulo = "Nota de prueba"
    contenido = "Este es el contenido de prueba"

    titulo_input = browser.find_element(By.NAME, "titulo")
    contenido_input = browser.find_element(By.NAME, "contenido")
    boton_guardar = browser.find_element(By.CSS_SELECTOR, "button[type='submit']")

    titulo_input.send_keys(titulo)
    contenido_input.send_keys(contenido)
    boton_guardar.click()

    # Verificar que aparezca en la lista de notas
    card_title = wait_for(browser, (By.CLASS_NAME, "card-title"))
    assert titulo in card_title.text

def test_detalle_nota(browser):
    browser.get(BASE_URL + "/")

    # Clic en el primer botón "Ver"
    boton_ver = wait_for(browser, (By.LINK_TEXT, "Ver"))
    js_click(browser, boton_ver)

    # Verificar título y contenido en detail.html
    h2 = wait_for(browser, (By.TAG_NAME, "h2"))
    p = wait_for(browser, (By.TAG_NAME, "p"))

    assert h2.text != ""  # Hay título
    assert p.text != ""   # Hay contenido

def test_eliminar_nota(browser):
    browser.get(BASE_URL + "/")

    try:
        boton_eliminar = wait_for(browser, (By.CSS_SELECTOR, "form button.btn-danger"), timeout=3)
        js_click(browser, boton_eliminar)
    except TimeoutException:
        pytest.skip("No hay notas para eliminar")

    # Después de eliminar, ya no debería haber ninguna tarjeta con botón Eliminar
    assert "Eliminar" not in browser.page_source
