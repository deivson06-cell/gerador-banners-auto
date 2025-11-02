import time, os, requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ==========================
# 🔧 CONFIGURAÇÃO DO CHROME
# ==========================
def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver


# ==========================
# 💬 ENVIO AO TELEGRAM
# ==========================
def enviar_telegram(texto):
    token = "7872091942:AAHbvXRGtdomQxgyKDAkuk1SoLULx0B9xEg"
    chat_id = "-1002169364087"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": texto,
        "parse_mode": "Markdown"
    }
    r = requests.post(url, data=payload)
    print("📨 Envio para Telegram:", r.status_code)
    if r.status_code != 200:
        print("❌ Erro ao enviar:", r.text)


# ==========================
# 🚀 FLUXO PRINCIPAL
# ==========================
def main():
    print("🚀 Iniciando captura de texto dos jogos...")
    driver = setup_driver()
    driver.get("https://gerador.pro/login.php")

    try:
        # Espera campo de login aparecer (campo de usuário ou e-mail)
        login_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((
                By.XPATH, "//input[@type='text' or @type='email' or contains(@placeholder, 'Usu') or contains(@placeholder, 'Email')]"
            ))
        )
        login_field.send_keys("deivson06")

        # Campo de senha
        senha_field = driver.find_element(
            By.XPATH, "//input[@type='password' or contains(@placeholder, 'Senha')]"
        )
        senha_field.send_keys("F9416280")

        # Botão de login
        botao_login = driver.find_element(
            By.XPATH, "//button[contains(., 'Entrar') or contains(., 'Login') or @type='submit']"
        )
        botao_login.click()
        print("✅ Login realizado!")

        # Ir até a página de Futebol
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Gerar Futebol"))
        ).click()
        print("⚽ Página de Futebol aberta")

        # Espera botão "Copiar texto" aparecer
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Copiar texto')]"))
        )
        time.sleep(2)

        # Tenta capturar o conteúdo do campo
        texto = ""
        try:
            texto = driver.find_element(By.ID, "textoCopiado").get_attribute("value")
        except:
            try:
                texto = driver.find_element(By.TAG_NAME, "textarea").get_attribute("value")
            except:
                print("⚠️ Não encontrou campo de texto.")
        
        if texto:
            print("📝 Texto capturado:")
            print(texto[:400], "...")
            enviar_telegram(texto)
            print("✅ Texto enviado com sucesso!")
        else:
            print("⚠️ Nenhum texto encontrado para enviar.")

    except Exception as e:
        print(f"❌ Erro geral: {e}")

    finally:
        driver.quit()
        print("🔒 Navegador fechado.")


if __name__ == "__main__":
    main()
