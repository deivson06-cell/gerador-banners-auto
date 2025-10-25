import os, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    print("🔧 Configurando Chrome...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    print("✅ Chrome configurado!")
    return driver

def fazer_login(driver, login, senha):
    print("🔑 Fazendo login no GERADOR PRO...")
    driver.get("https://gerador.pro/login.php")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username")))

    driver.find_element(By.NAME, "username").send_keys(login)
    driver.find_element(By.NAME, "password").send_keys(senha)
    # Esperar o botão "Enviar todas as imagens" aparecer e estar clicável
print("🚀 Aguardando botão 'Enviar todas as imagens'...")
botao_enviar = WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Enviar todas as imagens')]"))
)

# Fazer o clique via JavaScript (garante execução mesmo se o site usar eventos JS modernos)
driver.execute_script("arguments[0].click();", botao_enviar)
print("📤 Clique no botão 'Enviar todas as imagens' realizado com sucesso!")

# Esperar um tempo pra dar tempo do envio ser processado
time.sleep(10)
    WebDriverWait(driver, 10).until(lambda d: "index.php" in d.current_url)
    print("✅ Login bem-sucedido!")

def acessar_gerar_futebol(driver):
    print("⚽ Acessando menu 'Gerar Futebol'...")
    try:
        link = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Gerar Futebol"))
        )
        link.click()
        print("✅ Página 'Gerar Futebol' aberta!")
    except:
        print("❌ Não consegui encontrar o botão 'Gerar Futebol'")
        raise

def gerar_banner(driver):
    print("🧩 Iniciando geração de banner...")

    # Clica no botão Gerar
    try:
        gerar_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Gerar')]"))
        )
        gerar_btn.click()
        print("✅ Primeiro botão 'Gerar' clicado!")
    except:
        print("❌ Não encontrei o botão 'Gerar' inicial.")
        return False

    time.sleep(3)

    # Escolher modelo 15
    try:
        modelo15 = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@type='radio' and @value='15']"))
        )
        modelo15.click()
        print("✅ Modelo 15 selecionado!")
    except:
        print("❌ Modelo 15 não encontrado.")
        return False

    # Clicar novamente em "Gerar"
    try:
        gerar_btn2 = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Gerar')]"))
        )
        gerar_btn2.click()
        print("✅ Segundo botão 'Gerar' clicado!")
    except:
        print("❌ Não encontrei o segundo botão 'Gerar'.")
        return False

    # Clicar em OK
    try:
        ok_btn = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'OK')]"))
        )
        ok_btn.click()
        print("✅ Botão 'OK' clicado!")
    except:
        print("⚠️ Botão 'OK' não apareceu, continuando...")

    # Clicar em "Enviar todas as imagens"
    try:
        enviar_btn = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Enviar todas as imagens')]"))
        )
        enviar_btn.click()
        print("✅ Botão 'Enviar todas as imagens' clicado!")
        print("🎉 Banners enviados com sucesso para o Telegram!")
        return True
    except:
        print("❌ Não encontrei o botão 'Enviar todas as imagens'.")
        return False

def main():
    print("🚀 INICIANDO AUTOMAÇÃO COMPLETA - GERADOR PRO")
    login = os.environ.get("LOGIN")
    senha = os.environ.get("SENHA")

    if not login or not senha:
        print("❌ Credenciais não encontradas (defina as variáveis LOGIN e SENHA)!")
        return

    driver = setup_driver()
    try:
        fazer_login(driver, login, senha)
        acessar_gerar_futebol(driver)
        sucesso = gerar_banner(driver)
        if sucesso:
            print("🎯 Processo finalizado com sucesso!")
        else:
            print("⚠️ Processo finalizado com falhas.")
    except Exception as e:
        print(f"❌ ERRO: {e}")
    finally:
        driver.quit()
        print("🔒 Navegador fechado")

if __name__ == "__main__":
    main()
