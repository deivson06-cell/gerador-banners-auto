#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, time, traceback
from datetime import datetime
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# stealth
try:
    from selenium_stealth import stealth
except Exception:
    stealth = None

BASE_URL = "https://gerador.pro/"
LOGIN_URL = BASE_URL + "login.php"
NBA_URL = BASE_URL + "nba.php"
FUTEBOL_CARTAZES = BASE_URL + "futebol/cartazes/"

# -------------------------
# Utilitários
# -------------------------
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
        }, timeout=20)
        print("📨 Mensagem enviada ao Telegram!")
        return True
    except Exception as e:
        print("⚠️ Falha ao enviar Telegram:", e)
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

# -------------------------
# Setup driver + stealth
# -------------------------
def setup_driver():
    print("🚀 Iniciando Chrome com opções de stealth...")
    options = Options()

    # headless em Actions - mantemos headless new
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # User-Agent realista
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.118 Safari/537.36"
    )

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # execute CDP to overwrite navigator.webdriver
    try:
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
        })
    except Exception as e:
        print("⚠️ CDP set navigator.webdriver failed:", e)

    # apply selenium-stealth if available
    if stealth:
        try:
            stealth(driver,
                    languages=["pt-BR", "en-US"],
                    vendor="Google Inc.",
                    platform="Win32",
                    webgl_vendor="Intel Inc.",
                    renderer="Intel Iris OpenGL Engine",
                    fix_hairline=True)
            print("🛡️ selenium-stealth aplicado.")
        except Exception as e:
            print("⚠️ Falha ao aplicar selenium-stealth:", e)
    else:
        print("⚠️ selenium-stealth não instalado — instale selenium-stealth no workflow (recomendado).")

    return driver

# -------------------------
# Login via Selenium (camuflado)
# -------------------------
def fazer_login_selenium(driver, login, senha, tentativas=2):
    for tentativa in range(1, tentativas+1):
        try:
            print(f"🔁 Tentativa de login {tentativa}/{tentativas}")
            driver.get(LOGIN_URL)
            wait = WebDriverWait(driver, 12)

            # localizar campos
            user = wait.until(EC.presence_of_element_located((By.ID, "username")))
            pwd = wait.until(EC.presence_of_element_located((By.ID, "password")))
            btn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "btn-login")))

            user.clear()
            user.send_keys(login)
            pwd.clear()
            pwd.send_keys(senha)

            # clicar via JS (mais natural)
            driver.execute_script("arguments[0].click();", btn)

            # aguardar redirecionamento ou termos no page_source que indiquem painel
            try:
                WebDriverWait(driver, 10).until(
                    lambda d: ("painel" in d.current_url.lower()) or ("Painel" in d.page_source[:1000])
                )
                print("✅ Login realizado com sucesso (Selenium).")
                return True
            except TimeoutException:
                print("⚠️ Falha no redirecionamento após clique.")
                # tenta detectar mensagem de erro visível
                try:
                    erro = driver.find_element(By.CSS_SELECTOR, ".alert, .erro, .text-danger").text
                    print("📛 Mensagem de erro detectada:", erro)
                    return False
                except Exception:
                    # sem mensagem — pode ser proteção; tentaremos próxima tentativa com delay
                    print("⚠️ Nenhuma mensagem de erro visível; possível proteção.")
                    time.sleep(2 + tentativa)
                    continue

        except Exception as e:
            print("❌ Exceção durante login:", e)
            traceback.print_exc()
            time.sleep(2)
            continue

    return False

# -------------------------
# Geração e envio com Selenium
# -------------------------
def gerar_banners_esportes(driver):
    print("====================================================")
    print("ETAPA: Gerar banners esportes")
    print("====================================================")
    wait = WebDriverWait(driver, 12)
    try:
        driver.get(NBA_URL)
        time.sleep(1.0)

        # clicar "Todos Esportes" / "Gerar Futebol" se houver
        try:
            el = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(.,'Todos Esportes') or contains(.,'Gerar Futebol') or contains(.,'Gerar Futebol')]")))
            try:
                el.click()
            except Exception:
                driver.execute_script("arguments[0].click();", el)
            time.sleep(0.8)
        except TimeoutException:
            print("⚠️ Botão lateral não encontrado — continuando.")

        # selecionar modelo (ex: modelo=27)
        try:
            el_model = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'modelo=27') or contains(.,'Basquete Roxo') or contains(.,'Basquete')]")))
            try:
                el_model.click()
            except Exception:
                driver.execute_script("arguments[0].click();", el_model)
            time.sleep(0.8)
        except TimeoutException:
            print("⚠️ Modelo não encontrado — tentando prosseguir.")

        # clicar gerar banners
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
            print("⚠️ Nenhum popup detectado — pode já estar na galeria.")

        # ir para galeria e clicar 'Enviar Todas as Imagens'
        driver.get(FUTEBOL_CARTAZES)
        time.sleep(1)
        try:
            btn_env = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Enviar Todas as Imagens') or contains(., 'Enviar todas as imagens') or contains(., 'Enviar Todas')]")))
            driver.execute_script("arguments[0].click();", btn_env)
            time.sleep(1)
            print("📤 Envio acionado.")
            return True, "Banners gerados e envio acionado."
        except TimeoutException:
            return False, "Botão 'Enviar Todas as Imagens' não encontrado."
    except Exception as e:
        print("❌ Exceção na geração:", e)
        traceback.print_exc()
        return False, f"Erro na geração: {e}"

# -------------------------
# Fluxo principal
# -------------------------
def main():
    print("🚀 Iniciando automação (Selenium-stealth login)...")
    enviar_telegram("🚀 Iniciando automação Esportes (modo stealth)...")

    LOGIN = os.environ.get("LOGIN")
    SENHA = os.environ.get("SENHA")
    if not LOGIN or not SENHA:
        enviar_telegram("⚠️ LOGIN ou SENHA não configurados.")
        print("⚠️ LOGIN ou SENHA ausentes.")
        return

    driver = None
    try:
        driver = setup_driver()

        ok = fazer_login_selenium(driver, LOGIN, SENHA, tentativas=3)
        if not ok:
            caminho = salvar_print(driver, "erro_login_stealth")
            enviar_telegram("❌ Erro no script Esportes: Falha no login via Selenium stealth.")
            enviar_telegram(f"🖼️ Print salvo: {caminho}")
            return

        # gerar banners
        ok2, detalhe = gerar_banners_esportes(driver)
        if ok2:
            enviar_telegram(f"✅ {detalhe}")
        else:
            caminho = salvar_print(driver, "erro_gerar")
            enviar_telegram(f"❌ {detalhe}")
            enviar_telegram(f"🖼️ Print salvo: {caminho}")

    except Exception as e:
        print("❌ Erro geral:", e)
        traceback.print_exc()
        if driver:
            caminho = salvar_print(driver, "erro_geral")
            enviar_telegram(f"❌ Erro geral no script Esportes: {e}")
            enviar_telegram(f"🖼️ Print salvo: {caminho}")
    finally:
        if driver:
            try:
                driver.quit()
                print("🔒 Navegador fechado.")
            except:
                pass

if __name__ == "__main__":
    main()
