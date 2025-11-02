import time, os, requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ==========================
# 🔧 Configuração do Chrome
# ==========================
def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# ======================================
# 💬 Envio do texto formatado ao Telegram
# ======================================
def enviar_telegram(texto):
    token = "7872091942:AAHbvXRGtdomQxgyKDAkuk1SoLULx0B9xEg"
    chat_id = "-1002169364087"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": texto,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, data=payload)
    print("📨 Envio para Telegram:", response.status_code)

# ======================
# 🚀 Fluxo principal
# ======================
def main():
    print("🚀 Iniciando captura de texto dos jogos...")
    driver = setup_driver()
    driver.get("https://gerador.pro/login.php")

    # Login
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys("deivson06")
    driver.find_element(By.NAME, "password").send_keys("F9416280")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    print("✅ Login realizado!")

    # Ir até a página de futebol
    WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.LINK_TEXT, "Gerar Futebol"))).click()
    print("⚽ Página de Futebol aberta")

    # Espera o botão de copiar texto aparecer
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Copiar texto')]"))
        )
        time.sleep(2)

        # Captura o conteúdo do campo de texto
        try:
            texto = driver.find_element(By.ID, "textoCopiado").get_attribute("value")
        except:
            texto = driver.find_element(By.TAG_NAME, "textarea").get_attribute("value")

        if texto:
            print("📝 Texto capturado com sucesso!")
            print(texto[:300], "...")
            enviar_telegram(texto)
        else:
            print("⚠️ Nenhum texto encontrado no site.")

    except Exception as e:
        print("❌ Erro ao capturar texto:", e)

    driver.quit()
    print("🔒 Navegador fechado.")

if __name__ == "__main__":
    main()
