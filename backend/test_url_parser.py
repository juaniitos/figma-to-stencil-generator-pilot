import re
import sys

def parse_figma_url(url):
    """Parse Figma URLs to extract file_key"""
    print(f"Analizando URL: {url}")
    
    # Patron 1: URLs con /file/ - Ejemplo: https://www.figma.com/file/ABC123/nombre
    match_file = re.search(r'/file/([A-Za-z0-9]+)', url)
    
    # Patron 2: URLs con /design/ - Ejemplo: https://www.figma.com/design/ABC123/nombre
    match_design = re.search(r'/design/([A-Za-z0-9]+)', url)
    
    # Patron 3: URLs con ?node-id= o IDs largos - Ejemplo: https://www.figma.com/.../ABC123?node-id=...
    match_node = re.search(r'[/\?]([A-Za-z0-9]{22,})', url)
    
    if match_file:
        file_key = match_file.group(1)
        print(f"✅ file_key extraído del patrón /file/: {file_key}")
        return file_key
    elif match_design:
        file_key = match_design.group(1)
        print(f"✅ file_key extraído del patrón /design/: {file_key}")
        return file_key
    elif match_node:
        file_key = match_node.group(1)
        print(f"✅ file_key extraído del patrón de ID largo: {file_key}")
        return file_key
    else:
        print("❌ No se pudo extraer file_key")
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
        parse_figma_url(url)
    else:
        # Pruebas con URLs conocidas
        test_urls = [
            "https://www.figma.com/file/ABC123/FileName",
            "https://www.figma.com/design/b8nCEnaRdrICQ7QhH6wi2K/Cleo-DS---Components-Core?m=auto&fuid=1395458108668855529",
            "https://www.figma.com/proto/XYZ789/PrototypeFile?node-id=123%3A456",
            "https://www.figma.com/community/file/DEF456/CommunityFile"
        ]
        
        for url in test_urls:
            print("\n" + "-" * 50)
            parse_figma_url(url)
