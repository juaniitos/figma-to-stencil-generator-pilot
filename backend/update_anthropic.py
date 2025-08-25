import subprocess
import sys

def update_anthropic():
    print("🔄 Actualizando biblioteca anthropic...")
    try:
        # Desinstalar versiones existentes
        subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", "anthropic"])
        print("✅ Versión anterior desinstalada")
        
        # Instalar la versión más reciente
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "anthropic"])
        print("✅ Versión más reciente instalada")
        
        # Verificar la versión instalada
        result = subprocess.check_output([sys.executable, "-m", "pip", "show", "anthropic"])
        print("\n📊 Información de la biblioteca:")
        print(result.decode("utf-8"))
        
        return True
    except Exception as e:
        print(f"❌ Error actualizando anthropic: {str(e)}")
        return False

if __name__ == "__main__":
    update_anthropic()
