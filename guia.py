#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

LOGIN = os.environ.get("LOGIN")
SENHA = os.environ.get("SENHA")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def setup_driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=opts)

def enviar_mensagem(texto):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": texto}
    try:
        r = requests.post(url, data=data, timeout=30)
        print("Mensagem enviada:", r.text)
    except Exception as e:
        print("Erro ao enviar mensagem:", e)

def main():
    driver = setup_driver()
    try:
        driver.get("https://gerador.pro/login.php")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(LOGIN)
        driver.find_element(By.NAME, "password").send_keys(SENHA)
        driver.find_element(By.XPATH, "//button[contains(., 'Entrar')]").click()
        WebDriverWait(driver, 10).until(lambda d: "index" in d.current_url)
        print("✅ Login realizado com sucesso!")

        driver.get("https://gerador.pro/guitexto.php")
        print("➡️ Página do Guia Futebol carregada")

        # Clicar no botão 'Copiar Texto'
        try:
            btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'copiar texto')]")))
            driver.execute_script("arguments[0].click();", btn)
            print("📋 Botão 'Copiar Texto' clicado")
        except Exception as e:
            print("⚠️ Não foi possível clicar no botão copiar:", e)

        # Captura do texto
        try:
            textarea = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "textarea")))
            texto = textarea.get_attribute("value")
        except Exception:
            texto = "⚠️ Não foi possível capturar o texto do Guia Futebol."

        if texto.strip():
            enviar_mensagem(texto.strip())
        else:
            enviar_mensagem("⚠️ Nenhum texto encontrado na página Guia Futebol.")

    except Exception as e:
        enviar_mensagem(f"❌ Erro no script Guia Futebol: {e}")
    finally:
        driver.quit()
        print("🔒 Navegador fechado")

if __name__ == "__main__":
    main()
