#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import re
import traceback
from datetime import datetime
from urllib.parse import urljoin

import requests
import cloudscraper
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# ---------------------------
# Config
# ---------------------------
BASE_URL = "https://gerador.pro/"
LOGIN_URL = urljoin(BASE_URL, "login.php")
NBA_URL = urljoin(BASE_URL, "nba.php")
FUTEBOL_CARTAZES = urljoin(BASE_URL, "futebol/cartazes/")

# ---------------------------
# Utilitários
# ---------------------------
def enviar_telegram(msg: str):
    token = os.environ.get("BOT_TOKEN")
    chat_id = os.environ.get("CHAT_ID")
    if not token or not chat_id:
        print("⚠️ BOT_TOKEN ou CHAT_ID não configurados.")
        return False
    try:
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage", data={
            "chat_id": chat_id,
            "text": msg,
            "parse_mode": "Markdown"
        }, timeout=15)
        print("📨 Mensagem enviada ao Telegram!")
        return True
    except Exception as e:
        print("⚠️ Falha ao enviar mensagem Telegram:", e)
        return False

def salvar_print(driver, nome):
    pasta = "prints"
    os.makedirs(pasta, exist_ok=True)
    caminho = f"{pasta}/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{nome}.png"
    try:
        driver.save_screenshot(caminho)
        print("📸 Print salvo:", caminho)
    except Exception as e:
        print("⚠️ Falha ao salvar print:", e)
    return caminho

# ---------------------------
# Login via cloudscraper (resolve Cloudflare JS challenge)
# ---------------------------
def login_cloudscraper(login, senha, session=None):
    """
    Retorna (session, message) onde session é um cloudscraper.Session autenticado (ou None).
    """
    try:
        if session is None:
            session = cloudscraper.create_scraper()  # cloudscraper.Session-like

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/118.0.5993.118 Safari/537.36",
            "Referer": LOGIN_URL,
        }

        # 1) GET login page (cloudscraper lida com Cloudflare)
        r = session.get(LOGIN_URL, headers=headers, timeout=30)
        if r.status_code != 200:
            return None, f"Falha ao acessar login page: status {r.status_code}"

        # 2) extrair hidden inputs (simples)
        hidden = {}
        for match in re.finditer(r'<input[^>]+type=["\']hidden["\'][^>]*>', r.text, flags=re.I):
            tag = match.group(0)
            name_m = re.search(r'name=["\']([^"\']+)["\']', tag, flags=re.I)
            val_m = re.search(r'value=["\']([^"\']*)["\']', tag, flags=re.I)
            if name_m:
                hidden[name_m.group(1)] = val_m.group(1) if val_m else ""

        payload = {}
        payload.update(hidden)
        payload.update({
            "username": login,
            "password": senha,
        })

        # 3) POST login
        post_url = LOGIN_URL  # normalmente action=login.php
        r2 = session.post(post_url, data=payload, headers=headers, timeout=30, allow_redirects=True)

        # 4) checar sucesso
        final_url = r2.url.lower()
        body = (r2.text or "").lower()

        if "painel" in final_url or "painel" in body or "dashboard" in body:
            return session, "Login efetuado com sucesso (redir/painel detectado)."

        # tenta acessar /painel/ para checar
        try:
            r_check = session.get(urljoin(BASE_URL, "painel/"), timeout=20)
            if r_check.status_code == 200 and ("painel" in (r_check.text or "").lower()):
                return session, "Login efetuado (cheque em /painel ok)."
        except Exception:
            pass

        # Se houver indicação de erro explícito:
        if re.search(r'(usuário inválido|senha incorreta|login inválido|credenciais)', body, flags=re.I):
            return None, "Credenciais inválidas (mensagem detectada na resposta)."

        return None, "Falha no login via cloudscraper: sem indicação de sucesso."

    except Exception as e:
        return None, f"Exceção durante cloudscraper login: {e}"

# ---------------------------
# Transferir cookies requests/cloudscraper -> selenium
# ---------------------------
def transfer_cookies_to_selenium(session, driver):
    """
    session: requests-like session (cloudscraper)
    driver: selenium webdriver
    """
    driver.get(BASE_URL)  # necessário para adicionar cookies
    time.sleep(0.5)

    # session.cookies é um RequestsCookieJar
    for c in session.cookies:
        cookie = {
            "name": c.name,
            "value": c.value,
            "path": c.path or "/",
        }
        if c.domain:
            cookie["domain"] = c.domain
        try:
            driver.add_cookie(cookie)
        except Exception as e:
            # remover domínio se der problema
            try:
                cookie2 = {"name": c.name, "value": c.value, "path": c.path or "/"}
                driver.add_cookie(cookie2)
            except Exception:
                print("⚠️ Não foi possível adicionar cookie:", c.name, e)

# ---------------------------
# Setup Selenium (sem headless por segurança)
# ---------------------------
def setup_selenium():
    options = Options()
    # Remover headless para evitar detecção por alguns Cloudflare
    # options.add_argument("--headless=new")  # NÃO usar headless aqui
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.118 Safari/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # tentar mascarar navigator.webdriver
    try:
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
        })
    except Exception:
        pass

    return driver

