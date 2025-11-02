import time, os, requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)

def enviar_telegram(texto):
    token = "7872091942:AAHbvXRGtdomQxgyKDAkuk1SoLULx0B9xEg"
    chat_id = "-1002169364087"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": texto, "parse_mode": "Markdown"}
    r = requests.post(url, data=data)
    print("📨 Envio Telegram:", r.status_code)
    if r.status_code != 200:
        print("❌ Erro:", r.text)

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

        # botão copiar texto
        copiar_btn = WebDriverWait(driver, 25).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Copiar texto')]"))
        )
        driver.execute_script("arguments[0].click();", copiar_btn)
        print("📋 Botão 'Copiar texto' clicado")

        # executa JS pra ler o conteúdo da área de transferência
        time.sleep(2)
        texto = driver.execute_script("""
            return navigator.clipboard.readText()
                .then(t => t)
                .catch(e => '');
        """)

        # fallback se o navegador não permitir clipboard API
        if not texto:
            print("⚠️ Clipboard API não retornou texto. Tentando capturar via DOM alternativo...")
            elementos = driver.find_elements(By.XPATH, "//textarea | //pre | //div | //p")
            for el in elementos:
                val = el.get_attribute("value") or el.text
                if val and "📆" in val:
                    texto = val
                    break

        if texto:
            print("📝 Texto copiado com sucesso:")
            print(texto[:400], "...")
            enviar_telegram(texto)
        else:
            print("⚠️ Nenhum texto capturado — pode ter falhado o acesso ao clipboard.")

    except Exception as e:
        print("❌ Erro geral:", e)
    finally:
        driver.quit()
        print("🔒 Navegador fechado.")

if __name__ == "__main__":
    main()
