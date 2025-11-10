import os
import sys
import time
import traceback
import requests
from datetime import datetime

# Selenium imports
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
except ImportError as e:
    print(f"❌ Erro ao importar Selenium: {e}")
    print("📦 Instale com: pip install selenium")
    sys.exit(1)

# webdriver_manager opcional
try:
    from webdriver_manager.chrome import ChromeDriverManager
    USE_WEBDRIVER_MANAGER = True
except ImportError:
    USE_WEBDRIVER_MANAGER = False

# -----------------------
# === CONFIGURAÇÕES ===
# -----------------------
LOGIN = os.environ.get("GERADOR_LOGIN", "deivson06")
SENHA = os.environ.get("GERADOR_SENHA", "F9416280")
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "7872091942:AAHbvXRGtdomQxgyKDAkuk1SoLULx0B9xEg")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "-1002169364087")

WAIT_SHORT = 5
WAIT_MED = 15
WAIT_LONG = 40

# -----------------------
# === HELPERS TELEGRAM ===
# -----------------------
def send_telegram_message(text):
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️ Telegram não configurado")
        return False
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": text}
        resp = requests.post(url, data=payload, timeout=20)
        print(f"Telegram status: {resp.status_code}")
        return resp.status_code == 200
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem: {e}")
        return False

def send_telegram_photo(path, caption=""):
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️ Telegram não configurado para envio de foto")
        return False
    if not os.path.exists(path):
        print(f"❌ Arquivo não existe: {path}")
        return False
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        with open(path, "rb") as f:
            files = {"photo": f}
            data = {"chat_id": CHAT_ID, "caption": caption}
            resp = requests.post(url, files=files, data=data, timeout=60)
        print(f"Telegram photo status: {resp.status_code}")
        return resp.status_code == 200
    except Exception as e:
        print(f"❌ Erro ao enviar foto: {e}")
        return False

def save_screenshot(driver, name):
    try:
        folder = "prints"
        os.makedirs(folder, exist_ok=True)
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{name}.png"
        path = os.path.join(folder, filename)
        driver.save_screenshot(path)
        print(f"📸 Screenshot salvo: {path}")
        return path
    except Exception as e:
        print(f"⚠️ Falha ao salvar screenshot: {e}")
        return None

# -----------------------
# === SETUP WEBDRIVER ===
# -----------------------
def setup_driver():
    print("🔧 Configurando Chrome (headless)...")
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    options.add_argument("--log-level=3")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = None
    if USE_WEBDRIVER_MANAGER:
        try:
            print("🧭 Instalando ChromeDriver via webdriver_manager...")
            driver_path = ChromeDriverManager().install()
            service = Service(driver_path)
            driver = webdriver.Chrome(service=service, options=options)
        except Exception as e:
            print(f"⚠️ webdriver_manager falhou: {e}")
            driver = None

    if driver is None:
        try:
            print("🧭 Tentando ChromeDriver do sistema...")
            driver = webdriver.Chrome(options=options)
        except Exception as e:
            print(f"❌ Erro ao iniciar Chrome: {e}")
            raise

    driver.set_page_load_timeout(60)
    driver.implicitly_wait(5)

    # Anti-detect tweaks (pode falhar silenciosamente)
    try:
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    except Exception:
        pass

    print("✅ Chrome configurado")
    return driver

# -----------------------
# === AUX: localizadores flexíveis ===
# -----------------------
def find_input_flexible(driver, kind="username", timeout=10):
    """
    Tenta vários seletores para localizar campo de usuário ou senha.
    kind: "username" ou "password"
    Retorna o elemento encontrado ou None.
    """
    candidates = []
    if kind == "username":
        candidates = [
            (By.NAME, "username"),
            (By.NAME, "user"),
            (By.NAME, "login"),
            (By.NAME, "email"),
            (By.NAME, "usuario"),
            (By.ID, "username"),
            (By.ID, "user"),
            (By.CSS_SELECTOR, "input[placeholder*='user']"),
            (By.CSS_SELECTOR, "input[placeholder*='User']"),
            (By.CSS_SELECTOR, "input[type='email']"),
            (By.XPATH, "//input[@type='text' and (contains(@placeholder,'user') or contains(@placeholder,'Usu'))]"),
            (By.XPATH, "//input[contains(@name,'user')]"),
            (By.XPATH, "//input[contains(@id,'user')]")
        ]
    else:
        candidates = [
            (By.NAME, "password"),
            (By.NAME, "senha"),
            (By.NAME, "pass"),
            (By.ID, "password"),
            (By.CSS_SELECTOR, "input[type='password']"),
            (By.XPATH, "//input[@type='password']"),
            (By.XPATH, "//input[contains(@name,'pass')]"),
            (By.XPATH, "//input[contains(@id,'pass')]")
        ]

    for by, sel in candidates:
        try:
            el = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, sel)))
            # garantir que seja input e interativo
            tag = el.tag_name.lower()
            if tag in ("input", "textarea"):
                return el
        except Exception:
            continue
    return None

