def fazer_login_selenium(driver, login, senha, tentativas=2):
    for tentativa in range(1, tentativas + 1):
        try:
            print(f"🔁 Tentativa de login {tentativa}/{tentativas}")
            driver.get(LOGIN_URL)

            # 🔹 Espera total aumentada
            time.sleep(3)
            wait = WebDriverWait(driver, 20)

            # 🔹 Procura o campo de usuário por várias formas (ID, NAME, placeholder)
            try:
                user = wait.until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "//input[@id='username' or @name='username' or contains(@placeholder, 'usuário')]",
                        )
                    )
                )
            except TimeoutException:
                raise Exception("Campo de usuário não encontrado na página de login.")

            # 🔹 Procura o campo de senha
            try:
                pwd = wait.until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "//input[@id='password' or @name='password' or contains(@placeholder, 'senha')]",
                        )
                    )
                )
            except TimeoutException:
                raise Exception("Campo de senha não encontrado na página de login.")

            # 🔹 Procura o botão de login
            try:
                btn = wait.until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            "//button[contains(., 'Entrar') or contains(@class, 'btn-login')]",
                        )
                    )
                )
            except TimeoutException:
                raise Exception("Botão 'Entrar no Painel' não encontrado.")

            # 🔹 Preenche login e senha
            user.clear()
            user.send_keys(login)
            time.sleep(0.5)
            pwd.clear()
            pwd.send_keys(senha)
            time.sleep(0.5)

            # 🔹 Clica via JavaScript (evita bloqueio do Selenium)
            driver.execute_script("arguments[0].click();", btn)
            print("🖱️ Clique no botão 'Entrar' realizado.")

            # 🔹 Aguarda redirecionamento pro painel
            try:
                WebDriverWait(driver, 15).until(
                    lambda d: (
                        "painel" in d.current_url.lower()
                        or "dashboard" in d.current_url.lower()
                        or "futbanner" in d.current_url.lower()
                    )
                )
                print("✅ Login realizado com sucesso!")
                return True
            except TimeoutException:
                print("⚠️ Falha no redirecionamento após clique. Tentando verificar mensagens de erro...")

                # 🔹 Verifica se há alerta de erro visível
                try:
                    erro = driver.find_element(By.CSS_SELECTOR, ".alert, .erro, .text-danger").text
                    print("📛 Mensagem de erro detectada:", erro)
                    return False
                except NoSuchElementException:
                    print("⚠️ Nenhuma mensagem visível — possível bloqueio do site.")
                    time.sleep(2 + tentativa)
                    continue

        except Exception as e:
            print(f"❌ Exceção durante login: {e}")
            traceback.print_exc()
            time.sleep(3)
            continue

    # Se todas as tentativas falharem
    print("❌ Falha no login após múltiplas tentativas.")
    return False
