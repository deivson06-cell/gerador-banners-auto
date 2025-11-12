"""
EXTRATOR DE COOKIES - Execute localmente no seu computador

INSTRUÇÕES:
1. Instale: pip install browser-cookie3
2. Faça login manualmente no gerador.pro no Chrome
3. FECHE o Chrome completamente
4. Execute este script: python extrair_cookies.py
5. Copie o JSON que aparecer
6. Adicione como secret COOKIES no GitHub Actions
"""

import json

def extrair_cookies_chrome():
    """Extrai cookies do Chrome para o domínio gerador.pro"""
    try:
        import browser_cookie3
        
        print("🔍 Procurando cookies do gerador.pro no Chrome...")
        cookies = browser_cookie3.chrome(domain_name='gerador.pro')
        cookies_dict = {}
        
        for cookie in cookies:
            cookies_dict[cookie.name] = cookie.value
        
        if not cookies_dict:
            print("❌ Nenhum cookie encontrado!")
            print("\nVerifique se:")
            print("1. Você fez login no gerador.pro no Chrome")
            print("2. O Chrome está COMPLETAMENTE FECHADO")
            print("3. Você está usando Windows/Mac/Linux (não WSL)")
            return None
        
        print(f"✅ {len(cookies_dict)} cookies encontrados!")
        print("\n" + "="*70)
        print("COPIE TODO O CONTEÚDO ABAIXO (incluindo as chaves):")
        print("="*70)
        print(json.dumps(cookies_dict, indent=2))
        print("="*70)
        print("\n📝 PRÓXIMOS PASSOS:")
        print("1. Copie TUDO que está entre as linhas acima")
        print("2. Vá para: https://github.com/SEU_USUARIO/SEU_REPO/settings/secrets/actions")
        print("3. Clique em 'New repository secret'")
        print("4. Name: COOKIES")
        print("5. Value: Cole o JSON copiado")
        print("6. Clique em 'Add secret'")
        print("7. Execute o workflow novamente")
        
        return cookies_dict
        
    except ImportError:
        print("❌ Biblioteca browser-cookie3 não instalada!")
        print("\nExecute: pip install browser-cookie3")
        return None
    except Exception as e:
        print(f"❌ Erro ao extrair cookies: {e}")
        print("\nCertifique-se de que:")
        print("1. Você está logado no gerador.pro no Chrome")
        print("2. O Chrome está COMPLETAMENTE FECHADO")
        print("3. Você tem permissões para ler os dados do Chrome")
        return None

def extrair_cookies_firefox():
    """Alternativa: extrai do Firefox"""
    try:
        import browser_cookie3
        
        print("🔍 Procurando cookies do gerador.pro no Firefox...")
        cookies = browser_cookie3.firefox(domain_name='gerador.pro')
        cookies_dict = {}
        
        for cookie in cookies:
            cookies_dict[cookie.name] = cookie.value
        
        if not cookies_dict:
            print("❌ Nenhum cookie encontrado no Firefox!")
            return None
        
        print(f"✅ {len(cookies_dict)} cookies encontrados!")
        print("\n" + "="*70)
        print("COPIE TODO O CONTEÚDO ABAIXO:")
        print("="*70)
        print(json.dumps(cookies_dict, indent=2))
        print("="*70)
        
        return cookies_dict
        
    except Exception as e:
        print(f"⚠️ Erro no Firefox: {e}")
        return None

if __name__ == "__main__":
    print("=" * 70)
    print("🍪 EXTRATOR DE COOKIES - GERADOR.PRO")
    print("=" * 70)
    print()
    
    # Tenta Chrome primeiro
    resultado = extrair_cookies_chrome()
    
    # Se falhar, oferece Firefox
    if not resultado:
        print("\n" + "="*70)
        resposta = input("Tentar extrair do Firefox? (s/n): ").lower()
        if resposta == 's':
            extrair_cookies_firefox()
    
    print("\n" + "="*70)
    print("✅ Processo concluído!")
    print("=" * 70)
"""
EXTRATOR DE COOKIES - Execute localmente no seu computador

1. Faça login manualmente no gerador.pro no Chrome
2. Execute este script
3. Copie os cookies e adicione como secret no GitHub Actions
"""

import json
import browser_cookie3

def extrair_cookies_chrome():
    """Extrai cookies do Chrome para o domínio gerador.pro"""
    try:
        cookies = browser_cookie3.chrome(domain_name='gerador.pro')
        cookies_dict = {}
        
        for cookie in cookies:
            cookies_dict[cookie.name] = cookie.value
        
        print("🍪 Cookies extraídos com sucesso!")
        print("\n" + "="*60)
        print("COPIE ESTE JSON E ADICIONE COMO SECRET 'COOKIES' NO GITHUB:")
        print("="*60)
        print(json.dumps(cookies_dict, indent=2))
        print("="*60)
        
        return cookies_dict
        
    except Exception as e:
        print(f"❌ Erro ao extrair cookies: {e}")
        print("\nCertifique-se de que:")
        print("1. Você está logado no gerador.pro no Chrome")
        print("2. O Chrome está fechado")
        print("3. Instalou: pip install browser-cookie3")
        return None

if __name__ == "__main__":
    extrair_cookies_chrome()
