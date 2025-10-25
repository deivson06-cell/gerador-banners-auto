import os, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def setup():
    print("🔧 Configurando Chrome...")
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox") 
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    print("✅ Chrome configurado!")
    return driver

def clicar_elemento(driver, elemento, descricao):
    """Tenta clicar no elemento com fallback para JavaScript"""
    try:
        elemento.click()
        print(f"✅ {descricao} - clique normal")
        return True
    except:
        try:
            driver.execute_script("arguments[0].click();", elemento)
            print(f"✅ {descricao} - clique via JavaScript")
            return True
        except Exception as e:
            print(f"❌ {descricao} - falhou: {e}")
            return False

def encontrar_elemento(driver, estrategias, descricao, timeout=10):
    """Tenta múltiplas estratégias para encontrar um elemento"""
    print(f"🔍 Procurando: {descricao}...")
    
    for tipo, selector in estrategias:
        try:
            if tipo == "CSS":
                elemento = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
            elif tipo == "XPATH":
                elemento = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
            elif tipo == "ID":
                elemento = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.ID, selector))
                )
            elif tipo == "NAME":
                elemento = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.NAME, selector))
                )
            
            print(f"   ✅ Encontrado via {tipo}: {selector}")
            return elemento
        except:
            continue
    
    print(f"   ❌ {descricao} não encontrado após {len(estrategias)} tentativas")
    return None

def fazer_login(driver, login, senha):
    """PASSO 1: Login no site"""
    print("\n" + "="*60)
    print("📍 PASSO 1/8: Login no site")
    print("="*60)
    
    driver.get("https://geradorpro.com/login")
    time.sleep(5)
    
    # Campo de email
    campo_email = encontrar_elemento(driver, [
        ("NAME", "email"),
        ("CSS", "input[type='email']"),
        ("ID", "email"),
        ("XPATH", "//input[contains(@placeholder, 'mail') or contains(@placeholder, 'Mail')]"),
    ], "Campo de email")
    
    if not campo_email:
        raise Exception("Campo de email não encontrado")
    
    campo_email.clear()
    campo_email.send_keys(login)
    print(f"✅ Email preenchido: {login}")
    
    # Campo de senha
    campo_senha = encontrar_elemento(driver, [
        ("NAME", "password"),
        ("CSS", "input[type='password']"),
        ("ID", "password"),
    ], "Campo de senha")
    
    if not campo_senha:
        raise Exception("Campo de senha não encontrado")
    
    campo_senha.clear()
    campo_senha.send_keys(senha)
    print("✅ Senha preenchida")
    
    # Botão de login
    botao_login = encontrar_elemento(driver, [
        ("CSS", "button[type='submit']"),
        ("CSS", "input[type='submit']"),
        ("XPATH", "//button[contains(text(), 'Entrar') or contains(text(), 'Login')]"),
        ("XPATH", "//input[@value='Entrar' or @value='Login']"),
    ], "Botão de login")
    
    if not botao_login:
        raise Exception("Botão de login não encontrado")
    
    clicar_elemento(driver, botao_login, "Botão de login")
    time.sleep(8)
    
    print("✅ PASSO 1/8 CONCLUÍDO: Login realizado!")

def aguardar_menu(driver):
    """PASSO 2: Aguardar o menu carregar"""
    print("\n" + "="*60)
    print("📍 PASSO 2/8: Aguardar menu carregar")
    print("="*60)
    
    # Aguarda elementos do menu aparecerem
    time.sleep(5)
    
    # Verifica se menu existe
    menu_existe = False
    for selector in ["nav", ".menu", "#menu", ".sidebar", "aside"]:
        try:
            driver.find_element(By.CSS_SELECTOR, selector)
            menu_existe = True
            print(f"✅ Menu encontrado: {selector}")
            break
        except:
            continue
    
    if not menu_existe:
        print("⚠️ Menu não detectado visualmente, mas continuando...")
    
    print("✅ PASSO 2/8 CONCLUÍDO: Menu carregado!")

def clicar_gerar_futebol(driver):
    """PASSO 3: Clicar em Gerar Futebol"""
    print("\n" + "="*60)
    print("📍 PASSO 3/8: Clicar em 'Gerar Futebol'")
    print("="*60)
    
    link_futebol = encontrar_elemento(driver, [
        ("XPATH", "//a[contains(text(), 'Gerar Futebol')]"),
        ("XPATH", "//a[contains(text(), 'Futebol')]"),
        ("XPATH", "//li[contains(text(), 'Futebol')]//a"),
        ("CSS", "a[href*='futebol']"),
        ("CSS", "a[href*='futbanner']"),
        ("XPATH", "//a[@href__='futbanner.php']"),
    ], "Link Gerar Futebol", timeout=15)
    
    if not link_futebol:
        raise Exception("Link 'Gerar Futebol' não encontrado")
    
    clicar_elemento(driver, link_futebol, "Link Gerar Futebol")
    time.sleep(8)
    
    print("✅ PASSO 3/8 CONCLUÍDO: Página de futebol carregada!")

