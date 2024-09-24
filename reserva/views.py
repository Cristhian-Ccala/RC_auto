from django.shortcuts import render
from django.contrib import messages

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from PIL import Image
import pytesseract
import os
import concurrent.futures

def home(request):
    output = ""
    
    if request.method == 'POST':
        # Usamos el método 'get' para evitar errores si la clave no existe
        codigo = request.POST.get('codigo', '')
        clave = request.POST.get('clave', '')
        
        if codigo and clave:
            try:
                # Ejecutar el código Python (esto es solo un ejemplo, exec() es peligroso)
                local_vars = {}
                exec(codigo, {}, local_vars)
                output = f"Resultado: {local_vars}"
            except Exception as e:
                output = f"Error al ejecutar el código: {str(e)}"
        else:
            output = "Por favor, introduce el código y la clave."

        ejecutarCodigo(request, codigo, clave)
    # Renderizar la página con el resultado
    return render(request, 'index.html', {'output': output})

def ejecutarCodigo(request, codigo, clave):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Ejecución en modo sin cabeza (sin ventana)
    options.add_argument('--no-sandbox')  # Necesario para evitar errores en entornos sin GUI como Colab
    options.add_argument('--disable-dev-shm-usage')  # Necesario para evitar errores de memoria en Colab

    # URL principal y la URL del formulario
    base_url = 'http://ccomputo.unsaac.edu.pe/bienestar/'
    form_url = 'http://ccomputo.unsaac.edu.pe/bienestar/registro.php'

    # Función para capturar y resolver el CAPTCHA
    def picture(driver, i):
        # Abrir la página
        driver.get(base_url)
        # Espera un momento para que la página se cargue completamente
        time.sleep(2)
        # Obtener el elemento que deseas capturar
        element = driver.find_element(By.XPATH, '//*[@id="imgcap"]')
        # Obtener la posición de desplazamiento actual
        scroll_x = driver.execute_script("return window.pageXOffset;")
        scroll_y = driver.execute_script("return window.pageYOffset;")
        # Desplazarse hasta la ubicación del elemento
        driver.execute_script("arguments[0].scrollIntoView();", element)
        # Espera un momento para que el desplazamiento se complete
        time.sleep(1)
        # Obtener la nueva posición de desplazamiento después del scroll
        new_scroll_x = driver.execute_script("return window.pageXOffset;")
        new_scroll_y = driver.execute_script("return window.pageYOffset;")
        # Obtener las coordenadas y dimensiones del elemento ajustadas por el desplazamiento
        x = element.location['x'] - new_scroll_x
        y = element.location['y'] - new_scroll_y
        width = element.size['width']
        height = element.size['height']
        # Tomar una captura de pantalla de toda la página
        driver.save_screenshot(f'captura_completa{i}.png')
        # Abrir la captura de pantalla completa y recortar la región deseada
        imagen_completa = Image.open(f'captura_completa{i}.png')
        imagen_recortada = imagen_completa.crop((x, y, x + width, y + height))
        imagen_recortada.save(f'captura_region{i}.png')
        # Convertir la imagen recortada en texto usando Tesseract OCR
        imagen_final = Image.open(f'captura_region{i}.png')
        captcha_text = pytesseract.image_to_string(imagen_final)
        return captcha_text.strip()  # Devolver el texto del CAPTCHA

    # Función para realizar la reserva
    def realizar_reserva(i):
        driver = webdriver.Chrome(options=options)
        captcha_text = picture(driver, i)
        cookies = driver.get_cookies()
        driver.quit()
        session = requests.Session()
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])
        data = {
            'codigo': codigo,
            'pass': clave,
            'cap': captcha_text
        }
        response = session.post(form_url, data=data)
        messages.success(request, f"Response {i}: {response.text}")
        #print(f"Response {i}: {response.text}")

    # Número de peticiones que deseas enviar
    num_peticiones = 20

    # Ejecutar peticiones concurrentes
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_peticiones) as executor:
        futures = [executor.submit(realizar_reserva, i) for i in range(num_peticiones)]
        concurrent.futures.wait(futures)


