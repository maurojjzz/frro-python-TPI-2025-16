import re
import time
from playwright.sync_api import Page, expect

email = f"test_{int(time.time())}@test.com"
password = "Password123"
url = "http://127.0.0.1:5000/"

def test_flujo_usuario_completo(page: Page):
    
    page.goto(url)
    expect(page).to_have_title(re.compile("Mi PlatoIA - Analisis Nutricional Inteligente"))
    
    print("\n✅ Index carga correctamente")
    
    expect(page.locator("h2.titulo")).to_contain_text("Sistema Nutricional")
    print("✅ Título en el index es correcto")
    
    
    expect(page.locator("p.subtitulo")).to_contain_text("Analiza el valor nutricional de tus comidas mediante inteligencia artificial")
    print("✅ Subtítulo en el index es correcto")
    
    # aca nos vamos a login pero por boton header
    
    page.get_by_role("link", name="Iniciar Sesión").hover()
    print("✅ Hover en el botón de Iniciar Sesión exitoso")
    
    time.sleep(2) 
    
    page.get_by_role("link", name="Iniciar Sesión").click()
    print("✅ Click en el botón de Iniciar Sesión exitoso")
    
    page.get_by_role("link", name="Regístrate aquí").hover()
    time.sleep(2)
    page.get_by_role("link", name="Regístrate aquí").click()
    print("✅ Click en el botón de Regístrate aquí exitoso")

    expect(page.locator("h2")).to_contain_text("Registro de Usuario")
    print("✅ Navegación a la página de registro exitosa")
    time.sleep(1)
        
    page.fill("input[name='nombre']", "Test")
    time.sleep(1)
    page.fill("input[name='apellido']", "Testing")
    time.sleep(1)
    page.fill("input[name='email']", email)
    time.sleep(1)
    page.fill("input[name='contrasena']", password)
    print("✅ Campos del formulario de registro completado")
    time.sleep(2)
    
    page.click("button[type='submit']")
    
    page.wait_for_url(re.compile(".*/login"))
    expect(page).to_have_url(re.compile(".*/login"))
    print("✅ Redirección a login después del registro funciona correctamente")

    expect(page.locator("h2")).to_contain_text("Iniciar Sesión")

    time.sleep(2)
    
    page.fill("input[name='email']", email)
    time.sleep(1)
    page.fill("input[name='contrasena']", password)
    print("✅ Campos del formulario de login completado")
    time.sleep(2)

    page.click("button[type='submit']")
    time.sleep(2)
    
    expect(page.locator("p.subtitulo")).to_contain_text("Analiza el valor nutricional de tus comidas mediante inteligencia artificial")
    print("✅ Subtítulo en el index es correcto")


    file_input = page.locator("#file-input")
    
    with page.expect_response(lambda r: "/subir-imagen" in r.url and r.request.method == "POST") as response_info:
        file_input.set_input_files("tests/e2e/alf_maizena.jpg")
        print("✅ Imagen seleccionada, esperando respuesta del servidor...")
    
    response = response_info.value
    print(f"✅ Servidor respondió con status {response.status}")
    
    upload_spinner = page.locator("#upload-spinner")
    expect(upload_spinner).to_be_hidden(timeout=5000)
    print("✅ Imagen subida exitosamente")
    
    
    analysis_spinner = page.locator("#analysis-spinner")
    expect(analysis_spinner).to_be_visible(timeout=5000)
    print("✅ Análisis nutricional iniciado")
    
    expect(analysis_spinner).to_be_hidden(timeout=60000)  
    print("✅ Análisis nutricional completado")
    time.sleep(2)
    
    expect(page.locator(".analisis-nutrientes")).to_be_visible()
    print("✅ Resultados del análisis visibles")
    time.sleep(2)
    
    # Navegar directamente a consumos
    page.goto(f"{url}consumos")
    page.wait_for_url(re.compile(".*/consumos"))
    print("✅ Navegación directa a página de consumos exitosa")
    time.sleep(3)

    expect(page.locator("#plotly-semanal")).to_be_visible()
    
    btn_7dias = page.locator('button[data-filtro="7dias"]')
    btn_7dias.click()
    print("✅ Click en filtro de últimos 7 días")
    
    
    loading_spinner = page.locator("#loading-spinner")
    expect(loading_spinner).to_be_visible(timeout=5000)
    expect(loading_spinner).to_be_hidden(timeout=15000)
    print("✅ Filtro de últimos 7 días aplicado correctamente")
    time.sleep(2)
    
    btn_30dias = page.locator('button[data-filtro="30dias"]')
    btn_30dias.click()
    print("✅ Click en filtro de últimos 30 días")
    
    expect(loading_spinner).to_be_visible(timeout=5000)
    expect(loading_spinner).to_be_hidden(timeout=15000)
    print("✅ Filtro de últimos 30 días aplicado correctamente")
    
    time.sleep(2)
    
    
    page.locator("#segunda-fila-graficos").scroll_into_view_if_needed()
    time.sleep(1)
    
    page.locator("#tercera-fila-graficos").scroll_into_view_if_needed()
    time.sleep(1)
    
    page.locator("#tabla-consumos-semana").scroll_into_view_if_needed()
    time.sleep(1)
    
    page.locator("header").scroll_into_view_if_needed()
    time.sleep(1)  
    page.get_by_role("link", name="Cerrar Sesión").hover()
    time.sleep(2)
    page.get_by_role("link", name="Cerrar Sesión").click()
    print("✅ Cierre de sesión exitoso")
    page.wait_for_url(re.compile(".*/login"))
    print("✅ Redirección a login después del logout funciona correctamente")
    
    time.sleep(4)

