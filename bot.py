import os, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    print("🔧 Configurando Chrome...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    print("✅ Chrome configurado!")
    return driver

def fazer_login(driver, login, senha):
    print("🔑 Fazendo login no GERADOR PRO...")
    driver.get("https://gerador.pro/login.php")
    time.sleep(5)
    
    # Preenche usuário
    campo_usuario = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )
    campo_usuario.clear()
    campo_usuario.send_keys(login)
    print("✅ Usuário preenchido")
    
    # Preenche senha
    campo_senha = driver.find_element(By.NAME, "password")
    campo_senha.clear()
    campo_senha.send_keys(senha)
    print("✅ Senha preenchida")
    
    # Clica no botão de login
    botao_login = driver.find_element(By.XPATH, "//button[@type='submit']")
    botao_login.click()
    print("✅ Login executado!")
    
    # Aguarda redirecionamento
    WebDriverWait(driver, 10).until(
        lambda driver: "index.php" in driver.current_url
    )
    print(f"✅ Login bem-sucedido! URL: {driver.current_url}")

def ir_gerar_futebol(driver):
    print("⚽ Indo para Gerar Futebol...")
    
    # Aguarda a página carregar completamente
    time.sleep(3)
    
    # Múltiplas estratégias para encontrar e clicar no link
    estrategias = [
        # Link direto por texto
        "//a[contains(text(), 'Gerar Futebol')]",
        "//a[text()='Gerar Futebol']",
        
        # Link por href
        "//a[@href='https://gerador.pro/futbanner.php']",
        "//a[contains(@href, 'futbanner.php')]",
        "//a[contains(@href, 'futebol')]",
        
        # Div ou outros elementos clicáveis
        "//div[contains(text(), 'Gerar Futebol')]",
        "//span[contains(text(), 'Gerar Futebol')]",
        "//li[contains(text(), 'Gerar Futebol')]",
        
        # Por posição (pode ser o terceiro link)
        "(//a)[3]",
        
        # Menu items
        "//nav//a[contains(text(), 'Gerar Futebol')]",
        "//*[@class and contains(text(), 'Gerar Futebol')]"
    ]
    
    link_clicado = False
    for i, strategy in enumerate(estrategias):
        try:
            print(f"🔍 Tentativa {i+1}: {strategy}")
            
            # Tenta encontrar o elemento
            elemento = driver.find_element(By.XPATH, strategy)
            
            # Verifica se está visível
            if elemento.is_displayed():
                # Tenta clicar normalmente
                try:
                    elemento.click()
                    link_clicado = True
                    print("✅ Clicou em Gerar Futebol (clique normal)")
                    break
                except:
                    # Se clique normal falhou, tenta JavaScript
                    try:
                        driver.execute_script("arguments[0].click();", elemento)
                        link_clicado = True
                        print("✅ Clicou em Gerar Futebol (JavaScript)")
                        break
                    except:
                        print("   ❌ Clique falhou")
            else:
                print("   ❌ Elemento não visível")
                
        except Exception as e:
            print(f"   ❌ Falhou: {str(e)[:50]}")
            continue
    
    # Se ainda não clicou, tenta navegar diretamente pela URL
    if not link_clicado:
        print("🔄 Tentando navegação direta...")
        try:
            driver.get("https://gerador.pro/futbanner.php")
            link_clicado = True
            print("✅ Navegou diretamente para futbanner.php")
        except:
            print("❌ Navegação direta falhou")
    
    if not link_clicado:
        raise Exception("Não foi possível acessar Gerar Futebol")
    
    # Aguarda carregar a nova página
    time.sleep(5)
    print(f"✅ Página carregada: {driver.current_url}")
    
    # Verifica se realmente está na página de futebol
    if "futbanner" not in driver.current_url.lower():
        print("⚠️ URL não contém 'futbanner', mas continuando...")

