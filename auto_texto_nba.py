import os
import sys
import time
import traceback
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# ===============================
# 🔧 CONFIGURAÇÕES
# ===============================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
CHAT_ID = os.environ.get("CHAT_ID", "")
LOGIN = os.environ.get("LOGIN", "")
SENHA = os.environ.get("SENHA", "")

# Validação
if not all([BOT_TOKEN, CHAT_ID, LOGIN, SENHA]):
    print("❌ ERRO: Variáveis não configuradas!")
    sys.exit(1)

print(f"✅ Bot Token: {BOT_TOKEN[:15]}...")
print(f"✅ Chat ID: {CHAT_ID}")
print(f"✅ Login: {LOGIN}")

# ===============================
# 📡 TELEGRAM
# ===============================
def enviar_telegram(msg, img=None):
    for i in range(3):
        try:
            if img and os.path.exists(img):
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
                with open(img, "rb") as f:
                    r = requests.post(url, data={"chat_id": CHAT_ID, "caption": msg}, files={"photo": f}, timeout=30)
            else:
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                r = requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=30)
            
            if r.status_code == 200:
                print(f"✅ Telegram OK")
                return True
            print(f"⚠️ Status {r.status_code}")
        except Exception as e:
            print(f"⚠️ Tentativa {i+1}: {e}")
            time.sleep(2)
    return False

def salvar_print(driver, nome):
    try:
        os.makedirs("prints", exist_ok=True)
        caminho = f"prints/{time.strftime('%H%M%S')}_{nome}.png"
        driver.save_screenshot(caminho)
        print(f"📸 {caminho}")
        return caminho
    except Exception as e:
        print(f"❌ Print erro: {e}")
        return None

# ===============================
# 🧠 CHROME
# ===============================
def setup_driver():
    print("\n🚀 Iniciando Chrome...")
    
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    opts.binary_location = "/usr/bin/chromium-browser"
    
    driver = webdriver.Chrome(options=opts)
    driver.set_page_load_timeout(60)
    print("✅ Chrome OK\n")
    return driver

# ===============================
# 🔐 LOGIN
# ===============================
def fazer_login(driver):
    print("🔐 Fazendo login...")
    enviar_telegram("🟡 Iniciando login...")
    
    try:
        driver.get("https://gerador.pro/painel")
        print(f"📄 {driver.current_url}")
        
        time.sleep(20)  # Cloudflare
        img1 = salvar_print(driver, "01_cloudflare")
        enviar_telegram("🛡️ Cloudflare OK", img1)
        
        user = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.NAME, "username")))
        pwd = driver.find_element(By.NAME, "password")
        
        user.send_keys(LOGIN)
        time.sleep(1)
        pwd.send_keys(SENHA)
        time.sleep(1)
        
        img2 = salvar_print(driver, "02_antes_login")
        enviar_telegram("📋 Credenciais OK", img2)
        
        btn = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Entrar')]"))
        )
        btn.click()
        
        time.sleep(10)
        WebDriverWait(driver, 30).until(EC.url_contains("painel"))
        
        print(f"✅ Login OK: {driver.current_url}")
        img3 = salvar_print(driver, "03_apos_login")
        enviar_telegram(f"✅ Login OK!\n{driver.current_url}", img3)
        time.sleep(3)
        return True
        
    except Exception as e:
        print(f"❌ Login erro: {e}")
        img = salvar_print(driver, "ERRO_login")
        enviar_telegram(f"❌ Erro login: {e}", img)
        return False

# ===============================
# 🏀 GERAR BANNERS NBA
# ===============================
def gerar_banners(driver):
    print("\n🏀 Gerando banners NBA...")
    
    try:
        driver.get("https://gerador.pro/nba")
        time.sleep(6)
        print(f"📄 {driver.current_url}")
        
        img1 = salvar_print(driver, "04_pagina_nba")
        enviar_telegram("📄 Página NBA OK", img1)
        
        btn15 = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'15')]"))
        )
        btn15.click()
        time.sleep(4)
        print("✅ Modelo 15 OK")
        
        img2 = salvar_print(driver, "05_modelo_15")
        enviar_telegram("✅ Modelo 15 NBA", img2)
        
        btn_gerar = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Gerar')]"))
        )
        btn_gerar.click()
        print("⏳ Gerando (25s)...")
        time.sleep(25)
        
        img3 = salvar_print(driver, "06_gerados")
        enviar_telegram("✅ Banners NBA gerados! 🏀", img3)
        
        try:
            ok = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'OK')]")))
            ok.click()
            time.sleep(5)
        except:
            print("⚠️ OK não encontrado")
        
        btn_enviar = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Enviar')]"))
        )
        btn_enviar.click()
        print("⏳ Enviando (20s)...")
        time.sleep(20)
        
        img4 = salvar_print(driver, "07_enviados")
        enviar_telegram("🎉 Banners NBA enviados! 🏀", img4)
        return True
        
    except Exception as e:
        print(f"❌ Gerar erro: {e}")
        img = salvar_print(driver, "ERRO_gerar")
        enviar_telegram(f"❌ Erro gerar: {e}", img)
        return False

# ===============================
# 🎯 MAIN
# ===============================
def main():
    print("="*50)
    print("🚀 AUTOMAÇÃO NBA INICIADA")
    print("="*50)
    
    inicio = time.time()
    driver = None
    ok_login = False
    ok_gerar = False
    
    try:
        enviar_telegram(f"🚀 AUTOMAÇÃO NBA INICIADA 🏀\n{time.strftime('%d/%m/%Y %H:%M:%S')}")
        
        driver = setup_driver()
        ok_login = fazer_login(driver)
        
        if not ok_login:
            raise Exception("Falha no login")
        
        ok_gerar = gerar_banners(driver)
        
        if not ok_gerar:
            raise Exception("Falha ao gerar")
        
        print("\n🎉 SUCESSO TOTAL NBA! 🏀")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        print(traceback.format_exc())
        if driver:
            img = salvar_print(driver, "ERRO_geral")
            enviar_telegram(f"❌ ERRO: {e}", img)
    
    finally:
        tempo = time.time() - inicio
        
        if driver:
            driver.quit()
            print("✅ Chrome fechado")
        
        status = "✅ SUCESSO" if (ok_login and ok_gerar) else "❌ FALHA"
        enviar_telegram(
            f"📊 RELATÓRIO NBA 🏀\n\n"
            f"Status: {status}\n"
            f"Login: {'✅' if ok_login else '❌'}\n"
            f"Geração: {'✅' if ok_gerar else '❌'}\n"
            f"Tempo: {tempo:.1f}s"
        )
        
        print(f"\n{'='*50}")
        print(f"STATUS: {status}")
        print(f"Tempo: {tempo:.1f}s")
        print(f"{'='*50}\n")

if __name__ == "__main__":
    main()
