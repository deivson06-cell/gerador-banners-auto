import os
import sys
import time
import traceback
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# ===============================
# 🔧 CONFIGURAÇÕES
# ===============================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
CHAT_ID = os.environ.get("CHAT_ID", "")
LOGIN = os.environ.get("LOGIN", "")
SENHA = os.environ.get("SENHA", "")
RUN_ID = os.environ.get("GITHUB_RUN_ID", "")
REPO = os.environ.get("GITHUB_REPOSITORY", "")

# Validação de variáveis obrigatórias
if not all([BOT_TOKEN, CHAT_ID, LOGIN, SENHA]):
    print("❌ ERRO: Variáveis de ambiente obrigatórias não configuradas!")
    print("Configure: BOT_TOKEN, CHAT_ID, LOGIN, SENHA")
    sys.exit(1)

# Timeouts configuráveis
TIMEOUT_CLOUDFLARE = 20
TIMEOUT_PADRAO = 35
TIMEOUT_GERAR = 25
TIMEOUT_ENVIAR = 20

print("✅ Variáveis de ambiente carregadas com sucesso!")
print(f"🤖 Bot Token: {BOT_TOKEN[:15]}...")
print(f"💬 Chat ID: {CHAT_ID}")
print(f"👤 Login: {LOGIN}")

# ===============================
# 📡 FUNÇÕES TELEGRAM
# ===============================
def enviar_telegram(msg, imagem=None, tentativas=3):
    """Envia mensagens ou imagens para o Telegram com retry."""
    for i in range(tentativas):
        try:
            if imagem and os.path.exists(imagem):
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
                with open(imagem, "rb") as img:
                    response = requests.post(
                        url, 
                        data={"chat_id": CHAT_ID, "caption": msg, "parse_mode": "HTML"}, 
                        files={"photo": img},
                        timeout=30
                    )
            else:
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                response = requests.post(
                    url, 
                    data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"},
                    timeout=30
                )
            
            if response.status_code == 200:
                print(f"✅ Telegram enviado: {msg[:60]}...")
                return True
            else:
                print(f"⚠️ Telegram falhou (Status {response.status_code}): {response.text}")
                
        except Exception as e:
            print(f"⚠️ Tentativa {i+1}/{tentativas} falhou: {e}")
            if i < tentativas - 1:
                time.sleep(2)
    
    print(f"❌ Falha ao enviar para Telegram após {tentativas} tentativas")
    return False

def salvar_print(driver, nome):
    """Salva screenshot e retorna o caminho."""
    try:
        pasta = "prints"
        os.makedirs(pasta, exist_ok=True)
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        caminho = os.path.join(pasta, f"{timestamp}_{nome}.png")
        driver.save_screenshot(caminho)
        print(f"📸 Print salvo: {caminho}")
        return caminho
    except Exception as e:
        print(f"❌ Erro ao salvar print: {e}")
        return None

# ===============================
# 🧠 CONFIGURAÇÃO DO CHROME
# ===============================
def setup_driver():
    """Configura Chrome com anti-detecção."""
    print("\n" + "="*60)
    print("🚀 INICIANDO CHROME COM ANTI-DETECÇÃO")
    print("="*60)
    
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Preferências adicionais
    prefs = {
        "profile.default_content_setting_values.notifications": 2,
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False
    }
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    try:
        # Tenta ChromeDriver padrão
        try:
            service = Service("/usr/local/bin/chromedriver")
            driver = webdriver.Chrome(service=service, options=chrome_options)
            print("✅ ChromeDriver padrão inicializado")
        except:
            # Fallback para Chromium
            chrome_options.binary_location = "/usr/bin/chromium-browser"
            driver = webdriver.Chrome(options=chrome_options)
            print("✅ Chromium inicializado")
        
        driver.set_page_load_timeout(60)
        driver.implicitly_wait(10)
        
        # Remove flags de automação
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("✅ Chrome configurado com sucesso!")
        print("="*60 + "\n")
        return driver
        
    except Exception as e:
        print(f"❌ Erro ao iniciar Chrome: {e}")
        enviar_telegram(f"❌ Falha ao iniciar navegador:\n{str(e)[:300]}")
        raise

