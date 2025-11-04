import os
import time
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager
import requests

def setup_driver():
    print("🔧 Configurando Chrome...")
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.page_load_strategy = 'normal'
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(60)
    print("✅ Chrome configurado!")
    return driver

def enviar_telegram(msg):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("CHAT_ID")
    if not token or not chat_id:
        print("⚠️ TELEGRAM_BOT_TOKEN ou CHAT_ID não configurados.")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            print("✅ Mensagem enviada ao Telegram!")
        else:
            print(f"⚠️ Falha ao enviar Telegram: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Erro ao enviar Telegram: {e}")

def wait_for_page_load(driver, timeout=10):
    """Aguarda a página carregar completamente"""
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(2)  # Espera adicional para JS executar
        return True
    except:
        return False

def fazer_login(driver, login, senha):
    print("🔑 Fazendo login no GERADOR PRO...")
    try:
        driver.get("https://gerador.pro/login.php")
        wait_for_page_load(driver)
        
        print("Localizando campo username...")
        username_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        username_field.clear()
        time.sleep(0.5)
        username_field.send_keys(login)
        print(f"Username '{login}' inserido")
        
        print("Localizando campo password...")
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        password_field.clear()
        time.sleep(0.5)
        password_field.send_keys(senha)
        print("Password inserido")
        
        print("Localizando botão submit...")
        submit_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[@type='submit']"))
        )
        
        # Tenta clicar de diferentes formas
        try:
            submit_button.click()
        except ElementClickInterceptedException:
            driver.execute_script("arguments[0].click();", submit_button)
        
        print("Aguardando redirecionamento após login...")
        WebDriverWait(driver, 20).until(
            lambda d: "login.php" not in d.current_url
        )
        
        wait_for_page_load(driver)
        print(f"✅ Login realizado! URL atual: {driver.current_url}")
        
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        print(f"URL atual: {driver.current_url}")
        raise

def acessar_todos_esportes(driver):
    print("🏆 Acessando menu 'Todos esportes'...")
    
    try:
        wait_for_page_load(driver, 15)
        
        # Tenta diferentes formas de localizar o link
        links_tentativas = [
            (By.XPATH, "//a[contains(text(),'Todos esportes')]"),
            (By.XPATH, "//a[contains(@href,'esportes.php')]"),
            (By.LINK_TEXT, "Todos esportes"),
            (By.PARTIAL_LINK_TEXT, "esportes"),
        ]
        
        link_encontrado = False
        for by, value in links_tentativas:
            try:
                print(f"Tentando localizar com {by}: {value}")
                link = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((by, value))
                )
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", link)
                link_encontrado = True
                print(f"✅ Clicou no link usando {by}")
                break
            except Exception as e:
                print(f"Tentativa com {by} falhou: {str(e)[:100]}")
                continue
        
        if not link_encontrado:
            print("⚠️ Link não encontrado, acessando URL direta")
            driver.get("https://gerador.pro/esportes.php")
        
        wait_for_page_load(driver, 20)
        
        # Verifica se chegou na página certa
        if "esportes" not in driver.current_url.lower():
            raise Exception(f"Não chegou na página de esportes. URL: {driver.current_url}")
        
        print(f"✅ Página de esportes carregada! URL: {driver.current_url}")
        
    except Exception as e:
        print(f"❌ Erro ao acessar esportes: {e}")
        raise

def selecionar_modelo_roxo(driver):
    print("🎨 Selecionando modelo 'Esportes Roxo'...")
    
    try:
        wait_for_page_load(driver, 10)
        
        # Scroll para ver os modelos
        driver.execute_script("window.scrollTo(0, 400);")
        time.sleep(2)
        
        # Lista de seletores para tentar
        seletores = [
            (By.XPATH, "//div[contains(text(),'Esportes Roxo')]"),
            (By.XPATH, "//div[contains(text(),'Roxo')]"),
            (By.XPATH, "//*[contains(@class,'modelo') and contains(text(),'Roxo')]"),
            (By.XPATH, "//button[contains(text(),'Roxo')]"),
            (By.XPATH, "//*[contains(text(),'roxo')]"),
        ]
        
        modelo_clicado = False
        for by, selector in seletores:
            try:
                print(f"Tentando seletor: {selector}")
                modelo = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((by, selector))
                )
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", modelo)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", modelo)
                modelo_clicado = True
                print(f"✅ Modelo clicado usando: {selector}")
                time.sleep(3)
                break
            except Exception as e:
                print(f"Seletor falhou: {str(e)[:80]}")
                continue
        
        if not modelo_clicado:
            print("⚠️ Tentando URL direta com parâmetro")
            driver.get("https://gerador.pro/esportes.php?modelo=roxo")
            wait_for_page_load(driver)
        
        print("✅ Modelo Roxo selecionado!")
        
    except Exception as e:
        print(f"❌ Erro ao selecionar modelo: {e}")
        raise

