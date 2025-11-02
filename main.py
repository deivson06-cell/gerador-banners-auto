#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automação: Gerar banners no site https://gerador.pro
Autor: Deivson Ricardo
Fluxo: Login → Gerar Futebol → Modelo 15 → Gerar → OK → Enviar todas as imagens
Envio para Telegram ocorre diretamente pelo site (não pelo script).
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException

# -------------------------------------------------------------------
# Variáveis de ambiente (vindas do GitHub Secrets)
# -------------------------------------------------------------------
LOGIN = os.environ.get("LOGIN")
SENHA = os.environ.get("SENHA")

BASE_URL = "https://gerador.pro"
LOGIN_URL = f"{BASE_URL}/login.php"
GERAR_FUTEBOL_URL = f"{BASE_URL}/futbanner.php?page=futebol&modelo=15"
GALERIA_URL = f"{BASE_URL}/futebol/cartazes/"

# -------------------------------------------------------------------
# Configurações do navegador (modo headless)
# -------------------------------------------------------------------
def setup_driver():
    print("🧩 Configurando Chrome headless...")
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-notifications")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    print("✅ Navegador iniciado.")
    return driver

# -------------------------------------------------------------------
# Etapas principais
# -------------------------------------------------------------------
def login(driver):
    print("➡️ Acessando página de login...")
    driver.get(LOGIN_URL)
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(LOGIN)
    driver.find_element(By.NAME, "password").send_keys(SENHA)
    driver.find_element(By.XPATH, "//button[contains(.,'Entrar') or contains(.,'Login')]").click()
    WebDriverWait(driver, 15).until(lambda d: "painel" in d.current_url or "futbanner" in d.current_url)
    print("✅ Login realizado com sucesso!")

def gerar_banners(driver):
    print("⚽ Acessando gerador de futebol (modelo 15)...")
    driver.get(GERAR_FUTEBOL_URL)
    time.sleep(2)

    print("🚀 Clicando em 'Gerar Banners'...")
    try:
        gerar_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'gerar banners')]"))
        )
        gerar_btn.click()
        time.sleep(3)
    except TimeoutException:
        raise Exception("❌ Botão 'Gerar Banners' não encontrado.")

    # Confirma popup de sucesso
    try:
        WebDriverWait(driver, 5).until(EC.alert_is_present())
        driver.switch_to.alert.accept()
        print("✅ Popup 'Sucesso!' confirmado.")
    except Exception:
        print("⚠️ Nenhum popup detectado, continuando...")

def enviar_todas_imagens(driver):
    print("🖼️ Indo para galeria...")
    driver.get(GALERIA_URL)
    time.sleep(2)

    print("📤 Clicando em 'Enviar todas as imagens'...")
    try:
        enviar_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'enviar todas')]"))
        )
        driver.execute_script("arguments[0].click();", enviar_btn)
        print("✅ Envio de todas as imagens acionado com sucesso (via site).")
    except TimeoutException:
        raise Exception("❌ Botão 'Enviar todas as imagens' não encontrado.")

# -------------------------------------------------------------------
# Função principal
# -------------------------------------------------------------------
def main():
    print("🚀 Iniciando automação...")
    driver = setup_driver()
    try:
        login(driver)
        gerar_banners(driver)
        enviar_todas_imagens(driver)
        print("🎯 Processo concluído com sucesso! Banners enviados pelo site.")
    except Exception as e:
        print("❌ Erro durante a execução:", e)
    finally:
        driver.quit()
        print("🔒 Navegador fechado.")

if __name__ == "__main__":
    main()
