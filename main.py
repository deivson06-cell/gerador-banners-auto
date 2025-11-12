import os, time, random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ------------------------------------------------------------
# CONFIGURAÇÃO DO NAVEGADOR (UNDETECTED CHROMEDRIVER)
# ------------------------------------------------------------
def setup_driver():
    print("🔧 Configurando Chrome com undetected-chromedriver...")
    
    options = uc.ChromeOptions()
    
    # Configurações básicas
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    
    # Desabilitar recursos que podem causar problemas
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-features=IsolateOrigins,site-per-process")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    # User agent
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    try:
        # undetected_chromedriver com versão específica
        driver = uc.Chrome(
            options=options,
            use_subprocess=True,
            version_main=None  # Detecta automaticamente
        )
        print("✅ Chrome configurado com proteção anti-detecção avançada")
        return driver
    except Exception as e:
        print(f"⚠️ Erro ao configurar undetected-chromedriver: {e}")
        print("Tentando com método alternativo...")
        
        # Fallback: tentar sem subprocess
        driver = uc.Chrome(options=options, use_subprocess=False)
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
def verificar_cloudflare(driver, max_wait=45):
    """Verifica se o Cloudflare está bloqueando e aguarda bypass"""
    page_source = driver.page_source.lower()
    
    if "cloudflare" in page_source or "just a moment" in page_source or "checking" in page_source:
        print("⚠️ Cloudflare detectado! Aguardando bypass automático...")
        
        for i in range(max_wait):
            time.sleep(1)
            current_source = driver.page_source.lower()
            
            if ("cloudflare" not in current_source and 
                "just a moment" not in current_source and 
                "checking" not in current_source):
                print(f"✅ Cloudflare superado após {i+1} segundos!")
                wait_random(1, 2)
                return True
            
            if i % 5 == 0 and i > 0:
                print(f"   ... aguardando ({i}/{max_wait}s)")
        
        print(f"❌ Timeout: Cloudflare não foi superado após {max_wait}s")
        return False
    
    return True

# ------------------------------------------------------------
# FUNÇÃO AUXILIAR: VERIFICAR SE PÁGINA CARREGOU
# ------------------------------------------------------------
def esperar_carregamento_completo(driver, timeout=30):
    """Aguarda o carregamento completo da página"""
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        return True
    except:
        return False

# ------------------------------------------------------------
# LOGIN COM ESTRATÉGIA MELHORADA
# ------------------------------------------------------------
def fazer_login(driver, login, senha):
    print("🔑 Acessando página de login...")
    
    max_tentativas = 3
    
    for tentativa in range(max_tentativas):
        try:
            print(f"\n📍 Tentativa {tentativa + 1}/{max_tentativas}")
            
            # Navega para página de login
            driver.get("https://gerador.pro/login.php")
            wait_random(3, 5)  # Aguarda mais tempo inicialmente
            
            # Espera carregamento completo
            if not esperar_carregamento_completo(driver, 20):
                print("⚠️ Página não carregou completamente")
            
            # Verifica Cloudflare
            if not verificar_cloudflare(driver, max_wait=60):
                if tentativa < max_tentativas - 1:
                    print(f"🔄 Aguardando antes da próxima tentativa...")
                    wait_random(5, 10)
                    continue
                else:
                    raise Exception("Cloudflare bloqueou todas as tentativas de login")
            
            print("🔐 Preenchendo credenciais...")
            
            # Localiza e preenche campo de usuário
            username_field = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            
            # Simula digitação humana
            username_field.clear()
            wait_random(0.8, 1.5)
            for char in login:
                username_field.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            wait_random(0.8, 1.5)
            
            # Localiza e preenche senha
            password_field = driver.find_element(By.NAME, "password")
            password_field.clear()
            wait_random(0.5, 1)
            for char in senha:
                password_field.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            wait_random(1, 2)
            
            # Clica no botão de submit
            submit_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
            driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
            wait_random(0.5, 1)
            submit_btn.click()
            
            print("⏳ Aguardando redirecionamento após login...")
            
            # Aguarda redirecionamento
            for i in range(30):
                current_url = driver.current_url
                if "index.php" in current_url or "dashboard" in current_url.lower():
                    print(f"✅ Redirecionado para: {current_url}")
                    break
                time.sleep(1)
            else:
                print(f"⚠️ URL atual após tentativa de login: {driver.current_url}")
            
            wait_random(2, 3)
            
            # Verifica Cloudflare após login
            if not verificar_cloudflare(driver, max_wait=45):
                if tentativa < max_tentativas - 1:
                    continue
                else:
                    raise Exception("Cloudflare bloqueou após login")
            
            # Verifica se login foi bem-sucedido
            if "index.php" in driver.current_url or "dashboard" in driver.current_url.lower():
                print("✅ Login realizado com sucesso!")
                return True
            else:
                print(f"⚠️ URL inesperada: {driver.current_url}")
                if tentativa < max_tentativas - 1:
                    continue
                
        except Exception as e:
            print(f"⚠️ Erro na tentativa {tentativa + 1}: {e}")
            if tentativa < max_tentativas - 1:
                print("🔄 Aguardando antes de tentar novamente...")
                wait_random(5, 8)
            else:
                raise
    
    raise Exception("Não foi possível fazer login após todas as tentativas")

