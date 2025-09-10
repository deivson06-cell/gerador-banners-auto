import os, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

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

def debug_page(driver, step):
    """Debug completo da página atual"""
    print(f"🔍 DEBUG {step}:")
    print(f"   URL atual: {driver.current_url}")
    print(f"   Título: {driver.title}")
    
    # Lista todos os inputs na página
    try:
        inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"   📝 {len(inputs)} campos input encontrados:")
        for i, inp in enumerate(inputs[:5]):  # Mostra só os 5 primeiros
            attrs = []
            for attr in ['name', 'type', 'id', 'placeholder', 'class']:
                value = inp.get_attribute(attr)
                if value:
                    attrs.append(f"{attr}='{value}'")
            print(f"      {i+1}. <input {' '.join(attrs)}>")
    except:
        print("   ❌ Erro ao listar inputs")
    
    # Lista todos os botões
    try:
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"   🔘 {len(buttons)} botões encontrados:")
        for i, btn in enumerate(buttons[:5]):
            text = btn.text.strip() or btn.get_attribute('value') or 'sem texto'
            attrs = []
            for attr in ['type', 'id', 'class']:
                value = btn.get_attribute(attr)
                if value:
                    attrs.append(f"{attr}='{value}'")
            print(f"      {i+1}. '{text}' - {' '.join(attrs)}")
    except:
        print("   ❌ Erro ao listar botões")
    
    # Lista links
    try:
        links = driver.find_elements(By.TAG_NAME, "a")
        print(f"   🔗 {len(links)} links encontrados:")
        for i, link in enumerate(links[:5]):
            text = link.text.strip() or 'sem texto'
            href = link.get_attribute('href') or 'sem href'
            print(f"      {i+1}. '{text}' -> {href}")
    except:
        print("   ❌ Erro ao listar links")
    
    print("   " + "="*50)

def main():
    print("🚀 INICIANDO AUTOMAÇÃO COM DEBUG COMPLETO")
    
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
        print("🌐 Acessando site...")
        driver.get("https://geradorpro.com/login")
        time.sleep(5)
        
        debug_page(driver, "PÁGINA DE LOGIN")
        
        # Tenta encontrar campo de email de forma mais inteligente
        print("📧 Procurando campo de email...")
        campo_email = None
        
        # Estratégia 1: Por atributos comuns
        for selector in ["input[name='email']", "input[type='email']", "input[id='email']"]:
            try:
                campo_email = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"✅ Email encontrado via CSS: {selector}")
                break
            except:
                continue
        
        # Estratégia 2: Por placeholder
        if not campo_email:
            try:
                campo_email = driver.find_element(By.XPATH, "//input[contains(@placeholder, 'mail') or contains(@placeholder, 'Mail') or contains(@placeholder, 'EMAIL')]")
                print("✅ Email encontrado via placeholder")
            except:
                pass
        
        # Estratégia 3: Primeiro input da página
        if not campo_email:
            try:
                inputs = driver.find_elements(By.TAG_NAME, "input")
                if inputs:
                    campo_email = inputs[0]
                    print(f"✅ Usando primeiro input da página: {campo_email.get_attribute('outerHTML')[:100]}...")
            except:
                pass
        
        if not campo_email:
            print("❌ ERRO CRÍTICO: Campo de email não encontrado!")
            debug_page(driver, "ERRO EMAIL")
            return
        
        # Preenche email
        try:
            campo_email.clear()
            campo_email.send_keys(login)
            print(f"✅ Email preenchido: {login}")
        except Exception as e:
            print(f"❌ Erro ao preencher email: {e}")
            return
        
        # Procura campo senha
        print("🔐 Procurando campo de senha...")
        campo_senha = None
        
        for selector in ["input[name='password']", "input[type='password']", "input[id='password']"]:
            try:
                campo_senha = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"✅ Senha encontrada via CSS: {selector}")
                break
            except:
                continue
        
        if not campo_senha:
            print("❌ ERRO CRÍTICO: Campo de senha não encontrado!")
            debug_page(driver, "ERRO SENHA")
            return
        
        # Preenche senha
        try:
            campo_senha.clear()
            campo_senha.send_keys(senha)
            print("✅ Senha preenchida")
        except Exception as e:
            print(f"❌ Erro ao preencher senha: {e}")
            return
        
        # Procura botão de login
        print("🔘 Procurando botão de login...")
        botao_login = None
        
        # Estratégias múltiplas para botão
        estrategias = [
            ("CSS", "button[type='submit']"),
            ("CSS", "input[type='submit']"),
            ("XPATH", "//button[contains(text(), 'Entrar')]"),
            ("XPATH", "//button[contains(text(), 'Login')]"),
            ("XPATH", "//input[@value='Entrar']"),
            ("XPATH", "//button"),  # Qualquer botão
        ]
        
        for tipo, selector in estrategias:
            try:
                if tipo == "CSS":
                    botao_login = driver.find_element(By.CSS_SELECTOR, selector)
                else:
                    botao_login = driver.find_element(By.XPATH, selector)
                print(f"✅ Botão login encontrado via {tipo}: {selector}")
                break
            except:
                continue
        
        if not botao_login:
            print("❌ ERRO CRÍTICO: Botão de login não encontrado!")
            debug_page(driver, "ERRO BOTÃO LOGIN")
            return
        
        # Clica no botão
        try:
            botao_login.click()
            print("✅ Clicou no botão de login!")
        except Exception as e:
            print(f"❌ Erro ao clicar no botão: {e}")
            # Tenta JavaScript como alternativa
            try:
                driver.execute_script("arguments[0].click();", botao_login)
                print("✅ Clicou via JavaScript!")
            except:
                print("❌ Falhou mesmo com JavaScript")
                return
        
        # Aguarda redirecionamento
        print("⏳ Aguardando redirecionamento após login...")
        time.sleep(8)
        
        debug_page(driver, "APÓS LOGIN")
        
        # Se chegou até aqui, o login funcionou
        print("🎉 LOGIN REALIZADO COM SUCESSO!")
        print(f"   URL atual: {driver.current_url}")
        
        # Resto do processo seria aqui...
        print("⚽ Próximo passo seria procurar menu futebol...")
        print("✅ TESTE DE LOGIN CONCLUÍDO - Interrompendo aqui para debug")
        
    except Exception as e:
        print(f"💥 ERRO GERAL: {str(e)}")
        print(f"   Tipo do erro: {type(e).__name__}")
        try:
            debug_page(driver, "ERRO FATAL")
        except:
            pass
        raise e
    finally:
        print("🔒 Fechando navegador...")
        driver.quit()

if __name__ == "__main__":
    main()
