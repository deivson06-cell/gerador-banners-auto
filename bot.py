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

def debug_login_completo(driver, login, senha):
    print("🔑 FAZENDO LOGIN COM DEBUG COMPLETO...")
    driver.get("https://gerador.pro/login.php")
    time.sleep(5)
    
    # 1. LISTAR TODOS OS ELEMENTOS DA PÁGINA
    print("📋 ANALISANDO PÁGINA DE LOGIN:")
    
    # Lista todos os inputs
    inputs = driver.find_elements(By.TAG_NAME, "input")
    print(f"📝 {len(inputs)} campos input encontrados:")
    for i, inp in enumerate(inputs):
        name = inp.get_attribute('name') or 'sem name'
        type_attr = inp.get_attribute('type') or 'sem type'
        id_attr = inp.get_attribute('id') or 'sem id'
        placeholder = inp.get_attribute('placeholder') or 'sem placeholder'
        value = inp.get_attribute('value') or 'sem value'
        print(f"   {i+1}. name='{name}' type='{type_attr}' id='{id_attr}' placeholder='{placeholder}' value='{value}'")
    
    # Lista todos os botões
    buttons = driver.find_elements(By.TAG_NAME, "button")
    print(f"🔘 {len(buttons)} botões encontrados:")
    for i, btn in enumerate(buttons):
        text = btn.text.strip() or 'sem texto'
        type_attr = btn.get_attribute('type') or 'sem type'
        onclick = btn.get_attribute('onclick') or 'sem onclick'
        print(f"   {i+1}. text='{text}' type='{type_attr}' onclick='{onclick}'")
    
    # Lista inputs de submit também
    submit_inputs = driver.find_elements(By.XPATH, "//input[@type='submit']")
    print(f"📨 {len(submit_inputs)} inputs submit encontrados:")
    for i, sub in enumerate(submit_inputs):
        value = sub.get_attribute('value') or 'sem value'
        name = sub.get_attribute('name') or 'sem name'
        print(f"   {i+1}. value='{value}' name='{name}'")
    
    # Lista formulários
    forms = driver.find_elements(By.TAG_NAME, "form")
    print(f"📝 {len(forms)} formulários encontrados:")
    for i, form in enumerate(forms):
        action = form.get_attribute('action') or 'sem action'
        method = form.get_attribute('method') or 'sem method'
        print(f"   {i+1}. action='{action}' method='{method}'")
    
    # 2. TENTAR PREENCHER CAMPOS DE MÚLTIPLAS FORMAS
    print("\n🔍 TENTANDO PREENCHER CAMPOS...")
    
    # Campo usuário/email
    campo_usuario = None
    strategies = [
        ("name", "usuario"),
        ("name", "email"), 
        ("name", "login"),
        ("name", "user"),
        ("id", "usuario"),
        ("id", "email"),
        ("id", "login"),
        ("type", "email"),
        ("type", "text")
    ]
    
    for attr, value in strategies:
        try:
            if attr == "type":
                campo_usuario = driver.find_element(By.XPATH, f"//input[@type='{value}']")
            else:
                campo_usuario = driver.find_element(By.XPATH, f"//input[@{attr}='{value}']")
            print(f"✅ Campo usuário encontrado via {attr}='{value}'")
            break
        except:
            continue
    
    # Se não encontrou, pega o primeiro input
    if not campo_usuario and inputs:
        campo_usuario = inputs[0]
        print("✅ Usando primeiro input como campo usuário")
    
    # Campo senha
    campo_senha = None
    try:
        campo_senha = driver.find_element(By.XPATH, "//input[@type='password']")
        print("✅ Campo senha encontrado")
    except:
        if len(inputs) > 1:
            campo_senha = inputs[1]
            print("✅ Usando segundo input como campo senha")
    
    if not campo_usuario or not campo_senha:
        print("❌ ERRO: Não foi possível identificar os campos!")
        return False
    
    # 3. PREENCHER OS CAMPOS
    print("\n📝 PREENCHENDO CAMPOS...")
    
    try:
        campo_usuario.clear()
        campo_usuario.send_keys(login)
        print(f"✅ Campo usuário preenchido com: {login}")
        
        campo_senha.clear() 
        campo_senha.send_keys(senha)
        print("✅ Campo senha preenchido")
        
        # Aguarda um pouco
        time.sleep(1)
        
    except Exception as e:
        print(f"❌ Erro ao preencher: {e}")
        return False
    
    # 4. TENTAR SUBMETER DE MÚLTIPLAS FORMAS
    print("\n🚀 TENTANDO SUBMETER FORMULÁRIO...")
    
    # Estratégia 1: Botão por texto "ENTRAR"
    try:
        botao_entrar = driver.find_element(By.XPATH, "//input[@value='ENTRAR NO PAINEL']")
        botao_entrar.click()
        print("✅ Clicou em 'ENTRAR NO PAINEL'")
        success = True
    except:
        success = False
        print("❌ Botão 'ENTRAR NO PAINEL' não encontrado")
    
    # Estratégia 2: Input submit
    if not success:
        try:
            submit_btn = driver.find_element(By.XPATH, "//input[@type='submit']")
            submit_btn.click()
            print("✅ Clicou no input submit")
            success = True
        except:
            print("❌ Input submit não encontrado")
    
    # Estratégia 3: Botão comum
    if not success:
        try:
            button = driver.find_element(By.TAG_NAME, "button")
            button.click()
            print("✅ Clicou no botão")
            success = True
        except:
            print("❌ Botão não encontrado")
    
    # Estratégia 4: Enter no campo senha
    if not success:
        try:
            campo_senha.send_keys(Keys.RETURN)
            print("✅ Pressionou Enter no campo senha")
            success = True
        except:
            print("❌ Enter não funcionou")
    
    # Estratégia 5: Submit do formulário via JavaScript
    if not success:
        try:
            driver.execute_script("document.forms[0].submit();")
            print("✅ Submit via JavaScript")
            success = True
        except:
            print("❌ Submit JavaScript falhou")
    
    if not success:
        print("❌ TODAS as estratégias de submit falharam!")
        return False
    
    # 5. AGUARDAR E VERIFICAR RESULTADO
    print("\n⏳ AGUARDANDO RESULTADO DO LOGIN...")
    
    for i in range(15):
        time.sleep(1)
        current_url = driver.current_url
        page_content = driver.find_element(By.TAG_NAME, "body").text
        
        print(f"   {i+1}s - URL: {current_url}")
        
        # Verifica se saiu da página de login
        if "login.php" not in current_url:
            print("🎉 LOGIN BEM-SUCEDIDO! Redirecionado!")
            print(f"✅ Nova URL: {current_url}")
            return True
        
        # Verifica se apareceu erro na mesma página
        if any(palavra in page_content.lower() for palavra in ['erro', 'incorret', 'inválid', 'falhou']):
            print("❌ LOGIN FALHOU - Erro encontrado na página")
            print(f"📄 Conteúdo: {page_content[:300]}")
            return False
    
    print("⚠️ Timeout - ainda na página de login após 15s")
    print(f"📄 Conteúdo atual: {driver.find_element(By.TAG_NAME, 'body').text[:200]}")
    return False