# ===============================
# 🔐 LOGIN
# ===============================
def fazer_login(driver):
    """Realiza o login no site."""
    print("\n" + "="*60)
    print("🔐 INICIANDO PROCESSO DE LOGIN")
    print("="*60)
    
    enviar_telegram("🟡 <b>Iniciando login no gerador.pro...</b>")
    
    try:
        # Acessa a página de login
        print("📄 Acessando: https://gerador.pro/painel")
        driver.get("https://gerador.pro/painel")
        print(f"✅ Página carregada: {driver.current_url}")
        
        # Aguarda Cloudflare
        print(f"⏳ Aguardando Cloudflare ({TIMEOUT_CLOUDFLARE}s)...")
        time.sleep(TIMEOUT_CLOUDFLARE)
        
        # Print pós-Cloudflare
        img1 = salvar_print(driver, "01_cloudflare")
        enviar_telegram("🛡️ Cloudflare bypass concluído", img1)
        
        # Aguarda campo de usuário
        print("⌨️ Procurando campos de login...")
        campo_user = WebDriverWait(driver, TIMEOUT_PADRAO).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        campo_pass = driver.find_element(By.NAME, "password")
        print("✅ Campos encontrados!")
        
        # Preenche com digitação humanizada
        print(f"✍️ Preenchendo usuário: {LOGIN}")
        campo_user.clear()
        time.sleep(0.5)
        for char in LOGIN:
            campo_user.send_keys(char)
            time.sleep(0.12)
        
        print("✍️ Preenchendo senha...")
        time.sleep(0.5)
        campo_pass.clear()
        time.sleep(0.5)
        for char in SENHA:
            campo_pass.send_keys(char)
            time.sleep(0.12)
        
        time.sleep(1.5)
        
        # Print antes do login
        img2 = salvar_print(driver, "02_antes_login")
        enviar_telegram("📋 Credenciais preenchidas", img2)
        
        # Clica no botão de login
        print("🖱️ Clicando em 'Entrar no painel'...")
        botao_login = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, 
                "//button[contains(text(),'Entrar') or contains(text(),'Login') or contains(text(),'Entrar no painel')]"))
        )
        driver.execute_script("arguments[0].click();", botao_login)
        print("✅ Botão clicado!")
        
        # Aguarda redirecionamento
        print("⏳ Aguardando redirecionamento (10s)...")
        time.sleep(10)
        
        WebDriverWait(driver, TIMEOUT_PADRAO).until(
            EC.url_contains("painel")
        )
        
        print(f"✅ Login realizado com sucesso!")
        print(f"📍 URL atual: {driver.current_url}")
        img3 = salvar_print(driver, "03_apos_login")
        enviar_telegram(f"✅ <b>Login realizado com sucesso!</b>\n📍 {driver.current_url}", img3)
        
        print("="*60 + "\n")
        time.sleep(3)
        return True
        
    except TimeoutException as e:
        print(f"⏱️ TIMEOUT durante login!")
        img = salvar_print(driver, "ERRO_timeout_login")
        enviar_telegram(f"⏱️ <b>Timeout no login</b>\nURL: {driver.current_url}", img)
        return False
    except Exception as e:
        print(f"❌ ERRO no login: {e}")
        img = salvar_print(driver, "ERRO_login")
        enviar_telegram(f"❌ <b>Erro no login</b>\n{str(e)[:300]}\nURL: {driver.current_url}", img)
        return False

