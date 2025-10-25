import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options

# ==========================
# CONFIGURAÇÕES
# ==========================
GERADOR_URL = "https://gerador.pro/"

# As credenciais são lidas automaticamente das variáveis secretas do GitHub Actions
USUARIO = os.getenv("GERADOR_USER")
SENHA = os.getenv("GERADOR_PASS")

if not USUARIO or not SENHA:
    print("❌ ERRO: As variáveis de ambiente GERADOR_USER e GERADOR_PASS não foram definidas.")
    print("Adicione-as nos Secrets do repositório em: Settings → Secrets → Actions.")
    exit(1)

# ==========================
# FUNÇÃO LOGIN
# ==========================
def login_gerador(driver):
    print("🔑 Fazendo login no Gerador Pro...")
    driver.get(GERADOR_URL)
    time.sleep(4)

    try:
        campo_email = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='email']"))
        )
        campo_senha = driver.find_element(By.XPATH, "//input[@type='password']")
        botao_login = driver.find_element(By.XPATH, "//button[contains(text(), 'Entrar')]")

        campo_email.send_keys(USUARIO)
        campo_senha.send_keys(SENHA)
        botao_login.click()

        print("✅ Login realizado com sucesso!")
    except Exception as e:
        print(f"❌ Falha no login: {e}")
        return False

    time.sleep(6)
    return True

# ==========================
# ACESSAR MENU GERAR FUTEBOL
# ==========================
def abrir_menu_futebol(driver):
    print("⚽ Acessando 'Gerar Futebol'...")
    try:
        menu = WebDriverWait(driver, 25).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Gerar Futebol')]"))
        )
        driver.execute_script("arguments[0].click();", menu)
        print("✅ Menu 'Gerar Futebol' aberto!")
    except Exception as e:
        print(f"❌ Erro ao abrir menu: {e}")
        return False

    time.sleep(5)
    return True

# ==========================
# SELECIONAR MODELO 15
# ==========================
def selecionar_modelo_15(driver):
    print("🎨 Selecionando modelo 15...")
    try:
        modelo = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@type='radio' and @value='15']"))
        )
        driver.execute_script("arguments[0].click();", modelo)
        print("✅ Modelo 15 selecionado.")
    except Exception as e:
        print(f"⚠️ Erro ao selecionar modelo 15: {e}")
        return False

    time.sleep(1)
    return True

# ==========================
# GERAR BANNERS
# ==========================
def gerar_banners(driver):
    print("🖼️ Gerando banners...")
    try:
        botao = WebDriverWait(driver, 25).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Gerar Banners')]"))
        )
        driver.execute_script("arguments[0].click();", botao)
        print("✅ 'Gerar Banners' clicado!")
    except Exception as e:
        print(f"❌ Erro ao clicar em 'Gerar Banners': {e}")
        return False

    print("⏳ Aguardando geração...")
    time.sleep(12)
    return True

# ==========================
# ENVIAR PARA TELEGRAM
# ==========================
def enviar_para_telegram(driver):
    print("📤 Preparando envio...")

    try:
        ok_btn = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'OK')]"))
        )
        driver.execute_script("arguments[0].click();", ok_btn)
        print("✅ Botão 'OK' clicado!")
    except Exception as e:
        print(f"⚠️ Botão 'OK' não encontrado: {e}")

    try:
        enviar_btn = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Enviar todas imagens')]"))
        )
        driver.execute_script("arguments[0].click();", enviar_btn)
        print("✅ Botão 'Enviar todas imagens' clicado!")
    except Exception as e:
        print(f"❌ Falha ao clicar em 'Enviar todas imagens': {e}")
        return False

    print("⏳ Aguardando envio...")
    time.sleep(10)
    driver.save_screenshot("debug_envio_github.png")
    print("📸 Screenshot salva: debug_envio_github.png")
    print("🎉 Envio finalizado com sucesso!")
    return True

# ==========================
# MAIN
# ==========================
def main():
    print("🚀 Iniciando automação no Gerador Pro (modo headless)...")

    options = Options()
    options.add_argument("--headless")  # Necessário para rodar no GitHub
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service()
    driver = webdriver.Edge(service=service, options=options)

    try:
        if not login_gerador(driver):
            return
        if not abrir_menu_futebol(driver):
            return
        if not selecionar_modelo_15(driver):
            return
        if not gerar_banners(driver):
            return
        enviar_para_telegram(driver)
    finally:
        driver.quit()
        print("✅ Processo concluído e navegador encerrado.")

# ==========================
# EXECUÇÃO
# ==========================
if __name__ == "__main__":
    main()
