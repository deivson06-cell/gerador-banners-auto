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
    try:
        driver.get("https://gerador.pro/login.php")
        
        campo_usuario = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        campo_usuario.clear()
        campo_usuario.send_keys(login)
        
        campo_senha = driver.find_element(By.NAME, "password")
        campo_senha.clear()
        campo_senha.send_keys(senha)
        
        botao_login = driver.find_element(By.XPATH, "//button[@type='submit']")
        botao_login.click()
        
        WebDriverWait(driver, 15).until(
            lambda driver: "index.php" in driver.current_url or "dashboard" in driver.current_url.lower()
        )
        print("✅ Login bem-sucedido!")
    except Exception as e:
        print(f"❌ Erro no login: {str(e)}")
        # Salvar screenshot para debug
        driver.save_screenshot("erro_login.png")
        raise

def ir_gerar_futebol(driver):
    print("⚽ Indo para Gerar Futebol...")
    try:
        driver.get("https://gerador.pro/futbanner.php")
        
        # Aguardar página carregar completamente
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print("✅ Página futbanner carregada!")
        time.sleep(3)  # Tempo extra para JavaScript carregar
    except Exception as e:
        print(f"❌ Erro ao acessar futbanner: {str(e)}")
        driver.save_screenshot("erro_futbanner.png")
        raise

def selecionar_opcoes_futebol(driver):
    print("🎨 Selecionando opções...")
    
    # Aguardar formulário carregar
    time.sleep(5)
    
    # Tentar múltiplas estratégias para encontrar o modelo 15
    modelo_selecionado = False
    estrategias_modelo = [
        "//input[@type='radio' and @value='15']",
        "//input[@type='radio' and @value='2']",
        "//label[contains(text(), '15')]//input[@type='radio']",
        "//label[contains(text(), 'Modelo 15')]//input[@type='radio']",
        "//input[@type='radio'][15]"
    ]
    
    for xpath in estrategias_modelo:
        try:
            elemento = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            driver.execute_script("arguments[0].click();", elemento)
            print(f"✅ Modelo selecionado com XPath: {xpath}")
            modelo_selecionado = True
            time.sleep(2)
            break
        except Exception as e:
            print(f"⚠️ Tentativa falhou: {xpath}")
            continue
    
    if not modelo_selecionado:
        print("⚠️ Nenhum modelo foi selecionado, tentando continuar...")
        driver.save_screenshot("erro_modelo.png")
    
    # Tentar selecionar opção "hoje" ou similar
    try:
        opcoes_hoje = [
            "//input[@type='radio' and contains(@value, 'hoje')]",
            "//label[contains(text(), 'Hoje')]//input[@type='radio']",
            "//input[@type='radio' and @value='hoje']"
        ]
        
        for xpath in opcoes_hoje:
            try:
                elemento = driver.find_element(By.XPATH, xpath)
                driver.execute_script("arguments[0].click();", elemento)
                print("✅ Opção 'hoje' selecionada!")
                time.sleep(2)
                break
            except:
                continue
    except Exception as e:
        print(f"⚠️ Erro ao selecionar 'hoje': {str(e)}")

def gerar_banners(driver):
    print("🔄 Gerando banners...")
    
    estrategias = [
        "//button[contains(text(), 'Gerar')]",
        "//input[@type='submit' and contains(@value, 'Gerar')]",
        "//button[@type='submit']",
        "//button[contains(@class, 'btn') and contains(text(), 'Gerar')]",
        "//a[contains(text(), 'Gerar')]"
    ]
    
    botao_clicado = False
    for strategy in estrategias:
        try:
            botao = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, strategy))
            )
            driver.execute_script("arguments[0].click();", botao)
            print(f"✅ Botão Gerar clicado! (Estratégia: {strategy})")
            botao_clicado = True
            break
        except:
            continue
    
    if not botao_clicado:
        print("❌ Nenhum botão de gerar encontrado!")
        driver.save_screenshot("erro_botao_gerar.png")
        print("HTML da página:", driver.page_source[:500])
    
    # Aguardar geração (ajuste o tempo conforme necessário)
    print("⏳ Aguardando geração dos banners...")
    time.sleep(30)