def debug_pagina_futebol(driver):
    """Debug da página de futebol para entender a estrutura"""
    print("🔍 ANALISANDO PÁGINA DE FUTEBOL:")
    
    try:
        # Pega o conteúdo da página
        body_text = driver.find_element(By.TAG_NAME, "body").text
        print("📄 Conteúdo da página (primeiros 1000 chars):")
        print(f"   {body_text[:1000]}...")
        
        # Lista todos os botões
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"\n🔘 {len(buttons)} botões encontrados:")
        for i, btn in enumerate(buttons):
            text = btn.text.strip()[:50] or "sem texto"
            onclick = btn.get_attribute('onclick') or "sem onclick"
            class_attr = btn.get_attribute('class') or "sem class"
            print(f"   {i+1}. '{text}' - class='{class_attr}' onclick='{onclick[:50]}...'")
        
        # Lista selects/dropdowns
        selects = driver.find_elements(By.TAG_NAME, "select")
        print(f"\n📋 {len(selects)} selects encontrados:")
        for i, select in enumerate(selects):
            name = select.get_attribute('name') or "sem name"
            id_attr = select.get_attribute('id') or "sem id"
            options = select.find_elements(By.TAG_NAME, "option")
            print(f"   {i+1}. name='{name}' id='{id_attr}' - {len(options)} opções")
            for j, opt in enumerate(options[:5]):  # Primeiras 5 opções
                value = opt.get_attribute('value')
                text = opt.text.strip()
                print(f"      {j+1}. value='{value}' text='{text}'")
        
        # Lista inputs
        inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"\n📝 {len(inputs)} inputs encontrados:")
        for i, inp in enumerate(inputs):
            type_attr = inp.get_attribute('type')
            name = inp.get_attribute('name') or "sem name"
            value = inp.get_attribute('value') or "sem value"
            if type_attr in ['radio', 'checkbox']:
                print(f"   {i+1}. type='{type_attr}' name='{name}' value='{value}'")
        
        # Procura por texto relacionado a modelos
        if "modelo" in body_text.lower():
            print("\n🎨 Palavra 'modelo' encontrada na página!")
        if "2" in body_text:
            print("🔢 Número '2' encontrado na página!")
        if "hoje" in body_text.lower():
            print("📅 Palavra 'hoje' encontrada na página!")
        if "gerar" in body_text.lower():
            print("🔄 Palavra 'gerar' encontrada na página!")
        if "telegram" in body_text.lower():
            print("📤 Palavra 'telegram' encontrada na página!")
            
    except Exception as e:
        print(f"❌ Erro no debug: {e}")

def selecionar_opcoes_futebol(driver):
    print("🎨 Configurando opções de geração...")
    
    # Debug da página primeiro
    debug_pagina_futebol(driver)
    
    # Aguarda um pouco para garantir que carregou
    time.sleep(2)
    
    # Estratégias para selecionar Modelo 2
    print("\n🎨 Tentando selecionar Modelo 2...")
    modelo_selecionado = False
    
    estrategias_modelo = [
        # Radio buttons
        "//input[@type='radio' and @value='2']",
        "//input[@type='radio' and contains(@name, 'modelo') and @value='2']",
        "//input[@type='radio'][2]",  # Segundo radio button
        
        # Select dropdown
        "//select//option[@value='2']",
        "//select//option[contains(text(), '2')]",
        "//select//option[contains(text(), 'Modelo 2')]",
        
        # Buttons ou divs clicáveis
        "//button[contains(text(), '2')]",
        "//div[contains(text(), 'Modelo 2')]",
        "//label[contains(text(), 'Modelo 2')]",
    ]
    
    for i, strategy in enumerate(estrategias_modelo):
        try:
            print(f"🔍 Estratégia {i+1}: {strategy}")
            elemento = driver.find_element(By.XPATH, strategy)
            
            if elemento.tag_name == "option":
                # Se for option, seleciona no dropdown
                select = elemento.find_element(By.XPATH, "./..")
                select.click()
                elemento.click()
            else:
                # Se for outro tipo, só clica
                elemento.click()
            
            modelo_selecionado = True
            print("✅ Modelo 2 selecionado!")
            break
            
        except Exception as e:
            print(f"   ❌ Falhou: {str(e)[:50]}")
            continue
    
    if not modelo_selecionado:
        print("⚠️ Modelo 2 não encontrado, continuando sem seleção...")
    
    time.sleep(1)
    
    # Estratégias para selecionar "Hoje" / "Dia atual"
    print("\n📅 Tentando selecionar jogos de hoje...")
    dia_selecionado = False
    
    estrategias_dia = [
        # Radio buttons
        "//input[@type='radio' and contains(@value, 'hoje')]",
        "//input[@type='radio' and contains(@value, 'today')]",
        "//input[@type='radio'][1]",  # Primeiro radio button (pode ser "hoje")
        
        # Select dropdown
        "//select//option[contains(text(), 'Hoje')]",
        "//select//option[contains(text(), 'hoje')]",
        "//select//option[contains(text(), 'Dia')]",
        
        # Buttons
        "//button[contains(text(), 'Hoje')]",
        "//button[contains(text(), 'hoje')]",
    ]
    
    for i, strategy in enumerate(estrategias_dia):
        try:
            print(f"🔍 Estratégia {i+1}: {strategy}")
            elemento = driver.find_element(By.XPATH, strategy)
            
            if elemento.tag_name == "option":
                select = elemento.find_element(By.XPATH, "./..")
                select.click()
                elemento.click()
            else:
                elemento.click()
            
            dia_selecionado = True
            print("✅ Jogos de hoje selecionados!")
            break
            
        except Exception as e:
            print(f"   ❌ Falhou: {str(e)[:50]}")
            continue
    
    if not dia_selecionado:
        print("⚠️ Seleção de 'hoje' não encontrada, continuando...")
    
    time.sleep(1)

