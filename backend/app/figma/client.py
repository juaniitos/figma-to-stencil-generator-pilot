import aiohttp
import asyncio
from typing import Dict, List, Optional, Any
import json

class FigmaClient:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://api.figma.com/v1"
        self.headers = {
            "X-Figma-Token": access_token,
            "Content-Type": "application/json"
        }

    async def test_connection(self) -> Dict[str, Any]:
        # Probar conexion con Figma
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/me", headers=self.headers) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        print("🔍 DEBUG - Respuesta completa de /me:")
                        print(user_data)
                        
                        return {
                            "success": True,
                            "user_email": user_data.get("email"),
                            "user_id": user_data.get("id"),
                            "user_handle": user_data.get("handle"),
                            "message": "Conexión exitosa. Usa URLs directas de archivos de Figma.",
                            "raw_data": user_data
                        }
                    else:
                        error_data = await response.text()
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_data}"
                        }
        except Exception as e:
            return {
                "success": False,
                "error": f"Connection failed: {str(e)}"
            }

    async def get_teams(self) -> List[Dict[str, Any]]:
        # Obtener equipos y crear opciones de acceso
        try:
            async with aiohttp.ClientSession() as session:
                print("\n🔍 DEBUG - Obteniendo equipos de Figma...")
                
                # Obtener datos del usuario actual
                print("📡 Llamando a API: GET /v1/me")
                async with session.get(f"{self.base_url}/me", headers=self.headers) as response:
                    if response.status == 200:
                        me_data = await response.json()
                        print(f"✅ Respuesta exitosa de /me - Status: {response.status}")
                        print(f"👤 Usuario: {me_data.get('handle', 'N/A')} ({me_data.get('email', 'N/A')})")
                        print(f"🆔 User ID: {me_data.get('id', 'N/A')}")
                        
                        # Obtener los equipos
                        print("\n📡 Llamando a API: GET /v1/teams")
                        async with session.get(f"{self.base_url}/teams", headers=self.headers) as teams_response:
                            teams_response_text = await teams_response.text()
                            print(f"📊 Respuesta completa de /teams:")
                            print(teams_response_text)
                            
                            if teams_response.status == 200:
                                try:
                                    teams_data = json.loads(teams_response_text)
                                    teams = teams_data.get("teams", [])
                                    print(f"✅ Respuesta exitosa de /teams - Status: {teams_response.status}")
                                    print(f"🏢 Equipos encontrados: {len(teams)}")
                                    
                                    for team in teams:
                                        print(f"\n🏢 Equipo: {team.get('name', 'N/A')}")
                                        print(f"   🆔 ID: {team.get('id', 'N/A')}")
                                        print(f"   📊 URL API: {self.base_url}/teams/{team.get('id')}/projects")
                                        print(f"   🔗 URL Web: https://www.figma.com/files/team/{team.get('id')}")
                                except json.JSONDecodeError:
                                    print(f"❌ Error decodificando JSON de equipos")
                            else:
                                print(f"❌ Error al obtener equipos: {teams_response.status}")
                                print(f"   Error: {teams_response_text}")
                        
                        access_items = []
                        
                        # Añadir equipos como opciones de acceso
                        if teams_response.status == 200:
                            try:
                                teams_data = json.loads(teams_response_text)
                                teams = teams_data.get("teams", [])
                                
                                # Añadir manualmente el equipo de la URL proporcionada
                                has_specific_team = False
                                specific_team_id = "1507023165279092081"
                                
                                for team in teams:
                                    team_id = team.get("id")
                                    if team_id == specific_team_id:
                                        has_specific_team = True
                                    
                                    access_items.append({
                                        "id": team_id,
                                        "name": f"🏢 {team.get('name')}",
                                        "type": "team",
                                        "files_count": 0,
                                        "description": f"Equipo de Figma ({team_id})"
                                    })
                                
                                # Si el equipo específico no está en la lista, añadirlo manualmente
                                if not has_specific_team:
                                    print(f"\n📌 Añadiendo manualmente el equipo ID: {specific_team_id}")
                                    access_items.append({
                                        "id": specific_team_id,
                                        "name": f"🏢 Equipo Manual (ID: {specific_team_id})",
                                        "type": "team",
                                        "files_count": 0,
                                        "description": f"Equipo de Figma añadido manualmente"
                                    })
                            except json.JSONDecodeError:
                                print(f"❌ Error procesando JSON de equipos para access_items")
                        
                        # Agregar opción para pegar URL directa
                        access_items.append({
                            "id": "direct_url",
                            "name": "🔗 Pegar URL de Archivo",
                            "type": "direct_url",
                            "files_count": 0,
                            "description": "Pega la URL directa de tu archivo de Figma"
                        })
                        
                        # Agregar archivos de ejemplo de tus teams
                        access_items.append({
                            "id": "examples",
                            "name": "📋 Archivos de Ejemplo",
                            "type": "examples",
                            "files_count": 5,
                            "description": "Archivos de ejemplo de tus teams (Website, Cleo.DS+)"
                        })
                        
                        # Agregar debug
                        access_items.append({
                            "id": "debug",
                            "name": "🔍 Debug - Ver respuesta API",
                            "type": "debug",
                            "files_count": 0,
                            "description": "Ver datos completos de la API"
                        })
                        
                        print(f"\n📊 Total de elementos de acceso: {len(access_items)}")
                        return access_items
                    else:
                        print(f"❌ Error al obtener datos del usuario: {response.status}")
                        error_text = await response.text()
                        print(f"   Error: {error_text}")
                        return []
        except Exception as e:
            print(f"❌ Error getting access items: {e}")
            return []

    async def get_team_by_id(self, team_id: str) -> Dict[str, Any]:
        """Obtener información directamente de un equipo específico por su ID"""
        try:
            print(f"\n🔍 DEBUG - Obteniendo información del equipo {team_id}...")
            
            # Intentar obtener proyectos del equipo
            print(f"📡 Llamando a API: GET /v1/teams/{team_id}/projects")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/teams/{team_id}/projects", headers=self.headers) as response:
                    response_text = await response.text()
                    print(f"📊 Respuesta completa:")
                    print(response_text)
                    
                    if response.status == 200:
                        try:
                            data = json.loads(response_text)
                            projects = data.get("projects", [])
                            print(f"✅ Respuesta exitosa - Status: {response.status}")
                            print(f"📂 Proyectos encontrados: {len(projects)}")
                            
                            for project in projects:
                                print(f"\n📂 Proyecto: {project.get('name', 'N/A')}")
                                print(f"   🆔 ID: {project.get('id', 'N/A')}")
                                print(f"   📊 URL API: {self.base_url}/projects/{project.get('id')}/files")
                            
                            return {
                                "success": True,
                                "team_id": team_id,
                                "projects_count": len(projects),
                                "projects": projects
                            }
                        except json.JSONDecodeError:
                            print(f"❌ Error decodificando JSON de proyectos")
                            return {
                                "success": False,
                                "error": "Error decodificando respuesta JSON",
                                "raw_response": response_text
                            }
                    else:
                        print(f"❌ Error al obtener proyectos: {response.status}")
                        print(f"   Error: {response_text}")
                        return {
                            "success": False,
                            "error": f"Error HTTP {response.status}",
                            "raw_response": response_text
                        }
        except Exception as e:
            print(f"❌ Error obteniendo información del equipo: {str(e)}")
            return {
                "success": False,
                "error": f"Exception: {str(e)}"
            }

    async def get_team_projects(self, team_id: str) -> List[Dict[str, Any]]:
        # Obtener proyectos de un equipo
        try:
            print(f"\n🔍 DEBUG - Obteniendo proyectos del equipo {team_id}...")
            print(f"📡 Llamando a API: GET /v1/teams/{team_id}/projects")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/teams/{team_id}/projects", headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        projects = data.get("projects", [])
                        print(f"✅ Respuesta exitosa - Status: {response.status}")
                        print(f"📂 Proyectos encontrados: {len(projects)}")
                        
                        for project in projects:
                            print(f"\n📂 Proyecto: {project.get('name', 'N/A')}")
                            print(f"   🆔 ID: {project.get('id', 'N/A')}")
                            print(f"   📊 URL API: {self.base_url}/projects/{project.get('id')}/files")
                        
                        return projects
                    else:
                        error_text = await response.text()
                        print(f"❌ Error al obtener proyectos: {response.status}")
                        print(f"   Error: {error_text}")
                        return []
        except Exception as e:
            print(f"❌ Error getting team projects: {e}")
            return []

    async def get_project_files(self, project_id: str) -> List[Dict[str, Any]]:
        # Obtener archivos de un proyecto
        try:
            print(f"\n🔍 DEBUG - Obteniendo archivos del proyecto {project_id}...")
            print(f"📡 Llamando a API: GET /v1/projects/{project_id}/files")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/projects/{project_id}/files", headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        files = data.get("files", [])
                        print(f"✅ Respuesta exitosa - Status: {response.status}")
                        print(f"📄 Archivos encontrados: {len(files)}")
                        
                        for file in files:
                            print(f"\n📄 Archivo: {file.get('name', 'N/A')}")
                            print(f"   🆔 Key: {file.get('key', 'N/A')}")
                            print(f"   📊 URL API: {self.base_url}/files/{file.get('key')}")
                        
                        return files
                    else:
                        error_text = await response.text()
                        print(f"❌ Error al obtener archivos: {response.status}")
                        print(f"   Error: {error_text}")
                        return []
        except Exception as e:
            print(f"❌ Error getting project files: {e}")
            return []

    async def get_files_from_access_item(self, item_id: str, item_type: str) -> List[Dict[str, Any]]:
        # Obtener archivos según el tipo de acceso
        try:
            if item_type == "team":
                # Si es un equipo, obtenemos sus proyectos
                print(f"\n🔍 DEBUG - Obteniendo archivos para el equipo {item_id}...")
                projects = await self.get_team_projects(item_id)
                
                # Si hay proyectos, mostrar opciones de proyectos
                if projects:
                    return [
                        {
                            "key": project.get("id"),
                            "name": f"📂 {project.get('name')}",
                            "team_id": item_id,
                            "access_type": "project",
                            "description": f"Proyecto de equipo ({project.get('id')})"
                        } 
                        for project in projects
                    ]
                return []
            elif item_type == "project":
                # Si es un proyecto, obtenemos sus archivos
                print(f"\n🔍 DEBUG - Obteniendo archivos para el proyecto {item_id}...")
                files = await self.get_project_files(item_id)
                
                if files:
                    return [
                        {
                            "key": file.get("key"),
                            "name": f"📄 {file.get('name')}",
                            "project_id": item_id,
                            "access_type": "file",
                            "last_modified": file.get("last_modified"),
                            "thumbnail_url": file.get("thumbnail_url")
                        }
                        for file in files
                    ]
                return []
            elif item_type == "direct_url":
                # Devolver instrucciones para URL directa
                return [{
                    "key": "instruction",
                    "name": "📝 Instrucciones para URL directa",
                    "instructions": "Para usar un archivo específico:\n1. Ve a figma.com\n2. Abre tu archivo\n3. Copia la URL (ejemplo: https://www.figma.com/file/ABC123/NombreArchivo)\n4. Extrae el file_key (ABC123)\n5. Úsalo directamente",
                    "access_type": "instructions"
                }]
            elif item_type == "examples":
                # Devolver archivos de ejemplo de tus teams
                return [
                    {
                        "key": "ejemplo1",
                        "name": "🎨 Cleo DS Beta (Ejemplo)",
                        "example_url": "figma.com/file/XXXXXXXXX/Cleo-DS-Beta",
                        "team": "Cleo.DS+",
                        "access_type": "example"
                    },
                    {
                        "key": "ejemplo2", 
                        "name": "📚 Design Libraries (Ejemplo)",
                        "example_url": "figma.com/file/YYYYYYYYY/Design-Libraries",
                        "team": "Website",
                        "access_type": "example"
                    },
                    {
                        "key": "ejemplo3",
                        "name": "🧑‍🏫 EDB Facilitadores (Ejemplo)",
                        "example_url": "figma.com/file/ZZZZZZZZZ/EDB-Facilitadores",
                        "team": "Cleo.DS+",
                        "access_type": "example"
                    }
                ]
            elif item_type == "debug":
                # Devolver datos raw para debug
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.base_url}/me", headers=self.headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            return [{
                                "key": "debug_data",
                                "name": "🔍 Datos completos de la API",
                                "debug_data": data,
                                "access_type": "debug"
                            }]
                return []
            else:
                return []
        except Exception as e:
            print(f"❌ Error getting files from access item: {e}")
            return []

    async def get_file_structure(self, file_key: str) -> Dict[str, Any]:
        # Obtener estructura completa de un archivo (paginas y frames)
        try:
            # Si es un file_key de ejemplo, devolver estructura mock
            if file_key in ["ejemplo1", "ejemplo2", "ejemplo3", "instruction"]:
                return {
                    "success": False,
                    "error": "Este es un archivo de ejemplo. Para usar un archivo real, necesitas el file_key real de Figma."
                }
            
            print(f"\n🔍 DEBUG - Obteniendo estructura del archivo {file_key}...")
            print(f"📡 Llamando a API: GET /v1/files/{file_key}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/files/{file_key}", headers=self.headers) as response:
                    response_text = await response.text()
                    
                    if response.status == 200:
                        try:
                            data = json.loads(response_text)
                            print(f"✅ Respuesta exitosa - Status: {response.status}")
                            print(f"📄 Nombre del archivo: {data.get('name', 'N/A')}")
                            
                            # Extraer paginas y frames
                            pages = []
                            document = data.get("document", {})
                            
                            for page in document.get("children", []):
                                if page.get("type") == "CANVAS":
                                    frames = []
                                    
                                    for child in page.get("children", []):
                                        if child.get("type") == "FRAME":
                                            frames.append({
                                                "id": child.get("id"),
                                                "name": child.get("name"),
                                                "type": child.get("type"),
                                                "width": child.get("absoluteBoundingBox", {}).get("width"),
                                                "height": child.get("absoluteBoundingBox", {}).get("height"),
                                                "background_color": child.get("backgroundColor")
                                            })
                                    
                                    pages.append({
                                        "id": page.get("id"),
                                        "name": page.get("name"),
                                        "type": page.get("type"),
                                        "frames_count": len(frames),
                                        "frames": frames
                                    })
                                    print(f"📑 Página: {page.get('name')} - {len(frames)} frames")
                            
                            return {
                                "success": True,
                                "file_key": file_key,
                                "file_name": data.get("name"),
                                "pages_count": len(pages),
                                "pages": pages,
                                "version": data.get("version"),
                                "last_modified": data.get("lastModified")
                            }
                        except json.JSONDecodeError as e:
                            print(f"❌ Error decodificando JSON: {str(e)}")
                            return {
                                "success": False,
                                "error": f"Error al decodificar la respuesta JSON: {str(e)}"
                            }
                    elif response.status == 404:
                        print(f"❌ Archivo no encontrado - Status: {response.status}")
                        return {
                            "success": False,
                            "error": f"Archivo no encontrado. Verifica que el file_key '{file_key}' sea correcto y tengas acceso al archivo."
                        }
                    elif response.status == 403:
                        print(f"❌ Acceso denegado - Status: {response.status}")
                        return {
                            "success": False,
                            "error": f"Acceso denegado. No tienes permisos para acceder a este archivo."
                        }
                    else:
                        error_data = response_text
                        print(f"❌ Error al obtener estructura: {response.status}")
                        print(f"   Error: {error_data}")
                        
                        error_message = "Error desconocido"
                        try:
                            error_json = json.loads(error_data)
                            if isinstance(error_json, dict):
                                error_message = error_json.get("err", error_message)
                        except:
                            pass
                        
                        return {
                            "success": False,
                            "error": f"Error HTTP {response.status}: {error_message}",
                            "raw_error": error_data
                        }
        except Exception as e:
            print(f"❌ Error getting file structure: {str(e)}")
            return {
                "success": False,
                "error": f"Error obteniendo la estructura del archivo: {str(e)}"
            }

    async def analyze_file_structure(self, file_key: str) -> Dict[str, Any]:
        # Analisis completo de un archivo de Figma
        return await self.get_file_structure(file_key)

    async def get_all_teams(self) -> List[Dict[str, Any]]:
        """Obtener todos los equipos disponibles para el usuario sin filtrar"""
        try:
            print("\n🔍 DEBUG - Obteniendo TODOS los equipos de Figma...")
            
            async with aiohttp.ClientSession() as session:
                # Llamada directa a la API de equipos
                print("📡 Llamando a API: GET /v1/teams")
                async with session.get(f"{self.base_url}/teams", headers=self.headers) as response:
                    response_text = await response.text()
                    print(f"📊 Respuesta completa de /teams:")
                    print(response_text)
                    
                    if response.status == 200:
                        try:
                            teams_data = json.loads(response_text)
                            teams = teams_data.get("teams", [])
                            print(f"✅ Respuesta exitosa - Status: {response.status}")
                            print(f"🏢 TODOS los equipos encontrados: {len(teams)}")
                            
                            all_teams = []
                            for team in teams:
                                team_name = team.get("name", "Sin nombre")
                                team_id = team.get("id", "ID desconocido")
                                print(f"\n🏢 Equipo: {team_name}")
                                print(f"   🆔 ID: {team_id}")
                                print(f"   📊 URL API: {self.base_url}/teams/{team_id}/projects")
                                print(f"   🔗 URL Web: https://www.figma.com/files/team/{team_id}")
                                
                                all_teams.append({
                                    "id": team_id,
                                    "name": team_name,
                                    "type": "team",
                                    "description": f"Equipo de Figma ({team_id})"
                                })
                            
                            # Agregar el equipo especial con ID específico si no está ya
                            specific_team_id = "1507023165279092081"
                            found = any(team["id"] == specific_team_id for team in all_teams)
                            
                            if not found:
                                print(f"\n📌 Añadiendo manualmente el equipo conocido ID: {specific_team_id}")
                                all_teams.append({
                                    "id": specific_team_id,
                                    "name": "Website Team",
                                    "type": "team",
                                    "description": "Equipo Website (añadido manualmente)"
                                })
                            
                            return all_teams
                            
                        except json.JSONDecodeError:
                            print(f"❌ Error decodificando JSON de equipos")
                            return []
                    else:
                        print(f"❌ Error al obtener equipos: {response.status}")
                        print(f"   Error: {response_text}")
                        return []
        except Exception as e:
            print(f"❌ Error getting all teams: {e}")
            return []

    async def check_team_access(self, team_id: str) -> Dict[str, Any]:
        """Verificar si tenemos acceso a un equipo específico"""
        try:
            print(f"🔍 Verificando acceso al equipo {team_id}...")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/teams/{team_id}/projects", headers=self.headers) as response:
                    if response.status == 200:
                        # Si podemos obtener los proyectos, entonces tenemos acceso
                        data = await response.json()
                        team_name = data.get("name", f"Equipo {team_id}")
                        projects_count = len(data.get("projects", []))
                        
                        print(f"✅ Acceso confirmado a equipo {team_name} con {projects_count} proyectos")
                        return {
                            "accessible": True,
                            "team_id": team_id,
                            "name": team_name,
                            "projects_count": projects_count
                        }
                    else:
                        print(f"❌ Sin acceso al equipo {team_id} - Status: {response.status}")
                        return {
                            "accessible": False,
                            "team_id": team_id,
                            "error": f"HTTP Status: {response.status}"
                        }
        except Exception as e:
            print(f"❌ Error verificando acceso al equipo {team_id}: {str(e)}")
            return {
                "accessible": False,
                "team_id": team_id,
                "error": str(e)
            }

    async def get_frame_details(self, file_key: str, frame_id: str) -> Dict[str, Any]:
        """Obtener detalles completos de un frame específico"""
        try:
            print(f"\n🔍 DEBUG - Obteniendo detalles del frame {frame_id} en archivo {file_key}...")
            
            # Primero necesitamos obtener más detalles con el endpoint de nodos
            print(f"📡 Llamando a API: GET /v1/files/{file_key}/nodes?ids={frame_id}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/files/{file_key}/nodes?ids={frame_id}",
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Respuesta exitosa - Status: {response.status}")
                        
                        # Extraer datos del frame específico
                        nodes = data.get("nodes", {})
                        frame_data = nodes.get(frame_id, {}).get("document", {})
                        
                        if not frame_data:
                            return {
                                "success": False,
                                "error": "No se encontraron datos del frame"
                            }
                        
                        # Extraer elementos hijos del frame con sus propiedades
                        frame_details = {
                            "id": frame_id,
                            "name": frame_data.get("name", "Sin nombre"),
                            "type": frame_data.get("type", "FRAME"),
                            "width": frame_data.get("absoluteBoundingBox", {}).get("width"),
                            "height": frame_data.get("absoluteBoundingBox", {}).get("height"),
                            "background_color": frame_data.get("backgroundColor"),
                            "children": frame_data.get("children", []),
                            "styles": frame_data.get("styles", {}),
                            "layout": frame_data.get("layoutMode"),
                            "constraints": frame_data.get("constraints", {}),
                            "effects": frame_data.get("effects", []),
                            "file_key": file_key,
                            "raw_data": frame_data  # Incluir datos completos para análisis
                        }
                        
                        # Obtener también las imágenes/renderizaciones del frame
                        print(f"📡 Obteniendo render del frame: GET /v1/images/{file_key}?ids={frame_id}")
                        
                        async with session.get(
                            f"{self.base_url}/images/{file_key}?ids={frame_id}&format=png&scale=2",
                            headers=self.headers
                        ) as img_response:
                            if img_response.status == 200:
                                img_data = await img_response.json()
                                frame_details["image_url"] = img_data.get("images", {}).get(frame_id)
                            else:
                                print(f"⚠️ No se pudo obtener la imagen del frame - Status: {img_response.status}")
                        
                        return {
                            "success": True,
                            "frame": frame_details
                        }
                    else:
                        error_text = await response.text()
                        print(f"❌ Error al obtener detalles del frame: {response.status}")
                        print(f"   Error: {error_text}")
                        return {
                            "success": False,
                            "error": f"Error al obtener detalles del frame: HTTP {response.status}",
                            "raw_error": error_text
                        }
        except Exception as e:
            print(f"❌ Error getting frame details: {str(e)}")
            return {
                "success": False,
                "error": f"Error obteniendo detalles del frame: {str(e)}"
            }

    async def get_file_components_and_styles(self, file_key: str) -> Dict[str, Any]:
        """Obtener componentes y estilos de un archivo de Figma"""
        try:
            components = []
            styles = []
            
            async with aiohttp.ClientSession() as session:
                print(f"\n🔍 DEBUG - Obteniendo componentes del archivo {file_key}...")
                print(f"📡 Llamando a API: GET /v1/files/{file_key}/components")
                
                async with session.get(f"{self.base_url}/files/{file_key}/components", headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        components = data.get("meta", {}).get("components", [])
                        print(f"✅ Componentes encontrados: {len(components)}")
                    else:
                        error_text = await response.text()
                        print(f"⚠️ Error obteniendo componentes: {response.status}")
                        print(f"   Error: {error_text}")
                
                print(f"\n🔍 DEBUG - Obteniendo estilos del archivo {file_key}...")
                print(f"📡 Llamando a API: GET /v1/files/{file_key}/styles")
                
                async with session.get(f"{self.base_url}/files/{file_key}/styles", headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        styles = data.get("meta", {}).get("styles", [])
                        print(f"✅ Estilos encontrados: {len(styles)}")
                    else:
                        error_text = await response.text()
                        print(f"⚠️ Error obteniendo estilos: {response.status}")
                        print(f"   Error: {error_text}")
            
            return {
                "success": True,
                "components": components,
                "styles": styles
            }
        except Exception as e:
            print(f"❌ Error obteniendo componentes y estilos: {str(e)}")
            return {
                "success": False,
                "error": f"Error obteniendo componentes y estilos: {str(e)}"
            }

    async def get_file_complete_details(self, file_key: str) -> Dict[str, Any]:
        """Obtener todos los detalles disponibles de un archivo de Figma"""
        try:
            # Obtener estructura básica del archivo
            structure = await self.get_file_structure(file_key)
            if not structure["success"]:
                return structure
            
            # Obtener componentes y estilos
            comp_styles = await self.get_file_components_and_styles(file_key)
            
            # Combinar toda la información
            return {
                "success": True,
                "file_key": file_key,
                "file_name": structure.get("file_name"),
                "last_modified": structure.get("last_modified"),
                "version": structure.get("version"),
                "pages": structure.get("pages", []),
                "components": comp_styles.get("components", []),
                "styles": comp_styles.get("styles", [])
            }
        except Exception as e:
            print(f"❌ Error obteniendo detalles completos: {str(e)}")
            return {
                "success": False,
                "error": f"Error obteniendo detalles completos: {str(e)}"
            }
            
    async def get_components_with_thumbnails(self, file_key: str) -> Dict[str, Any]:
        """Obtener componentes con imágenes de vista previa
        
        Este método obtiene todos los componentes de un archivo de Figma
        y solicita imágenes de vista previa para cada componente.
        """
        try:
            print(f"\n🔍 DEBUG - Obteniendo componentes con imágenes del archivo {file_key}...")
            
            # Paso 1: Obtener todos los componentes del archivo
            comp_result = await self.get_file_components_and_styles(file_key)
            
            if not comp_result.get("success", False):
                return comp_result
                
            components = comp_result.get("components", [])
            
            if not components:
                print("⚠️ No se encontraron componentes en el archivo")
                return {
                    "success": True,
                    "components": [],
                    "message": "No se encontraron componentes en el archivo"
                }
                
            print(f"✅ Se encontraron {len(components)} componentes")
            
            # Paso 2: Preparar los IDs para solicitar las imágenes
            component_ids = [component.get("node_id") for component in components if component.get("node_id")]
            
            if not component_ids:
                print("⚠️ No se pudieron extraer IDs de los componentes")
                return {
                    "success": False,
                    "error": "No se pudieron extraer IDs de los componentes",
                    "raw_components": components
                }
                
            # Limitar a 50 componentes para evitar problemas con la API
            if len(component_ids) > 50:
                print(f"⚠️ Limitando a 50 componentes de {len(component_ids)} encontrados")
                component_ids = component_ids[:50]
                
            # Paso 3: Solicitar imágenes para los componentes
            async with aiohttp.ClientSession() as session:
                print(f"📡 Solicitando imágenes para {len(component_ids)} componentes")
                
                # Construir la URL con todos los IDs (con formato=png y escala=1)
                ids_param = ",".join(component_ids)
                url = f"{self.base_url}/images/{file_key}?ids={ids_param}&format=png&scale=2"
                
                print(f"📡 Llamando a API: GET {url}")
                
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        image_urls = data.get("images", {})
                        print(f"✅ Se obtuvieron {len(image_urls)} imágenes")
                        
                        # Paso 4: Combinar los datos de los componentes con sus imágenes
                        components_with_images = []
                        
                        for component in components:
                            node_id = component.get("node_id")
                            if node_id in image_urls:
                                # Añadir la URL de la imagen al componente
                                component["thumbnail_url"] = image_urls[node_id]
                                
                            # Agregar más información útil
                            component["description"] = component.get("description", "")
                            component["key"] = component.get("key", "")
                            component["name"] = component.get("name", "Componente sin nombre")
                            component["page_name"] = component.get("page_name", component.get("containing_frame", {}).get("name", ""))
                            
                            # Añadir información sobre variantes si está disponible
                            component_name = component.get("name", "")
                            if "/" in component_name:
                                parts = component_name.split("/")
                                component["base_name"] = parts[0].strip()
                                component["variant_name"] = "/".join(parts[1:]).strip()
                                component["is_variant"] = True
                            else:
                                component["base_name"] = component_name
                                component["is_variant"] = False
                            
                            components_with_images.append(component)
                            
                        # Organizar componentes por grupos de variantes
                        component_groups = {}
                        for component in components_with_images:
                            base_name = component.get("base_name", "")
                            if not base_name:
                                base_name = "Sin grupo"
                                
                            if base_name not in component_groups:
                                component_groups[base_name] = []
                                
                            component_groups[base_name].append(component)
                        
                        return {
                            "success": True,
                            "components": components_with_images,
                            "component_groups": component_groups,
                            "total_count": len(components_with_images)
                        }
                    else:
                        error_text = await response.text()
                        print(f"❌ Error obteniendo imágenes: {response.status}")
                        print(f"   Error: {error_text}")
                        
                        # Devolver los componentes sin imágenes como fallback
                        return {
                            "success": False,
                            "error": f"Error obteniendo imágenes: HTTP {response.status}",
                            "components": components,
                            "total_count": len(components)
                        }
        except Exception as e:
            print(f"❌ Error obteniendo componentes con imágenes: {str(e)}")
            return {
                "success": False,
                "error": f"Error obteniendo componentes con imágenes: {str(e)}"
            }
