import os, time, random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ------------------------------------------------------------
# CONFIGURAÇÃO DO NAVEGADOR (ANTI-CLOUDFLARE)
# ------------------------------------------------------------
def setup_driver():
    print("🔧 Configurando Chrome com estratégias anti-detecção...")
    options = Options()
    
    # Estratégias para evitar detecção do Cloudflare
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    # User agent mais realista
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Headers adicionais
    options.add_argument("--accept-language=pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7")
    options.add_argument("--accept=text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Remover propriedades que indicam automação
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['pt-BR', 'pt', 'en-US', 'en']
            });
        '''
    })
    
    print("✅ Chrome configurado com proteção anti-detecção")
    return driver

# ------------------------------------------------------------
# FUNÇÃO AUXILIAR: AGUARDAR RANDOM
# ------------------------------------------------------------
def wait_random(min_sec=1, max_sec=3):
    """Espera um tempo aleatório para parecer mais humano"""
    time.sleep(random.uniform(min_sec, max_sec))

# ------------------------------------------------------------
# FUNÇÃO AUXILIAR: VERIFICAR CLOUDFLARE
# ------------------------------------------------------------
def verificar_cloudflare(driver):
    """Verifica se o Cloudflare está bloqueando"""
    page_text = driver.page_source.lower()
    if "cloudflare" in page_text and ("checking" in page_text or "verify" in page_text):
        print("⚠️ Cloudflare detectado! Aguardando bypass...")
        for i in range(30):  # Aguarda até 30 segundos
            time.sleep(1)
            if "cloudflare" not in driver.page_source.lower():
                print("✅ Cloudflare superado!")
                return True
        print("❌ Não foi possível superar o Cloudflare")
        return False
    return True

# ------------------------------------------------------------
# LOGIN COM RETRY
# ------------------------------------------------------------
def fazer_login(driver, login, senha):
    print("🔑 Acessando página de login...")
    
    for tentativa in range(3):
        try:
            driver.get("https://gerador.pro/login.php")
            wait_random(2, 4)
            
            if not verificar_cloudflare(driver):
                if tentativa < 2:
                    print(f"🔄 Tentativa {tentativa + 1}/3 - Tentando novamente...")
                    continue
                else:
                    raise Exception("Cloudflare bloqueou todas as tentativas")
            
            print(f"🔐 Preenchendo credenciais (tentativa {tentativa + 1})...")
            username_field = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_field.clear()
            wait_random(0.5, 1)
            username_field.send_keys(login)
            
            wait_random(0.5, 1)
            password_field = driver.find_element(By.NAME, "password")
            password_field.clear()
            password_field.send_keys(senha)
            
            wait_random(1, 2)
            submit_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
            submit_btn.click()
            
            print("⏳ Aguardando redirecionamento...")
            WebDriverWait(driver, 20).until(lambda d: "index.php" in d.current_url or "dashboard" in d.current_url.lower())
            
            wait_random(1, 2)
            if not verificar_cloudflare(driver):
                continue
                
            print("✅ Login realizado com sucesso!")
            return True
            
        except Exception as e:
            print(f"⚠️ Erro na tentativa {tentativa + 1}: {e}")
            if tentativa < 2:
                wait_random(3, 5)
            else:
                raise

# ------------------------------------------------------------
# ACESSA SEÇÃO GERAR FUTEBOL
# ------------------------------------------------------------
def ir_para_futebol(driver):
    print("⚽ Acessando seção de Futebol...")
    wait_random(2, 3)
    
    try:
        # Tenta encontrar e clicar no botão
        botao = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Gerar Futebol') or contains(.,'Gerar Futebol')]"))
        )
        driver.execute_script("arguments[0].click();", botao)
        print("✅ Menu clicado!")
        wait_random(2, 4)
        
        # Verifica se URL mudou
        if "futbanner.php" not in driver.current_url:
            print("⚠️ URL não mudou, navegando diretamente...")
            driver.get("https://gerador.pro/futbanner.php?page=futebol")
            wait_random(2, 3)
    
    except Exception as e:
        print(f"⚠️ Navegação direta: {e}")
        driver.get("https://gerador.pro/futbanner.php?page=futebol")
        wait_random(2, 3)
    
    verificar_cloudflare(driver)
    
    # Aguarda página carregar
    WebDriverWait(driver, 25).until(
        EC.presence_of_element_located((By.XPATH, "//h1 | //div[contains(@class,'modelo') or contains(@class,'banner')]"))
    )
    print("✅ Página de Futebol carregada!")

# ------------------------------------------------------------
# SELECIONA MODELO 15
# ------------------------------------------------------------
def selecionar_modelo_15(driver):
    print("🎨 Selecionando modelo 15...")
    wait_random(1, 2)
    
    modelo = WebDriverWait(driver, 25).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(@href,'modelo=15')]"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", modelo)
    wait_random(0.5, 1)
    driver.execute_script("arguments[0].click();", modelo)
    
    print("✅ Modelo 15 selecionado!")
    wait_random(2, 3)

# ------------------------------------------------------------
# GERAR BANNERS
# ------------------------------------------------------------
def gerar_banners(driver):
    print("⚙️ Gerando banners...")
    wait_random(1, 2)
    
    botao = WebDriverWait(driver, 25).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Gerar Banners')]"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", botao)
    wait_random(0.5, 1)
    driver.execute_script("arguments[0].click();", botao)
    
    print("🟠 Aguardando processamento (pode levar até 90s)...")
    
    try:
        WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Sucesso') or contains(text(),'Banners gerados') or contains(text(),'OK')]"))
        )
        print("✅ Processamento concluído!")
        
        wait_random(1, 2)
        try:
            ok_btn = driver.find_element(By.XPATH, "//button[contains(text(),'OK') or contains(text(),'Ok')]")
            driver.execute_script("arguments[0].click();", ok_btn)
            print("✅ Popup fechado")
        except:
            print("⚠️ Sem popup para fechar")
        
        wait_random(2, 3)
    except Exception as e:
        print(f"⚠️ Timeout ou erro: {e}")

# ------------------------------------------------------------
# ENVIAR PARA TELEGRAM
# ------------------------------------------------------------
def enviar_para_telegram(driver):
    print("📤 Preparando envio para Telegram...")
    
    # Aguarda estar na página da galeria
    WebDriverWait(driver, 60).until(EC.url_contains("futebol/cartazes"))
    wait_random(2, 3)
    
    print("🕓 Aguardando imagens carregarem...")
    for i in range(25):
        imagens = driver.find_elements(By.TAG_NAME, "img")
        if len(imagens) >= 2:
            print(f"🖼️ {len(imagens)} imagens encontradas")
            break
        time.sleep(2)
    
    wait_random(1, 2)
    
    botao_enviar = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Enviar') or contains(text(),'Telegram')]"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", botao_enviar)
    wait_random(1, 2)
    driver.execute_script("arguments[0].click();", botao_enviar)
    
    print("📨 Enviando para Telegram...")
    
    # Aguarda envio completar
    for i in range(50):
        try:
            if not botao_enviar.is_displayed():
                print("✅ Envio concluído!")
                break
        except:
            print("✅ Envio finalizado!")
            break
        time.sleep(3)

# ------------------------------------------------------------
# EXECUÇÃO PRINCIPAL
# ------------------------------------------------------------
def main():
    print("=" * 60)
    print("🚀 AUTOMAÇÃO DE FUTEBOL - VERSÃO ANTI-CLOUDFLARE")
    print("=" * 60)
    print(f"⏰ Horário: {time.strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    login = os.environ.get("LOGIN")
    senha = os.environ.get("SENHA")
    
    if not login or not senha:
        print("❌ ERRO: LOGIN ou SENHA não configurados!")
        print("Configure as variáveis de ambiente LOGIN e SENHA")
        return
    
    driver = None
    try:
        driver = setup_driver()
        print()
        
        fazer_login(driver, login, senha)
        print()
        
        ir_para_futebol(driver)
        print()
        
        selecionar_modelo_15(driver)
        print()
        
        gerar_banners(driver)
        print()
        
        enviar_para_telegram(driver)
        print()
        
        print("=" * 60)
        print("🎉 PROCESSO CONCLUÍDO COM SUCESSO!")
        print("📱 Verifique seu canal no Telegram")
        print("=" * 60)
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ ERRO GERAL: {e}")
        print("=" * 60)
        
        if driver:
            try:
                print(f"📍 URL atual: {driver.current_url}")
                print(f"📄 Título da página: {driver.title}")
                
                # Salva screenshot se possível
                try:
                    screenshot_path = "/tmp/erro_screenshot.png"
                    driver.save_screenshot(screenshot_path)
                    print(f"📸 Screenshot salvo em: {screenshot_path}")
                except:
                    pass
                
                # Mostra parte do HTML
                body_text = driver.find_element(By.TAG_NAME, "body").text
                print(f"📄 Conteúdo (primeiros 500 chars):")
                print(body_text[:500])
                print()
            except Exception as debug_err:
                print(f"⚠️ Erro ao coletar debug info: {debug_err}")
    
    finally:
        if driver:
            driver.quit()
            print("🔒 Navegador fechado")

# ------------------------------------------------------------
if __name__ == "__main__":
    main()
