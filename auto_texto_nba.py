import os, time, requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException

# ===============================================================
# ⚙️ CONFIGURAÇÃO DO NAVEGADOR
# ===============================================================
def setup_driver():
    print("🔧 Configurando Chrome headless...")
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/130.0.0.0 Safari/537.36"
    )
    options.add_argument("--disable-blink-features=AutomationControlled")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_cdp_cmd("Network.setUserAgentOverride", {
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                     "AppleWebKit/537.36 (KHTML, like Gecko) "
                     "Chrome/130.0.0.0 Safari/537.36"
    })
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
    })
    print("✅ Chrome configurado com sucesso!")
    return driver


# ===============================================================
# 🔑 LOGIN
# ===============================================================
def fazer_login(driver, login, senha):
    print("🔑 Fazendo login no GERADOR PRO...")
    driver.get("https://gerador.pro/login.php")

    WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(login)
    driver.find_element(By.NAME, "password").send_keys(senha)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    WebDriverWait(driver, 20).until(lambda d: "index.php" in d.current_url)
    print("✅ Login realizado com sucesso!")


# ===============================================================
# 🏀 PÁGINA NBA
# ===============================================================
def ir_gerar_nba(driver):
    print("🏀 Indo para a página de geração NBA...")
    driver.get("https://gerador.pro/nba.php")
    WebDriverWait(driver, 10).until(lambda d: "nba" in d.current_url)
    print(f"✅ Página NBA aberta: {driver.current_url}")


# ===============================================================
# 🟣 GERAR E ENVIAR TODOS OS BANNERS NBA
# ===============================================================
def gerar_banners(driver):
    print("🎨 Selecionando modelo 'Basquete Roxo'...")
    botao_roxo = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//*[contains(text(),'Basquete Roxo')]"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", botao_roxo)
    time.sleep(1)
    botao_roxo.click()
    print("✅ Clicou em 'Basquete Roxo'")

    WebDriverWait(driver, 15).until(lambda d: "modelo=27" in d.current_url)
    print(f"📄 Página do modelo carregada: {driver.current_url}")

    botao_gerar = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Gerar Banners')]"))
    )
    botao_gerar.click()
    print("⚙️ Clicou em 'Gerar Banners', aguardando popup...")

    popup_ok = WebDriverWait(driver, 25).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'OK')]"))
    )
    popup_ok.click()
    print("✅ Clicou em 'OK' do popup!")

    WebDriverWait(driver, 25).until(lambda d: "cartazes" in d.current_url)
    print(f"🖼️ Página de banners carregada: {driver.current_url}")

    # AGUARDAR CARREGAMENTO COMPLETO DAS IMAGENS
    print("⏳ Aguardando carregamento dos banners (30s)...")
    time.sleep(30)  # Tempo maior para garantir que os banners carregaram
    
    # ESTRATÉGIA 1: Tentar enviar individualmente por diferentes seletores
    banners_enviados = 0
    
    # Tentar localizar botões por diferentes métodos
    seletores = [
        "//button[contains(text(),'Enviar') and not(contains(text(),'Todas'))]",
        "//button[@class and contains(text(),'Enviar')]",
        "//form//button[contains(text(),'Enviar')]",
        "//div[@class='banner-item']//button",
        "//button[@type='submit' and contains(text(),'Enviar')]"
    ]
    
    botoes_encontrados = []
    for seletor in seletores:
        try:
            botoes = driver.find_elements(By.XPATH, seletor)
            if botoes:
                print(f"✅ Encontrados {len(botoes)} botões com seletor: {seletor[:50]}...")
                botoes_encontrados = botoes
                break
        except:
            continue
    
    if not botoes_encontrados:
        print("⚠️ Nenhum botão individual encontrado, tentando método alternativo...")
        
        # ESTRATÉGIA 2: Usar JavaScript para enviar os formulários
        try:
            print("🔄 Tentando enviar via JavaScript...")
            script = """
            var forms = document.querySelectorAll('form');
            var count = 0;
            forms.forEach(function(form, index) {
                if (form.querySelector('img') || form.querySelector('button')) {
                    setTimeout(function() {
                        form.submit();
                        console.log('Enviado formulário ' + (index + 1));
                    }, index * 3000);
                    count++;
                }
            });
            return count;
            """
            banners_enviados = driver.execute_script(script)
            print(f"✅ Tentativa de envio via JS: {banners_enviados} formulários")
            time.sleep(10)  # Aguardar envios
            
        except Exception as e:
            print(f"❌ Erro ao enviar via JS: {e}")
    
    else:
        # ESTRATÉGIA 3: Clicar nos botões encontrados
        for i, botao in enumerate(botoes_encontrados[:3], 1):  # Máximo 3 banners
            try:
                print(f"\n📤 Enviando banner {i}/3...")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", botao)
                time.sleep(1)
                
                # Tentar click normal, se falhar usar JS
                try:
                    botao.click()
                except:
                    driver.execute_script("arguments[0].click();", botao)
                
                print(f"✅ Clicou no botão do banner {i}")
                time.sleep(4)  # Aguardar processamento
                banners_enviados += 1
                
            except Exception as e:
                print(f"⚠️ Erro ao enviar banner {i}: {e}")
                continue
    
    # Aguardar confirmação final
    print(f"\n⏳ Aguardando confirmação final (15s)...")
    time.sleep(15)
    
    # Verificar quantos foram enviados checando o conteúdo da página
    body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
    confirmacoes = body_text.count("enviado") + body_text.count("sucesso")
    
    print(f"\n📊 Resumo: {banners_enviados} tentativas / {confirmacoes} confirmações detectadas")
    
    if banners_enviados >= 1 or confirmacoes >= 1:
        print(f"✅ Envio concluído! ({max(banners_enviados, confirmacoes)} banner(s))")
        return banners_enviados
    else:
        raise Exception("❌ Nenhum banner foi enviado. Verifique a estrutura da página.")


