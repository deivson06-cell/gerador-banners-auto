import os, time, requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ===============================================================
# ⚙️ CONFIGURAÇÃO DO DRIVER
# ===============================================================
def setup_driver():
    print("🔧 Configurando Chrome...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    print("✅ Chrome configurado!")
    return driver

# ===============================================================
# 🔑 LOGIN
# ===============================================================
def fazer_login(driver, login, senha):
    print("🔑 Fazendo login no GERADOR PRO...")
    driver.get("https://gerador.pro/login.php")

    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(login)
    driver.find_element(By.NAME, "password").send_keys(senha)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    WebDriverWait(driver, 15).until(lambda d: "index.php" in d.current_url)
    print("✅ Login realizado com sucesso!")

# ===============================================================
# 🏀 IR PARA PÁGINA DE NBA
# ===============================================================
def ir_gerar_nba(driver):
    print("🏀 Acessando página de geração NBA...")
    time.sleep(2)

    # tenta clicar no menu "Gerar NBA"
    estrategias = [
        "//a[contains(text(),'Gerar NBA')]",
        "//a[contains(@href, 'nba.php')]",
        "//div[contains(text(),'Gerar NBA')]",
    ]

    for xpath in estrategias:
        try:
            elemento = driver.find_element(By.XPATH, xpath)
            elemento.click()
            print("✅ Clicou em 'Gerar NBA'")
            break
        except:
            continue

    # tenta URL direta se não clicou
    if "nba" not in driver.current_url.lower():
        driver.get("https://gerador.pro/nba.php")

    WebDriverWait(driver, 10).until(lambda d: "nba" in d.current_url)
    print(f"✅ Página NBA carregada: {driver.current_url}")

# ===============================================================
# 🎨 SELECIONAR OPÇÃO "BASQUETE ROXO" E GERAR BANNERS
# ===============================================================
def gerar_banners(driver):
    print("🎨 Procurando e clicando em 'Basquete Roxo'...")

    estrategias = [
        "//button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), 'basquete roxo')]",
        "//div[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), 'basquete roxo')]",
        "//span[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), 'basquete roxo')]",
        "//p[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), 'basquete roxo')]",
    ]

    clicado = False
    for xpath in estrategias:
        try:
            elemento = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath)))
            driver.execute_script("arguments[0].scrollIntoView(true);", elemento)
            time.sleep(1)
            elemento.click()
            print("✅ Clicou em 'Basquete Roxo'")
            clicado = True
            break
        except Exception as e:
            print(f"❌ Falhou: {e}")
            continue

    if not clicado:
        raise Exception("❌ Não foi possível clicar em 'Basquete Roxo'")

    # botão Gerar
    print("⏳ Aguardando botão 'Gerar Banners'...")
    botao_gerar = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Gerar')]"))
    )
    botao_gerar.click()
    print("🏗️ Gerando banners NBA...")

    # aguarda popup "Sucesso!"
    try:
        WebDriverWait(driver, 15).until(EC.alert_is_present())
        alerta = driver.switch_to.alert
        print(f"📢 Alerta: {alerta.text}")
        alerta.accept()
        print("✅ Popup confirmado")
    except:
        print("⚠️ Nenhum alerta de sucesso detectado")

    # clicar em "Enviar todas as imagens"
    print("📤 Procurando botão 'Enviar todas as imagens'...")
    enviar_btn = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Enviar todas as imagens')]"))
    )
    enviar_btn.click()
    print("🎉 Banners NBA enviados para o Telegram com sucesso!")

# ===============================================================
# 🚀 FLUXO PRINCIPAL
# ===============================================================
def main():
    print("="*70)
    print("🚀 INICIANDO AUTOMAÇÃO NBA - GERADOR PRO")
    print("⏰", time.strftime("%d/%m/%Y %H:%M:%S"))
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

        print("="*70)
        print("✅ PROCESSO NBA FINALIZADO COM SUCESSO!")
        print("="*70)

    except Exception as e:
        print("❌ ERRO DURANTE A EXECUÇÃO:", str(e))
        try:
            print("📍 URL atual:", driver.current_url)
            body = driver.find_element(By.TAG_NAME, "body").text
            print("📄 Página atual:", body[:400])
        except:
            pass
    finally:
        driver.quit()
        print("🔒 Navegador fechado")

# ===============================================================
if __name__ == "__main__":
    main()