# ------------------------------------------------------------
# ACESSA SEÇÃO GERAR FUTEBOL
# ------------------------------------------------------------
def ir_para_futebol(driver):
    print("\n⚽ Acessando seção de Futebol...")
    wait_random(2, 4)
    
    try:
        # Tenta clicar no menu
        botao = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Gerar Futebol') or contains(.,'Gerar Futebol')]"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", botao)
        wait_random(0.5, 1)
        driver.execute_script("arguments[0].click();", botao)
        print("✅ Menu clicado!")
        wait_random(3, 5)
        
    except Exception as e:
        print(f"⚠️ Erro ao clicar no menu: {e}")
    
    # Sempre tenta navegação direta como fallback
    if "futbanner.php" not in driver.current_url:
        print("➡️ Navegando diretamente para página de futebol...")
        driver.get("https://gerador.pro/futbanner.php?page=futebol")
        wait_random(3, 5)
    
    # Verifica Cloudflare
    verificar_cloudflare(driver, max_wait=45)
    esperar_carregamento_completo(driver)
    
    # Aguarda elementos da página
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//h1 | //div[contains(@class,'modelo')] | //a[contains(@href,'modelo')]"))
        )
        print("✅ Página de Futebol carregada!")
    except Exception as e:
        print(f"⚠️ Erro ao verificar carregamento: {e}")
        print(f"📍 URL atual: {driver.current_url}")

# ------------------------------------------------------------
# SELECIONA MODELO 15
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
    esperar_carregamento_completo(driver)

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
    
    print("🟠 Aguardando processamento dos banners...")
    print("   (Isso pode levar até 2 minutos)")
    
    try:
        # Aguarda popup de sucesso com timeout maior
        WebDriverWait(driver, 150).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Sucesso') or contains(text(),'sucesso') or contains(text(),'Banners gerados') or contains(text(),'OK')]"))
        )
        print("✅ Processamento concluído!")
        
        wait_random(2, 3)
        
        # Tenta fechar popup
        try:
            ok_btn = driver.find_element(By.XPATH, "//button[contains(text(),'OK') or contains(text(),'Ok') or contains(text(),'ok')]")
            driver.execute_script("arguments[0].click();", ok_btn)
            print("✅ Popup fechado")
        except:
            print("⚠️ Popup não encontrado ou já fechado")
        
        wait_random(3, 4)
        
    except Exception as e:
        print(f"⚠️ Timeout ou erro ao gerar: {e}")
        print("Tentando prosseguir mesmo assim...")