def gerar_banners(driver):
    print("🔄 Procurando botão Gerar...")
    
    # Múltiplas estratégias para encontrar o botão gerar
    estrategias_gerar = [
        "//button[contains(text(), 'Gerar')]",
        "//input[@type='submit' and contains(@value, 'Gerar')]",
        "//button[@type='submit']",
        "//input[@type='submit']",
        "//button[contains(text(), 'GERAR')]",
        "//div[contains(text(), 'Gerar') and @onclick]",
        "//a[contains(text(), 'Gerar')]",
    ]
    
    botao_clicado = False
    for i, strategy in enumerate(estrategias_gerar):
        try:
            print(f"🔍 Tentativa {i+1}: {strategy}")
            botao = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, strategy))
            )
            botao.click()
            botao_clicado = True
            print("✅ Botão Gerar clicado!")
            break
            
        except Exception as e:
            print(f"   ❌ Falhou: {str(e)[:50]}")
            continue
    
    if not botao_clicado:
        raise Exception("Botão Gerar não encontrado!")
    
    print("⏳ Aguardando geração dos banners...")
    # Aguarda um tempo para a geração começar
    time.sleep(10)

def aguardar_e_enviar_telegram(driver):
    print("📤 Procurando próximos passos após geração...")
    
    # Primeiro, aguarda um pouco para ver se aparece algo
    time.sleep(5)
    
    # Verifica se apareceu seleção de cores ou outras opções
    print("🎨 Verificando se apareceram opções de cores...")
    
    opcoes_cores = [
        "//button[contains(@style, 'background') or contains(@class, 'cor')]",
        "//div[contains(@class, 'cor') or contains(@class, 'color')]", 
        "//button[contains(text(), 'Cor') or contains(text(), 'cor')]",
        "//div[contains(text(), 'Escolha') and contains(text(), 'cor')]",
        "//input[@type='radio' and contains(@name, 'cor')]",
        "//select[contains(@name, 'cor') or contains(@id, 'cor')]",
        "//button[contains(@onclick, 'cor')]"
    ]
    
    cor_selecionada = False
    for i, strategy in enumerate(opcoes_cores):
        try:
            print(f"🔍 Procurando cores - estratégia {i+1}")
            elementos_cor = driver.find_elements(By.XPATH, strategy)
            if elementos_cor:
                print(f"✅ Encontrou {len(elementos_cor)} opções de cor!")
                # Clica na primeira cor disponível (geralmente padrão)
                elementos_cor[0].click()
                cor_selecionada = True
                print("✅ Cor selecionada (primeira opção)")
                time.sleep(2)
                break
        except:
            continue
    
    if not cor_selecionada:
        print("⚠️ Nenhuma seleção de cor encontrada")
    
    # Procura por botões de confirmação/continuar após seleção de cor
    print("🔄 Procurando botão de confirmação...")
    
    botoes_confirmacao = [
        "//button[contains(text(), 'Confirmar')]",
        "//button[contains(text(), 'Continuar')]", 
        "//button[contains(text(), 'Avançar')]",
        "//button[contains(text(), 'Próximo')]",
        "//button[contains(text(), 'OK')]",
        "//input[@type='submit']",
        "//button[@type='submit']"
    ]
    
    confirmacao_clicada = False
    for i, strategy in enumerate(botoes_confirmacao):
        try:
            print(f"🔍 Procurando confirmação - estratégia {i+1}")
            botao = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, strategy))
            )
            botao.click()
            confirmacao_clicada = True
            print("✅ Botão de confirmação clicado!")
            time.sleep(3)
            break
        except:
            continue
    
    if not confirmacao_clicada:
        print("⚠️ Nenhum botão de confirmação encontrado")
    
    # Agora procura pelo botão de envio para Telegram
    print("📤 Procurando botão de envio para Telegram...")
    
    max_tentativas = 20  # Reduzido para 20 tentativas (1min 40s)
    
    estrategias_enviar = [
        "//button[contains(text(), 'Enviar')]",
        "//button[contains(text(), 'Telegram')]",
        "//button[contains(text(), 'ENVIAR')]",
        "//input[@type='button' and contains(@value, 'Enviar')]",
        "//a[contains(text(), 'Enviar')]",
        "//div[contains(text(), 'Enviar') and @onclick]",
        "//button[contains(@onclick, 'telegram')]",
        "//button[contains(text(), 'Finalizar')]",
        "//button[contains(text(), 'Concluir')]"
    ]
    
    for tentativa in range(max_tentativas):
        print(f"⏳ Tentativa {tentativa + 1}/{max_tentativas} - Procurando botão enviar...")
        
        # Debug: mostra o que tem na página atual
        if tentativa % 5 == 0:  # A cada 5 tentativas, mostra debug
            try:
                body_text = driver.find_element(By.TAG_NAME, "body").text
                print(f"📄 Debug da página atual: {body_text[:200]}...")
                
                # Lista botões visíveis
                buttons = driver.find_elements(By.TAG_NAME, "button")
                if buttons:
                    print(f"🔘 {len(buttons)} botões na página:")
                    for i, btn in enumerate(buttons[:3]):
                        text = btn.text.strip()[:30] or "sem texto"
                        print(f"   {i+1}. '{text}'")
            except:
                pass
        
        for i, strategy in enumerate(estrategias_enviar):
            try:
                botao_enviar = driver.find_element(By.XPATH, strategy)
                if botao_enviar.is_displayed() and botao_enviar.is_enabled():
                    botao_enviar.click()
                    print("✅ Botão enviar clicado!")
                    time.sleep(5)
                    print("🎉 BANNERS ENVIADOS PARA O TELEGRAM!")
                    return True
            except:
                continue
        
        time.sleep(5)
    
    print("⚠️ Botão de enviar não apareceu após as tentativas")
    print("💡 Verificando se apareceu algum link ou mensagem de sucesso...")
    
    # Verifica se apareceu alguma mensagem de sucesso
    try:
        body_text = driver.find_element(By.TAG_NAME, "body").text
        print(f"📄 Conteúdo final da página: {body_text[:500]}...")
        
        if any(palavra in body_text.lower() for palavra in ['sucesso', 'enviado', 'concluído', 'finalizado', 'pronto', 'gerado']):
            print("✅ Possível sucesso detectado no texto da página!")
            return True
        
        # Se não encontrou sucesso, lista todos os botões para debug
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"🔘 Botões disponíveis na página final ({len(buttons)}):")
        for i, btn in enumerate(buttons):
            text = btn.text.strip() or "sem texto"
            onclick = btn.get_attribute('onclick') or "sem onclick"
            print(f"   {i+1}. '{text}' - onclick: {onclick[:50]}")
            
    except:
        pass
    
    return False

