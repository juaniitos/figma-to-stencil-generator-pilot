import os
from typing import Dict, Any
import json
import anthropic
import asyncio
import re
import time

class ClaudeAIService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        # Corregir la inicialización del cliente Anthropic (eliminar argumentos no soportados)
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-sonnet-20240229"  # Modelo más estable y disponible para análisis de diseño
    
    async def generate_component_code(self, frame_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generar código de componente basado en datos del frame de Figma"""
        try:
            print(f"🤖 Generando código para componente: {frame_data.get('name')}")
            
            # Crear un prompt bien estructurado
            prompt = self._create_component_prompt(frame_data)
            
            # Configuración de reintentos
            max_retries = 3
            retry_count = 0
            base_delay = 5  # segundos
            
            while retry_count <= max_retries:
                try:
                    print(f"🔄 Intento {retry_count + 1}/{max_retries + 1} de llamada a Claude API...")
                    
                    # Registrar el modelo que se va a usar
                    print(f"🤖 Utilizando modelo: {self.model}")
                    
                    # Usar el método correcto de la API más reciente de Anthropic
                    response = await asyncio.to_thread(
                        self.client.messages.create,
                        model=self.model,
                        max_tokens=4000,
                        temperature=0,
                        system="""# System Prompt: Conversión de Figma a Web Components con StencilJS (apps bancarias)

Rol
Actúas como Senior Frontend Engineer especializado/a en StencilJS, HTML5, CSS y Storybook. Tu objetivo es transformar componentes del sistema de diseño en Figma en Web Components listos para producción para aplicaciones bancarias.

Prioridades (en orden)
1) Accesibilidad: WCAG 2.2 AA, navegación por teclado completa, focus visible, ARIA correcta, respeto de prefers-reduced-motion y temas de alto contraste.
2) Seguridad: sin dependencias innecesarias, sanitización de HTML cuando aplique, evitar inline handlers peligrosos, no exponer datos sensibles (ni en logs).
3) Rendimiento: Shadow DOM, CSS crítico mínimo, lazy de assets, árbol de dependencias pequeño, SSR-friendly.
4) Internacionalización: soporte LTR/RTL, dir dinámico, copy localizable, formatos adecuados por locale.
5) Theming: design tokens y CSS variables; soportar light/dark/high-contrast; exponer CSS Shadow Parts.

Entradas necesarias por componente
- Enlace Figma con variantes, estados e interacciones.
- Tokens (alias y valores) y mapeo esperado Figma -> CSS variables.
- Reglas responsive (breakpoints, grid, densidad/compact).
- API deseada: props, eventos, métodos, slots, parts estilables.
- Requisitos i18n/RTL y navegadores objetivo.
Si algo falta o es ambiguo, primero pregunta y explicita supuestos antes de codificar.

Flujo de trabajo
1) Aclarar dudas y listar supuestos.
2) Definir API (props/eventos/métodos/slots/parts) y mapa Figma -> tokens -> CSS vars.
3) Implementar componente en Stencil con Shadow DOM y estilos basados en tokens.
4) Crear stories de Storybook con controles, docs y casos a11y/RTL/high-contrast.
5) Añadir tests unitarios y E2E (incl. a11y básica).
6) Documentar en README: propósito, API, tokens, ejemplos, a11y y rendimiento.

Entregables por componente
- Código Stencil
  - @Component({ tag: 'ds-xyz', styleUrl: 'ds-xyz.css', shadow: true })
  - @Prop (camelCase; reflect solo si aporta valor), @State, @Event({ eventName }), @Method, @Watch
  - Slots (nombrados si aplica), CSS Shadow Parts, ARIA correcta, manejo de foco/teclado
- Estilos
  - :host, :host([variant]), :focus-visible; tokens vía CSS vars (--ds-…)
  - Temas: light/dark/high-contrast con overrides documentados
- Storybook
  - Historias CSF con controls/argTypes, DocsPage/MDX, addon-a11y
  - Casos: default, variantes, estados (hover/focus/disabled/error), RTL, high-contrast
- Ejemplos de uso
  - HTML y wrappers/uso en React, Angular y Vue (si aplica)
