#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import time
import traceback
# Importa uc no lugar de webdriver
import undetected_chromedriver as uc 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
# Não precisamos mais de Service ou ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import requests

# Use variáveis de ambiente para credenciais de forma segura
LOGIN = os.environ.get("LOGIN")
SENHA = os.environ.get("SENHA")

def setup_driver():
    print("🔧 Configurando Chrome com undetected_chromedriver...")
    options = Options()
    # options.add_argument("--headless=new") # Removido para ajudar a resolver o desafio Cloudflare visualmente se necessário
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    # uc.Chrome lida com a maioria das opções anti-detecção e downloads de driver automaticamente.
    driver = uc.Chrome(options=options, auto_subprocs=True, page_load_timeout=60)
    print("✅ Chrome configurado e pronto para bypass Cloudflare!")
    return driver

def enviar_telegram(msg):
    """Envia uma mensagem para o Telegram e força falha se houver erro."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("CHAT_ID")
    if not token or not chat_id:
        print("⚠️ TELEGRAM_BOT_TOKEN ou CHAT_ID não configurados. Pulando envio.")
        return # Permite que o script continue se as variáveis estiverem vazias
    
    url = f"api.telegram.org{token}/sendMessage"
    data = {"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}
    
    try:
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            print("✅ Mensagem enviada ao Telegram com sucesso!")
        else:
            print(f"⚠️ Falha ao enviar Telegram. Status: {response.status_code}, Resposta: {response.text}")
            # FORÇA O GITHUB ACTIONS A FALHAR AQUI
            raise Exception(f"Erro na API do Telegram: {response.text}") 
    except Exception as e:
        print(f"⚠️ Erro de conexão ao enviar Telegram: {e}")
        # FORÇA O GITHUB ACTIONS A FALHAR AQUI
        raise Exception(f"Erro de conexão ao enviar Telegram: {e}")

def wait_for_page_load(driver, timeout=20):
    """Aguarda a página carregar completamente, incluindo scripts Cloudflare."""
    print("⏳ Aguardando a página carregar e resolver desafios Cloudflare...")
    try:
        # Dá tempo extra para o Cloudflare resolver o desafio JS
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        # Verifica se o Cloudflare ainda está a apresentar um desafio
        if "Verifying" in driver.title or "Just a moment" in driver.page_source:
             print("Cloudflare challenge detectado. Aguardando resolução automática...")
             WebDriverWait(driver, 30).until_not(
                 EC.title_contains("Verifying")
             )
        time.sleep(3)
        return True
    except TimeoutException:
        print("⚠️ Tempo limite de carregamento excedido, mas a navegar de qualquer forma.")
        return False
    except Exception as e:
        print(f"⚠️ Erro ao esperar pelo carregamento da página: {e}")
        return False

def fazer_login(driver, login, senha):
    print("🔑 Fazendo login no GERADOR PRO...")
    try:
        driver.get("gerador.pro")
        wait_for_page_load(driver)
        
        username_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        username_field.clear()
        username_field.send_keys(login)
        print(f"Username inserido.")
        
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        password_field.clear()
        password_field.send_keys(senha)
        print("Password inserido.")
        
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
        )
        
        try:
            submit_button.click()
        except ElementClickInterceptedException:
            driver.execute_script("arguments[0].click();", submit_button)
        
        print("Aguardando redirecionamento após login...")
        WebDriverWait(driver, 20).until_not(
            EC.url_contains("login.php")
        )
        
        wait_for_page_load(driver)
        if "painel" in driver.current_url or "futbanner" in driver.current_url:
             print(f"✅ Login realizado! URL atual: {driver.current_url}")
        else:
            # Captura source da página se o login falhar
            # print(f"Source da página atual:\n{driver.page_source}")
            raise Exception(f"Login falhou. URL destino inesperada: {driver.current_url}")
        
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        enviar_telegram(f"❌ Automação falhou no login! Erro: {e}")
        raise

def acessar_todos_esportes(driver):
    print("🏆 Acessando menu 'Todos esportes'...")
    try:
        wait_for_page_load(driver, 15)
        
        selectors = [
            (By.LINK_TEXT, "Todos esportes"),
            (By.XPATH, "//a[contains(@href,'esportes.php')]"),
        ]
        
        link = None
        for by, value in selectors:
            try:
                link = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((by, value))
                )
                break
            except:
                continue
        
        if link:
            driver.execute_script("arguments[0].scrollIntoView(true);", link)
            time.sleep(1)
            link.click()
        else:
            print("⚠️ Link 'Todos esportes' não encontrado, acessando URL direta.")
            driver.get("gerador.pro")
        
        wait_for_page_load(driver, 20)
        
        if "esportes" not in driver.current_url.lower():
            raise Exception(f"Não chegou na página de esportes. URL: {driver.current_url}")
        
        print(f"✅ Página de esportes carregada! URL: {driver.current_url}")
        
    except Exception as e:
        print(f"❌ Erro ao acessar esportes: {e}")
        enviar_telegram(f"❌ Automação falhou ao acessar esportes! Erro: {e}")
        raise

def selecionar_modelo_roxo(driver):
    print("🎨 Selecionando modelo 'Esportes Roxo'...")
    try:
        wait_for_page_load(driver, 10)
        driver.execute_script("window.scrollTo(0, 400);")
        time.sleep(1)
        
        selectors ="),
            (By.XPATH, "//*[contains(@class,'modelo')]/*"),
            (By.XPATH, "//button"),
        ]
        
        modelo = None
        for by, selector in selectors:
            try:
                modelo = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((by, selector))
                )
                break
            except:
                continue

        if modelo:
            driver.execute_script("arguments[0].scrollIntoView(true);", modelo)
            time.sleep(1)
            modelo.click()
            time.sleep(3)
        else:
            print("⚠️ Modelo 'Roxo' não encontrado via clique, acessando URL direta.")
            driver.get("gerador.pro?modelo=roxo")
        
        wait_for_page_load(driver)
        print("✅ Modelo Roxo selecionado!")
        
    except Exception as e:
        print(f"❌ Erro ao selecionar modelo: {e}")
        enviar_telegram(f"❌ Automação falhou ao selecionar modelo! Erro: {e}")
        raise

def gerar_banners(driver):
    print("⚙️ Gerando banners...")
    try:
        wait_for_page_load(driver, 10)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        print("Procurando botão 'Gerar Banners'...")
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Gerar Banners') or contains(.,'Gerar')]"))
        )
        
        button.click()
        print("✅ Botão 'Gerar Banners' clicado.")
        
        try:
            WebDriverWait(driver, 5).until(EC.alert_is_present())
            driver.switch_to.alert.accept()
            print("Alerta JS aceito.")
        except TimeoutException:
            print("Nenhum alerta JS encontrado.")
            pass

        time.sleep(10) 
        wait_for_page_load(driver)

        if "cartazes" in driver.current_url:
             print("✅ Banners gerados com sucesso! Redirecionado para a galeria.")
        else:
             # print(f"Source da página:\n{driver.page_source}")
             raise Exception("Geração de banners falhou ou não redirecionou para 'cartazes'.")

    except Exception as e:
        print(f"❌ Erro ao gerar banners: {e}")
        enviar_telegram(f"❌ Automação falhou ao gerar banners! Erro: {e}")
        raise


def main():
    if not LOGIN or not SENHA:
        msg = "Erro: LOGIN ou SENHA não definidos nas variáveis de ambiente."
        print(msg)
        enviar_telegram(f"❌ Automação falhou: {msg}")
        return

    driver = None
    try:
        driver = setup_driver()
        fazer_login(driver, LOGIN, SENHA)
        acessar_todos_esportes(driver)
        selecionar_modelo_roxo(driver)
        gerar_banners(driver)
        
        print("🎉 Script principal concluído com sucesso!")
        enviar_telegram("✅ Automação 'AutoGerar Esportes' concluída com sucesso no GitHub Actions!")
        
    except Exception as e:
        print("\n" + "="*50)
        print("Ocorreu um erro crítico no fluxo principal.")
        print(f"Erro: {e}")
        print("Traceback:")
        traceback.print_exc()
        print("="*50)
        if driver:
            print(f"URL final onde o erro ocorreu: {driver.current_url}")
    finally:
        if driver:
            driver.quit()
            print("🔒 Navegador fechado.")

if __name__ == "__main__":
    main()
