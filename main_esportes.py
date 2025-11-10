#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import time
import json
import requests
from datetime import datetime
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

# ---------------------------
# Config / utilitários
# ---------------------------
BASE_URL = "https://gerador.pro/"
LOGIN_URL = urljoin(BASE_URL, "login.php")
NBA_URL = urljoin(BASE_URL, "nba.php")
FUTEBOL_CARTAZES = urljoin(BASE_URL, "futebol/cartazes/")

def enviar_telegram(msg):
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
# Login invisível com requests
# ---------------------------
def extract_hidden_inputs(html):
    # Extrai inputs hidden do form (name/value)
    hidden = {}
    # padrão simples: <input type="hidden" name="token" value="...">
    for match in re.finditer(r'<input[^>]+type=["\']hidden["\'][^>]*>', html, flags=re.I):
        tag = match.group(0)
        name_m = re.search(r'name=["\']([^"\']+)["\']', tag, flags=re.I)
        val_m = re.search(r'value=["\']([^"\']*)["\']', tag, flags=re.I)
        if name_m:
            hidden[name_m.group(1)] = val_m.group(1) if val_m else ""
    return hidden

def requests_login(login, senha, session=None):
    """
    Faz login usando requests.Session.
    Retorna (session, message) onde session é a sessão autenticada ou None.
    """
    if session is None:
        session = requests.Session()

    try:
        # 1) pegar página login para cookies e hidden fields
        r = session.get(LOGIN_URL, timeout=20)
        if r.status_code != 200:
            return None, f"Falha ao acessar login page: status {r.status_code}"

        # extrair campos hidden (csrf, etc.)
        hidden = extract_hidden_inputs(r.text)

        # preparar payload
        payload = {}
        # mantém os hidden inputs
        payload.update(hidden)
        # campos conhecidos
        payload.update({
            "username": login,
            "password": senha,
        })

        # headers (simular browser)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/118.0.5993.118 Safari/537.36",
            "Referer": LOGIN_URL,
        }

        # 2) postar login
        post_url = urljoin(BASE_URL, "login.php")  # normalmente action=login.php
        r2 = session.post(post_url, data=payload, headers=headers, timeout=20, allow_redirects=True)

        # 3) verificar sucesso de login
        # critérios: redirectou para painel (url diferente) ou página contém palavra "Painel" ou "dashboard"
        final_url = r2.url
        body = r2.text or ""

        if "painel" in final_url.lower() or "painel" in body or "dashboard" in body.lower():
            return session, "Login efetuado com sucesso (redirect/painel detectado)."

        # às vezes o site mantém na mesma url mas mostra mensagem de sucesso direta
        # verificar se há indicação de erro
        if re.search(r'(usuário inválido|senha incorreta|login inválido|credenciais)', body, flags=re.I):
            return None, "Credenciais inválidas (mensagem detectada na resposta)."

        # se não detectou sucesso nem erro, pode ter bloqueio; informar mas retornar a sessão (para debug)
        # vamos fazer uma requisição para /painel para ver se conseguimos acessá-lo
        try:
            r_check = session.get(urljoin(BASE_URL, "painel/"), timeout=15)
            if r_check.status_code == 200 and ("Painel" in (r_check.text or "" ) or "dashboard" in (r_check.text or "").lower()):
                return session, "Login realizado (cheque em /painel OK)."
        except Exception:
            pass

        # fallback: não sabemos, retornar None com mensagem
        return None, "Falha desconhecida no login (nenhuma indicação de sucesso)."

    except Exception as e:
        return None, f"Exceção durante requests login: {e}"

# ---------------------------
# Reusar cookies requests no Selenium
# ---------------------------
def transfer_cookies_requests_to_selenium(session, driver):
    """
    Session do requests -> cookies para selenium
    Deve chamar driver.get(BASE_URL) antes de adicionar cookies.
    """
    # visitar domínio principal para possibilitar adicionar cookies
    driver.get(BASE_URL)
    time.sleep(0.5)

    # requests cookies: session.cookies (RequestsCookieJar)
    for c in session.cookies:
        cookie_dict = {
            "name": c.name,
            "value": c.value,
            "path": c.path or "/",
            "domain": c.domain if c.domain else ".gerador.pro",
        }
        # selenium aceita only domain matches current domain
        try:
            driver.add_cookie(cookie_dict)
        except Exception as e:
            # se falhar por domínio, tente sem domain
            try:
                cookie_nodomain = {"name": c.name, "value": c.value, "path": c.path or "/"}
                driver.add_cookie(cookie_nodomain)
            except Exception:
                print("⚠️ Não foi possível adicionar cookie:", c.name, e)