def gerar_banners(driver):
    print("⚙️ Gerando banners...")
    
    try:
        wait_for_page_load(driver, 10)
        
        # Scroll até o final
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        print("Procurando botão 'Gerar Banners'...")
        seletores_botao = [
            (By.XPATH, "//button[contains(text(),'Gerar Banners')]"),
            (By.XPATH, "//button[contains(text(),'Gerar banners')]"),
            (By.XPATH, "//button[contains(text(),'GERAR')]"),
            (By.XPATH, "//*[@type='submit' and contains(text(),'Gerar')]"),
        ]
        
        botao = None
        for by, selector in seletores_botao:
            try:
                botao = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((by, selector))
                )
                if botao:
                    print(f"Botão encontrado com: {selector}")
                    break
            except:
                continue
        
        if not botao:
            raise Exception("Botão 'Gerar Banners' não encontrado")
        
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", botao)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", botao)
        print("✅ Botão 'Gerar Banners' clicado!")

        # Aguarda processamento - tempo maior
        print("Aguardando processamento dos banners...")
        time.sleep(8)

        # Tenta fechar popup de sucesso se aparecer
        try:
            popup_ok = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(text(),'OK') or contains(text(),'Ok')]"))
            )
            print("🎉 Popup de sucesso encontrado!")
            driver.execute_script("arguments[0].click();", popup_ok)
            time.sleep(3)
        except TimeoutException:
            print("⚠️ Popup não apareceu (isso pode ser normal)")
        
        wait_for_page_load(driver, 15)
        
    except Exception as e:
        print(f"❌ Erro ao gerar banners: {e}")
        raise

def enviar_todas_as_imagens(driver):
    print("📤 Enviando todas as imagens...")
    
    try:
        # Aguarda chegar na página de cartazes
        print("Aguardando página de cartazes...")
        WebDriverWait(driver, 30).until(
            lambda d: "cartazes" in d.current_url.lower() or "cartaz" in d.current_url.lower()
        )
        
        wait_for_page_load(driver, 15)
        print(f"✅ Página de cartazes carregada: {driver.current_url}")
        
        # Scroll até o final
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        
        print("Procurando botão 'Enviar Todas'...")
        seletores_enviar = [
            (By.XPATH, "//button[contains(text(),'Enviar Todas')]"),
            (By.XPATH, "//button[contains(text(),'Enviar todas')]"),
            (By.XPATH, "//button[contains(text(),'ENVIAR TODAS')]"),
            (By.XPATH, "//button[contains(text(),'Enviar')]"),
        ]
        
        botao_enviar = None
        for by, selector in seletores_enviar:
            try:
                botao_enviar = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((by, selector))
                )
                if botao_enviar:
                    print(f"Botão encontrado com: {selector}")
                    break
            except:
                continue
        
        if not botao_enviar:
            raise Exception("Botão 'Enviar Todas' não encontrado")
        
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", botao_enviar)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", botao_enviar)
        print("✅ Botão 'Enviar Todas as Imagens' clicado!")
        
        # Aguarda envio completar
        time.sleep(10)
        print("✅ Envio concluído!")
        
    except Exception as e:
        print(f"❌ Erro ao enviar imagens: {e}")
        raise

def main():
    print("=" * 60)
    print("🚀 AUTOMAÇÃO ESPORTES ROXO - INICIANDO")
    print("=" * 60)
    
    # Validação de variáveis de ambiente
    login = os.environ.get("LOGIN")
    senha = os.environ.get("SENHA")
    
    if not login or not senha:
        msg_erro = "❌ LOGIN ou SENHA não configurados nas variáveis de ambiente!"
        print(msg_erro)
        enviar_telegram(f"❌ *Erro Crítico:*\n{msg_erro}")
        return
    
    print(f"✅ Credenciais encontradas para usuário: {login}")
    
    driver = None
    
    try:
        # Etapa 1: Setup
        driver = setup_driver()
        print("\n" + "=" * 60)
        
        # Etapa 2: Login
        print("ETAPA 1/5: Login")
        print("=" * 60)
        fazer_login(driver, login, senha)
        
        # Etapa 3: Acessar esportes
        print("\n" + "=" * 60)
        print("ETAPA 2/5: Acessar Todos Esportes")
        print("=" * 60)
        acessar_todos_esportes(driver)
        
        # Etapa 4: Selecionar modelo
        print("\n" + "=" * 60)
        print("ETAPA 3/5: Selecionar Modelo Roxo")
        print("=" * 60)
        selecionar_modelo_roxo(driver)
        
        # Etapa 5: Gerar banners
        print("\n" + "=" * 60)
        print("ETAPA 4/5: Gerar Banners")
        print("=" * 60)
        gerar_banners(driver)
        
        # Etapa 6: Enviar imagens
        print("\n" + "=" * 60)
        print("ETAPA 5/5: Enviar Imagens")
        print("=" * 60)
        enviar_todas_as_imagens(driver)
        
        # Sucesso!
        print("\n" + "=" * 60)
        print("🎯 PROCESSO FINALIZADO COM SUCESSO!")
        print("=" * 60)
        enviar_telegram("✅ *Banners Esportes Roxo gerados e enviados com sucesso!*")
        
    except Exception as e:
        erro_completo = traceback.format_exc()
        print("\n" + "=" * 60)
        print("❌ ERRO DURANTE EXECUÇÃO")
        print("=" * 60)
        print(f"Erro: {str(e)}")
        print(f"\nStacktrace completo:\n{erro_completo}")
        
        enviar_telegram(f"❌ *Erro no script Esportes:*\n```\n{str(e)[:300]}\n```")
        
        # Salva screenshot
        if driver:
            try:
                screenshot_path = "erro_screenshot.png"
                driver.save_screenshot(screenshot_path)
                print(f"\n📸 Screenshot salvo: {screenshot_path}")
                print(f"URL no momento do erro: {driver.current_url}")
            except Exception as screenshot_error:
                print(f"⚠️ Não foi possível salvar screenshot: {screenshot_error}")
    
    finally:
        if driver:
            try:
                driver.quit()
                print("\n🔒 Navegador fechado.")
            except:
                pass

if __name__ == "__main__":
    main()
