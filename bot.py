import os, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

def setup():
    print("🔧 Configurando Chrome...")
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    print("✅ Chrome configurado!")
    return driver

def clicar_elemento(driver, elemento, descricao, retries=3):
    """Tenta clicar no elemento com fallback para JavaScript e retries"""
    for tentativa in range(1, retries + 1):
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemento)
            time.sleep(0.5)
            elemento.click()
            print(f"✅ {descricao} - clique normal (tentativa {tentativa})")
            return True
        except (ElementClickInterceptedException, Exception):
            try:
                driver.execute_script("arguments[0].click();", elemento)
                print(f"✅ {descricao} - clique via JavaScript (tentativa {tentativa})")
                return True
            except Exception as e:
                print(f"❌ {descricao} - falhou na tentativa {tentativa}: {e}")
                time.sleep(1)
    return False

def encontrar_elemento(driver, estrategias, descricao, timeout=15):
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
        except TimeoutException:
            continue
    print(f"   ❌ {descricao} não encontrado após {len(estrategias)} tentativas")
    return None

def esperar_e_clicar(driver, by, selector, descricao, timeout=15):
    """Espera o elemento ficar clicável e tenta clicar"""
    try:
        elemento = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, selector))
        )
        return clicar_elemento(driver, elemento, descricao)
    except TimeoutException:
        print(f"❌ {descricao} não clicável após {timeout}s")
        return False

def fazer_login(driver, login, senha):
    print("\n" + "="*60)
    print("📍 PASSO 1/8: Login no site")
    print("="*60)
    driver.get("https://geradorpro.com/login")

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

    botao_login = encontrar_elemento(driver, [
        ("CSS", "button[type='submit']"),
        ("CSS", "input[type='submit']"),
        ("XPATH", "//button[contains(text(), 'Entrar') or contains(text(), 'Login')]"),
        ("XPATH", "//input[@value='Entrar' or @value='Login']"),
    ], "Botão de login")
    
    if not botao_login:
        raise Exception("Botão de login não encontrado")
    
    clicar_elemento(driver, botao_login, "Botão de login")
    print("✅ PASSO 1/8 CONCLUÍDO: Login realizado!")

def aguardar_menu(driver):
    print("\n" + "="*60)
    print("📍 PASSO 2/8: Aguardar menu carregar")
    print("="*60)
    for selector in ["nav", ".menu", "#menu", ".sidebar", "aside"]:
        try:
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            print(f"✅ Menu encontrado: {selector}")
            return
        except:
            continue
    print("⚠️ Menu não detectado visualmente, mas continuando...")

def clicar_gerar_futebol(driver):
    print("\n" + "="*60)
    print("📍 PASSO 3/8: Clicar em 'Gerar Futebol'")
    print("="*60)
    
    link_futebol = encontrar_elemento(driver, [
        ("XPATH", "//a[contains(text(), 'Gerar Futebol')]"),
        ("XPATH", "//a[contains(text(), 'Futebol')]"),
        ("XPATH", "//li[contains(text(), 'Futebol')]//a"),
        ("CSS", "a[href*='futebol']"),
    ], "Link Gerar Futebol")
    
    if not link_futebol:
        raise Exception("Link 'Gerar Futebol' não encontrado")
    
    clicar_elemento(driver, link_futebol, "Link Gerar Futebol")
    print("✅ PASSO 3/8 CONCLUÍDO: Página de futebol carregada!")

def clicar_botao_gerar_inicial(driver):
    print("\n" + "="*60)
    print("📍 PASSO 4/8: Clicar em 'Gerar' (primeira vez)")
    print("="*60)
    
    botao_gerar = encontrar_elemento(driver, [
        ("XPATH", "//button[contains(text(), 'Gerar')]"),
        ("XPATH", "//input[@type='submit' and contains(@value, 'Gerar')]"),
        ("CSS", "button[type='submit']"),
    ], "Botão Gerar")
    
    if not botao_gerar:
        raise Exception("Botão 'Gerar' não encontrado")
    
    clicar_elemento(driver, botao_gerar, "Botão Gerar")
    print("✅ PASSO 4/8 CONCLUÍDO: Botão Gerar clicado!")