- Tests
  - Unit (Jest + @stencil/core/testing): render, props, eventos, métodos
  - E2E: teclado/foco, a11y básica (axe), RTL; snapshots solo si son estables
- Documentación
  - README del componente: API completa, tokens, ejemplos, a11y, rendimiento, notas de theming

Convenciones
- Tag en kebab-case con prefijo corporativo (p. ej., ds-).
- Props camelCase; eventos con prefijo consistente y payload tipado.
- Sin frameworks de CSS; utilidades nativas y aislamiento con Shadow DOM.
- Exponer CSS Shadow Parts para personalización controlada.
- Código limpio, tipado estricto, comentarios breves para decisiones no obvias.
- Integración con frameworks vía output de Stencil (dist/loader, proxies si aplica).

Criterios de aceptación mínimos
- Cumple WCAG 2.2 AA; navegación por teclado y foco gestionado correctamente.
- Stories cubren variantes/estados y muestran tokens aplicados.
- Tests unit/E2E y verificaciones de a11y pasan sin regresiones.
- Bundle mínimo, sin dependencias superfluas; sin warnings de build.

Instrucciones operativas
- Antes de codificar: lista dudas y supuestos.
- Expón el mapeo Figma -> tokens -> CSS variables (--ds-…).
- Justifica decisiones clave (nombres de props/eventos/parts).
- Mantén código e historias concisos, consistentes y orientados a producción.