def main():
    print("🚀 INICIANDO DEBUG COMPLETO DO LOGIN")
    print(f"⏰ Horário: {time.strftime('%d/%m/%Y %H:%M:%S')}")
    
    login = os.environ.get("LOGIN")
    senha = os.environ.get("SENHA")
    
    if not login or not senha:
        print("❌ Credenciais não encontradas!")
        return
    
    print(f"🔑 Login: {login}")
    print(f"🔐 Senha: {'*' * len(senha)}")
    
    driver = setup_driver()
    try:
        sucesso = debug_login_completo(driver, login, senha)
        
        if sucesso:
            print("🎉 LOGIN FUNCIONOU! Próximo passo seria procurar o menu...")
            print(f"📍 URL atual: {driver.current_url}")
            
            # Lista o que tem na nova página
            try:
                body_text = driver.find_element(By.TAG_NAME, "body").text
                print("📄 Conteúdo da nova página:")
                print(f"   {body_text[:500]}...")
                
                # Lista links da nova página
                links = driver.find_elements(By.TAG_NAME, "a")[:10]
                print(f"\n🔗 {len(links)} links encontrados na nova página:")
                for i, link in enumerate(links):
                    text = link.text.strip()[:30]
                    href = link.get_attribute('href') or 'sem href'
                    print(f"   {i+1}. '{text}' -> {href}")
                    
            except:
                pass
        else:
            print("❌ LOGIN FALHOU!")
            
    except Exception as e:
        print(f"💥 ERRO GERAL: {str(e)}")
        
    finally:
        print("🔒 Fechando navegador...")
        driver.quit()

if __name__ == "__main__":
    main()
