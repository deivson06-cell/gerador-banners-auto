import os
import time
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
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
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
    try:
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            print("✅ Mensagem enviada ao Telegram!")
        else:
            print(f"⚠️ Falha ao enviar Telegram: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Erro ao enviar Telegram: {e}")

def fazer_login(driver, login, senha):
    print("🔑 Fazendo login no GERADOR PRO...")
    driver.get("https://gerador.pro/login.php")
    
    # Aguarda carregamento completo da página
    time.sleep(2)
    
    username_field = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )
    username_field.clear()
    username_field.send_keys(login)
    
    password_field = driver.find_element(By.NAME, "password")
    password_field.clear()
    password_field.send_keys(senha)
    
    submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    driver.execute_script("arguments[0].click();", submit_button)
    
    # Aguarda redirecionamento após login
    WebDriverWait(driver, 15).until(
        lambda d: "index.php" in d.current_url or "painel" in d.current_url or "esportes" in d.current_url
    )
    print("✅ Login realizado com sucesso!")

def acessar_todos_esportes(driver):
    print("🏆 Acessando menu 'Todos esportes'...")
    
    # Aguarda página carregar completamente
    time.sleep(3)
    
    try:
        # Tenta encontrar e clicar no link
        link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(text(),'Todos esportes') or contains(@href,'esportes.php')]"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", link)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", link)
        print("✅ Clicou em 'Todos esportes'")
    except Exception as e:
        print(f"⚠️ Falhou ao clicar no menu, acessando URL direta: {e}")
        driver.get("https://gerador.pro/esportes.php")
    
    # Aguarda página de esportes carregar
    WebDriverWait(driver, 20).until(
        lambda d: "esportes.php" in d.current_url
    )
    time.sleep(2)
    print("✅ Página de esportes carregada!")

def selecionar_modelo_roxo(driver):
    print("🎨 Selecionando modelo 'Esportes Roxo'...")
    
    # Aguarda elementos carregarem
    time.sleep(3)
    
    try:
        # Scroll para garantir que o elemento está visível
        driver.execute_script("window.scrollTo(0, 300);")
        time.sleep(1)
        
        # Tenta diferentes seletores para o modelo roxo
        xpaths = [
            "//div[contains(text(),'Esportes Roxo')]",
            "//div[contains(text(),'Roxo')]",
            "//button[contains(text(),'Roxo')]",
            "//*[contains(@class,'modelo') and contains(text(),'Roxo')]"
        ]
        
        modelo = None
        for xpath in xpaths:
            try:
                modelo = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                if modelo:
                    break
            except:
                continue
        
        if modelo:
            driver.execute_script("arguments[0].scrollIntoView(true);", modelo)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", modelo)
            print("✅ Modelo 'Roxo' selecionado!")
            time.sleep(2)
        else:
            raise Exception("Modelo Roxo não encontrado com nenhum seletor")
            
    except Exception as e:
        print(f"⚠️ Falhou ao selecionar modelo, tentando URL direta: {e}")
        driver.get("https://gerador.pro/esportes.php?modelo=roxo")
        time.sleep(3)

def gerar_banners(driver):
    print("⚙️ Gerando banners...")
    
    # Aguarda página carregar
    time.sleep(2)
    
    # Scroll até o botão
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)
    
    botao = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, "//button[contains(text(),'Gerar Banners') or contains(text(),'Gerar banners')]"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", botao)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", botao)
    print("✅ Botão 'Gerar Banners' clicado!")

    # Aguarda processamento
    time.sleep(5)

    # Espera popup de sucesso ou redirecionamento
    try:
        popup_ok = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'OK') or contains(text(),'Ok')]"))
        )
        print("🎉 Sucesso detectado! Clicando em OK...")
        driver.execute_script("arguments[0].click();", popup_ok)
        time.sleep(2)
    except Exception as e:
        print(f"⚠️ Popup não encontrado (pode já ter redirecionado): {e}")

def enviar_todas_as_imagens(driver):
    print("📤 Enviando todas as imagens...")
    
    # Aguarda redirecionamento para página de cartazes
    WebDriverWait(driver, 25).until(
        lambda d: "cartazes" in d.current_url or "cartaz" in d.current_url
    )
    time.sleep(3)
    
    # Scroll até o botão
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)
    
    try:
        botao_enviar = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(text(),'Enviar Todas') or contains(text(),'Enviar todas') or contains(text(),'Enviar tudo')]"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", botao_enviar)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", botao_enviar)
        print("✅ Botão 'Enviar Todas as Imagens' clicado!")
        time.sleep(8)
    except Exception as e:
        print(f"⚠️ Erro ao clicar em enviar todas: {e}")
        raise

def main():
    print("🚀 Iniciando automação Esportes Roxo...")
    
    # Validação de variáveis de ambiente
    login = os.environ.get("LOGIN")
    senha = os.environ.get("SENHA")
    
    if not login or not senha:
        print("❌ LOGIN ou SENHA não configurados nas variáveis de ambiente!")
        enviar_telegram("❌ *Erro:* LOGIN ou SENHA não configurados!")
        return
    
    driver = None
    
    try:
        driver = setup_driver()
        fazer_login(driver, login, senha)
        acessar_todos_esportes(driver)
        selecionar_modelo_roxo(driver)
        gerar_banners(driver)
        enviar_todas_as_imagens(driver)
        enviar_telegram("✅ *Banners Esportes Roxo gerados e enviados com sucesso!*")
        print("🎯 Finalizado com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        enviar_telegram(f"❌ *Erro no script Esportes:*\n`{str(e)[:200]}`")
        
        # Salva screenshot em caso de erro
        if driver:
            try:
                driver.save_screenshot("erro_screenshot.png")
                print("📸 Screenshot salvo como 'erro_screenshot.png'")
            except:
                pass
    
    finally:
        if driver:
            driver.quit()
            print("🔒 Navegador fechado.")

if __name__ == "__main__":
    main()