def aguardar_e_enviar_telegram(driver):
    print("📤 Procurando botão de envio ao Telegram...")
    
    # Aguardar processamento
    time.sleep(10)
    
    estrategias_enviar = [
        "//button[contains(text(), 'Enviar todas as imagens')]",
        "//button[contains(text(), 'Enviar para o Telegram')]",
        "//button[contains(text(), 'Enviar')]",
        "//button[contains(@class, 'telegram')]",
        "//input[@type='button' and contains(@value, 'Enviar todas as imagens')]",
        "//input[@type='button' and contains(@value, 'Enviar')]",
        "//input[@type='submit' and contains(@value, 'Enviar')]",
        "//a[contains(text(), 'Enviar todas as imagens')]",
        "//a[contains(@href, 'telegram')]",
        "//button[contains(@onclick, 'telegram')]",
        "//div[contains(@class, 'telegram') and @onclick]"
    ]
    
    max_tentativas = 60  # 5 minutos no total
    
    for tentativa in range(max_tentativas):
        print(f"🔍 Tentativa {tentativa + 1}/{max_tentativas}")
        
        for strategy in estrategias_enviar:
            try:
                botoes = driver.find_elements(By.XPATH, strategy)
                for botao_enviar in botoes:
                    if botao_enviar.is_displayed() and botao_enviar.is_enabled():
                        # Scroll até o elemento
                        driver.execute_script("arguments[0].scrollIntoView(true);", botao_enviar)
                        time.sleep(1)
                        
                        # Tentar clicar
                        try:
                            botao_enviar.click()
                        except:
                            driver.execute_script("arguments[0].click();", botao_enviar)
                        
                        print(f"✅ Botão enviar clicado! (Estratégia: {strategy})")
                        time.sleep(8)
                        print("🎉 BANNERS ENVIADOS PARA O TELEGRAM!")
                        return True
            except Exception as e:
                continue
        
        # Verificar mensagens de sucesso no texto da página
        try:
            body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
            palavras_sucesso = ['sucesso', 'enviado', 'concluído', 'finalizado', 'pronto', 'gerado', 'telegram']
            
            if any(palavra in body_text for palavra in palavras_sucesso):
                print("✅ Possível sucesso detectado no texto da página!")
                print(f"Texto encontrado: {body_text[:200]}")
                return True
        except:
            pass
        
        time.sleep(5)
    
    print("⚠️ Botão de enviar não apareceu após todas as tentativas")
    driver.save_screenshot("erro_envio_telegram.png")
    print("HTML da página:", driver.page_source[:1000])
    return False

def main():
    print("🚀 INICIANDO AUTOMAÇÃO COMPLETA - GERADOR PRO")
    print("=" * 50)
    
    login = os.environ.get("LOGIN")
    senha = os.environ.get("SENHA")
    
    if not login or not senha:
        print("❌ ERRO: Credenciais não encontradas nas variáveis de ambiente!")
        print("Configure LOGIN e SENHA antes de executar")
        return
    
    print(f"📧 Login: {login[:3]}***")
    
    driver = None
    try:
        driver = setup_driver()
        fazer_login(driver, login, senha)
        ir_gerar_futebol(driver)
        selecionar_opcoes_futebol(driver)
        gerar_banners(driver)
        
        sucesso_envio = aguardar_e_enviar_telegram(driver)
        
        if sucesso_envio:
            print("\n" + "=" * 50)
            print("🎉 AUTOMAÇÃO CONCLUÍDA COM SUCESSO!")
            print("=" * 50)
        else:
            print("\n" + "=" * 50)
            print("⚠️ Envio automático falhou - verifique os logs")
            print("=" * 50)
            
    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO: {str(e)}")
        import traceback
        print(traceback.format_exc())
        if driver:
            driver.save_screenshot("erro_geral.png")
            
    finally:
        if driver:
            driver.quit()
            print("🔒 Navegador fechado")

if __name__ == "__main__":
    main()