# ---------------------------
# Fluxo Selenium para gerar banners
# ---------------------------
def gerar_banners_with_selenium(driver):
    wait = WebDriverWait(driver, 15)
    try:
        driver.get(NBA_URL)
        time.sleep(1)

        # clicar no menu lateral se existir
        try:
            el = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(.,'Gerar Futebol') or contains(.,'Todos Esportes') or contains(.,'Gerar Futebol')]")))
            try:
                el.click()
            except Exception:
                driver.execute_script("arguments[0].click();", el)
            time.sleep(0.8)
        except TimeoutException:
            print("⚠️ Botão lateral não encontrado — continuando...")

        # selecionar modelo (exemplo: modelo=15 para futebol; ajuste conforme necessidade)
        try:
            el_model = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'modelo=15') or contains(.,'Modelo 15') or contains(.,'modelo=15')]")))
            try:
                el_model.click()
            except Exception:
                driver.execute_script("arguments[0].click();", el_model)
            time.sleep(0.8)
        except TimeoutException:
            print("⚠️ Modelo 15 não encontrado — tentando localizar alternativa...")

        # clicar Gerar Banners
        try:
            btn = wait.until(EC.element_to_be_clickable((By.ID, "generateButton")))
            driver.execute_script("arguments[0].click();", btn)
        except TimeoutException:
            try:
                btn2 = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Gerar Banners') or contains(., 'Gerar')]")))
                driver.execute_script("arguments[0].click();", btn2)
            except TimeoutException as e:
                raise Exception("Botão 'Gerar Banners' não encontrado.") from e

        # aguardar alert e aceitar
        try:
            WebDriverWait(driver, 12).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            msg = alert.text
            print("✅ Popup detectado:", msg)
            alert.accept()
            time.sleep(1)
        except TimeoutException:
            print("⚠️ Nenhum popup detectado após gerar — continuando...")

        # ir para galeria e clicar enviar todas as imagens
        driver.get(FUTEBOL_CARTAZES)
        time.sleep(1)
        try:
            btn_env = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Enviar Todas as Imagens') or contains(., 'Enviar todas as imagens') or contains(., 'Enviar Todas')]")))
            driver.execute_script("arguments[0].click();", btn_env)
            time.sleep(1)
            print("📤 Envio acionado.")
            return True, "Banners gerados e envio acionado."
        except TimeoutException:
            print("⚠️ Botão 'Enviar Todas as Imagens' não encontrado.")
            return False, "Botão 'Enviar Todas as Imagens' não encontrado."
        except Exception as e:
            return False, f"Erro ao enviar imagens: {e}"

    except Exception as e:
        print("❌ Exceção na etapa Selenium:", e)
        return False, f"Exceção Selenium: {e}"

# ---------------------------
# Fluxo principal
# ---------------------------
def main():
    print("🚀 Iniciando automação Esportes (cloudscraper -> selenium)...")
    enviar_telegram("🚀 Iniciando automação Esportes (teste cloudscraper)...")

    login = os.environ.get("LOGIN")
    senha = os.environ.get("SENHA")
    if not login or not senha:
        enviar_telegram("⚠️ LOGIN ou SENHA não configurados no repositório!")
        print("⚠️ LOGIN ou SENHA não configurados.")
        return

    # 1) login via cloudscraper (resolve Cloudflare)
    sess, msg = login_cloudscraper(login, senha)
    if sess is None:
        enviar_telegram(f"❌ Erro no script Esportes: {msg}")
        print("❌ Login cloudscraper falhou:", msg)
        return
    else:
        print("✅ Login cloudscraper OK:", msg)
        enviar_telegram("✅ Login via cloudscraper OK. Prosseguindo com Selenium...")

    # 2) iniciar selenium e transferir cookies
    driver = None
    try:
        driver = setup_selenium()
        transfer_cookies_to_selenium(sess, driver)

        # opcional: abrir painel para verificar
        driver.get(urljoin(BASE_URL, "painel/"))
        time.sleep(1)

        ok, detalhe = gerar_banners_with_selenium(driver)
        if ok:
            enviar_telegram(f"✅ {detalhe}")
        else:
            caminho = salvar_print(driver, "erro_apos_login")
            enviar_telegram(f"❌ Erro após login: {detalhe}")
            enviar_telegram(f"🖼️ Print salvo: {caminho}")

    except Exception as e:
        print("❌ Erro geral no fluxo:", e)
        traceback.print_exc()
        if driver:
            caminho = salvar_print(driver, "erro_geral")
            enviar_telegram(f"❌ Erro geral no script Esportes: {e}")
            enviar_telegram(f"🖼️ Print salvo: {caminho}")
        else:
            enviar_telegram(f"❌ Erro crítico antes de iniciar Selenium: {e}")

    finally:
        try:
            if driver:
                driver.quit()
                print("🔒 Navegador fechado.")
        except Exception:
            pass

if __name__ == "__main__":
    main()
