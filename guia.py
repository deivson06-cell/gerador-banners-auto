import time
import os
import sys
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
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "7872091942:AAHbvXRGtdomQxgyKDAkuk1SoLULx0B9xEg")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "-1002169364087")
LOGIN_USER = os.getenv("LOGIN_USER", "deivson06")
LOGIN_PASS = os.getenv("LOGIN_PASS", "F9416280")

def validar_credenciais():
    """Valida se as credenciais estão configuradas"""
    print("\n🔍 VALIDANDO CREDENCIAIS:")
    print(f"   Token Telegram: {'✅ Configurado' if TELEGRAM_TOKEN else '❌ Não encontrado'}")
    print(f"   Chat ID: {'✅ Configurado' if TELEGRAM_CHAT_ID else '❌ Não encontrado'}")
    print(f"   Login User: {'✅ Configurado' if LOGIN_USER else '❌ Não encontrado'}")
    print(f"   Login Pass: {'✅ Configurado' if LOGIN_PASS else '❌ Não encontrado'}")
    
    if not all([TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, LOGIN_USER, LOGIN_PASS]):
        print("\n❌ ERRO: Credenciais incompletas!")
        sys.exit(1)
    
    print("✅ Todas as credenciais estão configuradas\n")

def setup_driver():
    """Configura e retorna o driver do Chrome com bypass Cloudflare"""
    print("🔧 Configurando Chrome Driver (com anti-detecção)...")
    opts = Options()
    
    # Argumentos para parecer um navegador real
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--enable-clipboard")
    
    # User agent realista
    opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Headers adicionais
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--disable-infobars")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-dev-shm-usage")
    
    # Desabilita detecção de automação
    opts.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    opts.add_experimental_option('useAutomationExtension', False)
    
    # Preferências para parecer mais real
    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.default_content_setting_values.notifications": 2
    }
    opts.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), 
        options=opts
    )
    
    # Executa script para remover propriedades de webdriver
    driver.execute_cdp_cmd("Network.setUserAgentOverride", {
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })
    
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    print("✅ Chrome Driver configurado com anti-detecção")
    return driver

def testar_telegram():
    """Testa se o bot do Telegram está funcionando"""
    print("\n🧪 TESTANDO CONEXÃO COM TELEGRAM...")
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getMe"
    
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            bot_info = r.json()
            if bot_info.get("ok"):
                print(f"✅ Bot conectado: @{bot_info['result']['username']}")
                return True
            else:
                print(f"❌ Erro na resposta do bot: {bot_info}")
                return False
        else:
            print(f"❌ Erro HTTP {r.status_code}: {r.text}")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar Telegram: {e}")
        return False

def enviar_telegram(texto, force_send=False):
    """Envia mensagem para o Telegram com validação"""
    if not texto and not force_send:
        print("⚠️ Texto vazio, não enviando ao Telegram")
        return False
    
    print(f"\n📤 ENVIANDO PARA TELEGRAM...")
    print(f"   Tamanho da mensagem: {len(texto)} caracteres")
    print(f"   Chat ID: {TELEGRAM_CHAT_ID}")
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    # Divide mensagem se for muito grande (limite Telegram: 4096 chars)
    max_length = 4000
    partes = []
    
    if len(texto) > max_length:
        print(f"   ⚠️ Mensagem será dividida em partes")
        partes = [texto[i:i+max_length] for i in range(0, len(texto), max_length)]
    else:
        partes = [texto]
    
    sucesso = True
    for i, parte in enumerate(partes):
        if len(partes) > 1:
            mensagem = f"📊 *Parte {i+1}/{len(partes)}*\n\n{parte}"
        else:
            mensagem = parte
        
        data = {
            "chat_id": TELEGRAM_CHAT_ID, 
            "text": mensagem, 
            "parse_mode": "Markdown"
        }
        
        try:
            print(f"\n   Enviando parte {i+1}/{len(partes)}...")
            r = requests.post(url, data=data, timeout=15)
            
            print(f"   Status Code: {r.status_code}")
            
            if r.status_code == 200:
                resp = r.json()
                if resp.get("ok"):
                    print(f"   ✅ Parte {i+1} enviada com sucesso!")
                else:
                    print(f"   ❌ Erro na resposta: {resp}")
                    sucesso = False
            else:
                print(f"   ❌ Erro HTTP {r.status_code}")
                print(f"   Resposta: {r.text}")
                sucesso = False
            
            if len(partes) > 1:
                time.sleep(1)  # Evita rate limit
                
        except Exception as e:
            print(f"   ❌ Exceção ao enviar: {e}")
            sucesso = False
    
    return sucesso