# ===============================
# ⚙️ GERAR BANNERS
# ===============================
def gerar_banners(driver):
    """Gera e envia os banners."""
    print("\n" + "="*60)
    print("🎯 INICIANDO GERAÇÃO DE BANNERS")
    print("="*60)
    
    try:
        # Acessa página de futebol
        print("⚽ Acessando: https://gerador.pro/futebol")
        driver.get("https://gerador.pro/futebol")
        time.sleep(6)
        print(f"✅ Página carregada: {driver.current_url}")
        
        img1 = salvar_print(driver, "04_pagina_futebol")
        enviar_telegram("📄 Página Futebol carregada", img1)
        
        # Seleciona modelo 15
        print("🔢 Selecionando modelo 15...")
        enviar_telegram("📸 Selecionando modelo 15...")
        
        botao_15 = WebDriverWait(driver, TIMEOUT_PADRAO).until(
            EC.element_to_be_clickable((By.XPATH, 
                "//button[contains(text(),'15') or @data-model='15' or @value='15']"))
        )
        driver.execute_script("arguments[0].click();", botao_15)
        time.sleep(4)
        print("✅ Modelo 15 selecionado!")
        
        img2 = salvar_print(driver, "05_modelo_15")
        enviar_telegram("✅ Modelo 15 selecionado", img2)
        
        # Clica em Gerar Banners
        print("🎨 Clicando em 'Gerar Banners'...")
        enviar_telegram("⚙️ <b>Gerando banners do modelo 15...</b>")
        
        botao_gerar = WebDriverWait(driver, TIMEOUT_PADRAO).until(
            EC.element_to_be_clickable((By.XPATH, 
                "//button[contains(text(),'Gerar Banners') or contains(text(),'Gerar')]"))
        )
        driver.execute_script("arguments[0].click();", botao_gerar)
        print("✅ Botão 'Gerar' clicado!")
        
        # Aguarda geração
        print(f"⏳ Aguardando geração dos banners ({TIMEOUT_GERAR}s)...")
        time.sleep(TIMEOUT_GERAR)
        
        img3 = salvar_print(driver, "06_banners_gerados")
        enviar_telegram("✅ <b>Banners gerados com sucesso!</b>", img3)
        
        # Clica em OK
        print("🆗 Procurando botão OK...")
        try:
            botao_ok = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'OK')]"))
            )
            driver.execute_script("arguments[0].click();", botao_ok)
            time.sleep(5)
            print("✅ Botão OK clicado!")
        except TimeoutException:
            print("⚠️ Botão OK não encontrado, continuando...")
        
        # Envia todas as imagens
        print("📤 Clicando em 'Enviar todas as imagens'...")
        enviar_telegram("📤 <b>Enviando todas as imagens...</b>")
        
        botao_enviar = WebDriverWait(driver, TIMEOUT_PADRAO).until(
            EC.element_to_be_clickable((By.XPATH, 
                "//button[contains(text(),'Enviar todas as imagens') or contains(text(),'Enviar')]"))
        )
        driver.execute_script("arguments[0].click();", botao_enviar)
        print("✅ Botão 'Enviar' clicado!")
        
        # Aguarda envio
        print(f"⏳ Aguardando envio das imagens ({TIMEOUT_ENVIAR}s)...")
        time.sleep(TIMEOUT_ENVIAR)
        
        img4 = salvar_print(driver, "07_banners_enviados")
        enviar_telegram("🎉 <b>Banners gerados e enviados com sucesso!</b>", img4)
        
        print("="*60 + "\n")
        return True
        
    except TimeoutException as e:
        print(f"⏱️ TIMEOUT durante geração de banners!")
        img = salvar_print(driver, "ERRO_timeout_gerar")
        enviar_telegram(f"⏱️ <b>Timeout ao gerar banners</b>\nURL: {driver.current_url}", img)
        return False
    except Exception as e:
        print(f"❌ ERRO ao gerar banners: {e}")
        img = salvar_print(driver, "ERRO_gerar")
        enviar_telegram(f"❌ <b>Erro ao gerar banners</b>\n{str(e)[:300]}\nURL: {driver.current_url}", img)
        return False

