import os

print(" Configurando variables directamente...")

# Configurar variables directamente (usar con fines de prueba)
os.environ['FIGMA_ACCESS_TOKEN'] = 'your_figma_access_token_here'
os.environ['CLAUDE_API_KEY'] = 'your_claude_api_key_here'
os.environ['PORT'] = '8000'

figma_token = os.getenv("FIGMA_ACCESS_TOKEN")
claude_key = os.getenv("CLAUDE_API_KEY")
port = os.getenv("PORT")

print(f" FIGMA_ACCESS_TOKEN: {figma_token[:20] if figma_token else 'None'}...")
print(f" CLAUDE_API_KEY: {claude_key[:20] if claude_key else 'None'}...")
print(f" PORT: {port}")

print(f" Figma configurado: {bool(figma_token and figma_token != 'your_figma_token_here')}")
print(f" Claude configurado: {bool(claude_key and claude_key != 'your_claude_api_key_here')}")
