#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, time, requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# ============================================================
# 🧩 Configurações e utilitários
# ============================================================

def setup_driver():
    print("🚀 Iniciando navegador Chrome (modo headless)...")
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def enviar_telegram(msg):
    token = os.environ.get("BOT_TOKEN")
    chat_id = os.environ.get("CHAT_ID")
    if not token or not chat_id:
        print("⚠️ BOT_TOKEN ou CHAT_ID não configurados.")
        return
    try:
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage", data={
            "chat_id": chat_id,
            "text": msg,
            "parse_mode": "Markdown"
        })
        print("📨 Mensagem enviada ao Telegram!")
    except Exception as e:
        print(f"⚠️ Falha ao enviar mensagem Telegram: {e}")

def salvar_print(driver, nome):
    pasta = "prints"
    os.makedirs(pasta, exist_ok=True)
    caminho = f"{pasta}/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{nome}.png"
    driver.save_screenshot(caminho)
    print(f"📸 Print salvo: {caminho}")
    return caminho

# ============================================================
# 🧠 Login atualizado
# ============================================================

def fazer_login(driver, login, senha):
    print("====================================================")
    print("ETAPA 1/5: Login")
    print("====================================================")

    driver.get("https://gerador.pro/login.php")

    try:
        print("🔍 Localizando campo username...")
        user = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
        print("🔍 Localizando campo password...")
        passw = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password")))

        user.clear()
        user.send_keys(login)
        print("🧩 Username inserido...")
        passw.clear()
        passw.send_keys(senha)
        print("🔒 Password inserido...")

        print("➡️ Clicando no botão ENTRAR...")
        driver.find_element(By.CLASS_NAME, "btn-login").click()

        print("⏳ Aguardando redirecionamento após login...")
        try:
            WebDriverWait(driver, 8).until(EC.url_contains("painel"))
            print("✅ Login realizado com sucesso!")
            return True

        except TimeoutException:
            print("❌ Erro no login: nenhuma mudança de URL detectada.")
            erro_msg = None
            try:
                erro_msg = driver.find_element(By.CSS_SELECTOR, ".alert, .erro, .text-danger").text
                print(f"📛 Mensagem de erro detectada: {erro_msg}")
            except:
                print("⚠️ Nenhuma mensagem de erro visível.")

            caminho = salvar_print(driver, "erro_login")
            if erro_msg:
                enviar_telegram(f"❌ *Erro no script Esportes (login)*:\n{erro_msg}")
            else:
                enviar_telegram("❌ *Erro no script Esportes:* Falha desconhecida ao tentar logar.")
            enviar_telegram(f"🖼️ Print salvo: {caminho}")
            return False

    except Exception as e:
        caminho = salvar_print(driver, "erro_geral_login")
        enviar_telegram(f"❌ *Erro crítico no login:* {e}")
        enviar_telegram(f"🖼️ Print salvo: {caminho}")
        print(f"⚠️ Exceção durante login: {e}")
        return False

# ============================================================
# ⚙️ Etapas de geração e envio
# ============================================================

def gerar_banners_esportes(driver):
    print("====================================================")
    print("ETAPA 2/5: Acessar aba de esportes e gerar banners")
    print("====================================================")

    driver.get("https://gerador.pro/nba.php")

    try:
        # Clica no botão “Todos esportes” no menu lateral
        print("🏀 Clicando no botão 'Todos Esportes'...")
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(.,'Todos Esportes')]"))
        ).click()

        # Clica no modelo correto (exemplo: “Basquete Roxo”)
        print("🎨 Selecionando modelo 'Basquete Roxo'...")
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'modelo=27')]"))
        ).click()

        # Clica em “Gerar Banners”
        print("⚙️ Gerando banners...")
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "generateButton"))
        ).click()

        # Espera popup de sucesso e confirma
        print("⏳ Aguardando mensagem de sucesso...")
        WebDriverWait(driver, 10).until(
            EC.alert_is_present()
        )
        alert = driver.switch_to.alert
        msg = alert.text
        print(f"✅ Popup detectado: {msg}")
        alert.accept()
        print("👍 Popup confirmado, indo para galeria...")

    except Exception as e:
        caminho = salvar_print(driver, "erro_gerar_esportes")
        enviar_telegram(f"❌ *Erro ao gerar banners esportes:* {e}")
        enviar_telegram(f"🖼️ Print salvo: {caminho}")
        return False

    return True


def enviar_todas_as_imagens(driver):
    print("====================================================")
    print("ETAPA 3/5: Enviando todas as imagens")
    print("====================================================")

    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Enviar Todas as Imagens')]"))
        ).click()
        print("📤 Botão 'Enviar Todas as Imagens' clicado!")
        enviar_telegram("✅ Banners de esportes gerados e enviados com sucesso!")
        return True
    except Exception as e:
        caminho = salvar_print(driver, "erro_enviar_todas")
        enviar_telegram(f"❌ *Erro ao enviar imagens esportes:* {e}")
        enviar_telegram(f"🖼️ Print salvo: {caminho}")
        return False


# ============================================================
# 🏁 Fluxo principal
# ============================================================

def main():
    print("🚀 Iniciando automação Esportes...")

    login = os.environ.get("LOGIN")
    senha = os.environ.get("SENHA")

    if not login or not senha:
        enviar_telegram("⚠️ LOGIN ou SENHA não configurados no repositório!")
        return

    driver = setup_driver()

    try:
        if not fazer_login(driver, login, senha):
            driver.quit()
            return

        if not gerar_banners_esportes(driver):
            driver.quit()
            return

        enviar_todas_as_imagens(driver)

    except Exception as e:
        caminho = salvar_print(driver, "erro_geral")
        enviar_telegram(f"❌ *Erro geral no script Esportes:* {e}")
        enviar_telegram(f"🖼️ Print salvo: {caminho}")

    finally:
        driver.quit()
        print("🔒 Navegador fechado.")


if __name__ == "__main__":
    main()
