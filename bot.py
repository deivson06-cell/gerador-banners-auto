import os, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
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
    driver.get("https://geradorpro.com/login")
    time.sleep(5)
    
    # Campo email - múltiplas tentativas
    email_selectors = [
        "input[name='email']",
        "input[type='email']", 
        "input[id='email']",
        "input[placeholder*='mail']"
    ]
    
    campo_email = None
    for selector in email_selectors:
        try:
            campo_email = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            break
        except:
            continue
    
    if not campo_email:
        # Fallback - pega primeiro input
        inputs = driver.find_elements(By.TAG_NAME, "input")
        if inputs:
            campo_email = inputs[0]
    
    if campo_email:
        campo_email.clear()
        campo_email.send_keys(login)
        print("✅ Email preenchido")
    else:
        raise Exception("Campo de email não encontrado")
    
    # Campo senha
    campo_senha = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
    )
    campo_senha.clear()
    campo_senha.send_keys(senha)
    print("✅ Senha preenchida")
    
    # Botão login - múltiplas tentativas
    login_selectors = [
        "button[type='submit']",
        "input[type='submit']",
        "button:contains('Entrar')",
        "button:contains('Login')"
    ]
    
    botao_clicado = False
    for selector in login_selectors:
        try:
            if 'contains' in selector:
                # XPath para texto
                xpath = f"//button[contains(text(), '{selector.split(':contains(')[1][:-2]}')]"
                botao = driver.find_element(By.XPATH, xpath)
            else:
                botao = driver.find_element(By.CSS_SELECTOR, selector)
            
            botao.click()
            botao_clicado = True
            break
        except:
            continue
    
    if not botao_clicado:
        # Fallback - primeiro botão da página
        botoes = driver.find_elements(By.TAG_NAME, "button")
        if botoes:
            botoes[0].click()
            botao_clicado = True
    
    if botao_clicado:
        print("✅ Login executado!")
        time.sleep(5)
    else:
        raise Exception("Botão de login não encontrado")

def ir_gerar_futebol(driver):
    print("⚽ Procurando menu Gerar Futebol...")
    
    # Múltiplas estratégias para encontrar o menu
    futebol_selectors = [
        "//a[contains(text(), 'Gerar Futebol')]",
        "//a[contains(text(), 'Futebol')]",
        "//button[contains(text(), 'Gerar Futebol')]",
        "//div[contains(text(), 'Gerar Futebol')]",
        "//span[contains(text(), 'Futebol')]",
        "//li[contains(text(), 'Futebol')]",
        "//nav//a[contains(text(), 'Futebol')]"
    ]
    
    elemento_clicado = False
    for selector in futebol_selectors:
        try:
            elemento = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, selector))
            )
            elemento.click()
            elemento_clicado = True
            print(f"✅ Menu futebol encontrado!")
            break
        except:
            continue
    
    if not elemento_clicado:
        # Estratégia alternativa - procura por href
        try:
            link_futebol = driver.find_element(By.XPATH, "//a[contains(@href, 'futebol')]")
            link_futebol.click()
            elemento_clicado = True
            print("✅ Menu futebol encontrado via href!")
        except:
            pass
    
    if elemento_clicado:
        time.sleep(3)
    else:
        raise Exception("Menu Gerar Futebol não encontrado")

def selecionar_modelo_2(driver):
    print("🎨 Procurando Modelo 2...")
    
    modelo_selectors = [
        "//div[contains(text(), 'Modelo 2')]",
        "//button[contains(text(), 'Modelo 2')]",
        "//span[contains(text(), 'Modelo 2')]",
        "//label[contains(text(), 'Modelo 2')]",
        "//input[@value='2']",
        "//*[text()='2']",
        "//div[contains(@class, 'modelo') and contains(text(), '2')]"
    ]
    
    for selector in modelo_selectors:
        try:
            modelo = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, selector))
            )
            modelo.click()
            print("✅ Modelo 2 selecionado!")
            time.sleep(1)
            return
        except:
            continue
    
    print("⚠️ Modelo 2 não encontrado, continuando...")

