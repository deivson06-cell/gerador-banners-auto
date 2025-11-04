import os, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    print("🔧 Configurando Chrome (modo headless)...")
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
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(login)
    driver.find_element(By.NAME, "password").send_keys(senha)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    WebDriverWait(driver, 15).until(lambda d: "index.php" in d.current_url)
    print("✅ Login realizado com sucesso!")

def ir_para_nba(driver):
    print("🏀 Acessando seção Gerar NBA...")
    driver.get("https://gerador.pro/nba.php")
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, "//h1 | //div[contains(text(),'Basquete')]")))
    print("✅ Página de modelos do NBA carregada!")

def selecionar_basquete_roxo(driver):
    print("🎨 Selecionando modelo Basquete Roxo...")
    try:
        elemento = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(text(),'Basquete Roxo') or contains(text(),'Roxo')]"))
        )
        driver.execute_script("arguments[0].click();", elemento)
        print("✅ Modelo Basquete Roxo selecionado!")
    except Exception as e:
        raise Exception(f"❌ Erro ao selecionar modelo Basquete Roxo: {e}")
    time.sleep(3)

def gerar_banners(driver):
    print("⚙️ Gerando banners do NBA...")
    
    try:
        botao = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Gerar Banners')]"))
        )
        driver.execute_script("arguments[0].click();", botao)
        print("🟠 Clique em 'Gerar Banners' realizado, aguardando processo...")

        # Espera aparecer o texto de carregamento “Gerando seus banners...”
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Gerando') or contains(text(),'aguarde')]"))
            )
            print("⏳ Tela de carregamento detectada.")
        except:
            print("⚠️ Não detectou tela de carregamento, continuando mesmo assim...")

        # Agora espera até 90s pelo popup de sucesso
        WebDriverWait(driver, 90).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Sucesso') or contains(text(),'Banners gerados')]"))
        )
        print("✅ Popup de sucesso detectado!")

        # Clica no botão OK
        try:
            ok_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'OK') or contains(text(),'Ok')]"))
            )
            driver.execute_script("arguments[0].click();", ok_btn)
            print("✅ Botão OK clicado com sucesso!")
        except:
            print("⚠️ Botão OK não encontrado, prosseguindo...")

    except Exception as e:
        raise Exception(f"❌ Falha ao gerar banners: {e}")

def enviar_para_telegram(driver):
    print("📤 Procurando botão 'Enviar todas as imagens'...")
    try:
        WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Enviar') or contains(text(),'Enviar todas')]"))
        ).click()
        print("🎉 Banners do NBA enviados para o Telegram!")
    except Exception as e:
        print(f"⚠️ Não foi possível clicar em Enviar: {e}")

def main():
    print("🚀 INICIANDO AUTOMAÇÃO NBA - GERADOR PRO")
    print(f"⏰ Início: {time.strftime('%d/%m/%Y %H:%M:%S')}")
    
    login = os.environ.get("LOGIN")
    senha = os.environ.get("SENHA")
    
    if not login or not senha:
        print("❌ LOGIN ou SENHA não configurados nas variáveis de ambiente!")
        return

    driver = setup_driver()
    try:
        fazer_login(driver, login, senha)
        ir_para_nba(driver)
        selecionar_basquete_roxo(driver)
        gerar_banners(driver)
        enviar_para_telegram(driver)
        print("✅ Fluxo NBA concluído com sucesso!")
    except Exception as e:
        print(f"❌ ERRO GERAL: {e}")
        try:
            print("📍 URL atual:", driver.current_url)
            print("📄 Conteúdo parcial:", driver.find_element(By.TAG_NAME, "body").text[:400])
        except:
            pass
    finally:
        driver.quit()
        print("🔒 Navegador fechado")

if __name__ == "__main__":
    main()