# ===============================================================
# 📢 TELEGRAM
# ===============================================================
def enviar_telegram(msg):
    token = os.environ.get("BOT_TOKEN")
    chat_id = os.environ.get("CHAT_ID")
    if not token or not chat_id:
        print("⚠️ Bot Token ou Chat ID não configurados.")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": msg, "parse_mode": "HTML"}
    try:
        r = requests.post(url, data=data)
        if r.status_code == 200:
            print("📨 Mensagem enviada ao Telegram!")
        else:
            print(f"⚠️ Telegram retornou {r.status_code}: {r.text}")
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem: {e}")


# ===============================================================
# 🚀 FLUXO PRINCIPAL
# ===============================================================
def main():
    print("=" * 70)
    print("🚀 INICIANDO AUTOMAÇÃO NBA - GERADOR PRO")
    print(f"🕒 Executado em: {time.strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 70)

    login = os.environ.get("LOGIN")
    senha = os.environ.get("SENHA")

    driver = setup_driver()
    try:
        fazer_login(driver, login, senha)
        ir_gerar_nba(driver)
        enviados = gerar_banners(driver)

        hora = time.strftime("%H:%M")
        data = time.strftime("%d/%m/%Y")
        enviar_telegram(f"🏀 <b>NBA - {data}</b>\n✅ Envio completo às {hora}\n📸 {enviados} banner(s) enviado(s) com sucesso!")
        print("=" * 70)
        print("✅ AUTOMAÇÃO NBA FINALIZADA COM SUCESSO!")
        print("=" * 70)

    except Exception as e:
        print("❌ ERRO DURANTE A EXECUÇÃO:", e)
        enviar_telegram(f"❌ Erro ao gerar banners NBA: {e}")
    finally:
        driver.quit()
        print("🔒 Navegador fechado")


if __name__ == "__main__":
    main()