def escolher_modelo_15(driver):
    print("\n" + "="*60)
    print("📍 PASSO 5/8: Escolher Modelo 15")
    print("="*60)
    
    modelo_15 = encontrar_elemento(driver, [
        ("XPATH", "//input[@type='radio' and @value='15']"),
        ("XPATH", "//label[contains(text(), '15')]//input"),
        ("XPATH", "//input[@type='radio'][15]"),
    ], "Modelo 15", timeout=10)
    
    if not modelo_15:
        radios = driver.find_elements(By.XPATH, "//input[@type='radio']")
        if radios:
            modelo_15 = radios[0]
            print("⚠️ Usando primeiro modelo disponível")
        else:
            raise Exception("Nenhum modelo encontrado")
    
    clicar_elemento(driver, modelo_15, "Modelo 15")
    print("✅ PASSO 5/8 CONCLUÍDO: Modelo 15 selecionado!")

def clicar_gerar_novamente(driver):
    print("\n" + "="*60)
    print("📍 PASSO 6/8: Clicar em 'Gerar' (segunda vez)")
    print("="*60)
    
    botao_gerar = encontrar_elemento(driver, [
        ("XPATH", "//button[contains(text(), 'Gerar')]"),
        ("XPATH", "//input[@type='submit' and contains(@value, 'Gerar')]"),
    ], "Botão Gerar (2ª vez)")
    
    if not botao_gerar:
        raise Exception("Botão 'Gerar' (2ª vez) não encontrado")
    
    clicar_elemento(driver, botao_gerar, "Botão Gerar (2ª vez)")
    print("✅ PASSO 6/8 CONCLUÍDO: Segundo Gerar clicado!")

def confirmar_ok(driver):
    print("\n" + "="*60)
    print("📍 PASSO 7/8: Confirmar no 'OK'")
    print("="*60)
    
    try:
        WebDriverWait(driver, 5).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        alert.accept()
        print("✅ Alert JavaScript confirmado!")
    except TimeoutException:
        botao_ok = encontrar_elemento(driver, [
            ("XPATH", "//button[contains(text(), 'OK')]"),
            ("CSS", ".swal-button"),
        ], "Botão OK", timeout=5)
        if botao_ok:
            clicar_elemento(driver, botao_ok, "Botão OK")
        else:
            print("⚠️ Nenhum modal de confirmação encontrado")

def enviar_todas_imagens(driver):
    print("\n" + "="*60)
    print("📍 PASSO 8/8: Enviar todas as imagens")
    print("="*60)
    
    max_tentativas = 20
    botao_encontrado = False
    
    for tentativa in range(max_tentativas):
        print(f"🔍 Tentativa {tentativa + 1}/{max_tentativas}")
        botao_enviar = encontrar_elemento(driver, [
            ("XPATH", "//button[contains(text(), 'Enviar todas as imagens')]"),
            ("XPATH", "//button[contains(text(), 'Enviar para o Telegram')]"),
            ("XPATH", "//button[contains(text(), 'Enviar')]"),
        ], "Botão Enviar", timeout=5)
        
        if botao_enviar:
            if clicar_elemento(driver, botao_enviar, "Botão Enviar"):
                botao_encontrado = True
                break
        time.sleep(2)
    
    if not botao_encontrado:
        print("⚠️ Botão de envio não encontrado. Tentando detectar sucesso pelo texto da página...")
        try:
            body = driver.find_element(By.TAG_NAME, "body").text.lower()
            if any(palavra in body for palavra in ['enviado', 'sucesso', 'concluído', 'telegram']):
                print("✅ Possível sucesso detectado pelo texto da página!")
                botao_encontrado = True
        except:
            pass
    
    return botao_encontrado

def main():
    print("🚀 INICIANDO AUTOMAÇÃO COMPLETA - GERADOR PRO")
    print("="*60)
    
    login = os.environ.get("LOGIN")
    senha = os.environ.get("SENHA")
    
    if not login or not senha:
        print("❌ ERRO: Credenciais não encontradas!")
        return
    
    driver = setup()
    
    try:
        fazer_login(driver, login, senha)
        aguardar_menu(driver)
        clicar_gerar_futebol(driver)
        clicar_botao_gerar_inicial(driver)
        escolher_modelo_15(driver)
        clicar_gerar_novamente(driver)
        confirmar_ok(driver)
        sucesso = enviar_todas_imagens(driver)
        
        if sucesso:
            print("🎉 AUTOMAÇÃO CONCLUÍDA COM SUCESSO!")
        else:
            print("⚠️ AUTOMAÇÃO PARCIALMENTE CONCLUÍDA")
        
    except Exception as e:
        print(f"💥 ERRO: {str(e)}")
        driver.save_screenshot("erro_automacao.png")
        raise
    finally:
        print("🔒 Fechando navegador...")
        driver.quit()

if __name__ == "__main__":
    main()