def fazer_login(driver):
    """Realiza o login no site"""
    print("\n🔐 INICIANDO LOGIN...")
    
    try:
        # Salva screenshot da página de login
        driver.save_screenshot("01_pagina_login.png")
        print("   📸 Screenshot: 01_pagina_login.png")
        
        # Aguarda página carregar
        time.sleep(3)
        
        # Tenta múltiplos seletores para o campo de usuário
        print("   Procurando campo de usuário...")
        user_input = None
        
        selectores_user = [
            "//input[@name='username']",
            "//input[@name='user']",
            "//input[@name='email']",
            "//input[@type='text']",
            "//input[@id='username']",
            "//input[@id='user']",
            "//input[contains(@placeholder,'Usu')]",
            "//input[contains(@placeholder,'Email')]"
        ]
        
        for selector in selectores_user:
            try:
                user_input = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                print(f"   ✅ Campo encontrado com: {selector}")
                break
            except:
                continue
        
        if not user_input:
            print("   ❌ Campo de usuário não encontrado!")
            print("   HTML da página:")
            print(driver.page_source[:1000])
            return False
        
        # Preenche usuário
        user_input.clear()
        time.sleep(0.5)
        user_input.send_keys(LOGIN_USER)
        print(f"   ✅ Usuário '{LOGIN_USER}' inserido")
        
        # Campo de senha
        print("   Procurando campo de senha...")
        pwd_input = None
        
        selectores_pwd = [
            "//input[@name='password']",
            "//input[@name='senha']",
            "//input[@type='password']",
            "//input[@id='password']",
            "//input[contains(@placeholder,'Senha')]"
        ]
        
        for selector in selectores_pwd:
            try:
                pwd_input = driver.find_element(By.XPATH, selector)
                print(f"   ✅ Campo encontrado com: {selector}")
                break
            except:
                continue
        
        if not pwd_input:
            print("   ❌ Campo de senha não encontrado!")
            return False
        
        pwd_input.clear()
        time.sleep(0.5)
        pwd_input.send_keys(LOGIN_PASS)
        print("   ✅ Senha inserida")
        
        # Salva screenshot antes de clicar
        driver.save_screenshot("02_antes_login.png")
        print("   📸 Screenshot: 02_antes_login.png")
        
        # Botão de login
        print("   Procurando botão de login...")
        login_btn = None
        
        selectores_btn = [
            "//button[@type='submit']",
            "//input[@type='submit']",
            "//button[contains(text(),'Entrar')]",
            "//button[contains(text(),'Login')]",
            "//button[contains(text(),'ENTRAR')]",
            "//input[@value='Entrar']",
            "//a[contains(text(),'Entrar')]"
        ]
        
        for selector in selectores_btn:
            try:
                login_btn = driver.find_element(By.XPATH, selector)
                print(f"   ✅ Botão encontrado com: {selector}")
                break
            except:
                continue
        
        if not login_btn:
            print("   ❌ Botão de login não encontrado!")
            return False
        
        # Scroll até o botão e clica
        driver.execute_script("arguments[0].scrollIntoView(true);", login_btn)
        time.sleep(1)
        login_btn.click()
        print("   ✅ Botão clicado")
        
        # Aguarda redirecionamento
        time.sleep(5)
        
        # Salva screenshot após login
        driver.save_screenshot("03_apos_login.png")
        print("   📸 Screenshot: 03_apos_login.png")
        
        # Verifica se login foi bem-sucedido
        current_url = driver.current_url
        print(f"   URL atual: {current_url}")
        
        # Verifica se há mensagem de erro
        page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        
        if any(erro in page_text for erro in ["senha incorreta", "usuário não encontrado", "credenciais inválidas", "login falhou"]):
            print("   ❌ Mensagem de erro detectada na página")
            print(f"   Trecho: {page_text[:300]}")
            return False
        
        if "login" not in current_url.lower() or "dashboard" in current_url.lower() or "home" in current_url.lower():
            print("✅ LOGIN BEM-SUCEDIDO")
            return True
        else:
            print("⚠️ Ainda na página de login - pode ter falhado")
            return False
        
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        import traceback
        traceback.print_exc()
        
        try:
            driver.save_screenshot("login_error.png")
            print("   📸 Screenshot salvo: login_error.png")
        except:
            pass
        return False

