#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-gerador de banners (gerador.pro) -> envia para Telegram
Requisitos: selenium, webdriver-manager, requests, python-dotenv (opcional)
"""

import os
import time
import datetime
import requests
import shutil
from pathlib import Path
from typing import List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, ElementClickInterceptedException
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ---------------------------
# Config
# ---------------------------
LOGIN = os.environ.get("LOGIN")
SENHA = os.environ.get("SENHA")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")  # ex: -1001234567890 or -1695313463

BASE_URL = "https://gerador.pro"
LOGIN_URL = f"{BASE_URL}/login.php"
GERAR_FUTEBOL_URL = f"{BASE_URL}/futbanner.php"
GALERIA_URL_CONTAINS = "/futebol/cartazes/"

PRINTS_DIR = Path("prints")
IMAGES_DIR = Path("images")
PRINTS_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------
# Helpers
# ---------------------------
def timestamp() -> str:
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

def salvar_print(driver, name):
    path = PRINTS_DIR / f"{timestamp()}_{name}.png"
    try:
        driver.save_screenshot(str(path))
    except Exception:
        pass
    return str(path)

def setup_driver(headless=True):
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    # optional: disable images to speed up (uncomment if desired)
    # prefs = {"profile.managed_default_content_settings.images": 2}
    # options.add_experimental_option("prefs", prefs)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def safe_click(driver, by, selector, timeout=15, description="", javascript_fallback=True):
    try:
        el = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, selector))
        )
        el.click()
        return True
    except (TimeoutException, ElementClickInterceptedException) as e:
        # tentar via JavaScript se disponível
        if javascript_fallback:
            try:
                el = driver.find_element(by, selector)
                driver.execute_script("arguments[0].click();", el)
                return True
            except Exception:
                return False
        return False

def safe_find(driver, by, selector, timeout=12):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )
    except TimeoutException:
        return None

# ---------------------------
# Fluxo do site
# ---------------------------
def fazer_login(driver, login, senha):
    driver.get(LOGIN_URL)
    time.sleep(1)
    # Tenta encontrar campos por NAME, ID ou CSS alternativos
    # Campo username (nome pode variar)
    username_selectors = [(By.NAME, "username"), (By.NAME, "login"), (By.ID, "username"), (By.CSS_SELECTOR, "input[type='text']")]
    password_selectors = [(By.NAME, "password"), (By.NAME, "senha"), (By.ID, "password"), (By.CSS_SELECTOR, "input[type='password']")]

    found_user = False
    for by, sel in username_selectors:
        try:
            el = driver.find_element(by, sel)
            el.clear()
            el.send_keys(login)
            found_user = True
            break
        except Exception:
            continue
    if not found_user:
        raise RuntimeError("Campo de login não encontrado na página.")

    found_pass = False
    for by, sel in password_selectors:
        try:
            el = driver.find_element(by, sel)
            el.clear()
            el.send_keys(senha)
            found_pass = True
            break
        except Exception:
            continue
    if not found_pass:
        raise RuntimeError("Campo de senha não encontrado na página.")

    # botão entrar: procurar por texto "Entrar", "Login", "Logar"
    btn_selectors = [
        (By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'entrar')]"),
        (By.XPATH, "//input[@type='submit']"),
        (By.XPATH, "//button[contains(., 'Login')]"),
    ]
    clicked = False
    for by, sel in btn_selectors:
        try:
            btn = driver.find_element(by, sel)
            driver.execute_script("arguments[0].click();", btn)
            clicked = True
            break
        except Exception:
            continue
    if not clicked:
        # tentar submit do form
        try:
            form = driver.find_element(By.TAG_NAME, "form")
            form.submit()
        except Exception:
            raise RuntimeError("Botão de login não encontrado / não foi possível submeter o form.")

    # esperar redirecionamento
    WebDriverWait(driver, 15).until(lambda d: d.current_url != LOGIN_URL)
    time.sleep(1)

def ir_gerar_futebol(driver):
    # Acessa diretamente a url do gerador futebol (se isso funcionar)
    driver.get(GERAR_FUTEBOL_URL)
    time.sleep(1)
    # Caso haja menu lateral, tentar clicar no item "Gerar Futebol" / "Gerar futebol"
    safe_click(driver, By.XPATH, "//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'gerar futebol')]", timeout=5, description="menu gerar futebol")

def selecionar_modelo(driver, modelo_num=15):
    # o site pode listar modelos como links com query parametro modelo=X
    # tentar acessar a URL direta:
    url_modelo = f"{GERAR_FUTEBOL_URL}?page=futebol&modelo={modelo_num}"
    driver.get(url_modelo)
    time.sleep(1)
    # Se for necessário clicar em um item na lista:
    selector = f"//a[contains(@href,'modelo={modelo_num}') or contains(.,'{modelo_num}')]"
    safe_click(driver, By.XPATH, selector, timeout=6)

def clicar_gerar_banners(driver):
    # botão "Gerar Banners" (pode ter id/class diferente)
    # procuramos por botão com texto "Gerar" e "Banners" juntos ou generateButton
    possible_xpaths = [
        "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'gerar') and contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'banner')]",
        "//button[contains(., 'Gerar Banners')]",
        "//*[@id='generateButton']",
        "//button[contains(translate(., 'abcdefghijklmnopqrstuvwxyz','abcdefghijklmnopqrstuvwxyz'),'gerar banner')]",  # fallback
    ]
    clicked = False
    for xp in possible_xpaths:
        if safe_click(driver, By.XPATH, xp, timeout=6):
            clicked = True
            break
    if not clicked:
        # tentar botão único "Gerar"
        safe_click(driver, By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'gerar')]", timeout=6)

def confirmar_popup_ok(driver, timeout=12):
    # Após gerar aparece um popup com texto "Sucesso! Banners gerados! Clique no OK..."
    # Tentamos detectar alert JS
    try:
        WebDriverWait(driver, 3).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        alert.accept()
        return True
    except Exception:
        pass

    # tentar detectar modal com botão "OK"
    ok_selectors = [
        (By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'ok')]"),
        (By.XPATH, "//button[contains(., 'OK')]"),
        (By.XPATH, "//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'ok')]")
    ]
    for by, sel in ok_selectors:
        try:
            el = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, sel)))
            driver.execute_script("arguments[0].click();", el)
            time.sleep(1)
            return True
        except Exception:
            continue
    return False

def ir_para_galeria(driver):
    # se o site redirecionar, aguardar url com /futebol/cartazes/
    try:
        WebDriverWait(driver, 10).until(lambda d: GALERIA_URL_CONTAINS in d.current_url)
    except Exception:
        # tentar acessar diretamente
        possible_galeria = f"{BASE_URL}/futebol/cartazes/"
        driver.get(possible_galeria)
    time.sleep(1)

def clicar_enviar_todas(driver):
    # botão "Enviar todas as imagens"
    xps = [
        "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'enviar todas')]",
        "//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'enviar todas')]",
        "//button[contains(., 'Enviar todas as imagens')]",
    ]
    for xp in xps:
        if safe_click(driver, By.XPATH, xp, timeout=8):
            return True
    return False

def coletar_urls_da_galeria(driver) -> List[str]:
    # procurar por <img> dentro da galeria
    imgs = driver.find_elements(By.XPATH, "//div[contains(@class,'gallery')]|//div[contains(@class,'cartazes')]//img | //img[contains(@src,'cartazes') or contains(@src,'uploads') or contains(@src,'/images/')]")
    urls = []
    for img in imgs:
        try:
            src = img.get_attribute("src")
            if src and src not in urls:
                urls.append(src)
        except Exception:
            continue
    # fallback: procurar por links que apontam para as imagens
    if not urls:
        links = driver.find_elements(By.XPATH, "//a[contains(@href,'.jpg') or contains(@href,'.png') or contains(@href,'.jpeg')]")
        for a in links:
            try:
                href = a.get_attribute("href")
                if href and href not in urls:
                    urls.append(href)
            except Exception:
                continue
    return urls

def baixar_imagem(url, pasta=IMAGES_DIR) -> str:
    local_name = pasta / f"{timestamp()}_{os.path.basename(url.split('?')[0])}"
    try:
        r = requests.get(url, stream=True, timeout=20)
        if r.status_code == 200:
            with open(local_name, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
            return str(local_name)
    except Exception:
        pass
    return ""

def enviar_media_group(token, chat_id, filepaths: List[str], caption=None):
    # Usa sendMediaGroup para enviar até 10 fotos de uma vez
    url = f"https://api.telegram.org/bot{token}/sendMediaGroup"
    media = []
    files = {}
    for idx, path in enumerate(filepaths):
        key = f"file{idx}"
        # prepare media object for multipart
        media.append({"type": "photo", "media": f"attach://{key}"})
        files[key] = open(path, "rb")
    data = {"chat_id": chat_id, "media": str(media).replace("'", '"')}
    try:
        r = requests.post(url, data=data, files=files, timeout=60)
        for f in files.values():
            f.close()
        return r.status_code, r.text
    except Exception as e:
        for f in files.values():
            try: f.close()
            except: pass
        return None, str(e)

def enviar_photos_individuais(token, chat_id, filepaths: List[str]):
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    results = []
    for path in filepaths:
        try:
            with open(path, "rb") as f:
                r = requests.post(url, data={"chat_id": chat_id}, files={"photo": f}, timeout=60)
                results.append((r.status_code, r.text))
        except Exception as e:
            results.append((None, str(e)))
    return results

# ---------------------------
# Main
# ---------------------------
def main():
    if not LOGIN or not SENHA or not TELEGRAM_BOT_TOKEN or not CHAT_ID:
        print("❌ Variáveis de ambiente não configuradas. Configure LOGIN, SENHA, TELEGRAM_BOT_TOKEN e CHAT_ID.")
        return

    driver = setup_driver(headless=True)
    print("🔧 Driver inicializado")
    try:
        fazer_login(driver, LOGIN, SENHA)
        print("✅ Login realizado")
        time.sleep(1)

        ir_gerar_futebol(driver)
        print("➡️ Acessando Gerar Futebol")
        time.sleep(1)

        selecionar_modelo(driver, modelo_num=15)
        print("🔢 Modelo 15 selecionado (tentativa via URL/seleção)")

        clicar_gerar_banners(driver)
        print("🚀 Clicado em Gerar Banners (se disponível)")
        time.sleep(2)

        ok = confirmar_popup_ok(driver)
        print(f"📎 Popup OK detectado e clicado? {ok}")
        time.sleep(1)

        ir_para_galeria(driver)
        print("🖼️ Indo para galeria")
        time.sleep(2)
        salvar_print(driver, "galeria")

        # clicar em "Enviar todas as imagens" para acionar envio (se esse botão já envia automaticamente para o Telegram/externo)
        btn_enviar = clicar_enviar_todas(driver)
        print(f"📤 Botão 'Enviar todas as imagens' clicado? {btn_enviar}")
        time.sleep(2)
        salvar_print(driver, "depois_enviar_todas")

        # coletar URLs de imagens na galeria (caso precise enviar via bot)
        urls = coletar_urls_da_galeria(driver)
        print(f"🔎 URLs encontradas na galeria: {len(urls)}")
        if not urls:
            print("⚠️ Nenhuma imagem encontrada na galeria. Salvando print e saindo.")
            caminho = salvar_print(driver, "nenhuma_imagem")
            enviar_photos_individuais(TELEGRAM_BOT_TOKEN, CHAT_ID, [caminho])  # envia print para o chat
            return

        # baixar imagens localmente
        baixados = []
        for u in urls:
            local = baixar_imagem(u)
            if local:
                baixados.append(local)
                print(f"⬇️ Baixado: {local}")
            else:
                print(f"❌ Falha ao baixar: {u}")

        if not baixados:
            print("❌ Não foi possível baixar nenhuma imagem.")
            return

        # enviar em lotes de até 10
        def chunks(lst, n):
            for i in range(0, len(lst), n):
                yield lst[i:i+n]

        for grupo in chunks(baixados, 10):
            status, resp = enviar_media_group(TELEGRAM_BOT_TOKEN, CHAT_ID, grupo)
            print(f"📨 Envio grupo - status: {status} resp: {resp}")
            time.sleep(1)

        # Log final
        enviar_photos_individuais(TELEGRAM_BOT_TOKEN, CHAT_ID, [])  # apenas placeholder caso deseje enviar algo extra
        print("✅ Processo finalizado com sucesso.")

    except Exception as e:
        caminho = salvar_print(driver, "erro_geral")
        print("❌ Erro geral:", e)
        try:
            enviar_photos_individuais(TELEGRAM_BOT_TOKEN, CHAT_ID, [caminho])
        except Exception:
            pass
    finally:
        driver.quit()
        print("🔒 Navegador fechado")

if __name__ == "__main__":
    main()
