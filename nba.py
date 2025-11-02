import os, time, requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# ==========================
# CONFIGURAÇÕES
# ==========================
LOGIN = os.getenv("LOGIN")
SENHA = os.getenv("SENHA")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not all([LOGIN, SENHA, BOT_TOKEN, CHAT_ID]):
    print("❌ ERRO: Variáveis de ambiente obrigatórias não configuradas!")
    print("Configure: TELEGRAM_BOT_TOKEN, CHAT_ID, LOGIN, SENHA")
    exit(1)

# ==========================
# FUNÇÕES AUXILIARES
# ==========================

def setup_driver():
    print("🚀 Iniciando navegador headless...")
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def enviar_telegram(msg, img_path=None):
    try:
        if img_path and os.path.exists(img_path):
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
            with open(img_path, "rb") as photo:
                files = {"photo": photo}
                data = {"chat_id": CHAT_ID, "caption": msg, "parse_mode": "Markdown"}
                r = requests.post(url, data=data, files=files)
        else:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            data = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
            r = requests.post(url, data=data)
        print(f"📤 Mensagem enviada: {r.status_code}")
    except Exception as e:
        print(f"⚠️ Erro ao enviar mensagem: {e}")

def salvar_print(driver, nome):
    os.makedirs("prints", exist_ok=True)
    path = f"prints/{time.strftime('%Y%m%d_%H%M%S')}_{nome}.png"
    driver.save_screenshot(path)
    print(f"📸 Print salvo: {path}")
    return path

# ==========================
# FLUXO PRINCIPAL
# ==========================

def main():
    driver = setup_driver()
    try:
        print("🌐 Acessando site...")
        driver.get("https://gerador.pro/login.php")

        # LOGIN
        print("🔐 Fazendo login...")
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(LOGIN)
        driver.find_element(By.NAME, "password").send_keys(SENHA)
        driver.find_element(By.XPATH, "//button[contains(text(),'Entrar no painel')]").click()

        # ABRIR BASQUETE ROXO
        print("🏀 Acessando Basquete Roxo...")
        WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.LINK_TEXT, "Basquete Roxo"))).click()

        # AGUARDAR PÁGINA DO MODELO
        WebDriverWait(driver, 20).until(EC.url_contains("nba.php"))

        # CLICAR EM GERAR BANNERS
        print("🖼️ Gerando banners...")
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "generateButton"))).click()

        # CONFIRMAR POPUP DE SUCESSO
        WebDriverWait(driver, 20).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        print(f"✅ Mensagem: {alert.text}")
        alert.accept()

        # ESPERAR REDIRECIONAMENTO
        WebDriverWait(driver, 20).until(EC.url_contains("cartazes"))
        print("📂 Acessando galeria de banners...")

        # CLICAR EM ENVIAR TODAS AS IMAGENS
        enviar_todas = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Enviar Todas as Imagens')]"))
        )
        enviar_todas.click()
        print("📤 Enviando todas as imagens...")

        # PRINT FINAL
        caminho = salvar_print(driver, "nba_enviadas")
        enviar_telegram("✅ *Banners da NBA gerados e enviados com sucesso!*", caminho)

    except Exception as e:
        print(f"❌ Erro durante execução: {e}")
        caminho = salvar_print(driver, "erro_nba")
        enviar_telegram(f"⚠️ Erro na automação NBA: {e}", caminho)
    finally:
        driver.quit()
        print("🔒 Navegador fechado.")

# ==========================
# EXECUÇÃO
# ==========================
if __name__ == "__main__":
    main()
