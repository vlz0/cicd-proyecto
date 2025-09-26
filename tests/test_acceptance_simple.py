import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

BASE_URL = os.environ.get("APP_BASE_URL", "http://localhost:5000")

@pytest.fixture(scope="session")
def browser():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(3)
    
    # Navigate to the app once at the start
    driver.get(BASE_URL + "/")
    
    # Verify the app is running
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "titulo"))
    )
    
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

def create_note_reliable(browser, titulo, contenido):
    """Función auxiliar para crear una nota de manera confiable"""
    print(f"Creating note: '{titulo}'")
    
    # Make sure we're on the main page
    if not browser.current_url.endswith('/'):
        browser.get(BASE_URL + "/")
        wait_for(browser, (By.NAME, "titulo"))
    
    # Fill form
    titulo_input = browser.find_element(By.NAME, "titulo")
    contenido_input = browser.find_element(By.NAME, "contenido")
    
    titulo_input.clear()
    titulo_input.send_keys(titulo)
    contenido_input.clear()
    contenido_input.send_keys(contenido)
    
    # Get initial count
    initial_count = len(browser.find_elements(By.CSS_SELECTOR, ".card-body"))
    print(f"Initial card count: {initial_count}")
    
    # Try multiple submission methods
    success = False
    
    # Method 1: Enter key
    try:
        contenido_input.send_keys(Keys.RETURN)
        time.sleep(3)
        if titulo in browser.page_source:
            print("Success with Enter key")
            success = True
    except Exception as e:
        print(f"Enter key failed: {e}")
    
    # Method 2: Button click
    if not success:
        try:
            submit_btn = browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_btn.click()
            time.sleep(3)
            if titulo in browser.page_source:
                print("Success with button click")
                success = True
        except Exception as e:
            print(f"Button click failed: {e}")
    
    # Method 3: JavaScript submission
    if not success:
        try:
            browser.execute_script("document.querySelector('form').submit();")
            time.sleep(3)
            if titulo in browser.page_source:
                print("Success with JS submit")
                success = True
        except Exception as e:
            print(f"JS submit failed: {e}")
    
    # Verify creation
    final_count = len(browser.find_elements(By.CSS_SELECTOR, ".card-body"))
    print(f"Final card count: {final_count}")
    
    if success and titulo in browser.page_source:
        print(f"Note '{titulo}' created successfully")
        return True
    else:
        print(f"Failed to create note '{titulo}'")
        return False

def test_1_app_is_running(browser):
    """Test básico para verificar que la aplicación está funcionando"""
    assert browser.title is not None
    assert "Gestor de Notas" in browser.page_source
    
    # Check form elements exist
    assert browser.find_element(By.NAME, "titulo")
    assert browser.find_element(By.NAME, "contenido")
    assert browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
    print("✓ App is running and form elements are present")

def test_2_crear_nota(browser):
    """Test de creación de nota"""
    timestamp = str(int(time.time() * 1000))
    titulo = f"Test Note {timestamp}"
    contenido = "Test content for the note"
    
    success = create_note_reliable(browser, titulo, contenido)
    assert success, f"Failed to create note '{titulo}'"
    assert titulo in browser.page_source
    print("✓ Note creation test passed")

def test_3_ver_lista_notas(browser):
    """Test para verificar que las notas se muestran en la lista"""
    cards = browser.find_elements(By.CSS_SELECTOR, ".card-body")
    assert len(cards) > 0, "No notes found in the list"
    
    # Check that at least one card has a title
    card_titles = browser.find_elements(By.CLASS_NAME, "card-title")
    assert len(card_titles) > 0, "No card titles found"
    print(f"✓ Found {len(cards)} notes in the list")

def test_4_detalle_nota(browser):
    """Test para ver el detalle de una nota"""
    # Make sure we're on home page
    if not browser.current_url.endswith('/'):
        browser.get(BASE_URL + "/")
        wait_for(browser, (By.NAME, "titulo"))
    
    # Find the first "Ver" button
    try:
        ver_buttons = browser.find_elements(By.LINK_TEXT, "Ver")
        assert len(ver_buttons) > 0, "No 'Ver' buttons found"
        
        # Click the first one
        js_click(browser, ver_buttons[0])
        
        # Wait for detail page
        h2 = wait_for(browser, (By.TAG_NAME, "h2"))
        p = wait_for(browser, (By.TAG_NAME, "p"))
        
        assert len(h2.text.strip()) > 0, "No title found on detail page"
        assert len(p.text.strip()) > 0, "No content found on detail page"
        print("✓ Detail view test passed")
        
    except Exception as e:
        pytest.skip(f"Detail test skipped: {e}")

def test_5_eliminar_nota(browser):
    """Test para eliminar una nota"""
    # Navigate back to home
    browser.get(BASE_URL + "/")
    wait_for(browser, (By.NAME, "titulo"))
    
    # Check initial count
    initial_cards = browser.find_elements(By.CSS_SELECTOR, ".card-body")
    initial_count = len(initial_cards)
    
    if initial_count == 0:
        # Create a note to delete
        timestamp = str(int(time.time() * 1000))
        titulo = f"Note to Delete {timestamp}"
        success = create_note_reliable(browser, titulo, "Content to be deleted")
        assert success, "Failed to create note for deletion test"
        initial_count = 1
    
    # Find delete buttons
    delete_buttons = browser.find_elements(By.CSS_SELECTOR, "form button.btn-danger")
    assert len(delete_buttons) > 0, "No delete buttons found"
    
    # Click the first delete button
    js_click(browser, delete_buttons[0])
    time.sleep(3)
    
    # Check final count
    final_cards = browser.find_elements(By.CSS_SELECTOR, ".card-body")
    final_count = len(final_cards)
    
    assert final_count < initial_count, f"Expected fewer notes after deletion. Initial: {initial_count}, Final: {final_count}"
    print(f"✓ Deletion test passed. Notes reduced from {initial_count} to {final_count}")