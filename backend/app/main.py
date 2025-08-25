from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import aiohttp  # Añadir esta importación

# Cargar variables de entorno
# Por seguridad, las claves API ahora se cargan desde variables de entorno
# o del archivo .env
# Ver .env.example para el formato
os.environ['PORT'] = '8000'
# Para especificar un modelo de Claude personalizado, descomenta la siguiente línea:
# os.environ['CLAUDE_MODEL'] = 'claude-3-sonnet-20240229'  # Alternativas: claude-3-haiku-20240307

# DEBUG: Imprimir variables al inicio
print("🔍 DEBUG - Variables configuradas:")
figma_token = os.getenv("FIGMA_ACCESS_TOKEN")
claude_key = os.getenv("CLAUDE_API_KEY")
print(f"🎨 FIGMA_ACCESS_TOKEN: {figma_token[:20] if figma_token else 'None'}...")
print(f"🤖 CLAUDE_API_KEY: {claude_key[:20] if claude_key else 'None'}...")

app = FastAPI(title="Figma to Stencil Generator", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos de datos
class HealthResponse(BaseModel):
    status: str
    figma_configured: bool
    claude_configured: bool
    message: str
    timestamp: str

@app.get("/")
async def root():
    return {
        "message": "🎨 Figma to Stencil Generator API", 
        "status": "running", 
        "user": "cleodisenobg",
        "timestamp": "2025-08-16 06:54:39"
    }

@app.get("/debug/env")
async def debug_env():
    # Endpoint para debug de variables de entorno
    figma_token = os.getenv("FIGMA_ACCESS_TOKEN")
    claude_key = os.getenv("CLAUDE_API_KEY")
    
    return {
        "figma_token_exists": bool(figma_token),
        "figma_token_preview": figma_token[:20] + "..." if figma_token else None,
        "claude_key_exists": bool(claude_key),
        "claude_key_preview": claude_key[:20] + "..." if claude_key else None,
        "figma_configured": bool(figma_token and figma_token != "your_figma_token_here"),
        "claude_configured": bool(claude_key and claude_key != "your_claude_api_key_here"),
        "timestamp": "2025-08-16 06:54:39"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    # Verificar estado de configuracion
    figma_token = os.getenv("FIGMA_ACCESS_TOKEN")
    claude_key = os.getenv("CLAUDE_API_KEY")
    
    return HealthResponse(
        status="ok",
        figma_configured=bool(figma_token and figma_token != "your_figma_token_here"),
        claude_configured=bool(claude_key and claude_key != "your_claude_api_key_here"),
        message="API funcionando correctamente",
        timestamp="2025-08-16 06:54:39"
    )

@app.get("/test/figma")
async def test_figma():
    # Probar conexion con Figma
    try:
        from app.figma.client import FigmaClient
        
        figma_token = os.getenv("FIGMA_ACCESS_TOKEN")
        print(f"🔍 Token en endpoint: {figma_token[:20] if figma_token else 'None'}...")
        
        if not figma_token or figma_token == "your_figma_token_here":
            raise HTTPException(status_code=500, detail="❌ Token de Figma requerido")
        
        figma_client = FigmaClient(figma_token)
        result = await figma_client.test_connection()
        
        if result["success"]:
            return {
                "status": "success", 
                "message": "✅ Conexión exitosa con Figma",
                "data": result,
                "timestamp": "2025-08-16 06:54:39"
            }
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/figma/access")
async def get_figma_access():
    # Obtener acceso a archivos (archivos recientes + teams si existen)
    try:
        from app.figma.client import FigmaClient
        
        figma_token = os.getenv("FIGMA_ACCESS_TOKEN")
        if not figma_token:
            raise HTTPException(status_code=500, detail="❌ Token de Figma requerido")
        
        figma_client = FigmaClient(figma_token)
        access_items = await figma_client.get_teams()  # Ahora retorna archivos recientes + teams
        
        return {
            "status": "success",
            "data": access_items,
            "count": len(access_items),
            "timestamp": "2025-08-16 06:54:39"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/figma/access/{item_id}/files")
async def get_access_files(item_id: str, item_type: str = "recent_files"):
    # Obtener archivos de un elemento de acceso (archivos recientes o team)
    try:
        from app.figma.client import FigmaClient
        
        figma_token = os.getenv("FIGMA_ACCESS_TOKEN")
        if not figma_token:
            raise HTTPException(status_code=500, detail="❌ Token de Figma requerido")
        
        figma_client = FigmaClient(figma_token)
        files = await figma_client.get_files_from_access_item(item_id, item_type)
        
        return {
            "status": "success",
            "item_id": item_id,
            "item_type": item_type,
            "data": files,
            "count": len(files),
            "timestamp": "2025-08-16 06:54:39"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Mantener endpoints anteriores para compatibilidad
@app.get("/figma/teams")
async def get_figma_teams():
    # Redirigir al nuevo endpoint
    return await get_figma_access()

@app.get("/figma/teams/{team_id}/projects")
async def get_team_projects(team_id: str):
    # Obtener proyectos de un team especifico
    try:
        from app.figma.client import FigmaClient
        
        figma_token = os.getenv("FIGMA_ACCESS_TOKEN")
        if not figma_token:
            raise HTTPException(status_code=500, detail="❌ Token de Figma requerido")
        
        figma_client = FigmaClient(figma_token)
        projects = await figma_client.get_team_projects(team_id)
        
        return {
            "status": "success",
            "team_id": team_id,
            "data": projects,
            "count": len(projects),
            "timestamp": "2025-08-16 06:54:39"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/figma/projects/{project_id}/files")
async def get_project_files(project_id: str):
    # Obtener archivos de un proyecto especifico
    try:
        from app.figma.client import FigmaClient
        
        figma_token = os.getenv("FIGMA_ACCESS_TOKEN")
        if not figma_token:
            raise HTTPException(status_code=500, detail="❌ Token de Figma requerido")
        
        figma_client = FigmaClient(figma_token)
        files = await figma_client.get_project_files(project_id)
        
        return {
            "status": "success",
            "project_id": project_id,
            "data": files,
            "count": len(files),
            "timestamp": "2025-08-16 06:54:39"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/figma/files/{file_key}/structure")
async def get_file_structure(file_key: str):
    # Obtener estructura de un archivo (paginas y frames)
    try:
        from app.figma.client import FigmaClient
        
        figma_token = os.getenv("FIGMA_ACCESS_TOKEN")
        if not figma_token:
            raise HTTPException(status_code=500, detail="❌ Token de Figma requerido")
        
        figma_client = FigmaClient(figma_token)
        structure = await figma_client.get_file_structure(file_key)
        
        if structure["success"]:
            return {
                "status": "success",
                "data": structure,
                "timestamp": "2025-08-16 06:54:39"
            }
        else:
            raise HTTPException(status_code=500, detail=structure["error"])
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/figma/files/{file_key}/components")
async def get_file_components_and_styles(file_key: str):
    # Obtener componentes y estilos de un archivo
    try:
        from app.figma.client import FigmaClient
        
        figma_token = os.getenv("FIGMA_ACCESS_TOKEN")
        if not figma_token:
            raise HTTPException(status_code=500, detail="❌ Token de Figma requerido")
        
        figma_client = FigmaClient(figma_token)
        result = await figma_client.get_file_components_and_styles(file_key)
        
        if result.get("success", False):
            return {
                "status": "success",
                "data": result,
                "timestamp": "2025-08-16 06:54:39"
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Error desconocido"))
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
        
@app.get("/figma/files/{file_key}/components-with-thumbnails")
async def get_components_with_thumbnails(file_key: str):
    # Obtener componentes con imágenes de vista previa
    try:
        from app.figma.client import FigmaClient
        
        figma_token = os.getenv("FIGMA_ACCESS_TOKEN")
        if not figma_token:
            raise HTTPException(status_code=500, detail="❌ Token de Figma requerido")
        
        figma_client = FigmaClient(figma_token)
        result = await figma_client.get_components_with_thumbnails(file_key)
        
        if result.get("success", False):
            return {
                "status": "success",
                "data": result,
                "components": result.get("components", []),
                "component_groups": result.get("component_groups", {}),
                "total_count": result.get("total_count", 0),
                "timestamp": "2025-08-16 06:54:39"
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Error desconocido"))
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/figma/analyze")
async def analyze_figma_file(file_data: dict):
    # Analizar archivo de Figma
    try:
        from app.figma.client import FigmaClient
        
        figma_client = FigmaClient(os.getenv("FIGMA_ACCESS_TOKEN"))
        file_key = file_data.get("file_key")
        
        if not file_key:
            raise HTTPException(status_code=400, detail="file_key requerido")
        
        result = await figma_client.analyze_file_structure(file_key)
        
        if result["success"]:
            return {"status": "success", "data": result}
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Informacion del desarrollador
@app.get("/info")
async def info():
    return {
        "project": "Figma to Stencil Generator",
        "developer": "cleodisenobg",
        "date": "2025-08-16 06:54:39",
        "version": "1.0.0",
        "status": "Development"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print("🚀 Iniciando Figma to Stencil Generator...")
    print(f"📱 Servidor: http://localhost:{port}")
    print(f"📚 Documentación: http://localhost:{port}/docs")
    print(f"👤 Usuario: cleodisenobg")
    print(f"📅 Fecha: 2025-08-16 06:54:39")
    print("🔄 Manteniendo servidor activo... (Ctrl+C para salir)")
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)

@app.post("/figma/file-direct")
async def analyze_file_direct(request_data: dict):
    # Analizar archivo usando file_key directo
    try:
        from app.figma.client import FigmaClient
        
        figma_token = os.getenv("FIGMA_ACCESS_TOKEN")
        if not figma_token:
            raise HTTPException(status_code=500, detail="❌ Token de Figma requerido")
        
        file_key = request_data.get("file_key")
        file_url = request_data.get("file_url")
        
        # Si se proporciona URL, extraer file_key
        if file_url and not file_key:
            print(f"📝 Intentando extraer file_key de URL: {file_url}")
            
            # Intentar diferentes patrones de URL de Figma
            import re
            
            # Patron 1: URLs con /file/ - Ejemplo: https://www.figma.com/file/ABC123/nombre
            match_file = re.search(r'/file/([A-Za-z0-9]+)', file_url)
            
            # Patron 2: URLs con /design/ - Ejemplo: https://www.figma.com/design/ABC123/nombre
            match_design = re.search(r'/design/([A-Za-z0-9]+)', file_url)
            
            # Patron 3: URLs con ?node-id= - Ejemplo: https://www.figma.com/.../ABC123?node-id=...
            match_node = re.search(r'[/\?]([A-Za-z0-9]{22,})', file_url)
            
            if match_file:
                file_key = match_file.group(1)
                print(f"✅ file_key extraído del patrón /file/: {file_key}")
            elif match_design:
                file_key = match_design.group(1)
                print(f"✅ file_key extraído del patrón /design/: {file_key}")
            elif match_node:
                file_key = match_node.group(1)
                print(f"✅ file_key extraído del patrón de ID largo: {file_key}")
            else:
                raise HTTPException(status_code=400, detail=f"URL de Figma inválida: No se pudo extraer el file_key de '{file_url}'")
        
        if not file_key:
            raise HTTPException(status_code=400, detail="file_key o file_url requerido")
        
        print(f"🔍 Analizando archivo con file_key: {file_key}")
        figma_client = FigmaClient(figma_token)
        structure = await figma_client.get_file_structure(file_key)
        
        if structure["success"]:
            return {
                "status": "success",
                "data": structure,
                "timestamp": "2025-08-16 07:12:42"
            }
        else:
            print(f"❌ Error al obtener estructura: {structure['error']}")
            raise HTTPException(status_code=500, detail=structure["error"])
        
    except Exception as e:
        print(f"❌ Error en analyze_file_direct: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/test/teams")
async def test_teams():
    """Endpoint para probar la obtención de equipos y mostrar información detallada en consola"""
    try:
        from app.figma.client import FigmaClient
        
        figma_token = os.getenv("FIGMA_ACCESS_TOKEN")
        print("\n🔍 DEBUG - Probando obtención de equipos...")
        print(f"🎨 Token: {figma_token[:20] if figma_token else 'None'}...")
        
        if not figma_token or figma_token == "your_figma_token_here":
            raise HTTPException(status_code=500, detail="❌ Token de Figma requerido")
        
        figma_client = FigmaClient(figma_token)
        teams = await figma_client.get_teams()
        
        print("\n✅ Información de equipos obtenida con éxito")
        
        return {
            "status": "success", 
            "message": "✅ Información de equipos mostrada en consola",
            "data": teams,
            "count": len(teams),
            "timestamp": "2025-08-16 06:54:39"
        }
            
    except Exception as e:
        print(f"❌ Error obteniendo equipos: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/test/specific-team/{team_id}")
async def test_specific_team(team_id: str):
    """Endpoint para probar la obtención de un equipo específico por su ID"""
    try:
        from app.figma.client import FigmaClient
        
        figma_token = os.getenv("FIGMA_ACCESS_TOKEN")
        print(f"\n🔍 DEBUG - Probando obtención del equipo específico: {team_id}")
        
        if not figma_token or figma_token == "your_figma_token_here":
            raise HTTPException(status_code=500, detail="❌ Token de Figma requerido")
        
        figma_client = FigmaClient(figma_token)
        team_info = await figma_client.get_team_by_id(team_id)
        
        if team_info["success"]:
            return {
                "status": "success", 
                "message": f"✅ Información del equipo {team_id} mostrada en consola",
                "data": team_info,
                "timestamp": "2025-08-16 06:54:39"
            }
        else:
            raise HTTPException(status_code=500, detail=team_info["error"])
            
    except Exception as e:
        print(f"❌ Error obteniendo equipo específico: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/test/all-teams")
async def test_all_teams():
    """Endpoint para obtener TODOS los equipos a los que tiene acceso el usuario"""
    try:
        from app.figma.client import FigmaClient
        import json
        
        figma_token = os.getenv("FIGMA_ACCESS_TOKEN")
        print("\n🔍 DEBUG - Obteniendo TODOS los equipos disponibles...")
        print(f"🎨 Token: {figma_token[:20] if figma_token else 'None'}...")
        
        if not figma_token or figma_token == "your_figma_token_here":
            raise HTTPException(status_code=500, detail="❌ Token de Figma requerido")
        
        # Lista de IDs de equipos conocidos que queremos probar
        # Esta lista la podemos expandir con otros equipos que conocemos
        known_team_ids = [
            {"id": "1507023165279092081", "name": "Website"},
            {"id": "1097987766409007563", "name": "Cleo Design System"}, 
            {"id": "1245249892784512820", "name": "Cleo Design Initiatives"},
            {"id": "1180159344031449867", "name": "Cleo Digital Presence"},
            {"id": "1112173701821536588", "name": "Design Core Team"}
        ]
        
        # Verificar cuáles de estos equipos son accesibles
        figma_client = FigmaClient(figma_token)
        accessible_teams = []
        
        print("\n🔍 DEBUG - Verificando acceso a equipos conocidos...")
        for team in known_team_ids:
            try:
                team_info = await figma_client.check_team_access(team["id"])
                if team_info["accessible"]:
                    print(f"✅ Acceso confirmado a equipo: {team['name']} (ID: {team['id']})")
                    accessible_teams.append({
                        "id": team["id"],
                        "name": team_info.get("name", team["name"]),
                        "type": "team",
                        "description": f"Equipo verificado de Figma ({team['id']})"
                    })
                else:
                    print(f"❌ Sin acceso a equipo: {team['name']} (ID: {team['id']})")
            except Exception as e:
                print(f"❌ Error verificando equipo {team['id']}: {str(e)}")
        
        # Si no se encontró ningún equipo accesible, devolvemos al menos el equipo Website
        if not accessible_teams:
            print("❌ No se encontró ningún equipo accesible")
            specific_team_id = "1507023165279092081"
            print(f"📌 Devolviendo equipo manual ID: {specific_team_id}")
            return {
                "status": "success",
                "message": "Se encontró 1 equipo añadido manualmente",
                "data": [{
                    "id": specific_team_id,
                    "name": "Website Team",
                    "type": "team",
                    "description": "Equipo de Website (añadido manualmente)"
                }],
                "count": 1,
                "timestamp": "2025-08-16 06:54:39"
            }
        
        print(f"\n✅ Se encontraron {len(accessible_teams)} equipos accesibles")
        
        return {
            "status": "success", 
            "message": f"✅ Se encontraron {len(accessible_teams)} equipos accesibles",
            "data": accessible_teams,
            "count": len(accessible_teams),
            "timestamp": "2025-08-16 06:54:39"
        }
            
    except Exception as e:
        print(f"❌ Error obteniendo todos los equipos: {e}")
        return {
            "status": "error",
            "message": f"Error: {str(e)}",
            "data": [{
                "id": "1507023165279092081",
                "name": "Website Team (Error Fallback)",
                "type": "team",
                "description": f"Equipo fallback por error: {str(e)}"
            }],
            "count": 1,
            "timestamp": "2025-08-16 06:54:39"
        }

@app.get("/figma/files/{file_key}/details")
async def get_file_details(file_key: str):
    """Obtener detalles completos de un archivo de Figma"""
    try:
        from app.figma.client import FigmaClient
        
        figma_token = os.getenv("FIGMA_ACCESS_TOKEN")
        if not figma_token:
            raise HTTPException(status_code=500, detail="❌ Token de Figma requerido")
        
        figma_client = FigmaClient(figma_token)
        
        # Obtener la estructura completa del archivo
        structure = await figma_client.get_file_structure(file_key)
        
        if not structure["success"]:
            raise HTTPException(status_code=500, detail=structure["error"])
        
        # Enriquecer con más detalles si es necesario
        details = {
            "file_key": file_key,
            "file_name": structure.get("file_name", "Archivo sin nombre"),
            "last_modified": structure.get("last_modified", "Desconocido"),
            "pages": structure.get("pages", []),
            "version": structure.get("version", "Desconocido"),
            "components": [],  # Se llenará con componentes si existen
            "styles": []       # Se llenará con estilos si existen
        }
        
        # Obtener información adicional sobre componentes y estilos
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{figma_client.base_url}/files/{file_key}/components",
                    headers=figma_client.headers
                ) as response:
                    if response.status == 200:
                        components_data = await response.json()
                        details["components"] = components_data.get("meta", {}).get("components", [])
                
                async with session.get(
                    f"{figma_client.base_url}/files/{file_key}/styles",
                    headers=figma_client.headers
                ) as response:
                    if response.status == 200:
                        styles_data = await response.json()
                        details["styles"] = styles_data.get("meta", {}).get("styles", [])
        except Exception as e:
            print(f"⚠️ Error obteniendo detalles adicionales: {str(e)}")
        
        return {
            "status": "success",
            "data": details,
            "timestamp": "2025-08-16 07:54:39"
        }
        
    except Exception as e:
        print(f"❌ Error en get_file_details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/figma/generate-component")
async def generate_component(frame_data: dict):
    """Generar componente Stencil usando Claude AI a partir de datos de frame"""
    try:
        from app.figma.client import FigmaClient
        from app.claude.service import ClaudeAIService
        
        figma_token = os.getenv("FIGMA_ACCESS_TOKEN")
        claude_key = os.getenv("CLAUDE_API_KEY")
        
        if not figma_token:
            raise HTTPException(status_code=500, detail="❌ Token de Figma requerido")
        
        if not claude_key:
            raise HTTPException(status_code=500, detail="❌ API Key de Claude requerido")
        
        file_key = frame_data.get("file_key")
        frame_id = frame_data.get("frame_id")
        
        if not file_key or not frame_id:
            raise HTTPException(status_code=400, detail="file_key y frame_id son requeridos")
        
        # 1. Obtener detalles completos del frame
        figma_client = FigmaClient(figma_token)
        frame_details = await figma_client.get_frame_details(file_key, frame_id)
        
        if not frame_details.get("success"):
            raise HTTPException(status_code=500, detail=frame_details.get("error", "Error obteniendo detalles del frame"))
        
        print(f"✅ Detalles del frame obtenidos correctamente: {frame_details.get('frame', {}).get('name')}")
        
        # 2. Obtener componentes y estilos para design tokens
        comp_styles = await figma_client.get_file_components_and_styles(file_key)
        
        # Verificar versión de la librería anthropic
        try:
            import anthropic
            print(f"📦 Versión de anthropic: {anthropic.__version__}")
        except Exception as version_error:
            print(f"⚠️ No se pudo obtener la versión de anthropic: {str(version_error)}")
        
        # 3. Enviar a Claude para generar el componente
        try:
            print(f"🤖 Inicializando servicio Claude con API Key: {claude_key[:10]}...")
            claude_service = ClaudeAIService(claude_key)
            print(f"✅ Servicio Claude inicializado correctamente")
            
            # Verificar si hay un modelo específico a usar (opcional)
            if os.getenv("CLAUDE_MODEL"):
                claude_service.model = os.getenv("CLAUDE_MODEL")
                print(f"🔧 Usando modelo configurado manualmente: {claude_service.model}")
            
            print(f"🚀 Generando componente con Claude...")
            generation_result = await claude_service.generate_component_code(frame_details.get("frame"))
            
            if not generation_result.get("success"):
                error_msg = generation_result.get("error", "Error generando el código del componente")
                
                # Manejo especial para errores de límite de tasa
                if generation_result.get("rate_limited"):
                    print(f"⚠️ Límite de tasa de la API de Claude alcanzado: {error_msg}")
                    raise HTTPException(
                        status_code=429, 
                        detail="Se ha alcanzado el límite de solicitudes a la API de Claude. Por favor, espera unos minutos e inténtalo de nuevo."
                    )
                
                raise HTTPException(status_code=500, detail=error_msg)
            
            # Validar que al menos algunos bloques de código se generaron correctamente
            missing_blocks = []
            if not generation_result.get("html_code"):
                missing_blocks.append("HTML")
            if not generation_result.get("css_code"):
                missing_blocks.append("CSS")
            if not generation_result.get("stencil_code"):
                missing_blocks.append("Stencil Component (TSX)")
            
            if missing_blocks:
                warning_msg = f"⚠️ Atención: Los siguientes bloques de código no fueron generados: {', '.join(missing_blocks)}"
                print(warning_msg)
                # Añadir mensaje de advertencia, pero seguir procesando
                generation_result["warning"] = warning_msg
            
            # Asegurarnos de que la URL de la imagen esté incluida en la respuesta
            if "image_url" not in generation_result:
                generation_result["image_url"] = frame_details.get("frame", {}).get("image_url")
                
            return {
                "status": "success",
                "data": generation_result,
                "frame_name": frame_details.get("frame", {}).get("name"),
                "timestamp": "2025-08-16 08:30:45"
            }
        except HTTPException as http_err:
            # Propagar errores HTTP ya formateados
            raise http_err
        except Exception as claude_error:
            error_message = str(claude_error)
            print(f"❌ Error específico en el servicio Claude: {error_message}")
            
            # Manejo específico para diferentes tipos de errores
            if "rate_limit" in error_message.lower() or "429" in error_message:
                raise HTTPException(
                    status_code=429, 
                    detail="Se ha alcanzado el límite de solicitudes a la API de Claude. Por favor, espera unos minutos e inténtalo de nuevo."
                )
            elif "token" in error_message.lower() or "api key" in error_message.lower():
                raise HTTPException(status_code=401, detail="Error de autenticación con la API de Claude. Verifica tu API key.")
            else:
                raise HTTPException(status_code=500, detail=f"Error al generar el componente: {error_message}")
    except Exception as e:
        print(f"❌ Error general en generate-component: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error general: {str(e)}")


@app.post("/figma/generate-multiple-components")
async def generate_multiple_components(request_data: dict):
    """Endpoint para generar múltiples componentes a partir de sus node_ids"""
    try:
        # Importar clientes
        from app.figma.client import FigmaClient
        from app.claude.service import ClaudeAIService
        
        # Validar datos de entrada
        file_key = request_data.get("file_key")
        components = request_data.get("components", [])
        
        if not file_key:
            raise HTTPException(status_code=400, detail="Se requiere el file_key del archivo de Figma")
        
        if not components or not isinstance(components, list) or len(components) == 0:
            raise HTTPException(status_code=400, detail="Se requiere una lista de componentes para generar")
            
        # Inicializar clientes
        figma_client = FigmaClient(os.getenv("FIGMA_ACCESS_TOKEN"))
        claude_service = ClaudeAIService(os.getenv("CLAUDE_API_KEY"))
        
        # Verificar si hay un modelo específico a usar (opcional)
        if os.getenv("CLAUDE_MODEL"):
            claude_service.model = os.getenv("CLAUDE_MODEL")
            print(f"🔧 Usando modelo configurado manualmente: {claude_service.model}")
        
        results = []
        
        # Procesar cada componente
        for component in components:
            node_id = component.get("node_id")
            component_name = component.get("name", "Unknown Component")
            
            if not node_id:
                results.append({
                    "node_id": node_id,
                    "name": component_name,
                    "success": False,
                    "error": "ID del nodo no proporcionado"
                })
                continue
                
            try:
                print(f"\n🔍 Obteniendo detalles del componente {node_id} ({component_name})...")
                
                # Obtener detalles del componente usando la API de Figma
                component_details = await figma_client.get_frame_details(file_key, node_id)
                
                if not component_details.get("success", False):
                    results.append({
                        "node_id": node_id,
                        "name": component_name,
                        "success": False,
                        "error": component_details.get("error", "No se pudieron obtener los detalles del componente")
                    })
                    continue
                    
                # Generar el código con Claude AI
                print(f"🤖 Generando código para el componente {component_name}...")
                generation_result = await claude_service.generate_component_code(component_details.get("frame", {}))
                
                if not generation_result.get("success", False):
                    results.append({
                        "node_id": node_id,
                        "name": component_name,
                        "success": False,
                        "error": generation_result.get("error", "Error generando el código del componente"),
                        "rate_limited": generation_result.get("rate_limited", False)
                    })
                    continue
                
                # Verificar que todos los bloques de código se generaron
                missing_blocks = []
                if not generation_result.get("html_code"):
                    missing_blocks.append("HTML")
                if not generation_result.get("css_code"):
                    missing_blocks.append("CSS")
                if not generation_result.get("stencil_code"):
                    missing_blocks.append("Stencil Component (TSX)")
                
                # Si falta algún bloque, agregarlo como advertencia pero continuar
                warning = None
                if missing_blocks:
                    warning = f"Los siguientes bloques de código no fueron generados: {', '.join(missing_blocks)}"
                
                # Agregar resultado exitoso
                results.append({
                    "node_id": node_id,
                    "name": component_name,
                    "success": True,
                    "warning": warning,
                    "html_code": generation_result.get("html_code"),
                    "css_code": generation_result.get("css_code"),
                    "stencil_code": generation_result.get("stencil_code"),
                    "storybook_code": generation_result.get("storybook_code"),
                    "image_url": component_details.get("frame", {}).get("image_url"),
                    "props": generation_result.get("props"),
                    "component_name": generation_result.get("component_name")
                })
                
            except Exception as component_error:
                print(f"❌ Error procesando componente {component_name}: {str(component_error)}")
                results.append({
                    "node_id": node_id,
                    "name": component_name,
                    "success": False,
                    "error": str(component_error)
                })
        
        # Contar éxitos y errores
        success_count = len([r for r in results if r.get("success")])
        error_count = len(results) - success_count
        
        return {
            "status": "success",
            "total": len(results),
            "success_count": success_count,
            "error_count": error_count,
            "results": results,
            "timestamp": "2025-08-21 10:45:30"
        }
            
    except HTTPException as http_err:
        # Propagar errores HTTP ya formateados
        raise http_err
    except Exception as e:
        print(f"❌ Error en generate-multiple-components: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Proporcionar mensaje de error más amigable
        user_message = "Ha ocurrido un error al procesar tu solicitud. Por favor, intenta con un componente más simple o contacta al administrador."
        raise HTTPException(status_code=500, detail=f"Error al generar los componentes: {str(e)}")