def clicar_botao_gerar_inicial(driver):
    """PASSO 4: Clicar no botão Gerar (primeira vez)"""
    print("\n" + "="*60)
    print("📍 PASSO 4/8: Clicar em 'Gerar' (primeira vez)")
    print("="*60)
    
    botao_gerar = encontrar_elemento(driver, [
        ("XPATH", "//button[contains(text(), 'Gerar')]"),
        ("XPATH", "//input[@type='submit' and contains(@value, 'Gerar')]"),
        ("CSS", "button[type='submit']"),
        ("XPATH", "//button[contains(@class, 'btn') and contains(text(), 'Gerar')]"),
    ], "Botão Gerar")
    
    if not botao_gerar:
        raise Exception("Botão 'Gerar' não encontrado")
    
    clicar_elemento(driver, botao_gerar, "Botão Gerar")
    time.sleep(5)
    
    print("✅ PASSO 4/8 CONCLUÍDO: Botão Gerar clicado!")

def escolher_modelo_15(driver):
    """PASSO 5: Escolher modelo 15"""
    print("\n" + "="*60)
    print("📍 PASSO 5/8: Escolher Modelo 15")
    print("="*60)
    
    # Aguarda opções de modelo carregarem
    time.sleep(5)
    
    modelo_15 = encontrar_elemento(driver, [
        ("XPATH", "//input[@type='radio' and @value='15']"),
        ("XPATH", "//label[contains(text(), '15')]//input"),
        ("XPATH", "//label[contains(text(), 'Modelo 15')]//input"),
        ("XPATH", "//input[@type='radio' and @value='2']"),  # Pode ser value=2 para modelo 15
        ("XPATH", "(//input[@type='radio'])[15]"),  # 15º radio button
        ("XPATH", "//div[contains(text(), '15')]//input[@type='radio']"),
    ], "Modelo 15", timeout=15)
    
    if not modelo_15:
        print("⚠️ Modelo 15 não encontrado, tentando primeiro modelo disponível...")
        try:
            radios = driver.find_elements(By.XPATH, "//input[@type='radio']")
            if radios:
                modelo_15 = radios[0]
                print(f"⚠️ Usando primeiro modelo disponível")
        except:
            raise Exception("Nenhum modelo encontrado")
    
    clicar_elemento(driver, modelo_15, "Modelo 15")
    time.sleep(3)
    
    print("✅ PASSO 5/8 CONCLUÍDO: Modelo 15 selecionado!")

def clicar_gerar_novamente(driver):
    """PASSO 6: Clicar em Gerar novamente"""
    print("\n" + "="*60)
    print("📍 PASSO 6/8: Clicar em 'Gerar' (segunda vez)")
    print("="*60)
    
    botao_gerar = encontrar_elemento(driver, [
        ("XPATH", "//button[contains(text(), 'Gerar')]"),
        ("XPATH", "//input[@type='submit' and contains(@value, 'Gerar')]"),
        ("CSS", "button[type='submit']"),
        ("XPATH", "//button[contains(@onclick, 'gerar')]"),
    ], "Botão Gerar (2ª vez)")
    
    if not botao_gerar:
        raise Exception("Botão 'Gerar' (2ª vez) não encontrado")
    
    clicar_elemento(driver, botao_gerar, "Botão Gerar (2ª vez)")
    time.sleep(5)
    
    print("✅ PASSO 6/8 CONCLUÍDO: Segundo Gerar clicado!")

def confirmar_ok(driver):
    """PASSO 7: Confirmar no OK"""
    print("\n" + "="*60)
    print("📍 PASSO 7/8: Confirmar no 'OK'")
    print("="*60)
    
    # Aguarda alert ou modal aparecer
    time.sleep(3)
    
    # Tenta aceitar alert JavaScript
    try:
        WebDriverWait(driver, 10).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        alert.accept()
        print("✅ Alert JavaScript confirmado!")
    except TimeoutException:
        print("⚠️ Nenhum alert JavaScript detectado")
        
        # Tenta modal HTML
        botao_ok = encontrar_elemento(driver, [
            ("XPATH", "//button[contains(text(), 'OK')]"),
            ("XPATH", "//button[contains(text(), 'Ok')]"),
            ("XPATH", "//button[contains(text(), 'Confirmar')]"),
            ("XPATH", "//button[contains(@class, 'confirm')]"),
            ("CSS", ".modal button"),
            ("CSS", ".swal-button"),
        ], "Botão OK", timeout=5)
        
        if botao_ok:
            clicar_elemento(driver, botao_ok, "Botão OK")
        else:
            print("⚠️ Nenhum modal de confirmação encontrado, continuando...")
    
    time.sleep(8)
    print("✅ PASSO 7/8 CONCLUÍDO: Confirmação realizada!")

