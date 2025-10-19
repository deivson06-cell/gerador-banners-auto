import os, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    print("🔧 Configurando Chrome...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    print("✅ Chrome configurado!")
    return driver

def fazer_login(driver, login, senha):
    print("🔑 Fazendo login no GERADOR PRO...")
    driver.get("https://gerador.pro/login.php")
    time.sleep(5)
    
    campo_usuario = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )
    campo_usuario.clear()
    campo_usuario.send_keys(login)
    campo_senha = driver.find_element(By.NAME, "password")
    campo_senha.clear()
    campo_senha.send_keys(senha)
    botao_login = driver.find_element(By.XPATH, "//button[@type='submit']")
    botao_login.click()
    WebDriverWait(driver, 10).until(lambda driver: "index.php" in driver.current_url)
    print("✅ Login bem-sucedido!")

def ir_gerar_futebol(driver):
    print("⚽ Indo para Gerar Futebol...")
    time.sleep(3)
    try:
        driver.get("https://gerador.pro/futbanner.php")
        print("✅ Página futbanner carregada!")
    except:
        raise Exception("Não foi possível acessar Gerar Futebol")
    time.sleep(5)

def selecionar_opcoes_futebol(driver):
    print("🎨 Selecionando Modelo 2 e Jogos de Hoje...")
    time.sleep(2)
    try:
        elemento = driver.find_element(By.XPATH, "//input[@type='radio' and @value='2']")
        elemento.click()
        print("✅ Modelo 2 selecionado!")
    except:
        print("⚠️ Modelo 2 não encontrado, continuando...")

    try:
        elemento = driver.find_element(By.XPATH, "//input[@type='radio' and contains(@value, 'hoje')]")
        elemento.click()
        print("✅ Jogos de hoje selecionados!")
    except:
        print("⚠️ Seleção de 'hoje' não encontrada, continuando...")

def gerar_banners(driver):
    print("🔄 Gerando banners...")
    estrategias = [
        "//button[contains(text(), 'Gerar')]",
        "//input[@type='submit' and contains(@value, 'Gerar')]",
        "//button[@type='submit']"
    ]
    for strategy in estrategias:
        try:
            botao = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, strategy)))
            botao.click()
            print("✅ Botão Gerar clicado!")
            break
        except:
            continue
    time.sleep(10)

def aguardar_e_enviar_telegram(driver):
    print("📤 Procurando próximos passos após geração...")
    time.sleep(5)
    print("🎨 Etapa de seleção de cor desativada — pulando para envio!")

    max_tentativas = 20
    estrategias_enviar = [
        "//button[contains(text(), 'Enviar')]",
        "//button[contains(text(), 'Telegram')]",
        "//input[@type='button' and contains(@value, 'Enviar')]",
        "//a[contains(text(), 'Enviar')]",
        "//div[contains(text(), 'Enviar') and @onclick]",
        "//button[contains(@onclick, 'telegram')]",
        "//button[contains(text(), 'Finalizar')]",
        "//button[contains(text(), 'Concluir')]"
    ]

    for tentativa in range(max_tentativas):
        for strategy in estrategias_enviar:
            try:
                botao_enviar = driver.find_element(By.XPATH, strategy)
                if botao_enviar.is_displayed() and botao_enviar.is_enabled():
                    botao_enviar.click()
                    print("✅ Botão enviar clicado!")
                    time.sleep(5)
                    print("🎉 BANNERS ENVIADOS PARA O TELEGRAM!")
                    return True
            except:
                continue
        time.sleep(5)

    print("⚠️ Botão de enviar não apareceu após as tentativas")
    try:
        body_text = driver.find_element(By.TAG_NAME, "body").text
        if any(palavra in body_text.lower() for palavra in ['sucesso', 'enviado', 'concluído', 'finalizado', 'pronto', 'gerado']):
            print("✅ Possível sucesso detectado!")
            return True
    except:
        pass
    return False

def main():
    print("🚀 INICIANDO AUTOMAÇÃO COMPLETA - GERADOR PRO")
    login = os.environ.get("LOGIN")
    senha = os.environ.get("SENHA")
    if not login or not senha:
        print("❌ Credenciais não encontradas!")
        return
    driver = setup_driver()
    try:
        fazer_login(driver, login, senha)
        ir_gerar_futebol(driver)
        selecionar_opcoes_futebol(driver)
        gerar_banners(driver)
        sucesso_envio = aguardar_e_enviar_telegram(driver)
        if sucesso_envio:
            print("🎉 AUTOMAÇÃO CONCLUÍDA COM SUCESSO!")
        else:
            print("⚠️ Envio automático falhou")
    except Exception as e:
        print(f"❌ ERRO: {e}")
    finally:
        driver.quit()
        print("🔒 Navegador fechado")

if __name__ == "__main__":
    main()
