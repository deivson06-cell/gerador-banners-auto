name: Envio Automático de Banners

on:
  schedule:
    # Executa todos os dias às 10:00 (horário de Brasília = 13:00 UTC)
    - cron: '0 13 * * *'
  
  # Permite executar manualmente pelo GitHub
  workflow_dispatch:

jobs:
  gerar-e-enviar-banners:
    runs-on: ubuntu-latest
    
    steps:
    - name: 📥 Checkout do código
      uses: actions/checkout@v4
    
    - name: 🐍 Configurar Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: 📦 Instalar dependências
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: 🔧 Instalar Google Chrome
      run: |
        wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
        sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
        sudo apt-get update
        sudo apt-get install -y google-chrome-stable
    
    - name: 🚀 Executar automação
      env:
        LOGIN: ${{ secrets.LOGIN }}
        SENHA: ${{ secrets.SENHA }}
      run: python main.py
    
    - name: 📤 Upload de screenshots (em caso de erro)
      if: failure()
      uses: actions/upload-artifact@v3
      with:
        name: prints-erro
        path: prints/
        retention-days: 7
