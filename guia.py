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
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    return driver

# ==========================
# 💬 ENVIO AO TELEGRAM
# ==========================
def enviar_telegram(texto):
    token = "7872091942:AAHbvXRGtdomQxgyKDAkuk1SoLULx0B9xEg"
    chat_id = "-1002169364087"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": texto, "parse_mode": "Markdown"}
    r = requests.post(url, data=data)
    print("📨 Envio Telegram:", r.status_code)
    if r.status_code != 200:
        print("❌ Erro ao enviar:", r.text)

# ==========================
# 🚀 FLUXO PRINCIPAL
# ==========================
def main():
    print("🚀 Iniciando captura do texto dos jogos...")
    driver = setup_driver()
    driver.get("https://gerador.pro/login.php")

    try:
        # login
        user = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((
                By.XPATH, "//input[@type='text' or @type='email' or contains(@placeholder,'Usu') or contains(@placeholder,'Email')]"
            ))
        )
        user.send_keys("deivson06")

        pwd = driver.find_element(By.XPATH, "//input[@type='password' or contains(@placeholder,'Senha')]")
        pwd.send_keys("F9416280")

        driver.find_element(By.XPATH, "//button[contains(.,'Entrar') or contains(.,'Login') or @type='submit']").click()
        print("✅ Login realizado!")

        # ir para página de futebol
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.LINK_TEXT, "Gerar Futebol"))).click()
        print("⚽ Página Futebol aberta")

        # aguarda botão "Copiar texto"
        botao_copiar = WebDriverWait(driver, 25).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Copiar texto')]"))
        )
        print("📋 Botão 'Copiar texto' encontrado")

        # tenta pegar o conteúdo do botão
        texto = (
            botao_copiar.get_attribute("data-clipboard-text")
            or botao_copiar.get_attribute("onclick")
            or botao_copiar.text
        )

        if texto and len(texto.strip()) > 10:
            print("📝 Texto capturado diretamente do botão:")
            print(texto[:400], "...")
            enviar_telegram(texto)
        else:
            print("⚠️ Nenhum texto encontrado dentro do botão. Pode ser que o site gere o texto após outra ação.")

    except Exception as e:
        print("❌ Erro geral:", e)
    finally:
        driver.quit()
        print("🔒 Navegador fechado.")

if __name__ == "__main__":
    main()