# ===============================
# 📊 RELATÓRIO FINAL
# ===============================
def relatorio(status_login, status_geracao, tempo_total, caminho_print=None):
    """Envia relatório final ao Telegram."""
    link_print = ""
    if caminho_print and RUN_ID and REPO:
        link_print = f"\n🖼️ <a href='https://github.com/{REPO}/actions/runs/{RUN_ID}'>Ver prints no GitHub Actions</a>"

    status_final = "✅ <b>SUCESSO TOTAL</b>" if (status_login and status_geracao) else "❌ <b>PROCESSO FALHOU</b>"
    
    msg = (
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🧾 <b>RELATÓRIO FINAL — P2PLUS BANNER</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📊 Status Geral: {status_final}\n\n"
        f"🔑 Login: {'✅ Sucesso' if status_login else '❌ Falhou'}\n"
        f"⚽ Geração de Banners: {'✅ Sucesso' if status_geracao else '❌ Falhou'}\n"
        f"⏱️ Duração Total: <b>{tempo_total:.1f}s</b> ({tempo_total/60:.1f} min)\n"
        f"{link_print}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📢 Canal: @P2PLUS\n"
        f"🤖 Automação GitHub Actions"
    )
    enviar_telegram(msg)

# ===============================
# 🎯 EXECUÇÃO PRINCIPAL
# ===============================
def main():
    """Função principal."""
    print("\n" + "="*60)
    print("🚀 AUTOMAÇÃO P2PLUS BANNER - INICIANDO")
    print("="*60)
    print(f"⏰ Horário de início: {time.strftime('%d/%m/%Y %H:%M:%S')}")
    print("="*60 + "\n")
    
    inicio = time.time()
    status_login = False
    status_geracao = False
    driver = None
    caminho_print = None

    try:
        enviar_telegram(
            f"🚀 <b>AUTOMAÇÃO INICIADA</b>\n\n"
            f"⏰ Horário: {time.strftime('%d/%m/%Y %H:%M:%S')}\n"
            f"🤖 GitHub Actions\n"
            f"📢 Canal: @P2PLUS"
        )
        
        # 1. Configurar driver
        driver = setup_driver()
        
        # 2. Fazer login
        status_login = fazer_login(driver)
        
        if not status_login:
            raise Exception("❌ Falha no login - Processo abortado")
        
        # 3. Gerar banners
        status_geracao = gerar_banners(driver)
        
        if status_geracao:
            caminho_print = salvar_print(driver, "08_SUCESSO_FINAL")
            print("\n" + "="*60)
            print("🎉 PROCESSO CONCLUÍDO COM SUCESSO TOTAL!")
            print("="*60 + "\n")
        else:
            raise Exception("❌ Falha na geração de banners")

    except Exception as e:
        print("\n" + "="*60)
        print(f"❌ ERRO CRÍTICO: {e}")
        print("="*60)
        print(f"📋 Traceback completo:\n{traceback.format_exc()}")
        
        if driver:
            caminho_print = salvar_print(driver, "ERRO_CRITICO")
            enviar_telegram(
                f"❌ <b>ERRO DURANTE EXECUÇÃO</b>\n\n"
                f"Detalhes: {str(e)[:400]}\n\n"
                f"Verifique os prints enviados anteriormente.",
                caminho_print
            )
        else:
            enviar_telegram(f"❌ <b>ERRO CRÍTICO</b>\n\n{str(e)[:400]}")

    finally:
        # Calcular tempo total
        tempo_total = time.time() - inicio
        
        # Fechar navegador
        if driver:
            try:
                driver.quit()
                print("✅ Navegador fechado com sucesso")
            except:
                print("⚠️ Erro ao fechar navegador")
        
        # Enviar relatório final
        print("\n📊 Gerando relatório final...")
        relatorio(status_login, status_geracao, tempo_total, caminho_print)
        
        # Status final
        print("\n" + "="*60)
        if status_login and status_geracao:
            print("✅ STATUS FINAL: SUCESSO TOTAL")
        else:
            print("❌ STATUS FINAL: PROCESSO FALHOU")
        print(f"⏰ Horário de término: {time.strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"⏱️ Duração total: {tempo_total:.1f}s ({tempo_total/60:.1f} min)")
        print("="*60)
        print("🏁 EXECUÇÃO FINALIZADA")
        print("="*60 + "\n")

if __name__ == "__main__":
    main()
