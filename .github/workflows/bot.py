import os, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def setup():
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox") 
    opts.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(ChromeDriverManager().install(), options=opts)

def main():
    login = os.environ["LOGIN"]
    senha = os.environ["SENHA"]
    
    driver = setup()
    try:
        print("🔑 Fazendo login...")
        driver.get("https://geradorpro.com/login")
        
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email")))
        driver.find_element(By.NAME, "email").send_keys(login)
        driver.find_element(By.NAME, "password").send_keys(senha)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(3)
        
        print("⚽ Indo para Gerar Futebol...")
        driver.find_element(By.XPATH, "//a[contains(text(), 'Gerar Futebol')]").click()
        time.sleep(2)
        
        print("🎨 Selecionando Modelo 2...")
        driver.find_element(By.XPATH, "//div[contains(text(), 'Modelo 2')]").click()
        time.sleep(1)
        
        print("🏆 Gerando banners do dia...")
        driver.find_element(By.XPATH, "//button[contains(text(), 'Hoje')]").click()
        driver.find_element(By.XPATH, "//button[contains(text(), 'Gerar')]").click()
        
        print("⏳ Aguardando geração...")
        WebDriverWait(driver, 120).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Enviar')]")))
        
        print("📤 Enviando para Telegram...")
        driver.find_element(By.XPATH, "//button[contains(text(), 'Enviar')]").click()
        time.sleep(5)
        
        print("✅ Concluído! Banners enviados às", time.strftime('%H:%M'))
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
