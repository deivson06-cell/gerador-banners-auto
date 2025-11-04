import os, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ------------------------------------------------------------
# CONFIGURAÇÃO DO NAVEGADOR
# ------------------------------------------------------------
def setup_driver():
    print("🔧 Configurando Chrome (modo headless)...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# ------------------------------------------------------------
# LOGIN
# ------------------------------------------------------------
def fazer_login(driver, login, senha):
    print("🔑 Fazendo login no GERADOR PRO...")
    driver.get("https://gerador.pro/login.php")
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(login)
    driver.find_element(By.NAME, "password").send_keys(senha)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    WebDriverWait(driver, 15).until(lambda d: "index.php" in d.current_url)
    print("✅ Login realizado com sucesso!")

# ------------------------------------------------------------
# ACESSA SEÇÃO GERAR FUTEBOL (COM CORREÇÃO)
# ------------------------------------------------------------
def ir_para_futebol(driver):
    print("⚽ Procurando e acessando 'Gerar Futebol'...")
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    time.sleep(2)

    try:
        botao = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Gerar Futebol') or contains(.,'Gerar Futebol')]"))
        )
        driver.execute_script("arguments[0].click();", botao)
        print("✅ Clique realizado no menu lateral!")

        # Aguarda a nova URL carregar
        for i in range(20):  # até 20 tentativas (~20 segundos)
            current_url = driver.current_url
            if "futbanner.php" in current_url and ("page=futebol" in current_url or "modelo" in current_url):
                print(f"✅ Página de geração carregada: {current_url}")
                break
            time.sleep(1)
        else:
            print("⚠️ URL não mudou, tentando navegação direta...")
            driver.get("https://gerador.pro/futbanner.php?page=futebol")
            time.sleep(3)

    except Exception as e:
        print(f"⚠️ Erro ao clicar no menu: {e}")
        print("➡️ Indo direto para página de geração...")
        driver.get("https://gerador.pro/futbanner.php?page=futebol")
        time.sleep(3)

    # Aguarda aparecer o cabeçalho ou os modelos
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//h1 | //div[contains(text(),'Modelo') or contains(text(),'Escolha')]"))
    )
    print("✅ Página de Futebol confirmada e carregada!")

# ------------------------------------------------------------
# SELECIONA MODELO 15
# ------------------------------------------------------------
def selecionar_modelo_15(driver):
    print("🎨 Selecionando modelo 15...")
    modelo = WebDriverWait(driver, 25).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(@href,'modelo=15')]"))
    )
    driver.execute_script("arguments[0].click();", modelo)
    print("✅ Modelo 15 selecionado!")
    time.sleep(3)

# ------------------------------------------------------------
# GERAR BANNERS
# ------------------------------------------------------------
def gerar_banners(driver):
    print("⚙️ Gerando banners...")
    botao = WebDriverWait(driver, 25).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Gerar Banners')]"))
    )
    driver.execute_script("arguments[0].click();", botao)
    print("🟠 Aguardando popup de sucesso...")

    WebDriverWait(driver, 90).until(
        EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Sucesso') or contains(text(),'Banners gerados')]"))
    )
    print("✅ Popup detectado!")

    try:
        ok_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'OK') or contains(text(),'Ok')]"))
        )
        driver.execute_script("arguments[0].click();", ok_btn)
        print("✅ Botão OK clicado, indo para galeria...")
    except:
        print("⚠️ Botão OK não encontrado, prosseguindo...")
    time.sleep(3)

# ------------------------------------------------------------
# ENVIAR TODAS AS IMAGENS PARA TELEGRAM
# ------------------------------------------------------------
def enviar_para_telegram(driver):
    print("📤 Preparando envio dos banners...")
    WebDriverWait(driver, 40).until(EC.url_contains("futebol/cartazes"))

    print("🕓 Aguardando carregamento da galeria...")
    for i in range(20):
        imagens = driver.find_elements(By.TAG_NAME, "img")
        if len(imagens) >= 2:
            print(f"🖼️ {len(imagens)} imagens encontradas (incluindo capa).")
            break
        time.sleep(3)

    botao_enviar = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Enviar') or contains(text(),'Enviar todas')]"))
    )
    driver.execute_script("arguments[0].click();", botao_enviar)
    print("📨 Enviando para o Telegram...")

    for _ in range(40):
        try:
            if not botao_enviar.is_displayed():
                print("✅ Envio concluído!")
                break
        except:
            print("✅ Envio finalizado.")
            break
        time.sleep(3)

# ------------------------------------------------------------
# EXECUÇÃO PRINCIPAL
# ------------------------------------------------------------
def main():
    print("🚀 Iniciando Automação de Futebol...")
    print(f"⏰ Horário: {time.strftime('%d/%m/%Y %H:%M:%S')}")

    login = os.environ.get("LOGIN")
    senha = os.environ.get("SENHA")

    if not login or not senha:
        print("❌ LOGIN ou SENHA não configurados nas variáveis de ambiente!")
        return

    driver = setup_driver()
    try:
        fazer_login(driver, login, senha)
        ir_para_futebol(driver)
        selecionar_modelo_15(driver)
        gerar_banners(driver)
        enviar_para_telegram(driver)
        print("🎉 Processo concluído com sucesso! Verifique seu canal no Telegram.")
    except Exception as e:
        print(f"❌ ERRO GERAL: {e}")
        try:
            print(f"📍 URL atual: {driver.current_url}")
            print("📄 Conteúdo parcial:", driver.find_element(By.TAG_NAME, "body").text[:400])
        except:
            pass
    finally:
        driver.quit()
        print("🔒 Navegador fechado")

# ------------------------------------------------------------
if __name__ == "__main__":
    main()
