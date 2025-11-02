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
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/130.0.0.0 Safari/537.36"
    )
    options.add_argument("--disable-blink-features=AutomationControlled")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_cdp_cmd("Network.setUserAgentOverride", {
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                     "AppleWebKit/537.36 (KHTML, like Gecko) "
                     "Chrome/130.0.0.0 Safari/537.36"
    })
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
    })
    print("✅ Chrome configurado com sucesso!")
    return driver


# ===============================================================
# 🔑 LOGIN
# ===============================================================
def fazer_login(driver, login, senha):
    print("🔑 Fazendo login no GERADOR PRO...")
    driver.get("https://gerador.pro/login.php")
    WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(login)
    driver.find_element(By.NAME, "password").send_keys(senha)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    WebDriverWait(driver, 20).until(lambda d: "index.php" in d.current_url)
    print("✅ Login realizado com sucesso!")


# ===============================================================
# 🏀 PÁGINA NBA
# ===============================================================
def ir_gerar_nba(driver):
    print("🏀 Indo para a página de geração NBA...")
    driver.get("https://gerador.pro/nba.php")
    WebDriverWait(driver, 10).until(lambda d: "nba" in d.current_url)
    print(f"✅ Página NBA aberta: {driver.current_url}")


# ===============================================================
# 🟣 GERAR BANNERS E BAIXAR LINKS
# ===============================================================
def gerar_banners(driver):
    print("🎨 Selecionando modelo 'Basquete Roxo'...")
    botao_roxo = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//*[contains(text(),'Basquete Roxo')]"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", botao_roxo)
    botao_roxo.click()
    print("✅ Clicou em 'Basquete Roxo'")

    WebDriverWait(driver, 15).until(lambda d: "modelo=27" in d.current_url)
    print(f"📄 Página do modelo carregada: {driver.current_url}")

    botao_gerar = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Gerar Banners')]"))
    )
    botao_gerar.click()
    print("⚙️ Clicou em 'Gerar Banners', aguardando popup...")

    popup_ok = WebDriverWait(driver, 25).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'OK')]"))
    )
    popup_ok.click()
    print("✅ Clicou em 'OK' do popup!")

    WebDriverWait(driver, 25).until(lambda d: "cartazes" in d.current_url)
    print(f"🖼️ Página de banners carregada: {driver.current_url}")

    # Captura todos os links de imagem
    print("🔍 Capturando links das imagens geradas...")
    time.sleep(3)
    imagens = driver.find_elements(By.XPATH, "//img[contains(@src, 'cartazes')]")
    urls = []
    for img in imagens:
        src = img.get_attribute("src")
        if src and "cartazes" in src and src.endswith(".png"):
            urls.append(src)

    print(f"✅ {len(urls)} imagens encontradas.")
    return urls


# ===============================================================
# 📤 ENVIAR AS IMAGENS PRO TELEGRAM
# ===============================================================
def enviar_imagens_telegram(urls):
    token = os.environ.get("BOT_TOKEN")
    chat_id = os.environ.get("CHAT_ID")
    if not token or not chat_id:
        print("⚠️ Bot Token ou Chat ID não configurados.")
        return

    for i, url in enumerate(urls, 1):
        try:
            print(f"📸 Enviando imagem {i}: {url}")
            response = requests.get(url)
            if response.status_code == 200:
                photo = response.content
                api_url = f"https://api.telegram.org/bot{token}/sendPhoto"
                files = {"photo": ("banner.png", photo)}
                data = {"chat_id": chat_id, "caption": f"🏀 Banner NBA {i}"}
                requests.post(api_url, data=data, files=files)
                time.sleep(2)
        except Exception as e:
            print(f"❌ Erro ao enviar imagem {i}: {e}")


# ===============================================================
# 🚀 FLUXO PRINCIPAL
# ===============================================================
def main():
    print("=" * 70)
    print("🚀 INICIANDO AUTOMAÇÃO NBA - GERADOR PRO")
    print(f"🕒 Executado em: {time.strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 70)

    login = os.environ.get("LOGIN")
    senha = os.environ.get("SENHA")

    driver = setup_driver()
    try:
        fazer_login(driver, login, senha)
        ir_gerar_nba(driver)
        urls = gerar_banners(driver)

        if urls:
            enviar_imagens_telegram(urls)
            enviar_telegram(f"🏀✅ Envio concluído: {len(urls)} banners NBA enviados com sucesso!")
        else:
            enviar_telegram("⚠️ Nenhum banner encontrado para envio!")

        print("=" * 70)
        print("✅ AUTOMAÇÃO NBA FINALIZADA COM SUCESSO!")
        print("=" * 70)

    except Exception as e:
        print("❌ ERRO DURANTE A EXECUÇÃO:", e)
        enviar_telegram(f"❌ Erro ao gerar banners NBA: {e}")
    finally:
        driver.quit()
        print("🔒 Navegador fechado")


# ===============================================================
# 📨 MENSAGEM SIMPLES TELEGRAM
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
        requests.post(url, data=data)
    except:
        pass


if __name__ == "__main__":
    main()
