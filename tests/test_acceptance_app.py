import os
import time
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
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(3)  # Implicit wait for all elements
    yield driver
    driver.quit()

def wait_for(browser, locator, timeout=10):
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

    # Esperar a que la página se cargue completamente
    wait_for(browser, (By.NAME, "titulo"))

    # Completar formulario con identificador único
    timestamp = str(int(time.time() * 1000))
    titulo = f"Nota de prueba {timestamp}"
    contenido = "Este es el contenido de prueba"

    titulo_input = browser.find_element(By.NAME, "titulo")
    contenido_input = browser.find_element(By.NAME, "contenido")
    boton_guardar = browser.find_element(By.CSS_SELECTOR, "button[type='submit']")

    titulo_input.clear()
    titulo_input.send_keys(titulo)
    contenido_input.clear()
    contenido_input.send_keys(contenido)
    
    # Usar JavaScript para enviar el formulario
    browser.execute_script("arguments[0].click();", boton_guardar)

    # Esperar a que aparezca la nota específica en la lista
    WebDriverWait(browser, 15).until(
        lambda driver: titulo in driver.page_source
    )

    # Verificar que aparezca en la lista de notas
    assert titulo in browser.page_source
    card_titles = browser.find_elements(By.CLASS_NAME, "card-title")
    found_title = any(titulo in title.text for title in card_titles)
    assert found_title, f"No se encontró el título '{titulo}' en las notas"

def test_detalle_nota(browser):
    browser.get(BASE_URL + "/")

    # Primero crear una nota para asegurar que hay algo que ver
    timestamp = str(int(time.time() * 1000))
    titulo = f"Nota para detalle {timestamp}"
    contenido = "Contenido para ver detalle"
    
    wait_for(browser, (By.NAME, "titulo"))
    titulo_input = browser.find_element(By.NAME, "titulo")
    contenido_input = browser.find_element(By.NAME, "contenido")
    boton_guardar = browser.find_element(By.CSS_SELECTOR, "button[type='submit']")

    titulo_input.clear()
    titulo_input.send_keys(titulo)
    contenido_input.clear()
    contenido_input.send_keys(contenido)
    
    # Usar JavaScript para enviar el formulario
    browser.execute_script("arguments[0].click();", boton_guardar)
    
    # Esperar a que aparezca la nota
    WebDriverWait(browser, 15).until(
        lambda driver: titulo in driver.page_source
    )

    # Encontrar la tarjeta específica y su botón "Ver"
    cards = browser.find_elements(By.CSS_SELECTOR, ".card")
    target_card = None
    
    for card in cards:
        if titulo in card.text:
            target_card = card
            break
    
    assert target_card is not None, f"No se encontró la tarjeta con el título: {titulo}"
    
    # Hacer clic en el botón "Ver" de la tarjeta específica
    boton_ver = target_card.find_element(By.LINK_TEXT, "Ver")
    js_click(browser, boton_ver)

    # Verificar título y contenido en detail.html
    h2 = wait_for(browser, (By.TAG_NAME, "h2"))
    p = wait_for(browser, (By.TAG_NAME, "p"))

    assert titulo in h2.text  # Verificar el título específico
    assert contenido in p.text   # Verificar el contenido específico

def test_eliminar_nota(browser):
    browser.get(BASE_URL + "/")

    # Contar las notas existentes antes de agregar una nueva
    existing_cards = browser.find_elements(By.CSS_SELECTOR, ".card-body")
    initial_count = len(existing_cards)

    # Crear una nota específica para eliminar con timestamp para garantizar unicidad
    timestamp = str(int(time.time() * 1000))  # milliseconds timestamp
    titulo_unico = f"Nota para eliminar {timestamp}"
    contenido_unico = "Esta nota será eliminada"
    
    # Esperar a que la página cargue y llenar el formulario
    wait_for(browser, (By.NAME, "titulo"))
    titulo_input = browser.find_element(By.NAME, "titulo")
    contenido_input = browser.find_element(By.NAME, "contenido")
    boton_guardar = browser.find_element(By.CSS_SELECTOR, "button[type='submit']")

    titulo_input.clear()
    titulo_input.send_keys(titulo_unico)
    contenido_input.clear()
    contenido_input.send_keys(contenido_unico)
    
    # Usar JavaScript para enviar el formulario de manera más confiable
    browser.execute_script("arguments[0].click();", boton_guardar)

    # Esperar a que la página se recargue y aparezca la nueva nota
    # Esperamos hasta que encontremos el título específico en la página
    WebDriverWait(browser, 15).until(
        lambda driver: titulo_unico in driver.page_source
    )

    # Verificar que la nota existe antes de eliminarla
    assert titulo_unico in browser.page_source

    # Verificar que ahora hay una nota más
    new_cards = browser.find_elements(By.CSS_SELECTOR, ".card-body")
    assert len(new_cards) == initial_count + 1, f"Expected {initial_count + 1} cards, but found {len(new_cards)}"

    # Encontrar todos los botones eliminar y buscar el correcto para nuestra nota
    cards = browser.find_elements(By.CSS_SELECTOR, ".card")
    target_card = None
    
    for card in cards:
        if titulo_unico in card.text:
            target_card = card
            break
    
    assert target_card is not None, f"No se encontró la tarjeta con el título: {titulo_unico}"
    
    # Encontrar el botón eliminar dentro de la tarjeta específica
    boton_eliminar = target_card.find_element(By.CSS_SELECTOR, "form button.btn-danger")
    js_click(browser, boton_eliminar)

    # Esperar a que la página se recargue después de la eliminación
    WebDriverWait(browser, 15).until(
        lambda driver: titulo_unico not in driver.page_source
    )

    # Verificar que la nota específica ya no está en la página
    assert titulo_unico not in browser.page_source
    
    # Verificar que volvemos al número original de tarjetas
    final_cards = browser.find_elements(By.CSS_SELECTOR, ".card-body")
    assert len(final_cards) == initial_count, f"Expected {initial_count} cards after deletion, but found {len(final_cards)}"