def gerar_banners_dia_atual(driver):
    print("🏆 Procurando opção do dia atual...")
    
    # Seleciona jogos de hoje
    dia_selectors = [
        "//button[contains(text(), 'Hoje')]",
        "//button[contains(text(), 'Dia')]",
        "//div[contains(text(), 'Hoje')]",
        "//span[contains(text(), 'Hoje')]",
        "//input[@value='hoje']",
        "//label[contains(text(), 'Hoje')]",
        "//option[contains(text(), 'Hoje')]"
    ]
    
    for selector in dia_selectors:
        try:
            elemento_dia = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, selector))
            )
            elemento_dia.click()
            print("✅ Jogos de hoje selecionados!")
            time.sleep(1)
            break
        except:
            continue
    
    # Clica no botão gerar
    print("🔄 Procurando botão Gerar...")
    gerar_selectors = [
        "//button[contains(text(), 'Gerar')]",
        "//input[@value='Gerar']",
        "//button[contains(@class, 'gerar')]",
        "//div[contains(text(), 'Gerar')]",
        "//span[contains(text(), 'Gerar')]"
    ]
    
    gerar_clicado = False
    for selector in gerar_selectors:
        try:
            botao_gerar = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, selector))
            )
            botao_gerar.click()
            gerar_clicado = True
            print("✅ Geração iniciada!")
            break
        except:
            continue
    
    if not gerar_clicado:
        raise Exception("Botão Gerar não encontrado")
    
    print("⏳ Aguardando geração dos banners...")

def aguardar_e_enviar_telegram(driver):
    print("📤 Aguardando conclusão para enviar ao Telegram...")
    
    # Aguarda até 3 minutos pela conclusão
    enviar_selectors = [
        "//button[contains(text(), 'Enviar')]",
        "//button[contains(text(), 'Telegram')]",
        "//div[contains(text(), 'Enviar')]",
        "//span[contains(text(), 'Enviar')]",
        "//a[contains(text(), 'Enviar')]",
        "//button[contains(text(), 'Enviar Todas')]"
    ]
    
    max_tentativas = 36  # 36 x 5s = 3 minutos
    for tentativa in range(max_tentativas):
        print(f"⏳ Tentativa {tentativa + 1}/{max_tentativas}...")
        
        for selector in enviar_selectors:
            try:
                botao_enviar = driver.find_element(By.XPATH, selector)
                if botao_enviar.is_displayed() and botao_enviar.is_enabled():
                    botao_enviar.click()
                    print("✅ Banners enviados para o Telegram!")
                    return True
            except:
                continue
        
        time.sleep(5)
    
    raise Exception("Botão de enviar não apareceu após 3 minutos")

def main():
    print("🚀 INICIANDO AUTOMAÇÃO GERADOR PRO")
    print(f"⏰ Horário: {time.strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Pega credenciais
    login = os.environ.get("LOGIN")
    senha = os.environ.get("SENHA")
    
    if not login or not senha:
        print("❌ Credenciais não encontradas!")
        return
    
    print(f"🔑 Login: {login}")
    
    driver = setup_driver()
    try:
        # Fluxo completo
        fazer_login(driver, login, senha)
        ir_gerar_futebol(driver)
        selecionar_modelo_2(driver)
        gerar_banners_dia_atual(driver)
        aguardar_e_enviar_telegram(driver)
        
        print("🎉 AUTOMAÇÃO CONCLUÍDA COM SUCESSO!")
        print("🔔 Verifique seu canal no Telegram")
        
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        print(f"📍 URL atual: {driver.current_url}")
        
        # Salva screenshot para debug
        try:
            driver.save_screenshot("erro_debug.png")
            print("📸 Screenshot salva")
        except:
            pass
        
        raise e
        
    finally:
        driver.quit()
        print("🔒 Navegador fechado")

if __name__ == "__main__":
    main()
