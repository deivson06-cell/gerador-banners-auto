import os, time, requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException

# ===============================================================
# ⚙️ CONFIGURAÇÃO DO NAVEGADOR
# ===============================================================
def setup_driver():
    print("🔧 Configurando Chrome headless...")
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    # 🧩 Anti-bloqueio Cloudflare: user-agent + headers
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/130.0.0.0 Safari/537.36"
    )
    options.add_argument("--disable-blink-features=AutomationControlled")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_cdp_cmd(
        "Network.setUserAgentOverride",
        {"userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/130.0.0.0 Safari/537.36"}
    )
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": """
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        """}
    )
    print("✅ Chrome configurado com sucesso!")
    return driver


# ===============================================================
# 🔑 LOGIN
# ===============================================================
def fazer_login(driver, login, senha):
    print("🔑 Fazendo login no GERADOR PRO...")
    driver.get("https://gerador.pro/login.php")

    try:
        WebDriverWait(driver, 25).until(
            EC.presence_of_element_located((By.NAME, "username"))
        ).send_keys(login)
        driver.find_element(By.NAME, "password").send_keys(senha)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        WebDriverWait(driver, 20).until(lambda d: "index.php" in d.current_url)
        print("✅ Login realizado com sucesso!")
    except TimeoutException:
        raise Exception("🚫 Bloqueado pelo Cloudflare ou campos de login não encontrados!")


# ===============================================================
# 🏀 ABRIR PÁGINA NBA
# ===============================================================
def ir_gerar_nba(driver):
    print("🏀 Indo para a página de geração NBA...")
    try:
        driver.get("https://gerador.pro/nba.php")
        WebDriverWait(driver, 10).until(lambda d: "nba" in d.current_url)
        print(f"✅ Página NBA aberta: {driver.current_url}")
    except Exception as e:
        raise Exception(f"❌ Falha ao abrir página NBA: {e}")


# ===============================================================
# 🟣 GERAR BANNERS NBA (BASQUETE ROXO)
# ===============================================================
def gerar_banners(driver):
    print("🎨 Selecionando modelo 'Basquete Roxo'...")

    botao_roxo = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//*[contains(text(),'Basquete Roxo')]"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", botao_roxo)
    time.sleep(1)
    botao_roxo.click()
    print("✅ Clicou em 'Basquete Roxo'")

    WebDriverWait(driver, 15).until(lambda d: "modelo=27" in d.current_url)
    print(f"📄 Página do modelo carregada: {driver.current_url}")

    botao_gerar = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Gerar Banners')]"))
    )
    botao_gerar.click()
    print("⚙️ Clicou em 'Gerar Banners', aguardando popup...")

    try:
        popup_ok = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'OK')]"))
        )
        popup_ok.click()
        print("✅ Clicou em 'OK' do popup!")
    except TimeoutException:
        raise Exception("❌ Popup de sucesso não encontrado.")

    WebDriverWait(driver, 25).until(lambda d: "cartazes" in d.current_url)
    print(f"🖼️ Página de banners carregada: {driver.current_url}")

    enviar_btn = WebDriverWait(driver, 25).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Enviar Todas as Imagens')]"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", enviar_btn)
    time.sleep(1)
    enviar_btn.click()
    print("🎉 BANNERS NBA ENVIADOS COM SUCESSO PARA O TELEGRAM!")


# ===============================================================
# 📢 MENSAGEM TELEGRAM
# ===============================================================
def enviar_telegram(msg):
    token = os.environ.get("BOT_TOKEN")
    chat_id = os.environ.get("CHAT_ID")
    if not token or not chat_id:
        print("⚠️ Bot Token ou Chat ID não configurados.")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": msg, "parse_mode": "HTML"}
    try:
        r = requests.post(url, data=data)
        if r.status_code == 200:
            print("📨 Mensagem enviada ao Telegram!")
        else:
            print(f"⚠️ Telegram retornou status {r.status_code}: {r.text}")
    except Exception as e:
        print(f"❌ Falha ao enviar mensagem ao Telegram: {e}")


# ===============================================================
# 🚀 FLUXO PRINCIPAL
# ===============================================================
def main():
    print("="*70)
    print("🚀 INICIANDO AUTOMAÇÃO NBA - GERADOR PRO")
    print(f"🕒 Executado em: {time.strftime('%d/%m/%Y %H:%M:%S')}")
    print("="*70)

    login = os.environ.get("LOGIN")
    senha = os.environ.get("SENHA")

    if not login or not senha:
        print("❌ Credenciais não encontradas!")
        return

    driver = setup_driver()
    try:
        fazer_login(driver, login, senha)
        ir_gerar_nba(driver)
        gerar_banners(driver)
        enviar_telegram("🏀✅ Banners NBA gerados e enviados com sucesso para o canal!")
        print("="*70)
        print("✅ AUTOMAÇÃO NBA FINALIZADA COM SUCESSO!")
        print("="*70)
    except Exception as e:
        print("❌ ERRO DURANTE A EXECUÇÃO:", e)
        enviar_telegram(f"❌ Erro ao gerar banners NBA: {e}")
        try:
            print("📍 URL atual:", driver.current_url)
            print("📄 Página parcial:", driver.find_element(By.TAG_NAME, "body").text[:400])
        except Exception:
            pass
    finally:
        driver.quit()
        print("🔒 Navegador fechado")


if __name__ == "__main__":
    main()
