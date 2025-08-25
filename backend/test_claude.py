import anthropic
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def test_claude_import():
    print("🧪 Prueba de importación de Anthropic")
    try:
        print(f"📦 Versión de anthropic: {anthropic.__version__}")
        print("✅ Importación exitosa")
        
        # Verificar métodos disponibles
        print("\n📊 Métodos disponibles en anthropic.Anthropic:")
        client = anthropic.Anthropic(api_key="test_key_not_used")
        print(f"- Métodos: {dir(client)}")
        print(f"- Atributos: {client.__dict__}")
        
        return True
    except Exception as e:
        print(f"❌ Error importando anthropic: {str(e)}")
        return False

def test_claude_api():
    print("\n🧪 Prueba de API de Claude")
    api_key = os.getenv("CLAUDE_API_KEY")
    
    if not api_key:
        print("❌ No se encontró CLAUDE_API_KEY en las variables de entorno")
        return False
        
    try:
        print(f"🔑 Usando API key: {api_key[:10]}...")
        client = anthropic.Anthropic(api_key=api_key)
        
        # Verificar que la inicialización fue exitosa
        print(f"✅ Cliente inicializado: {client}")
        
        # Prueba básica (sin hacer llamada real)
        print("✅ Cliente de API creado exitosamente")
        return True
    except Exception as e:
        print(f"❌ Error creando cliente de Claude: {str(e)}")
        return False

if __name__ == "__main__":
    import_result = test_claude_import()
    api_result = test_claude_api()
    
    if import_result and api_result:
        print("\n✅ Todas las pruebas exitosas. La biblioteca anthropic está funcionando correctamente.")
    else:
        print("\n❌ Algunas pruebas fallaron. Revisa los errores anteriores.")