def click_flexible(driver, xpaths_or_css, timeout=8):
    """Tenta uma lista de seletores (XPath ou CSS) e clica no primeiro clicável."""
    for sel in xpaths_or_css:
        try:
            if sel.startswith("/") or sel.startswith("(") or sel.startswith(".//"):
                el = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, sel)))
            else:
                el = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.CSS_SELECTOR, sel)))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
            time.sleep(0.3)
            try:
                el.click()
            except:
                driver.execute_script("arguments[0].click();", el)
            return True
        except Exception:
            continue
    return False

# -----------------------
# === FLUXO PRINCIPAL ===
# -----------------------
def executar_fluxo_completo(driver):
    try:
        print("\n" + "="*60)
        print("📋 ETAPA 1: Acessando página de login")
        print("="*60)

        login_url = "https://gerador.pro/login.php"
        driver.get(login_url)
        time.sleep(2)

        p1 = save_screenshot(driver, "01_pagina_login")
        if p1: send_telegram_photo(p1, "📋 ETAPA 1: Página de login")

        print("\n" + "="*60)
        print("📋 ETAPA 2: Realizando login automático")
        print("="*60)

        # localizar campo usuário de forma resiliente
        campo_user = find_input_flexible(driver, kind="username", timeout=10)
        if not campo_user:
            # tentar inputs visíveis como fallback
            try:
                inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='email']")
                for i in inputs:
                    if i.is_displayed():
                        campo_user = i
                        break
            except:
                pass

        if not campo_user:
            raise Exception("❌ Campo de usuário não localizado (verifique o formulário)")

        print(f"   ✅ Campo usuário localizado: tag={campo_user.tag_name} name={campo_user.get_attribute('name')} id={campo_user.get_attribute('id')}")
        campo_user.clear()
        campo_user.send_keys(LOGIN)
        time.sleep(0.5)

        campo_pass = find_input_flexible(driver, kind="password", timeout=6)
        if not campo_pass:
            # fallback: procurar input[type=password]
            try:
                campos = driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
                for c in campos:
                    if c.is_displayed():
                        campo_pass = c
                        break
            except:
                pass

        if not campo_pass:
            raise Exception("❌ Campo de senha não localizado")

        print(f"   ✅ Campo senha localizado: name={campo_pass.get_attribute('name')} id={campo_pass.get_attribute('id')}")
        campo_pass.clear()
        campo_pass.send_keys(SENHA)
        time.sleep(0.5)

        p2 = save_screenshot(driver, "02_credenciais_preenchidas")
        if p2: send_telegram_photo(p2, "📋 ETAPA 2: Credenciais preenchidas")

        print("🖱️ Procurando botão de login...")
        btn_selectors = [
            "//button[contains(., 'Entrar no painel')]",
            "//button[contains(., 'ENTRAR NO PAINEL')]",
            "//button[contains(., 'Entrar')]",
            "//button[contains(., 'Login')]",
            "//input[@type='submit']",
            "//button[@type='submit']",
            "button[type='submit']",
            "input[type='submit']"
        ]

        clicked = click_flexible(driver, btn_selectors, timeout=8)
        if not clicked:
            # tentar por texto visível
            try:
                all_buttons = driver.find_elements(By.XPATH, "//button|//input[@type='submit']")
                for btn in all_buttons:
                    try:
                        if btn.is_displayed() and btn.is_enabled():
                            texto = (btn.text or btn.get_attribute("value") or "").strip()
                            if texto:
                                driver.execute_script("arguments[0].click();", btn)
                                clicked = True
                                break
                    except:
                        continue
            except:
                pass

        if not clicked:
            raise Exception("❌ Botão de login não encontrado")

        print("⏳ Aguardando redirecionamento pós-login...")
        try:
            WebDriverWait(driver, WAIT_LONG).until(EC.url_contains("index.php"))
        except TimeoutException:
            # pode ser que não mude a URL mas o login tenha ocorrido; esperar um pouco e seguir
            print("⚠️ Timeout esperando index.php; continuando pois pode ter logado sem redirecionar")
        print(f"✅ URL atual: {driver.current_url}")

        p3 = save_screenshot(driver, "03_login_realizado")
        if p3: send_telegram_photo(p3, "✅ ETAPA 2: Login realizado")

        # ===== ETAPA 3: Menu Gerar Futebol =====
        print("\n" + "="*60)
        print("📋 ETAPA 3: Acessando Gerar Futebol (modelo 15)")
        print("="*60)

        # tentar abrir diretamente a página do modelo 15 (mais confiável)
        try:
            driver.get("https://gerador.pro/futbanner.php?page=futebol&modelo=15")
            WebDriverWait(driver, WAIT_MED).until(EC.url_contains("futbanner.php"))
        except Exception:
            # fallback: clicar no menu
            menu_selectors = [
                "//a[contains(., 'Gerar Futebol')]",
                "//a[contains(., 'Futebol')]",
                "//li[contains(., 'Gerar Futebol')]//a",
                "//nav//a[contains(., 'Futebol')]"
            ]
            click_flexible(driver, menu_selectors, timeout=10)

        time.sleep(2)
        p4 = save_screenshot(driver, "04_menu_futebol")
        if p4: send_telegram_photo(p4, "📋 ETAPA 3: Menu Gerar Futebol")

        # ===== ETAPA 4: Selecionar modelo 15 =====
        print("\n" + "="*60)
        print("📋 ETAPA 4: Selecionando modelo 15")
        print("="*60)

        model_selectors = [
            "//button[contains(., '15')]",
            "//input[@value='15']",
            "//label[contains(., '15')]",
            "//div[contains(@class,'modelo') and contains(.,'15')]",
            "//a[contains(., '15')]"
        ]

        clicked = click_flexible(driver, model_selectors, timeout=8)
        if not clicked:
            print("⚠️ Não localizou botão/exibição do modelo 15 automaticamente, seguindo mesmo assim...")
        else:
            print("✅ Modelo 15 selecionado")

        time.sleep(2)
        p5 = save_screenshot(driver, "05_modelo_15")
        if p5: send_telegram_photo(p5, "📋 ETAPA 4: Modelo 15 (ou página do modelo)")

        # ===== ETAPA 5: GERAR BANNERS =====
        print("\n" + "="*60)
        print("📋 ETAPA 5: Clicando em 'Gerar Banners'")
        print("="*60)

        # esperar corpo carregado
        try:
            WebDriverWait(driver, WAIT_MED).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        except:
            pass
        time.sleep(1)

        gerar_selectors = [
            "//button[contains(., 'Gerar Banners')]",
            "//button[contains(translate(., 'GERAR', 'gerar'), 'gerar')]",
            "//input[contains(@value, 'Gerar')]",
            "//a[contains(., 'Gerar')]",
            "//form//button[contains(., 'Gerar')]",
            "button.btn-primary",
            ".btn-gerar",
            "#btnGerar"
        ]

        clicked = click_flexible(driver, gerar_selectors, timeout=8)

        if not clicked:
            # tentar qualquer botão visível como último recurso
            print("   ⚠️ Botão 'Gerar' não detectado nos seletores primários — buscando qualquer botão visível...")
            try:
                all_buttons = driver.find_elements(By.XPATH, "//button | //input[@type='submit'] | //input[@type='button'] | //a")
                for btn in all_buttons:
                    try:
                        if btn.is_displayed() and btn.is_enabled():
                            text = (btn.text or btn.get_attribute("value") or btn.get_attribute("aria-label") or "").lower()
                            if "gerar" in text or "criar" in text or "gerar banner" in text:
                                driver.execute_script("arguments[0].click();", btn)
                                clicked = True
                                print(f"   ✅ Clique em botão genérico: {text}")
                                break
                    except:
                        continue
            except Exception as e:
                print(f"   ❌ Erro buscando botões genéricos: {e}")

        if not clicked:
            p_dbg = save_screenshot(driver, "debug_botao_nao_encontrado")
            if p_dbg: send_telegram_photo(p_dbg, "❌ DEBUG: Botão Gerar não encontrado")
            raise Exception("❌ Botão Gerar não encontrado")

        print("   ⏳ Aguardando processamento após clique em Gerar...")
        time.sleep(5)

        p6 = save_screenshot(driver, "06_gerando")
        if p6: send_telegram_photo(p6, "📋 ETAPA 5: Gerando banners...")

        # ===== ETAPA 6: POPUP OK ou redirecionamento =====
        print("\n" + "="*60)
        print("📋 ETAPA 6: Detectando popup de sucesso ou redirecionamento")
        print("="*60)

        sucesso_detectado = False
        # tentar detectar textos comuns de sucesso
        try:
            WebDriverWait(driver, 12).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Sucesso') or contains(text(),'Banners gerados') or contains(text(),'Banners gerado') or contains(text(),'Sucesso!')]"))
            )
            sucesso_detectado = True
            print("✅ Popup de sucesso detectado")
            # tentar clicar OK se existir
            try:
                ok_btn = WebDriverWait(driver, 6).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".swal2-confirm, .swal-button, button.confirm, button.ok")))
                driver.execute_script("arguments[0].click();", ok_btn)
                print("✅ Botão OK do popup clicado")
                time.sleep(1)
            except:
                print("⚠️ Botão OK não encontrado/visível (pode ter fechado sozinho)")
        except TimeoutException:
            print("⚠️ Popup de sucesso não apareceu no tempo esperado")

        # se não detectou popup, verificar URL
        current = driver.current_url or ""
        if not sucesso_detectado:
            if "futbanner.php?page=futebol" in current or "/futebol/cartazes/" in current or "cartazes" in current:
                sucesso_detectado = True
                print("✅ Padrão de URL de galeria detectado (assumindo sucesso)")

        p7 = save_screenshot(driver, "07_popup_ou_url")
        if p7: send_telegram_photo(p7, "📋 ETAPA 6: Resultado após gerar")

        # ===== ETAPA 7: GALERIA =====
        print("\n" + "="*60)
        print("📋 ETAPA 7: Indo para galeria")
        print("="*60)

        try:
            if "/futebol/cartazes/" not in driver.current_url:
                # tentar abrir a galeria diretamente
                driver.get("https://gerador.pro/futebol/cartazes/")
                WebDriverWait(driver, WAIT_MED).until(EC.url_contains("/futebol/cartazes/"))
        except Exception:
            # se não conseguir por URL, tentar clicar em algo que leve à galeria
            gal_selectors = [
                "//a[contains(., 'Galeria')]",
                "//a[contains(., 'Cartazes')]",
                "//a[contains(., 'Galeria de banners')]"
            ]
            click_flexible(driver, gal_selectors, timeout=6)

        time.sleep(2)
        p8 = save_screenshot(driver, "08_galeria")
        if p8: send_telegram_photo(p8, "📋 ETAPA 7: Galeria")

        # ===== ETAPA 8: ENVIAR TODAS =====
        print("\n" + "="*60)
        print("📋 ETAPA 8: Enviando todas as imagens")
        print("="*60)

        enviar_selectors = [
            "//button[contains(., 'Enviar todas')]",
            "//a[contains(., 'Enviar todas')]",
            "//button[contains(., 'Enviar tudo')]",
            "//a[contains(., 'Enviar tudo')]",
            "//button[contains(., 'Enviar')]"
        ]

        clicked_send = click_flexible(driver, enviar_selectors, timeout=12)
        if not clicked_send:
            # tentar ícone/tipo Telegram caso exista
            try:
                btns = driver.find_elements(By.XPATH, "//button|//a")
                for b in btns:
                    try:
                        if b.is_displayed() and b.is_enabled():
                            text = (b.text or b.get_attribute("title") or b.get_attribute("aria-label") or "").lower()
                            if "enviar" in text:
                                driver.execute_script("arguments[0].click();", b)
                                clicked_send = True
                                break
                    except:
                        continue
            except:
                pass

        if not clicked_send:
            p9 = save_screenshot(driver, "debug_enviar_nao_encontrado")
            if p9: send_telegram_photo(p9, "❌ DEBUG: Botão Enviar não encontrado")
            raise Exception("❌ Botão Enviar não encontrado")

        time.sleep(6)
        p10 = save_screenshot(driver, "09_enviando")
        if p10: send_telegram_photo(p10, "📋 ETAPA 8: Enviando")

        send_telegram_message("🎉 CONCLUIDO! Banners gerados e enviados com sucesso")
        p11 = save_screenshot(driver, "10_final")
        if p11: send_telegram_photo(p11, "✅ FINALIZADO")

        print("\n✨ FLUXO COMPLETO - SUCESSO!")
        return True

    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        traceback.print_exc()
        try:
            p_err = save_screenshot(driver, "erro")
            if p_err:
                send_telegram_photo(p_err, f"❌ Erro: {str(e)[:200]}")
            else:
                send_telegram_message(f"❌ Erro: {e}")
        except:
            pass
        return False

def main():
    start = time.time()
    driver = None
    success = False

    print("="*60)
    print("🚀 AUTOMAÇÃO GERADOR.PRO (resiliente)")
    print("="*60)
    print(f"Login: {LOGIN}")
    print(f"Telegram: {'✓' if BOT_TOKEN else '✗'}")
    print("="*60)

    try:
        if BOT_TOKEN:
            send_telegram_message("🚀 Iniciando automação (resiliente) Gerador.Pro")

        driver = setup_driver()
        success = executar_fluxo_completo(driver)

        if success:
            send_telegram_message("✅ Automação finalizada com SUCESSO!")
        else:
            send_telegram_message("❌ Automação finalizada com ERROS")

    except Exception as e:
        print(f"‼️ Erro crítico: {e}")
        traceback.print_exc()
        send_telegram_message(f"❌ Erro crítico: {e}")

    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

        elapsed = time.time() - start
        status = "✅ SUCESSO" if success else "❌ FALHOU"
        msg = f"📊 Relatório Final\n\n{status}\nTempo: {elapsed:.1f}s"
        send_telegram_message(msg)
        print(f"\n🏁 FIM - {elapsed:.1f}s - {status}")
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
