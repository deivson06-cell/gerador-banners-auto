#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import time
import traceback
from datetime import datetime
from urllib.parse import urljoin
import cloudscraper
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

# =====================================================
# CONFIGURAÇÕES GERAIS
# =====================================================
BASE_URL = "https://gerador.pro/"
LOGIN_URL = urljoin(BASE_URL, "login.php")
FUTEBOL_URL = urljoin(BASE_URL, "futbanner.php?page=futebol&modelo=15")
NBA_URL = urljoin(BASE_URL, "nba.php?page=futebol&modelo=27")
FUTSAL_URL = urljoin(BASE_URL, "futsal.php?page=futsal&modelo=31")
CARTAZES_URL = urljoin(BASE_URL, "futebol/cartazes/")

# =====================================================
# FUNÇÕES DE UTILIDADE
# =====================================================
def enviar_telegram(msg: str):
    token = os.environ.get("BOT_TOKEN")
    chat_id = os.environ.get("CHAT_ID")
    if not token or not chat_id:
        print("⚠️ BOT_TOKEN ou CHAT_ID ausentes.")
        return
    try:
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                      data={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"},
                      timeout=15)
        print("📨 Mensagem enviada ao Telegram")
    except Exception as e:
        print("⚠️ Falha ao enviar Telegram:", e)

def salvar_print(driver, nome):
    pasta = "prints"
    os.makedirs(pasta, exist_ok=True)
    caminho = f"{pasta}/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{nome}.png"
    driver.save_screenshot(caminho)
    print("📸 Print salvo:", caminho)
    return caminho

# =====================================================
# LOGIN USANDO CLOUDSCRAPER (bypass Cloudflare)
# =====================================================
def login_cloudscraper(login, senha):
    try:
        sess = cloudscraper.create_scraper()
        r = sess.get(LOGIN_URL, timeout=30)
        if r.status_code != 200:
            return None, f"Falha ao acessar página de login ({r.status_code})"

        payload = {"username": login, "password": senha}
        r2 = sess.post(LOGIN_URL, data=payload, allow_redirects=True, timeout=30)
        if "painel" in r2.text.lower():
            return sess, "Login efetuado via cloudscraper"
        return None, "Falha no login (não encontrou painel)"
    except Exception as e:
        return None, f"Erro cloudscraper: {e}"

# =====================================================
# CONFIGURAR SELENIUM
# =====================================================
def setup_driver():
    opts = Options()
    # ⚠️ use headless para GitHub Actions
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    return driver

def transfer_cookies(sess, driver):
    driver.get(BASE_URL)
    for c in sess.cookies:
        try:
            driver.add_cookie({
                "name": c.name,
                "value": c.value,
                "domain": c.domain or "gerador.pro",
                "path": "/"
            })
        except Exception:
            pass

# =====================================================
# GERAÇÃO DE BANNERS (GENÉRICA)
# =====================================================
def gerar_banners(driver, modo="futebol"):
    wait = WebDriverWait(driver, 15)
    if modo == "nba":
        url = NBA_URL
        modelo_nome = "Basquete Roxo"
    elif modo == "futsal":
        url = FUTSAL_URL
        modelo_nome = "Futsal"
    else:
        url = FUTEBOL_URL
        modelo_nome = "Modelo 15"

    print(f"➡️ Gerando banners modo: {modo.upper()} ({modelo_nome})")
    driver.get(url)
    time.sleep(1)

    try:
        btn_gerar = wait.until(EC.element_to_be_clickable((By.ID, "generateButton")))
        driver.execute_script("arguments[0].click();", btn_gerar)
    except TimeoutException:
        raise Exception("Botão 'Gerar Banners' não encontrado")

    # Esperar popup e clicar OK
    try:
        WebDriverWait(driver, 12).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        print("✅ Popup detectado:", alert.text)
        alert.accept()
    except TimeoutException:
        print("⚠️ Nenhum popup após gerar.")

    # Ir para galeria e clicar "Enviar todas as imagens"
    driver.get(CARTAZES_URL)
    try:
        btn_env = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(.,'Enviar Todas as Imagens') or contains(.,'Enviar todas as imagens')]")))
        driver.execute_script("arguments[0].click();", btn_env)
        print("📤 Envio de imagens acionado.")
        return True
    except TimeoutException:
        return False

# =====================================================
# FLUXO PRINCIPAL
# =====================================================
def main():
    workflow_name = os.environ.get("GITHUB_WORKFLOW", "").lower()
    if "nba" in workflow_name or "esporte" in workflow_name:
        modo = "nba"
    elif "futsal" in workflow_name:
        modo = "futsal"
    else:
        modo = "futebol"

    print(f"🚀 Iniciando automação para: {modo.upper()}")
    enviar_telegram(f"🚀 Iniciando automação {modo.upper()} (Cloudscraper ativo)")

    login = os.environ.get("LOGIN")
    senha = os.environ.get("SENHA")
    if not login or not senha:
        enviar_telegram("⚠️ LOGIN/SENHA não configurados.")
        return

    sess, msg = login_cloudscraper(login, senha)
    if not sess:
        enviar_telegram(f"❌ Falha no login: {msg}")
        return

    print("✅ Login OK:", msg)
    enviar_telegram("✅ Login via cloudscraper OK. Prosseguindo...")

    driver = setup_driver()
    try:
        transfer_cookies(sess, driver)
        ok = gerar_banners(driver, modo)
        if ok:
            enviar_telegram(f"✅ Banners de {modo.upper()} gerados e enviados!")
        else:
            caminho = salvar_print(driver, f"erro_{modo}")
            enviar_telegram(f"❌ Erro ao gerar/enviar banners {modo.upper()}")
            enviar_telegram(f"🖼️ Print salvo: {caminho}")
    except Exception as e:
        print("❌ Erro geral:", e)
        caminho = salvar_print(driver, "erro_geral")
        enviar_telegram(f"❌ Erro geral no script {modo.upper()}: {e}")
        enviar_telegram(f"🖼️ Print salvo: {caminho}")
    finally:
        driver.quit()
        print("🔒 Navegador fechado.")

if __name__ == "__main__":
    main()
