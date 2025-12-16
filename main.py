#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


BASE = "https://gerador.pro"
MODELO_FUTEBOL = 15  # <<< modelo


def setup_driver():
    print("🔧 Configurando Chrome (VPS)...")

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--lang=pt-BR")
    options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36")

    # chromedriver instalado via apt (caminho padrão)
    service = Service("/usr/bin/chromedriver")

    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(60)
    print("✅ Chrome configurado!")
    return driver


def screenshot(driver, name):
    try:
        ts = time.strftime("%Y%m%d-%H%M%S")
        path = f"{name}-{ts}.png"
        driver.save_screenshot(path)
        print(f"🖼️ Screenshot salvo: {path}")
    except:
        pass


def wait_page_ready(driver, timeout=30):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


def safe_click(driver, by,
