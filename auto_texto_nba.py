import os, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


# ===============================================================
# ⚙️ CONFIGURAÇÃO DO NAVEGADOR
# ===============================================================
def setup_driver():
    print("🔧 Configurando Chrome headless...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    print("✅ Chrome configurado com sucesso!")
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
# 🏀 ABRIR PÁGINA NBA
# ===============================================================
def ir_gerar_nba(driver):
    print("🏀 Indo para a página de geração NBA...")
    try:
        link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Gerar NBA')]"))
        )
        link.click()
        print("✅ Clicou em 'Gerar NBA'")
    except:
        driver.get("https://gerador.pro/nba.php")

    WebDriverWait(driver, 10).until(lambda d: "nba" in d.current_url)
    print(f"✅ Página NBA aberta: {driver.current_url}")


# ===============================================================
# 🟣 CLICAR EM BASQUETE ROXO → GERAR BANNERS → ENVIAR
# ===============================================================
def gerar_banners(driver):
    print("🎨 Selecionando modelo 'Basquete Roxo'...")

    # 1️⃣ clicar no modelo “Basquete Roxo”
    botao_roxo = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//*[contains(text(),'Basquete Roxo')]"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", botao_roxo)
    time.sleep(1)
    botao_roxo.click()
    print("✅ Clicou em 'Basquete Roxo'")

    # 2️⃣ aguardar redirecionamento do modelo
    WebDriverWait(driver, 15).until(lambda d: "modelo=27" in d.current_url)
    print(f"📄 Página do modelo carregada: {driver.current_url}")

    # 3️⃣ clicar em “Gerar Banners”
    botao_gerar = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Gerar Banners')]"))
    )
    botao_gerar.click()
    print("⚙️ Clicou em 'Gerar Banners', aguardando popup de sucesso...")

    # 4️⃣ popup de sucesso
    WebDriverWait(driver, 15).until(EC.alert_is_present())
    alerta = driver.switch_to.alert
    print(f"📢 Popup detectado: {alerta.text}")
    alerta.accept()
    print("✅ Popup confirmado (OK clicado)")

    # 5️⃣ aguardar redirecionamento para /futebol/cartazes/
    WebDriverWait(driver, 15).until(lambda d: "cartazes" in d.current_url)
    print(f"🖼️ Página de banners carregada: {driver.current_url}")

    # 6️⃣ clicar em “Enviar todas as imagens”
    enviar_btn = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Enviar Todas as Imagens')]"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", enviar_btn)
    time.sleep(1)
    enviar_btn.click()
    print("🎉 BANNERS NBA ENVIADOS COM SUCESSO PARA O TELEGRAM!")


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
        print("❌ Credenciais não encontradas nas variáveis de ambiente!")
        return

    driver = setup_driver()
    try:
        fazer_login(driver, login, senha)
        ir_gerar_nba(driver)
        gerar_banners(driver)
        print("="*70)
        print("✅ AUTOMAÇÃO NBA FINALIZADA COM SUCESSO!")
        print("="*70)
    except Exception as e:
        print("❌ ERRO DURANTE A EXECUÇÃO:", e)
        try:
            print("📍 URL atual:", driver.current_url)
            print("📄 Texto da página:", driver.find_element(By.TAG_NAME, "body").text[:400])
        except:
            pass
    finally:
        driver.quit()
        print("🔒 Navegador fechado")


if __name__ == "__main__":
    main()