# ------------------------------------------------------------
# ENVIAR PARA TELEGRAM
# ------------------------------------------------------------
def enviar_para_telegram(driver):
    print("\n📤 Preparando envio para Telegram...")
    
    # Aguarda estar na página da galeria
    try:
        WebDriverWait(driver, 90).until(EC.url_contains("futebol/cartazes"))
        print("✅ Na página da galeria")
    except:
        print(f"⚠️ URL atual: {driver.current_url}")
        if "cartazes" not in driver.current_url:
            print("❌ Não está na página de galeria. Abortando envio.")
            return
    
    wait_random(3, 5)
    esperar_carregamento_completo(driver)
    
    print("🕓 Aguardando imagens carregarem...")
    for i in range(30):
        imagens = driver.find_elements(By.TAG_NAME, "img")
        if len(imagens) >= 2:
            print(f"🖼️ {len(imagens)} imagens encontradas na galeria")
            break
        if i % 5 == 0 and i > 0:
            print(f"   ... aguardando ({i}/30)")
        time.sleep(2)
    
    wait_random(2, 3)
    
    # Procura botão de enviar
    try:
        botao_enviar = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Enviar') or contains(text(),'enviar') or contains(text(),'Telegram')]"))
        )
        
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", botao_enviar)
        wait_random(1, 2)
        driver.execute_script("arguments[0].click();", botao_enviar)
        
        print("📨 Enviando para Telegram...")
        
        # Aguarda envio completar
        for i in range(60):
            try:
                if not botao_enviar.is_displayed():
                    print("✅ Envio concluído!")
                    break
            except:
                print("✅ Envio finalizado!")
                break
            
            if i % 10 == 0 and i > 0:
                print(f"   ... aguardando conclusão ({i}/60)")
            time.sleep(3)
        
    except Exception as e:
        print(f"⚠️ Erro ao enviar: {e}")

# ------------------------------------------------------------
# EXECUÇÃO PRINCIPAL
# ------------------------------------------------------------
def main():
    print("=" * 70)
    print("🚀 AUTOMAÇÃO DE FUTEBOL - UNDETECTED CHROMEDRIVER")
    print("=" * 70)
    print(f"⏰ Horário de início: {time.strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    login = os.environ.get("LOGIN")
    senha = os.environ.get("SENHA")
    
    if not login or not senha:
        print("❌ ERRO: Variáveis LOGIN ou SENHA não configuradas!")
        print("Configure as secrets no GitHub Actions")
        return
    
    print(f"👤 Usuário: {login}")
    print()
    
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
        print("🎉 PROCESSO CONCLUÍDO COM SUCESSO!")
        print("📱 Verifique seu canal no Telegram")
        print("=" * 70)
        print(f"⏰ Horário de conclusão: {time.strftime('%d/%m/%Y %H:%M:%S')}")
        
    except Exception as e:
        print()
        print("=" * 70)
        print(f"❌ ERRO GERAL: {type(e).__name__}")
        print(f"   Mensagem: {str(e)}")
        print("=" * 70)
        
        if driver:
            try:
                print(f"\n📍 URL atual: {driver.current_url}")
                print(f"📄 Título: {driver.title}")
                
                # Tenta salvar screenshot
                try:
                    screenshot_path = "/tmp/erro_screenshot.png"
                    driver.save_screenshot(screenshot_path)
                    print(f"📸 Screenshot salvo: {screenshot_path}")
                except Exception as ss_err:
                    print(f"⚠️ Não foi possível salvar screenshot: {ss_err}")
                
                # Mostra conteúdo da página
                try:
                    body_text = driver.find_element(By.TAG_NAME, "body").text
                    print(f"\n📄 Primeiros 600 caracteres da página:")
                    print("-" * 70)
                    print(body_text[:600])
                    print("-" * 70)
                except Exception as body_err:
                    print(f"⚠️ Não foi possível obter conteúdo: {body_err}")
                    
            except Exception as debug_err:
                print(f"⚠️ Erro ao coletar informações de debug: {debug_err}")
    
    finally:
        if driver:
            try:
                driver.quit()
                print("\n🔒 Navegador fechado")
            except:
                pass

# ------------------------------------------------------------
if __name__ == "__main__":
    main()