def capturar_texto_jogos(driver):
    """Captura o texto dos jogos usando múltiplos métodos"""
    print("\n⚽ NAVEGANDO PARA GUIA FUTEBOL...")
    
    try:
        # MÉTODO 1: Tentar acessar diretamente pela URL
        print("   Tentando acesso direto pela URL...")
        driver.get("https://gerador.pro/guitexto.php")
        time.sleep(5)
        
        current_url = driver.current_url
        print(f"   URL atual: {current_url}")
        
        # Se não funcionou, tenta pelo menu
        if "guitexto" not in current_url:
            print("   ⚠️ URL direta falhou, tentando pelo menu...")
            
            # Procura pelo link "Guia Futebol" no menu
            try:
                link_guia = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.LINK_TEXT, "Guia Futebol"))
                )
                link_guia.click()
                print("   ✅ Link 'Guia Futebol' clicado")
                time.sleep(5)
            except:
                # Tenta outros seletores
                try:
                    link_guia = driver.find_element(By.XPATH, "//a[contains(text(), 'Guia Futebol') or contains(@href, 'guitexto')]")
                    link_guia.click()
                    print("   ✅ Link alternativo clicado")
                    time.sleep(5)
                except Exception as e:
                    print(f"   ❌ Erro ao clicar no link: {e}")
                    return None
        
        # Salva screenshot da página
        driver.save_screenshot("pagina_futebol.png")
        print("   📸 Screenshot salvo: pagina_futebol.png")
        
        current_url = driver.current_url
        print(f"   URL final: {current_url}")
        
        # Verifica se há erro na página
        page_text = driver.find_element(By.TAG_NAME, "body").text
        if "Não foi possível carregar os jogos" in page_text:
            print("   ⚠️ Página mostra erro: 'Não foi possível carregar os jogos'")
            print("   Tentando aguardar carregamento...")
            time.sleep(5)
            driver.refresh()
            time.sleep(5)
        
        # MÉTODO 1: Botão "Copiar Texto"
        print("\n🔍 MÉTODO 1: Procurando botão 'Copiar Texto'")
        try:
            # Espera um pouco para o JavaScript carregar
            time.sleep(3)
            
            # Múltiplos seletores para o botão
            selectores_copiar = [
                "//button[contains(text(), 'Copiar Texto')]",
                "//button[contains(text(), 'Copiar texto')]",
                "//button[contains(text(), 'COPIAR TEXTO')]",
                "//button[contains(@onclick, 'copiar')]",
                "//button[contains(@class, 'copiar')]",
                "//a[contains(text(), 'Copiar Texto')]",
                "//*[contains(text(), 'Copiar Texto')]"
            ]
            
            copiar_btn = None
            for selector in selectores_copiar:
                try:
                    copiar_btn = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    print(f"   ✅ Botão encontrado com: {selector}")
                    break
                except:
                    continue
            
            if copiar_btn:
                # Scroll até o botão
                driver.execute_script("arguments[0].scrollIntoView(true);", copiar_btn)
                time.sleep(1)
                
                # Salva screenshot antes de clicar
                driver.save_screenshot("antes_copiar.png")
                print("   📸 Screenshot antes de copiar: antes_copiar.png")
                
                # Clica no botão
                driver.execute_script("arguments[0].click();", copiar_btn)
                print("   ✅ Botão 'Copiar Texto' clicado")
                
                time.sleep(3)
                
                # Tenta ler do clipboard
                texto = driver.execute_script("""
                    return navigator.clipboard.readText()
                        .then(t => t)
                        .catch(e => '');
                """)
                
                if texto and len(texto) > 50:
                    print(f"   ✅ SUCESSO! Capturado {len(texto)} caracteres via clipboard")
                    return texto
                else:
                    print(f"   ⚠️ Clipboard retornou texto curto: {len(texto) if texto else 0} chars")
            else:
                print("   ⚠️ Botão 'Copiar Texto' não encontrado")
                
        except Exception as e:
            print(f"   ⚠️ Erro no método 1: {e}")
        
        # MÉTODO 2: Textareas
        print("\n🔍 MÉTODO 2: Procurando em textareas")
        textareas = driver.find_elements(By.TAG_NAME, "textarea")
        print(f"   Encontradas {len(textareas)} textareas")
        
        for i, ta in enumerate(textareas):
            texto = ta.get_attribute("value") or ta.text
            if texto:
                print(f"   Textarea {i+1}: {len(texto)} caracteres")
                # Verifica se tem conteúdo de jogos
                if len(texto) > 50 and any(x in texto for x in ["⚽", "vs", "×", "Rodada", "Campeonato", "📆", "🏟️"]):
                    print(f"   ✅ SUCESSO! Texto relevante encontrado em textarea")
                    return texto
        
        # MÉTODO 3: Elementos DOM específicos
        print("\n🔍 MÉTODO 3: Procurando em elementos DOM")
        
        # Seletores específicos para a página
        selectores_texto = [
            "//div[contains(@class, 'jogos')]",
            "//div[contains(@class, 'texto')]",
            "//div[contains(@class, 'content')]",
            "//div[contains(@id, 'texto')]",
            "//div[contains(@id, 'jogos')]",
            "//pre",
            "//code"
        ]
        
        for selector in selectores_texto:
            try:
                elementos = driver.find_elements(By.XPATH, selector)
                for el in elementos:
                    texto = el.text
                    if texto and len(texto) > 100:
                        if any(x in texto for x in ["⚽", "vs", "×", "Rodada", "Campeonato", "📆"]):
                            print(f"   ✅ SUCESSO! Encontrado com {selector}")
                            return texto
            except:
                continue
        
        # MÉTODO 4: Captura TODO o texto da área principal
        print("\n🔍 MÉTODO 4: Capturando área de conteúdo principal")
        try:
            # Tenta encontrar o container principal
            main_content = driver.find_element(By.XPATH, "//main | //div[@class='container'] | //div[@id='content']")
            texto = main_content.text
            
            if texto and len(texto) > 100:
                print(f"   ⚠️ Capturado conteúdo principal: {len(texto)} caracteres")
                return texto
        except:
            pass
        
        # MÉTODO 5: Body completo (último recurso)
        print("\n🔍 MÉTODO 5: Body completo (último recurso)")
        body_text = driver.find_element(By.TAG_NAME, "body").text
        print(f"   Body: {len(body_text)} caracteres")
        
        if body_text and len(body_text) > 100:
            # Filtra apenas texto relevante
            linhas = body_text.split('\n')
            texto_filtrado = '\n'.join([l for l in linhas if any(x in l for x in ["⚽", "vs", "×", "📆", ":", "-"])])
            
            if texto_filtrado:
                print(f"   ⚠️ Texto filtrado do body: {len(texto_filtrado)} caracteres")
                return texto_filtrado
            
            print("   ⚠️ Retornando body completo")
            return body_text
        
        print("\n❌ NENHUM MÉTODO CAPTUROU TEXTO VÁLIDO")
        
        # Debug: mostra o que está na página
        print("\n📄 CONTEÚDO DA PÁGINA (primeiros 500 chars):")
        print(driver.find_element(By.TAG_NAME, "body").text[:500])
        
        return None
        
    except Exception as e:
        print(f"\n❌ ERRO GERAL na captura: {e}")
        import traceback
        traceback.print_exc()
        
        try:
            driver.save_screenshot("erro_captura.png")
            print("📸 Screenshot salvo: erro_captura.png")
        except:
            pass
        return None

