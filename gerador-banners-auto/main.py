#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, time, datetime, requests, shutil
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

LOGIN = os.environ.get("LOGIN")
SENHA = os.environ.get("SENHA")
BASE_URL = "https://gerador.pro"
LOGIN_URL = f"{BASE_URL}/login.php"
GERAR_URL = f"{BASE_URL}/futbanner.php?page=futebol&modelo=15"

def setup_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def wait_and_click(driver, xpath, timeout=15):
    try:
        el = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        el.click()
        return True
    except Exception:
        return False

def main():
    driver = setup_driver()
    print("🔧 Iniciando...")
    try:
        driver.get(LOGIN_URL)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(LOGIN)
        driver.find_element(By.NAME, "password").send_keys(SENHA)
        driver.find_element(By.XPATH, "//button[contains(.,'Entrar') or contains(.,'Login')]").click()
        WebDriverWait(driver, 10).until(lambda d: "painel" in d.current_url or "futbanner" in d.current_url)
        print("✅ Login feito")

        driver.get(GERAR_URL)
        print("➡️ Gerando banners modelo 15...")
        wait_and_click(driver, "//button[contains(.,'Gerar Banners')]", 10)
        time.sleep(3)

        try:
            WebDriverWait(driver, 5).until(EC.alert_is_present())
            driver.switch_to.alert.accept()
        except Exception:
            pass

        driver.get(f"{BASE_URL}/futebol/cartazes/")
        print("🖼️ Indo para galeria...")
        wait_and_click(driver, "//button[contains(.,'Enviar todas')]", 10)
        print("📤 Enviando todas as imagens (via site)...")
        time.sleep(5)
        print("✅ Processo concluído com sucesso!")

    except Exception as e:
        print("❌ Erro:", e)
    finally:
        driver.quit()
        print("🔒 Navegador fechado")

if __name__ == "__main__":
    main()
