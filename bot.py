import os
import time
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ==========================
# 🔔 CONFIGURAÇÕES TELEGRAM
# ==========================
TELEGRAM_BOT_TOKEN = "8032336208:AAGVgZoOqxuoaKLv56QJX4A9DirBXQEjbSU"       # <- Cole seu token do bot aqui
TELEGRAM_CHAT_ID = "-1002169364087"        # Seu canal

def enviar_telegram(mensagem):
    """Envia mensagem para o canal via bot do Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": mensagem}
        requests.post(url, data=data)
        print("📤 Mensagem enviada para o Telegram!")
    except Exception as e:
        print(f"⚠️ Erro ao enviar mensagem para o Telegram: {e}")

def salvar_print(driver, etapa):
    pasta = "prints"
    os.makedirs(pasta, exist_ok=True)
    nome_arquivo = f"{pasta}/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{etapa}.png"
    driver.save_screenshot(nome_arquivo)
    print(f"📸 Print salvo: {nome_arquivo}")
    return nome_arquivo

# ==========================
# ⚙️ Setup Chrome
# ==========================
def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# ==========================
# 🔑 Login
# ==========================
def fazer_login(driver, login, senha):
    driver.get("https://gerador.pro/login.php")
    time.sleep(5)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(login)
    driver.find_element(By.NAME, "password").send_keys(senha)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    WebDriverWait(driver, 15).until(lambda d: "index.php" in d.current_url)
    print("✅ Login bem-sucedido")

# ==========================
# ⚽ Ir para Gerar Futebol
# ==========================
def ir_gerar_futebol(driver):
    try:
        botao = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Gerar Futebol')]"))
        )
        botao.click()
    except:
        driver.get("https://gerador.pro/futbanner.php")
    WebDriverWait(driver, 10).until(lambda d: "futbanner" in d.current_url)
    print("✅ Página de Futebol aberta")

# ==========================
# 🎨 Selecionar Modelo 15
# ==========================
def selecionar_opcoes_futebol(driver):
    estrategias = [
        "//input[@type='radio' and @value='15']",
        "//select//option[@value='15']",
        "//select//option[contains(text(), '15')]",
    ]
    for x in estrategias:
        try:
            el = driver.find_element(By.XPATH, x)
            driver.execute_script("arguments[0].scrollIntoView(true);", el)
            el.click()
            print("✅ Modelo 15 selecionado")
            return
        except:
            continue
    print("⚠️ Modelo 15 não encontrado")

# ==========================
# 🔄 Gerar banners
# ==========================
def gerar_banners(driver):
    botoes = [
        "//button[contains(text(), 'Gerar')]",
        "//input[@type='submit' and contains(@value, 'Gerar')]",
    ]
    for b in botoes:
        try:
            el = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, b)))
            el.click()
            print("✅ Botão 'Gerar' clicado")
            return
        except:
            continue
    raise Exception("Botão 'Gerar' não encontrado")

# ==========================
# 🟢 Confirmar Sucesso e Enviar
# ==========================
def confirmar_sucesso_e_enviar(driver):
    try:
        WebDriverWait(driver, 40).until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Sucesso"))
        print("🎉 Banners gerados com sucesso")
    except:
        print("⚠️ Mensagem de sucesso não detectada")

    # Botão OK
    try:
        ok_btn = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'OK')]")))
        ok_btn.click()
        print("✅ Botão OK clicado")
    except:
        print("⚠️ Botão OK não encontrado")

    time.sleep(3)
    # Botão Enviar todas as imagens
    try:
        enviar_btn = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Enviar todas')]")))
        enviar_btn.click()
        print("✅ Botão 'Enviar todas as imagens' clicado")
    except Exception as e:
        caminho = salvar_print(driver, "erro_enviar")
        enviar_telegram(f"❌ Erro ao clicar em 'Enviar todas as imagens'. Print: {caminho}")
        raise e

# ==========================
# 🚀 Principal
# ==========================
def main():
    login = os.environ.get("LOGIN")
    senha = os.environ.get("SENHA")
    if not login or not senha:
        print("❌ LOGIN ou SENHA não configurados nas variáveis de ambiente")
        return

    driver = setup_driver()
    try:
        fazer_login(driver, login, senha)
        ir_gerar_futebol(driver)
        selecionar_opcoes_futebol(driver)
        gerar_banners(driver)
        confirmar_sucesso_e_enviar(driver)
        enviar_telegram("✅ Banners de futebol gerados e enviados com sucesso!")
    except Exception as e:
        caminho = salvar_print(driver, "erro_geral")
        enviar_telegram(f"❌ Erro geral no script: {e}. Print: {caminho}")
    finally:
        driver.quit()
        print("🔒 Navegador fechado")

if __name__ == "__main__":
    main()
✅ Passos finais:
Cole seu token do bot no TELEGRAM_BOT_TOKEN = "8032336208:AAGVgZoOqxuoaKLv56QJX4A9DirBXQEjbSU"

Configure suas variáveis de ambiente LOGIN e SENHA com seu usuário do site:

bash
Copiar código
export LOGIN="seu_usuario"
export SENHA="sua_senha"
(ou no Windows use set LOGIN=seu_usuario)

Instale dependências:

bash
Copiar código
pip install selenium webdriver_manager requests
Rode:

bash
Copiar código
python nome_do_arquivo.py