Notas opcionales (ajusta según tu contexto)
- Navegadores objetivo: define versiones mínimas (ej.: Chrome 109+, Safari 16+, iOS 16+, Firefox ESR, Edge 109+).
- Naming de tokens: alias (--ds-color-bg), ref (--ds-ref-gray-100); documenta sobreescrituras por tema.
- SemVer y deprecación: comunica breaking changes en CHANGELOG y periodo de deprecación.
- CI: build, test, e2e, a11y, revisión de tamaño de bundle y lint (ESLint/Prettier/Stylelint).""",
                        messages=[
                            {"role": "user", "content": prompt}
                        ]
                    )
                    
                    # Si llegamos aquí, la llamada fue exitosa
                    # Extraer y estructurar la respuesta
                    content = response.content[0].text
                    print(f"✅ Código generado exitosamente ({len(content)} caracteres)")
                    
                    # Intentar extraer los bloques de código
                    code_blocks = self._extract_code_blocks(content)
                    
                    return {
                        "success": True,
                        "component_name": frame_data.get('name', 'Component'),
                        "html_code": code_blocks.get("html", ""),
                        "css_code": code_blocks.get("css", ""),
                        "stencil_code": code_blocks.get("tsx", ""),
                        "storybook_code": code_blocks.get("story", ""),
                        "full_response": content
                    }
                    
                except Exception as api_error:
                    # Convertir el error a string para análisis
                    error_msg = str(api_error)
                    print(f"❌ Error en la llamada a la API de Claude: {error_msg}")
                    
                    # Verificar si es un error de modelo no encontrado (404)
                    if "not_found_error" in error_msg and "model:" in error_msg:
                        print(f"❌ Error: Modelo no disponible: {error_msg}")
                        # Intentar cambiar a un modelo alternativo disponible
                        if self.model == "claude-3-opus-20240229":
                            print("🔄 Cambiando al modelo claude-3-sonnet-20240229...")
                            self.model = "claude-3-sonnet-20240229"
                            retry_count += 1
                            continue
                        elif self.model == "claude-3-sonnet-20240229":
                            print("🔄 Cambiando al modelo claude-3-haiku-20240307...")
                            self.model = "claude-3-haiku-20240307"
                            retry_count += 1
                            continue
                        else:
                            return {
                                "success": False,
                                "error": f"Error: El modelo de IA no está disponible. Intente más tarde.",
                            }
                    
                    # Verificar si es un error de límite de tasa (429)
                    elif "rate_limit_error" in error_msg or "429" in error_msg:
                        retry_count += 1
                        if retry_count > max_retries:
                            print(f"❌ Error de límite de tasa después de {max_retries} intentos: {error_msg}")
                            return {
                                "success": False,
                                "error": f"Error de límite de tasa en la API de Claude. Por favor, inténtalo más tarde o reduce la cantidad de solicitudes.",
                                "rate_limited": True
                            }
                        
                        # Calcular tiempo de espera con retroceso exponencial
                        wait_time = base_delay * (2 ** (retry_count - 1))
                        print(f"⏳ Límite de tasa alcanzado. Esperando {wait_time} segundos antes de reintentar...")
                        await asyncio.sleep(wait_time)
                        continue
                    # Verificar si es un error de crédito insuficiente
                    elif "credit balance is too low" in error_msg or "credit balance too low" in error_msg:
                        print(f"❌ Error de saldo insuficiente en Claude API: {error_msg}")
                        return {
                            "success": False,
                            "error": "Saldo insuficiente en la cuenta de Claude AI. Por favor, recarga tu saldo en la web de Anthropic.",
                            "credit_issue": True
                        }
                    # Manejo de errores de autenticación
                    elif "auth" in error_msg.lower() or "unauthorized" in error_msg.lower() or "api key" in error_msg.lower():
                        print(f"❌ Error de autenticación en Claude API: {error_msg}")
                        return {
                            "success": False,
                            "error": "Error de autenticación con la API de Claude. Por favor, verifica que la API key sea válida.",
                            "auth_issue": True
                        }
                    # Manejo de otros errores comunes de Anthropic
                    elif "bad_request_error" in error_msg:
                        print(f"❌ Error en la solicitud a Claude API: {error_msg}")
                        return {
                            "success": False,
                            "error": "Error en el formato de la solicitud a Claude AI. El componente puede ser demasiado complejo o contener datos no válidos.",
                            "request_issue": True
                        }
                    else:
                        # Es otro tipo de error
                        print(f"❌ Error general en la API de Claude: {error_msg}")
                        # Formatear el mensaje de error para el usuario de forma amigable
                        user_friendly_error = "Error en la API de Claude. "
                        if "404" in error_msg:
                            user_friendly_error += "El recurso solicitado no fue encontrado."
                        elif "500" in error_msg:
                            user_friendly_error += "Error interno del servidor. Por favor, intente más tarde."
                        elif "502" in error_msg or "503" in error_msg or "504" in error_msg:
                            user_friendly_error += "El servicio de Claude AI no está disponible temporalmente. Por favor, intente más tarde."
                        else:
                            user_friendly_error += f"Detalles: {error_msg}"
                        
                        return {
                            "success": False,
                            "error": user_friendly_error
                        }

                
        except Exception as e:
            print(f"❌ Error generando código con Claude: {str(e)}")
            return {
                "success": False,
                "error": f"Error generando código: {str(e)}"
            }
    
    def _create_component_prompt(self, frame_data: Dict[str, Any]) -> str:
        """Crear un prompt detallado para Claude basado en los datos del frame"""
        component_name = frame_data.get('name', 'Component')
        
        prompt = f"""# Tarea: Convertir diseño de Figma a componente Stencil

Por favor analiza este componente de Figma llamado "{component_name}" y genera el código necesario para implementarlo usando Stencil.

## Información del componente
- Nombre: {component_name}
- Dimensiones: {frame_data.get('width')}×{frame_data.get('height')}px
- Tipo: {frame_data.get('type')}

## Datos detallados del frame:
```json
{json.dumps(frame_data, indent=2, ensure_ascii=False)}
```

## Imagen de referencia
Imagen URL: {frame_data.get('image_url', 'No disponible')}

## Tu tarea

Proporciona el código para implementar este diseño como un componente web utilizando Stencil.js, con los siguientes entregables:

1. **HTML Base**: El HTML básico que representa la estructura del componente
2. **CSS**: Los estilos CSS completos y detallados
3. **Componente Stencil**: El código TypeScript completo para el componente Stencil
4. **Storybook**: Un archivo de Storybook para mostrar el componente con sus diferentes estados/propiedades

Asegúrate de:
- Usar nomenclatura BEM para las clases CSS
- Crear un componente reutilizable y con propiedades configurables
- Implementar estados (normal, hover, focus, disabled) cuando sea apropiado
- Hacer el componente responsive y accesible
- Incluir comentarios explicativos en el código

