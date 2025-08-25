import anthropic
from typing import Dict, List, Any
import json
import os

class ClaudeClient:
    def __init__(self, api_key: str):
        if not api_key or api_key == "your_claude_api_key_here":
            raise ValueError("❌ Claude API key requerido")
        
        self.client = anthropic.Anthropic(api_key=api_key)
        
    async def generate_stencil_component(self, component_data: Dict[str, Any], design_tokens: Dict[str, Any]) -> Dict[str, Any]:
        """Generar componente Stencil usando Claude"""
        
        prompt = f"""
Eres un experto desarrollador de Stencil.js. Genera un componente Stencil completo basado en estos datos de Figma:

DATOS DEL COMPONENTE:
{json.dumps(component_data, indent=2)}

DESIGN TOKENS DISPONIBLES:
{json.dumps(design_tokens, indent=2)}

REQUISITOS:
1. Crear un componente Stencil funcional (.tsx)
2. Incluir estilos CSS correspondientes
3. Usar las mejores prácticas de Stencil
4. Hacer el componente responsivo
5. Incluir PropTypes/interfaces TypeScript
6. Agregar comentarios explicativos

RESPUESTA EN FORMATO JSON:
{{
  "component_name": "nombre-del-componente",
  "tsx_content": "código TSX completo",
  "css_content": "estilos CSS completos", 
  "interface_content": "interfaces TypeScript",
  "documentation": "documentación del componente"
}}

Genera SOLO el JSON, sin texto adicional.
"""

        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=4000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extraer contenido
            content = response.content[0].text
            
            # Intentar parsear JSON
            try:
                result = json.loads(content)
                return {
                    "success": True,
                    "data": result
                }
            except json.JSONDecodeError:
                # Si no es JSON válido, estructurar la respuesta
                return {
                    "success": True,
                    "data": {
                        "component_name": component_data.get("name", "unknown-component").lower().replace(" ", "-"),
                        "tsx_content": content,
                        "css_content": "/* Estilos generados por Claude */",
                        "documentation": "Componente generado automáticamente"
                    }
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_storybook_story(self, component_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generar historia de Storybook"""
        
        prompt = f"""
Genera una historia de Storybook para este componente:

DATOS DEL COMPONENTE:
{json.dumps(component_data, indent=2)}

REQUISITOS:
1. Historia completa de Storybook 6+
2. Incluir controles interactivos
3. Múltiples variantes del componente
4. Documentación clara

RESPUESTA EN FORMATO JSON:
{{
  "story_content": "código de la historia completa",
  "story_name": "nombre de la historia"
}}
"""

        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = response.content[0].text
            
            try:
                result = json.loads(content)
                return {
                    "success": True,
                    "data": result
                }
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "data": {
                        "story_name": f"{component_data.get('name', 'Component')}.stories.tsx",
                        "story_content": content
                    }
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def test_connection(self) -> Dict[str, Any]:
        """Probar conexión con Claude"""
        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=100,
                messages=[
                    {"role": "user", "content": "Responde solo con: 'Conexión exitosa con Claude'"}
                ]
            )
            
            return {
                "success": True,
                "message": response.content[0].text,
                "model": "claude-3-haiku-20240307"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