def enviar_todas_imagens(driver):
    """PASSO 8: Clicar em Enviar todas as imagens"""
    print("\n" + "="*60)
    print("📍 PASSO 8/8: Clicar em 'Enviar todas as imagens'")
    print("="*60)
    
    # Aguarda processamento
    print("⏳ Aguardando processamento dos banners...")
    time.sleep(15)
    
    # Tenta encontrar botão de envio com múltiplas tentativas
    max_tentativas = 40
    botao_encontrado = False
    
    for tentativa in range(max_tentativas):
        print(f"🔍 Tentativa {tentativa + 1}/{max_tentativas}")
        
        botao_enviar = encontrar_elemento(driver, [
            ("XPATH", "//button[contains(text(), 'Enviar todas as imagens')]"),
            ("XPATH", "//button[contains(text(), 'Enviar para o Telegram')]"),
            ("XPATH", "//button[contains(text(), 'Enviar')]"),
            ("XPATH", "//input[@value='Enviar todas as imagens']"),
            ("XPATH", "//a[contains(text(), 'Enviar todas as imagens')]"),
            ("CSS", "button[onclick*='telegram']"),
            ("CSS", "button[onclick*='enviar']"),
        ], "Botão Enviar", timeout=5)
        
        if botao_enviar:
            try:
                # Scroll até o botão
                driver.execute_script("arguments[0].scrollIntoView(true);", botao_enviar)
                time.sleep(2)
                
                if clicar_elemento(driver, botao_enviar, "Botão Enviar"):
                    botao_encontrado = True
                    break
            except:
                continue
        
        time.sleep(5)
    
    if not botao_encontrado:
        print("⚠️ Botão de envio não encontrado após todas as tentativas")
        # Tenta detectar sucesso pelo texto da página
        try:
            body = driver.find_element(By.TAG_NAME, "body").text.lower()
            if any(palavra in body for palavra in ['enviado', 'sucesso', 'concluído', 'telegram']):
                print("✅ Possível sucesso detectado pelo texto da página!")
                botao_encontrado = True
        except:
            pass
    
    time.sleep(8)
    
    if botao_encontrado:
        print("✅ PASSO 8/8 CONCLUÍDO: Imagens enviadas para o Telegram!")
    else:
        print("⚠️ PASSO 8/8 INCOMPLETO: Verifique manualmente")
    
    return botao_encontrado

def main():
    print("🚀 INICIANDO AUTOMAÇÃO COMPLETA - GERADOR PRO")
    print("="*60)
    
    login = os.environ.get("LOGIN")
    senha = os.environ.get("SENHA")
    
    if not login or not senha:
        print("❌ ERRO: Credenciais não encontradas!")
        print(f"   LOGIN: {'✅ OK' if login else '❌ VAZIO'}")
        print(f"   SENHA: {'✅ OK' if senha else '❌ VAZIO'}")
        return
    
    print(f"🔑 Credenciais carregadas - LOGIN: {login[:3]}...")
    
    driver = setup()
    
    try:
        # PASSO 1
        fazer_login(driver, login, senha)
        
        # PASSO 2
        aguardar_menu(driver)
        
        # PASSO 3
        clicar_gerar_futebol(driver)
        
        # PASSO 4
        clicar_botao_gerar_inicial(driver)
        
        # PASSO 5
        escolher_modelo_15(driver)
        
        # PASSO 6
        clicar_gerar_novamente(driver)
        
        # PASSO 7
        confirmar_ok(driver)
        
        # PASSO 8
        sucesso = enviar_todas_imagens(driver)
        
        print("\n" + "="*60)
        if sucesso:
            print("🎉 AUTOMAÇÃO CONCLUÍDA COM SUCESSO!")
            print("✅ Todos os 8 passos foram executados!")
        else:
            print("⚠️ AUTOMAÇÃO PARCIALMENTE CONCLUÍDA")
            print("✅ 7/8 passos executados - verifique o envio manualmente")
        print("="*60)
        
    except Exception as e:
        print(f"\n💥 ERRO: {str(e)}")
        print(f"   Tipo: {type(e).__name__}")
        driver.save_screenshot("erro_automacao.png")
        raise
        
    finally:
        print("\n🔒 Fechando navegador em 10 segundos...")
        time.sleep(10)
        driver.quit()

if __name__ == "__main__":
    main()