def main():
    print("🚀 INICIANDO AUTOMAÇÃO COMPLETA - GERADOR PRO")
    print(f"⏰ Horário: {time.strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Pega credenciais
    login = os.environ.get("LOGIN")
    senha = os.environ.get("SENHA")
    
    if not login or not senha:
        print("❌ Credenciais não encontradas!")
        return
    
    print(f"🔑 Login: {login}")
    
    driver = setup_driver()
    try:
        # Fluxo completo
        fazer_login(driver, login, senha)
        ir_gerar_futebol(driver)
        selecionar_opcoes_futebol(driver)
        gerar_banners(driver)
        
        sucesso_envio = aguardar_e_enviar_telegram(driver)
        
        if sucesso_envio:
            print("🎉 AUTOMAÇÃO CONCLUÍDA COM SUCESSO!")
            print("🔔 Verifique seu canal no Telegram para os banners!")
        else:
            print("⚠️ Geração pode ter sido concluída, mas envio automático falhou")
            print("💡 Verifique manualmente se os banners estão disponíveis no site")
        
        print(f"📍 URL final: {driver.current_url}")
        
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        print(f"📍 URL atual: {driver.current_url}")
        
        # Debug da página atual em caso de erro
        try:
            body_text = driver.find_element(By.TAG_NAME, "body").text
            print(f"📄 Conteúdo da página atual: {body_text[:500]}...")
        except:
            pass
        
        raise e
        
    finally:
        driver.quit()
        print("🔒 Navegador fechado")

if __name__ == "__main__":
    main()