def main():
    """Função principal"""
    print("\n" + "=" * 70)
    print("🚀 INICIANDO AUTOMAÇÃO - CAPTURA JOGOS DE FUTEBOL")
    print("=" * 70)
    
    # Valida credenciais
    validar_credenciais()
    
    # Testa Telegram
    if not testar_telegram():
        print("\n⚠️ AVISO: Problemas na conexão com Telegram, mas continuando...")
    
    driver = None
    
    try:
        # Configura driver
        driver = setup_driver()
        
        # Acessa página de login
        print("\n🌐 ACESSANDO SITE...")
        driver.get("https://gerador.pro/login.php")
        print(f"   URL carregada: {driver.current_url}")
        
        # Aguarda o Cloudflare (se aparecer)
        print("   Aguardando possível verificação Cloudflare...")
        time.sleep(10)  # Aguarda 10 segundos para Cloudflare processar
        
        # Verifica se passou do Cloudflare
        page_title = driver.title.lower()
        print(f"   Título da página: {driver.title}")
        
        if "just a moment" in page_title or "cloudflare" in page_title:
            print("   ⚠️ Cloudflare detectado! Aguardando mais 10 segundos...")
            time.sleep(10)
            
            # Tenta recarregar a página
            if "just a moment" in driver.title.lower():
                print("   🔄 Cloudflare ainda ativo, tentando recarregar...")
                driver.refresh()
                time.sleep(10)
        
        print(f"   ✅ Título final: {driver.title}")
        
        # Faz login
        if not fazer_login(driver):
            erro_msg = "❌ *FALHA NO LOGIN*\nVerifique as credenciais!"
            print(f"\n{erro_msg}")
            enviar_telegram(erro_msg, force_send=True)
            return
        
        # Captura texto
        texto = capturar_texto_jogos(driver)
        
        if texto and len(texto) > 50:
            print("\n" + "=" * 70)
            print("📝 TEXTO CAPTURADO COM SUCESSO")
            print("=" * 70)
            print(f"Tamanho: {len(texto)} caracteres")
            print("\nPrévio (primeiros 300 chars):")
            print("-" * 70)
            print(texto[:300] + "..." if len(texto) > 300 else texto)
            print("=" * 70)
            
            # Envia para Telegram
            if enviar_telegram(texto):
                print("\n✅ PROCESSO CONCLUÍDO COM SUCESSO! 🎉")
            else:
                print("\n⚠️ Texto capturado, mas falha ao enviar ao Telegram")
        else:
            erro_msg = "⚠️ *ALERTA*\nNão foi possível capturar o texto dos jogos.\nVerifique os logs do GitHub Actions."
            print(f"\n{erro_msg}")
            enviar_telegram(erro_msg, force_send=True)
    
    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        
        erro_msg = f"❌ *ERRO CRÍTICO NO SCRIPT*\n\n```\n{str(e)[:200]}\n```"
        try:
            enviar_telegram(erro_msg, force_send=True)
        except:
            print("❌ Não foi possível enviar notificação de erro ao Telegram")
    
    finally:
        if driver:
            driver.quit()
            print("\n🔒 Navegador fechado")
        
        print("\n" + "=" * 70)
        print("🏁 EXECUÇÃO FINALIZADA")
        print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