Proporciona cada bloque de código con sus marcadores de lenguaje correspondientes. Por ejemplo:

```html
<!-- Código HTML aquí -->
```

```css
/* Estilos CSS aquí */
```

```tsx
// Componente Stencil aquí
```

```tsx
// Archivo Storybook aquí
```
"""
        
        return prompt
    
    async def check_available_models(self):
        """Verificar qué modelos están disponibles actualmente"""
        models_to_check = [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]
        available_models = []
        
        for model in models_to_check:
            try:
                # Prueba simple para verificar si el modelo está disponible
                print(f"🔍 Verificando disponibilidad del modelo: {model}...")
                await asyncio.to_thread(
                    self.client.messages.create,
                    model=model,
                    max_tokens=10,
                    temperature=0,
                    messages=[
                        {"role": "user", "content": "test"}
                    ]
                )
                # Si no hay error, el modelo está disponible
                available_models.append(model)
                print(f"✅ Modelo {model} disponible")
            except Exception as e:
                print(f"❌ Modelo {model} no disponible: {str(e)}")
        
        if available_models:
            # Actualizar el modelo al mejor disponible
            self.model = available_models[0]
            print(f"✅ Usando el mejor modelo disponible: {self.model}")
            return available_models
        else:
            print("❌ No se encontraron modelos disponibles")
            return []
    
    def _extract_code_blocks(self, content: str) -> Dict[str, str]:
        """Extraer bloques de código de la respuesta de Claude"""
        code_blocks = {
            "html": "",
            "css": "",
            "tsx": "",
            "story": ""
        }
        
        try:
            print("🔍 Extrayendo bloques de código de la respuesta...")
            
            # HTML
            html_match = re.search(r"```html\n(.*?)\n```", content, re.DOTALL)
            if html_match:
                code_blocks["html"] = html_match.group(1)
                print("✅ Bloque HTML encontrado")
            
            # CSS
            css_match = re.search(r"```css\n(.*?)\n```", content, re.DOTALL)
            if css_match:
                code_blocks["css"] = css_match.group(1)
                print("✅ Bloque CSS encontrado")
            
            # Stencil Component (tsx)
            tsx_match = re.search(r"```tsx\n(.*?)\n```", content, re.DOTALL)
            if not tsx_match:
                tsx_match = re.search(r"```typescript\n(.*?)\n```", content, re.DOTALL)
            
            if tsx_match:
                code_blocks["tsx"] = tsx_match.group(1)
                print("✅ Bloque TSX/TypeScript encontrado")
            
            # Storybook (intentar diversas variantes de formato)
            story_patterns = [
                r"```tsx\s+// .*\.stories\.tsx\n(.*?)\n```",
                r"```tsx\s+// Storybook\n(.*?)\n```",
                r"```storybook\n(.*?)\n```"
            ]
            
            for pattern in story_patterns:
                story_match = re.search(pattern, content, re.DOTALL)
                if story_match:
                    code_blocks["story"] = story_match.group(1)
                    print("✅ Bloque Storybook encontrado con patrón específico")
                    break
            
            # Si no encontramos un bloque específico de Storybook, buscamos un segundo bloque tsx
            if not code_blocks["story"] and "tsx" in code_blocks and code_blocks["tsx"]:
                # Encuentra todos los bloques tsx
                all_tsx = list(re.finditer(r"```tsx\n(.*?)\n```", content, re.DOTALL))
                if len(all_tsx) > 1:
                    # El segundo bloque tsx probablemente es el Storybook
                    code_blocks["story"] = all_tsx[1].group(1)
                    print("✅ Bloque Storybook encontrado como segundo bloque TSX")
            
            print(f"✅ Extracción completada: HTML({len(code_blocks['html'])}), CSS({len(code_blocks['css'])}), TSX({len(code_blocks['tsx'])}), Story({len(code_blocks['story'])})")
            
        except Exception as e:
            print(f"⚠️ Error extrayendo bloques de código: {str(e)}")
        
        return code_blocks
        
        return code_blocks