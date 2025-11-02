import time
import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# ==================== CONFIGURAÇÕES ====================
# IMPORTANTE: Use variáveis de ambiente para credenciais em produção
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "7872091942:AAHbvXRGtdomQxgyKDAkuk1SoLULx0B9xEg")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "-1002169364087")
LOGIN_USER = os.getenv("LOGIN_USER", "deivson06")
LOGIN_PASS = os.getenv("LOGIN_PASS", "F9416280")

def setup_driver():
    """Configura e retorna o driver do Chrome"""
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option('useAutomationExtension', False)
    
    # Necessário para acesso ao clipboard
    opts.add_argument("--enable-clipboard")
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), 
        options=opts
    )
    return driver

def enviar_telegram(texto):
    """Envia mensagem para o Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    # Divide mensagem se for muito grande (limite Telegram: 4096 chars)
    max_length = 4000
    if len(texto) > max_length:
        partes = [texto[i:i+max_length] for i in range(0, len(texto), max_length)]
        for i, parte in enumerate(partes):
            data = {
                "chat_id": TELEGRAM_CHAT_ID, 
                "text": f"📊 Parte {i+1}/{len(partes)}\n\n{parte}", 
                "parse_mode": "Markdown"
            }
            r = requests.post(url, data=data)
            print(f"📨 Envio Telegram (parte {i+1}): {r.status_code}")
            if r.status_code != 200:
                print(f"❌ Erro: {r.text}")
            time.sleep(0.5)  # Evita rate limit
    else:
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": texto, "parse_mode": "Markdown"}
        r = requests.post(url, data=data)
        print(f"📨 Envio Telegram: {r.status_code}")
        if r.status_code != 200:
            print(f"❌ Erro: {r.text}")
        return r.status_code == 200

def fazer_login(driver):
    """Realiza o login no site"""
    print("🔐 Iniciando login...")
    
    try:
        # Aguarda campo de usuário
        user_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((
                By.XPATH, 
                "//input[@type='text' or @type='email' or contains(@placeholder,'Usu') or contains(@placeholder,'Email')]"
            ))
        )
        user_input.clear()
        user_input.send_keys(LOGIN_USER)
        print(f"✅ Usuário '{LOGIN_USER}' inserido")
        
        # Campo de senha
        pwd_input = driver.find_element(
            By.XPATH, 
            "//input[@type='password' or contains(@placeholder,'Senha')]"
        )
        pwd_input.clear()
        pwd_input.send_keys(LOGIN_PASS)
        print("✅ Senha inserida")
        
        # Botão de login
        login_btn = driver.find_element(
            By.XPATH, 
            "//button[contains(.,'Entrar') or contains(.,'Login') or @type='submit']"
        )
        login_btn.click()
        print("✅ Botão de login clicado")
        
        time.sleep(3)  # Aguarda redirecionamento
        return True
        
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        return False

def capturar_texto_jogos(driver):
    """Captura o texto dos jogos usando múltiplos métodos"""
    print("⚽ Navegando para página de futebol...")
    
    try:
        # Clica no link "Gerar Futebol"
        link_futebol = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Gerar Futebol"))
        )
        link_futebol.click()
        print("✅ Página de futebol aberta")
        
        time.sleep(3)  # Aguarda carregamento da página
        
        # MÉTODO 1: Tentar clicar no botão "Copiar texto"
        try:
            copiar_btn = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((
                    By.XPATH, 
                    "//button[contains(., 'Copiar texto') or contains(., 'Copiar') or contains(@onclick, 'copiar')]"
                ))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", copiar_btn)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", copiar_btn)
            print("📋 Botão 'Copiar texto' clicado")
            
            time.sleep(2)
            
            # Tenta ler do clipboard
            texto = driver.execute_script("""
                return navigator.clipboard.readText()
                    .then(t => t)
                    .catch(e => '');
            """)
            
            if texto and len(texto) > 50:
                print("✅ Texto capturado via clipboard")
                return texto
                
        except TimeoutException:
            print("⚠️ Botão 'Copiar texto' não encontrado")
        
        # MÉTODO 2: Buscar em textareas
        print("🔍 Tentando capturar via textarea...")
        textareas = driver.find_elements(By.TAG_NAME, "textarea")
        for ta in textareas:
            texto = ta.get_attribute("value") or ta.text
            if texto and len(texto) > 50 and any(x in texto for x in ["📆", "⚽", "vs", "×"]):
                print("✅ Texto capturado via textarea")
                return texto
        
        # MÉTODO 3: Buscar em divs/pre com conteúdo relevante
        print("🔍 Tentando capturar via elementos DOM...")
        elementos = driver.find_elements(By.XPATH, 
            "//pre | //div[@class] | //div[@id] | //code"
        )
        
        for el in elementos:
            texto = el.text
            if texto and len(texto) > 100 and any(x in texto for x in ["📆", "⚽", "vs", "×", "Rodada"]):
                print("✅ Texto capturado via elemento DOM")
                return texto
        
        # MÉTODO 4: Captura todo o body como último recurso
        print("⚠️ Tentando capturar body completo...")
        body_text = driver.find_element(By.TAG_NAME, "body").text
        if body_text and len(body_text) > 100:
            print("⚠️ Texto capturado do body (pode conter elementos extras)")
            return body_text
        
        print("❌ Nenhum texto foi capturado por nenhum método")
        return None
        
    except Exception as e:
        print(f"❌ Erro ao capturar texto: {e}")
        # Salva screenshot para debug
        try:
            driver.save_screenshot("erro_captura.png")
            print("📸 Screenshot salvo: erro_captura.png")
        except:
            pass
        return None

def main():
    """Função principal"""
    print("=" * 60)
    print("🚀 INICIANDO CAPTURA DE JOGOS DE FUTEBOL")
    print("=" * 60)
    
    driver = None
    
    try:
        # Configura o driver
        driver = setup_driver()
        print("✅ Driver configurado")
        
        # Acessa a página de login
        driver.get("https://gerador.pro/login.php")
        print("✅ Página de login carregada")
        
        # Faz login
        if not fazer_login(driver):
            print("❌ Falha no login. Abortando...")
            return
        
        # Captura o texto dos jogos
        texto = capturar_texto_jogos(driver)
        
        if texto:
            print("\n" + "=" * 60)
            print("📝 TEXTO CAPTURADO:")
            print("=" * 60)
            print(texto[:500] + "..." if len(texto) > 500 else texto)
            print("=" * 60)
            print(f"📏 Tamanho total: {len(texto)} caracteres\n")
            
            # Envia para o Telegram
            enviar_telegram(texto)
            print("✅ Processo concluído com sucesso!")
        else:
            print("❌ Falha ao capturar texto dos jogos")
            enviar_telegram("⚠️ *Alerta:* Falha ao capturar texto dos jogos de futebol.")
    
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()
        
        try:
            enviar_telegram(f"❌ *Erro no script:*\n```\n{str(e)}\n```")
        except:
            pass
    
    finally:
        if driver:
            driver.quit()
            print("\n🔒 Navegador fechado")
        
        print("=" * 60)
        print("🏁 EXECUÇÃO FINALIZADA")
        print("=" * 60)

if __name__ == "__main__":
    main()
