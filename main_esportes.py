import os, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import requests

def setup_driver():
    print("🔧 Configurando Chrome...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    print("✅ Chrome configurado!")
    return driver

def enviar_telegram(msg):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("CHAT_ID")
    if not token or not chat_id:
        print("⚠️ TELEGRAM_BOT_TOKEN ou CHAT_ID não configurados.")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}
    requests.post(url, data=data)

def fazer_login(driver, login, senha):
    print("🔑 Fazendo login no GERADOR PRO...")
    driver.get("https://gerador.pro/login.php")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(login)
    driver.find_element(By.NAME, "password").send_keys(senha)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    # Espera o redirecionamento completo para o painel
    WebDriverWait(driver, 25).until(lambda d: "index" in d.current_url or "painel" in d.current_url)
    time.sleep(2)
    print(f"✅ Login realizado com sucesso! URL atual: {driver.current_url}")

def acessar_todos_esportes(driver):
    print("🏆 Acessando menu 'Todos esportes'...")
    try:
        link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(.,'Todos esportes')]"))
        )
        driver.execute_script("arguments[0].click();", link)
        print("✅ Clicou em 'Todos esportes'")
    except Exception as e:
        print(f"⚠️ Falhou ao clicar no menu: {e}")
        print("➡️ Tentando navegação direta para /esportes.php ...")
        driver.get("https://gerador.pro/esportes.php")

    WebDriverWait(driver, 20).until(lambda d: "esportes" in d.current_url)
    print("✅ Página de esportes carregada!")

def selecionar_modelo_roxo(driver):
    print("🎨 Selecionando modelo 'Esportes Roxo'...")
    try:
        modelo = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(.,'Esportes Roxo') or contains(.,'Roxo')]"))
        )
        driver.execute_script("arguments[0].click();", modelo)
        print("✅ Modelo 'Roxo' selecionado!")
    except Exception:
        print("⚠️ Não achou o modelo na tela, indo direto para a URL...")
        driver.get("https://gerador.pro/esportes.php?page=futebol&modelo=roxo")

def gerar_banners(driver):
    print("⚙️ Gerando banners...")
    botao = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Gerar Banners')]"))
    )
    driver.execute_script("arguments[0].click();", botao)
    print("✅ Botão 'Gerar Banners' clicado!")

    # Espera o popup de sucesso
    try:
        popup_ok = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'OK') or contains(.,'Ok')]"))
        )
        print("🎉 Sucesso detectado! Clicando em OK...")
        popup_ok.click()
    except:
        print("⚠️ Popup não encontrado — pode já ter redirecionado automaticamente.")

def enviar_todas_as_imagens(driver):
    print("📤 Enviando todas as imagens...")
    WebDriverWait(driver, 25).until(lambda d: "cartazes" in d.current_url)
    botao_enviar = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Enviar Todas') or contains(.,'Enviar todas')]"))
    )
    driver.execute_script("arguments[0].click();", botao_enviar)
    print("✅ Botão 'Enviar Todas as Imagens' clicado!")
    time.sleep(5)

def main():
    print("🚀 Iniciando automação Esportes Roxo...")
    login = os.environ.get("LOGIN")
    senha = os.environ.get("SENHA")

    driver = setup_driver()

    try:
        fazer_login(driver, login, senha)
        acessar_todos_esportes(driver)
        selecionar_modelo_roxo(driver)
        gerar_banners(driver)
        enviar_todas_as_imagens(driver)
        enviar_telegram("✅ *Banners Esportes Roxo gerados e enviados com sucesso!*")
        print("🎯 Finalizado com sucesso!")
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        enviar_telegram(f"❌ *Erro no script Esportes:* {e}")
        try:
            print(f"📍 URL atual: {driver.current_url}")
            print(f"📄 Trecho da página: {driver.find_element(By.TAG_NAME,'body').text[:400]}")
        except:
            pass
    finally:
        driver.quit()
        print("🔒 Navegador fechado.")

if __name__ == "__main__":
    main()
