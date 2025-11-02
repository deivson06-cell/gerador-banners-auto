#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoGerador Futebol (Deivson Ricardo)
Fluxo completo:
1️⃣ Login no gerador.pro
2️⃣ Gerar modelo 15
3️⃣ Confirmar popup de sucesso
4️⃣ Entrar na galeria
5️⃣ Baixar todas as imagens
6️⃣ Enviar diretamente via bot do Telegram (sem depender do site)
"""

import os
import time
import requests
import shutil
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

# Variáveis de ambiente
LOGIN = os.environ.get("LOGIN")
SENHA = os.environ.get("SENHA")
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

BASE_URL = "https://gerador.pro"
LOGIN_URL = f"{BASE_URL}/login.php"
GERAR_URL = f"{BASE_URL}/futbanner.php?page=futebol&modelo=15"
GALERIA_URL = f"{BASE_URL}/futebol/cartazes/"

IMAGES_DIR = Path("images")
IMAGES_DIR.mkdir(exist_ok=True)

def setup_driver():
    print("🧩 Iniciando Chrome headless...")
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    print("✅ Chrome configurado.")
    return driver

def fazer_login(driver):
    print("➡️ Acessando página de login...")
    driver.get(LOGIN_URL)
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(LOGIN)
    driver.find_element(By.NAME, "password").send_keys(SENHA)
    driver.find_element(By.XPATH, "//button[contains(.,'Entrar') or contains(.,'Login')]").click()
    WebDriverWait(driver, 15).until(lambda d: "painel" in d.current_url or "futbanner" in d.current_url)
    print("✅ Login realizado com sucesso!")

def gerar_banners(driver):
    print("⚽ Acessando modelo 15...")
    driver.get(GERAR_URL)
    time.sleep(2)

    print("🚀 Gerando banners...")
    try:
        gerar_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'gerar banners')]"))
        )
        gerar_btn.click()
        time.sleep(3)
    except TimeoutException:
        print("⚠️ Botão 'Gerar Banners' não encontrado, continuando...")

    try:
        WebDriverWait(driver, 5).until(EC.alert_is_present())
        driver.switch_to.alert.accept()
        print("✅ Popup de sucesso confirmado.")
    except Exception:
        print("⚠️ Nenhum popup detectado.")

def coletar_urls(driver):
    print("🖼️ Acessando galeria...")
    driver.get(GALERIA_URL)
    time.sleep(2)

    imagens = driver.find_elements(By.XPATH, "//img[contains(@src,'.jpg') or contains(@src,'.png')]")
    urls = []
    for img in imagens:
        src = img.get_attribute("src")
        if src and src not in urls:
            urls.append(src)

    print(f"📸 {len(urls)} imagens encontradas na galeria.")
    return urls

def baixar_imagem(url):
    nome = IMAGES_DIR / os.path.basename(url.split("?")[0])
    try:
        r = requests.get(url, stream=True, timeout=20)
        if r.status_code == 200:
            with open(nome, "wb") as f:
                shutil.copyfileobj(r.raw, f)
            return str(nome)
    except Exception as e:
        print("Erro ao baixar:", e)
    return None

def enviar_telegram(files):
    print("📤 Enviando imagens para o canal P2PLUS...")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMediaGroup"
    media = []
    data_files = {}
    for i, img_path in enumerate(files):
        key = f"file{i}"
        media.append({"type": "photo", "media": f"attach://{key}"})
        data_files[key] = open(img_path, "rb")

    payload = {"chat_id": CHAT_ID, "media": str(media).replace("'", '"')}
    r = requests.post(url, data=payload, files=data_files)
    for f in data_files.values():
        f.close()
    print("✅ Resposta Telegram:", r.status_code, r.text[:200])

def main():
    if not LOGIN or not SENHA or not BOT_TOKEN or not CHAT_ID:
        print("❌ Falta configurar as variáveis de ambiente.")
        return

    driver = setup_driver()
    try:
        fazer_login(driver)
        gerar_banners(driver)
        urls = coletar_urls(driver)

        if not urls:
            print("⚠️ Nenhuma imagem encontrada, abortando.")
            return

        baixadas = [baixar_imagem(u) for u in urls if baixar_imagem(u)]
        if baixadas:
            for i in range(0, len(baixadas), 10):
                enviar_telegram(baixadas[i:i+10])
                time.sleep(1)
            print("🎯 Envio concluído com sucesso!")
        else:
            print("❌ Nenhuma imagem foi baixada.")
    except Exception as e:
        print("❌ Erro:", e)
    finally:
        driver.quit()
        print("🔒 Navegador fechado.")

if __name__ == "__main__":
    main()
