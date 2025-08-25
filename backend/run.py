import uvicorn
import os
import sys
from dotenv import load_dotenv

# Configurar correctamente el PATH para importaciones
sys.path.append(os.path.abspath("."))
sys.path.append(os.path.abspath("backend"))

# Cargar variables de entorno
try:
    load_dotenv()
    print("✅ Variables de entorno cargadas correctamente")
except Exception as e:
    print(f"⚠️ Error cargando .env: {e}")
    print("⚠️ Usando variables de entorno predeterminadas")

# Validar token de Figma
figma_token = os.getenv("FIGMA_ACCESS_TOKEN")
if figma_token:
    print(f"✅ Token de Figma configurado: {figma_token[:10]}...")
else:
    print("❌ Token de Figma no configurado")

# Configuración del servidor
host = "0.0.0.0"
port = int(os.getenv("PORT", "8000"))

# Imprimir información útil
print("\n🚀 Iniciando Figma to Stencil Generator...")
print(f"📱 Servidor: http://localhost:{port}")
print(f"📚 Documentación: http://localhost:{port}/docs")

# URLs útiles para probar
print("\n📋 URLs útiles:")
print(f"✅ Test conexión Figma: http://localhost:{port}/test/figma")
print(f"🏢 Test equipos: http://localhost:{port}/test/teams")
print(f"🏢 Todos los equipos: http://localhost:{port}/test/all-teams")
print(f"📂 Test equipo específico: http://localhost:{port}/test/specific-team/1507023165279092081")

if __name__ == "__main__":
    print("\n🔄 Iniciando servidor con recarga automática...")
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
