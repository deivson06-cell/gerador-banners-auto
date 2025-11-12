import os, time, random

# Tenta importar undetected_chromedriver, se falhar usa selenium padrão
try:
    import undetected_chromedriver as uc
    USAR_UNDETECTED = True
    print("📦 undetected_chromedriver disponível - modo avançado ativado")
except ImportError:
    USAR_UNDETECTED = False
    print("⚠️ undetected_chromedriver não disponível - usando selenium padrão")
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ------------------------------------------------------------
# CONFIGURAÇÃO DO NAVEGADOR
# ------------------------------------------------------------
def setup_driver():
    print("🔧 Configurando Chrome...")
    
    if USAR_UNDETECTED:
        # MODO AVANÇADO: Undetected ChromeDriver
        print("   Usando undetected-chromedriver (anti-detecção avançada)")
        
        options = uc.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=IsolateOrigins,site-per-process")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        driver = uc.Chrome(options=options, use_subprocess=True, version_main=None)
        
    else:
        # MODO PADRÃO: Selenium com configurações avançadas
        print("   Usando selenium padrão (com otimizações anti-detecção)")
        
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # Remove propriedades de detecção
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                Object.defineProperty(navigator, 'languages', {get: () => ['pt-BR', 'pt', 'en-US', 'en']});
            '''
        })
    
    print("✅ Chrome configurado com sucesso")
    return driver

# ------------------------------------------------------------
# FUNÇÕES AUXILIARES
# ------------------------------------------------------------
def wait_random(min_sec=1, max_sec=3):
    """Espera aleatória para simular comportamento humano"""
    time.sleep(random.uniform(min_sec, max_sec))

def esperar_carregamento_completo(driver, timeout=30):
    """Aguarda carregamento completo da página"""
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        return True
    except:
        return False

def verificar_cloudflare(driver, max_wait=60):
    """Verifica e aguarda bypass do Cloudflare"""
    page_source = driver.page_source.lower()
    
    keywords = ["cloudflare", "just a moment", "checking your browser", "verify you are human"]
    is_cloudflare = any(keyword in page_source for keyword in keywords)
    
    if is_cloudflare:
        print("⚠️ Cloudflare detectado! Aguardando bypass automático...")
        
        for i in range(max_wait):
            time.sleep(1)
            current_source = driver.page_source.lower()
            
            # Verifica se cloudflare sumiu
            if not any(keyword in current_source for keyword in keywords):
                print(f"✅ Cloudflare superado após {i+1} segundos!")
                wait_random(1, 2)
                return True
            
            # Log de progresso
            if i > 0 and i % 10 == 0:
                print(f"   ... tentando bypass ({i}/{max_wait}s)")
        
        print(f"❌ Cloudflare não foi superado após {max_wait}s")
        return False
    
    return True

def digitar_como_humano(element, text):
    """Simula digitação humana caractere por caractere"""
    element.clear()
    wait_random(0.3, 0.7)
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.15))

# ------------------------------------------------------------
# LOGIN
# ------------------------------------------------------------
def fazer_login(driver, login, senha):
    print("🔑 Acessando página de login...")
    
    max_tentativas = 3
    
    for tentativa in range(max_tentativas):
        try:
            print(f"\n📍 Tentativa {tentativa + 1}/{max_tentativas}")
            
            driver.get("https://gerador.pro/login.php")
            wait_random(3, 6)
            esperar_carregamento_completo(driver, 20)
            
            # Verifica Cloudflare
            if not verificar_cloudflare(driver, max_wait=60):
                if tentativa < max_tentativas - 1:
                    print(f"🔄 Aguardando 10 segundos antes de tentar novamente...")
                    time.sleep(10)
                    continue
                else:
                    raise Exception("Cloudflare bloqueou todas as tentativas")
            
            print("🔐 Preenchendo credenciais...")
            
            # Campo username
            username_field = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            digitar_como_humano(username_field, login)
            wait_random(0.8, 1.5)
            
            # Campo password
            password_field = driver.find_element(By.NAME, "password")
            digitar_como_humano(password_field, senha)
            wait_random(1, 2)
            
            # Submit
            submit_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
            driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
            wait_random(0.5, 1)
            submit_btn.click()
            
            print("⏳ Aguardando redirecionamento...")
            
            # Aguarda redirect
            for i in range(30):
                if "index.php" in driver.current_url or "dashboard" in driver.current_url.lower():
                    print(f"✅ Redirecionado: {driver.current_url}")
                    break
                time.sleep(1)
            
            wait_random(2, 3)
            
            # Verifica Cloudflare pós-login
            if not verificar_cloudflare(driver, max_wait=45):
                if tentativa < max_tentativas - 1:
                    continue
            
            # Verifica sucesso
            if "index.php" in driver.current_url or "dashboard" in driver.current_url.lower():
                print("✅ Login realizado com sucesso!")
                return True
            else:
                print(f"⚠️ URL inesperada: {driver.current_url}")
                if tentativa < max_tentativas - 1:
                    continue
                
        except Exception as e:
            print(f"⚠️ Erro: {e}")
            if tentativa < max_tentativas - 1:
                print("🔄 Tentando novamente em 8 segundos...")
                time.sleep(8)
            else:
                raise
    
    raise Exception("Falha no login após todas as tentativas")

# ------------------------------------------------------------
# IR PARA FUTEBOL
# ------------------------------------------------------------
def ir_para_futebol(driver):
    print("\n⚽ Acessando seção de Futebol...")
    wait_random(2, 4)
    
    try:
        botao = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Gerar Futebol') or contains(.,'Gerar Futebol')]"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", botao)
        wait_random(0.5, 1)
        driver.execute_script("arguments[0].click();", botao)
        print("✅ Menu clicado!")
        wait_random(3, 5)
    except Exception as e:
        print(f"⚠️ Erro ao clicar: {e}")
    
    if "futbanner.php" not in driver.current_url:
        print("➡️ Navegação direta...")
        driver.get("https://gerador.pro/futbanner.php?page=futebol")
        wait_random(3, 5)
    
    verificar_cloudflare(driver, max_wait=45)
    esperar_carregamento_completo(driver)
    
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//h1 | //div[contains(@class,'modelo')] | //a[contains(@href,'modelo')]"))
        )
        print("✅ Página de Futebol carregada!")
    except Exception as e:
        print(f"⚠️ Verificação: {e}")

# ------------------------------------------------------------
# SELECIONAR MODELO 15
# ------------------------------------------------------------
def selecionar_modelo_15(driver):
    print("\n🎨 Selecionando modelo 15...")
    wait_random(2, 3)
    
    modelo = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(@href,'modelo=15')]"))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", modelo)
    wait_random(1, 2)
    driver.execute_script("arguments[0].click();", modelo)
    
    print("✅ Modelo 15 selecionado!")
    wait_random(3, 4)

# ------------------------------------------------------------
# GERAR BANNERS
# ------------------------------------------------------------
def gerar_banners(driver):
    print("\n⚙️ Gerando banners...")
    wait_random(2, 3)
    
    botao = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Gerar Banners')]"))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", botao)
    wait_random(1, 2)
    driver.execute_script("arguments[0].click();", botao)
    
    print("🟠 Processando (até 2 minutos)...")
    
    try:
        WebDriverWait(driver, 150).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Sucesso') or contains(text(),'sucesso') or contains(text(),'Banners gerados')]"))
        )
        print("✅ Processamento concluído!")
        
        wait_random(2, 3)
        try:
            ok_btn = driver.find_element(By.XPATH, "//button[contains(text(),'OK') or contains(text(),'Ok')]")
            driver.execute_script("arguments[0].click();", ok_btn)
            print("✅ Popup fechado")
        except:
            print("⚠️ Sem popup")
        
        wait_random(3, 4)
    except Exception as e:
        print(f"⚠️ Timeout: {e}")

# ------------------------------------------------------------
# ENVIAR PARA TELEGRAM
# ------------------------------------------------------------
def enviar_para_telegram(driver):
    print("\n📤 Enviando para Telegram...")
    
    try:
        WebDriverWait(driver, 90).until(EC.url_contains("futebol/cartazes"))
    except:
        print(f"⚠️ URL: {driver.current_url}")
        if "cartazes" not in driver.current_url:
            return
    
    wait_random(3, 5)
    
    print("🕓 Aguardando imagens...")
    for i in range(30):
        imgs = driver.find_elements(By.TAG_NAME, "img")
        if len(imgs) >= 2:
            print(f"🖼️ {len(imgs)} imagens")
            break
        if i > 0 and i % 5 == 0:
            print(f"   ... ({i}/30)")
        time.sleep(2)
    
    wait_random(2, 3)
    
    try:
        botao = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Enviar') or contains(text(),'Telegram')]"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", botao)
        wait_random(1, 2)
        driver.execute_script("arguments[0].click();", botao)
        print("📨 Enviando...")
        
        for i in range(60):
            try:
                if not botao.is_displayed():
                    print("✅ Envio concluído!")
                    break
            except:
                print("✅ Finalizado!")
                break
            time.sleep(3)
    except Exception as e:
        print(f"⚠️ Erro: {e}")

# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
def main():
    print("=" * 70)
    print("🚀 AUTOMAÇÃO DE FUTEBOL")
    print("=" * 70)
    print(f"⏰ {time.strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    login = os.environ.get("LOGIN")
    senha = os.environ.get("SENHA")
    
    if not login or not senha:
        print("❌ LOGIN/SENHA não configurados!")
        return
    
    driver = None
    try:
        driver = setup_driver()
        print()
        
        fazer_login(driver, login, senha)
        ir_para_futebol(driver)
        selecionar_modelo_15(driver)
        gerar_banners(driver)
        enviar_para_telegram(driver)
        
        print()
        print("=" * 70)
        print("🎉 SUCESSO! Verifique o Telegram")
        print("=" * 70)
        
    except Exception as e:
        print()
        print("=" * 70)
        print(f"❌ ERRO: {e}")
        print("=" * 70)
        
        if driver:
            try:
                print(f"\n📍 {driver.current_url}")
                try:
                    driver.save_screenshot("/tmp/erro.png")
                    print("📸 Screenshot: /tmp/erro.png")
                except:
                    pass
                print(f"\n📄 {driver.find_element(By.TAG_NAME, 'body').text[:600]}")
            except:
                pass
    finally:
        if driver:
            driver.quit()
            print("\n🔒 Navegador fechado")

if __name__ == "__main__":
    main()
