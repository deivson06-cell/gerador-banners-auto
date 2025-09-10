import os, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def setup():
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox") 
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=opts)

def tentar_cliques(driver, seletores, nome_acao):
    """Tenta vários seletores até encontrar um que funcione"""
    for i, seletor in enumerate(seletores):
        try:
            print(f"🔍 Tentando {nome_acao} - opção {i+1}")
            element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, seletor)))
            element.click()
            print(f"✅ {nome_acao} - sucesso!")
            return True
        except:
            continue
    return False

def main():
    login = os.environ["LOGIN"]
    senha = os.environ["SENHA"]
    
    driver = setup()
    try:
        print("🔑 Fazendo login...")
        driver.get("https://geradorpro.com/login")
        time.sleep(3)
        
        # Múltiplas opções para campo de email
        email_seletores = [
            "//input[@name='email']",
            "//input[@type='email']", 
            "//input[@placeholder='Email']",
            "//input[@id='email']",
            "//input[contains(@class, 'email')]"
        ]
        
        email_encontrado = False
        for seletor in email_seletores:
            try:
                campo_email = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, seletor)))
                campo_email.clear()
                campo_email.send_keys(login)
                print("✅ Campo email preenchido!")
                email_encontrado = True
                break
            except:
                continue
                
        if not email_encontrado:
            print("❌ Campo email não encontrado!")
            driver.save_screenshot("erro_email.png")
            return
        
        # Múltiplas opções para senha