# ---------------------------
# Setup Selenium
# ---------------------------
def setup_selenium():
    options = Options()
    # tenta headless "novo" - se der problema, remova
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.118 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# ---------------------------
# Fluxo de geração com Selenium (assumindo sessão já autenticada via cookies)
# ---------------------------
def gerar_banners_com_selenium(driver):
    try:
        driver.get(NBA_URL)
        wait = WebDriverWait(driver, 12)

        # caso precise clicar no menu lateral "Gerar Futebol" / "Todos Esportes"
        # tento clicar em "Todos Esportes" (se existir)
        try:
            el_todos = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(.,'Todos Esportes') or contains(.,'Gerar Futebol') or contains(.,'Gerar Futebol')]")))
            try:
                el_todos.click()
            except Exception:
                driver.execute_script("arguments[0].click();", el_todos)
            time.sleep(0.8)
        except TimeoutException:
            print("⚠️ Botão 'Todos Esportes' não encontrado — continuando...")

        # selecionar modelo exemplo: modelo=27 (basquete roxo)
        try:
            el_model = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'modelo=27') or contains(.,'Basquete Roxo') or contains(.,'Basquete')]")))
            try:
                el_model.click()
            except Exception:
                driver.execute_script("arguments[0].click();", el_model)
            time.sleep(0.8)
        except TimeoutException:
            print("⚠️ Modelo específico não encontrado. Tentando continuar...")

        # clicar em Gerar Banners (pode ser ID generateButton)
        try:
            btn = wait.until(EC.element_to_be_clickable((By.ID, "generateButton")))
            driver.execute_script("arguments[0].click();", btn)
        except TimeoutException:
            # tenta por texto
            try:
                btn2 = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Gerar Banners') or contains(., 'Gerar')]")))
                driver.execute_script("arguments[0].click();", btn2)
            except TimeoutException as e:
                raise Exception("Botão 'Gerar Banners' não encontrado.") from e

        # aguardar alert/popup e aceitar
        try:
            WebDriverWait(driver, 12).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            msg = alert.text
            print("✅ Popup detectado:", msg)
            alert.accept()
            time.sleep(1)
        except TimeoutException:
            print("⚠️ Nenhum popup detectado após gerar (talvez já esteja na galeria).")

        # após ir para galeria, clicar em 'Enviar Todas as Imagens'
        try:
            # navegar para a galeria (exemplo: /futebol/cartazes/)
            driver.get(FUTEBOL_CARTAZES)
            time.sleep(1)
            btn_env = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Enviar Todas as Imagens') or contains(., 'Enviar todas as imagens') or contains(., 'Enviar Todas')]")))
            driver.execute_script("arguments[0].click();", btn_env)
            time.sleep(1)
            print("📤 Botão 'Enviar Todas as Imagens' clicado.")
            return True, "Banners gerados e envio acionado."
        except TimeoutException:
            print("⚠️ Botão 'Enviar Todas as Imagens' não encontrado.")
            return False, "Botão 'Enviar Todas as Imagens' não encontrado."
        except Exception as e:
            print("⚠️ Erro ao tentar enviar todas as imagens:", e)
            return False, f"Erro ao enviar imagens: {e}"

    except Exception as e:
        print("❌ Exceção na etapa Selenium:", e)
        return False, f"Exceção Selenium: {e}"

# ---------------------------
# Fluxo principal
# ---------------------------
def main():
    print("🚀 Iniciando automação Esportes (login via requests)...")
    enviar_telegram("🚀 Iniciando automação Esportes...")

    login = os.environ.get("LOGIN")
    senha = os.environ.get("SENHA")

    if not login or not senha:
        enviar_telegram("⚠️ LOGIN ou SENHA não configurados no repositório!")
        print("⚠️ LOGIN ou SENHA não configurados.")
        return

    sess, msg = requests_login(login, senha)
    if sess is None:
        enviar_telegram(f"❌ Erro no script Esportes: {msg}")
        print("❌ Login requests falhou:", msg)
        return
    else:
        print("✅ Login via requests OK:", msg)
        enviar_telegram("✅ Login via requests OK. Prosseguindo com Selenium...")

    # inicia selenium e injeta cookies
    driver = None
    try:
        driver = setup_selenium()
        transfer_cookies_requests_to_selenium(sess, driver)

        # validar que painel está acessível (opcional)
        driver.get(urljoin(BASE_URL, "painel/"))
        time.sleep(1)
        # se quisermos checar presença do painel:
        if "Login" in driver.title or "Entrar" in driver.page_source[:300]:
            print("⚠️ Atenção: ainda na tela de login no Selenium - mas continuamos para gerar (pode ser ok).")

        # gerar com selenium
        ok, detalhe = gerar_banners_com_selenium(driver)
        if ok:
            enviar_telegram(f"✅ {detalhe}")
        else:
            caminho = salvar_print(driver, "erro_apos_login")
            enviar_telegram(f"❌ Erro após login: {detalhe}")
            enviar_telegram(f"🖼️ Print salvo: {caminho}")

    except Exception as e:
        print("❌ Erro geral no fluxo:", e)
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
