# Figma to Stencil Generator

Esta aplicación permite generar componentes Stencil.js a partir de diseños creados en Figma. Utiliza la API de Figma para obtener los componentes y la API de Claude AI para generar el código correspondiente.

## Características

- Acceso directo a archivos de Figma mediante URL
- Visualización de componentes con imágenes de vista previa
- Generación de código HTML, CSS, StencilJS y Storybook
- Vista previa del componente generado junto a la imagen original de Figma
- Generación por lotes de múltiples componentes

## Configuración

### Backend (Python)

1. Instala las dependencias:
```
cd backend
pip install -r requirements.txt
```

2. Configura las variables de entorno:
   - Crea un archivo `.env` en la carpeta `backend` usando el archivo `.env.example` como base
   - Agrega tu token de acceso a Figma en `FIGMA_ACCESS_TOKEN`
   - Agrega tu clave de API de Anthropic Claude en `CLAUDE_API_KEY`

   **Nota importante:** Nunca subas tus claves API a repositorios públicos.

3. Inicia el servidor:
```
python run.py
```

### Frontend

1. Abre `frontend/index.html` en tu navegador o usa un servidor web local.

## Uso

1. Accede a la URL directa de tu archivo Figma
2. Selecciona los componentes que deseas generar
3. Haz clic en "Generar Seleccionados"
4. Visualiza y descarga el código generado

## Tecnologías utilizadas

- Backend: Python, FastAPI, Anthropic Claude API
- Frontend: HTML, CSS, JavaScript
- APIs: Figma API, Claude AI

## Licencia

[MIT](LICENSE)
