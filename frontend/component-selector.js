// Este código se agregará a index.html para manejar el selector de componentes

// Variables globales para componentes
let fileComponents = [];
let selectedComponents = [];

// Función para cargar componentes con vistas previas
async function fetchComponents() {
    // Asegurarse de que tenemos un archivo actual
    if (!currentFile) {
        alert('Error: No hay ningún archivo seleccionado. Por favor, selecciona un archivo de Figma primero.');
        return;
    }

    const contentArea = document.getElementById('component-selector-content');
    const componentGrid = document.getElementById('component-selector-grid');

    // Mostrar cargando
    contentArea.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <p>Cargando componentes del archivo...</p>
        </div>
    `;
    contentArea.style.display = 'block';
    componentGrid.style.display = 'none';
    
    try {
        const response = await fetch(`${API_BASE}/figma/files/${currentFile.key}/components-with-thumbnails`);
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Error ${response.status}: ${errorText}`);
        }
        
        const data = await response.json();
        
        // Guardar los componentes en variable global
        if (data.status === 'success' && data.components && data.components.length > 0) {
            fileComponents = data.components;
            
            // Habilitar botones
            document.getElementById('select-all-btn').disabled = false;
            document.getElementById('deselect-all-btn').disabled = false;
            document.getElementById('component-filter-container').style.display = 'block';
            
            // Mostrar los componentes
            displayComponents(fileComponents);
        } else {
            contentArea.innerHTML = `
                <div class="message-box warning">
                    <h3>⚠️ No se encontraron componentes</h3>
                    <p>Este archivo no contiene componentes o no se pudieron cargar.</p>
                </div>
            `;
            componentGrid.style.display = 'none';
            contentArea.style.display = 'block';
        }
    } catch (error) {
        console.error('Error fetching components:', error);
        contentArea.innerHTML = `
            <div class="message-box error">
                <h3>❌ Error al cargar componentes</h3>
                <p>${error.message}</p>
            </div>
        `;
        componentGrid.style.display = 'none';
        contentArea.style.display = 'block';
    }
}

// Función para mostrar componentes en la interfaz
function displayComponents(components) {
    const contentArea = document.getElementById('component-selector-content');
    const componentGrid = document.getElementById('component-selector-grid');
    
    if (!components || components.length === 0) {
        contentArea.innerHTML = `
            <div class="message-box warning">
                <h3>⚠️ No se encontraron componentes</h3>
                <p>Este archivo no contiene componentes.</p>
            </div>
        `;
        componentGrid.style.display = 'none';
        contentArea.style.display = 'block';
        return;
    }
    
    // Organizar por grupos
    const componentGroups = {};
    components.forEach(component => {
        const baseName = component.base_name || 'Sin Grupo';
        if (!componentGroups[baseName]) {
            componentGroups[baseName] = [];
        }
        componentGroups[baseName].push(component);
    });
    
    // Construir HTML
    let html = '';
    
    // Para cada grupo de componentes
    for (const groupName in componentGroups) {
        const groupComponents = componentGroups[groupName];
        
        html += `
            <div class="component-group">
                <div class="component-group-header">
                    <h3>${groupName}</h3>
                    <span class="component-count">${groupComponents.length} componente${groupComponents.length !== 1 ? 's' : ''}</span>
                </div>
                <div class="component-group-items">
        `;
        
        // Agregar componentes individuales
        groupComponents.forEach(component => {
            const hasImage = component.thumbnail_url ? true : false;
            const id = component.node_id;
            const isSelected = selectedComponents.includes(id);
            
            html += `
                <div class="component-item ${isSelected ? 'selected' : ''}" data-id="${id}">
                    <div class="component-checkbox">
                        <input type="checkbox" id="comp-${id}" ${isSelected ? 'checked' : ''} 
                            onchange="toggleComponentSelection('${id}')">
                    </div>
                    <div class="component-preview" onclick="toggleComponentSelection('${id}')">
                        ${hasImage 
                            ? `<img src="${component.thumbnail_url}" alt="${component.name}" loading="lazy">` 
                            : `<div class="no-preview">Sin Vista Previa</div>`
                        }
                    </div>
                    <div class="component-info">
                        <div class="component-name">${component.name}</div>
                        <div class="component-page-name">${component.page_name || 'Sin página'}</div>
                        ${component.is_variant 
                            ? `<div class="component-variant-badge">Variante</div>` 
                            : ''
                        }
                    </div>
                </div>
            `;
        });
        
        html += `
                </div>
            </div>
        `;
    }
    
    // Mostrar componentes
    componentGrid.innerHTML = html;
    contentArea.style.display = 'none';
    componentGrid.style.display = 'grid';
    
    // Actualizar contador
    updateSelectedCount();
}

// Función para alternar la selección de un componente
function toggleComponentSelection(id) {
    const checkbox = document.getElementById(`comp-${id}`);
    const componentItem = document.querySelector(`.component-item[data-id="${id}"]`);
    
    // Si ya está seleccionado, deseleccionar
    const index = selectedComponents.indexOf(id);
    if (index !== -1) {
        selectedComponents.splice(index, 1);
        componentItem.classList.remove('selected');
        if (checkbox) checkbox.checked = false;
    } else {
        // Si no está seleccionado, seleccionar
        selectedComponents.push(id);
        componentItem.classList.add('selected');
        if (checkbox) checkbox.checked = true;
    }
    
    // Actualizar contador y estado del botón
    updateSelectedCount();
}

// Función para seleccionar todos los componentes
function selectAllComponents() {
    // Limpiar selección actual
    selectedComponents = [];
    
    // Seleccionar todos los componentes visibles
    const componentItems = document.querySelectorAll('.component-item');
    componentItems.forEach(item => {
        const id = item.dataset.id;
        selectedComponents.push(id);
        item.classList.add('selected');
        
        const checkbox = document.getElementById(`comp-${id}`);
        if (checkbox) checkbox.checked = true;
    });
    
    // Actualizar contador
    updateSelectedCount();
}

// Función para deseleccionar todos los componentes
function deselectAllComponents() {
    // Limpiar selección
    selectedComponents = [];
    
    // Deseleccionar todos los componentes visibles
    const componentItems = document.querySelectorAll('.component-item');
    componentItems.forEach(item => {
        item.classList.remove('selected');
        
        const checkbox = document.getElementById(`comp-${id}`);
        if (checkbox) checkbox.checked = false;
    });
    
    // Actualizar contador
    updateSelectedCount();
}

// Función para actualizar el contador de componentes seleccionados
function updateSelectedCount() {
    const generateBtn = document.getElementById('generate-selected-btn');
    
    if (selectedComponents.length > 0) {
        generateBtn.innerHTML = `🚀 Generar ${selectedComponents.length} Componentes`;
        generateBtn.disabled = false;
    } else {
        generateBtn.innerHTML = `🚀 Generar Seleccionados`;
        generateBtn.disabled = true;
    }
}

// Función para generar los componentes seleccionados
async function generateSelectedComponents() {
    if (!selectedComponents.length) {
        alert("Por favor, selecciona al menos un componente para generar.");
        return;
    }

    // Mostrar mensaje de progreso
    const contentArea = document.getElementById('component-selector-content');
    contentArea.style.display = 'block';
    document.getElementById('component-selector-grid').style.display = 'none';
    
    contentArea.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <p>Iniciando generación de ${selectedComponents.length} componentes...</p>
            <div id="generation-progress">
                <div class="progress-label">Preparando datos...</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: 0%"></div>
                </div>
            </div>
        </div>
    `;

    try {
        // Obtener detalles de los componentes seleccionados
        const componentsToGenerate = fileComponents.filter(comp => 
            selectedComponents.includes(comp.node_id)
        );
        
        // Crear lista para seguimiento de resultados
        const results = [];
        let completed = 0;

            
            // Preparar los datos para la generación por lotes
            const componentsToSend = componentsToGenerate.map(comp => ({
                node_id: comp.node_id,
                name: comp.name
            }));
            
            // Actualizar la barra de progreso
            const progressLabel = document.querySelector('.progress-label');
            const progressFill = document.querySelector('.progress-fill');
            
            progressLabel.textContent = `Enviando solicitud para ${componentsToGenerate.length} componentes...`;
            progressFill.style.width = `10%`; // Indicar que el proceso ha comenzado
            
            try {
                // Llamar a la API para generar todos los componentes
                const response = await fetch(`${API_BASE}/figma/generate-multiple-components`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        file_key: currentFile.key,
                        components: componentsToSend
                    })
                });
                
                // Actualizar progreso a 80%
                progressLabel.textContent = `Procesando respuesta...`;
                progressFill.style.width = `80%`;
                
                const batchResult = await response.json();
                
                // Actualizar progreso a 100%
                progressLabel.textContent = `Completado!`;
                progressFill.style.width = `100%`;
                
                if (batchResult.status === 'success') {
                    // Mapear los resultados y mostrarlos
                    const mappedResults = batchResult.results.map(result => ({
                        name: result.name,
                        node_id: result.node_id,
                        success: result.success,
                        error: result.error || (result.warning ? `Advertencia: ${result.warning}` : null),
                        html_code: result.html_code,
                        css_code: result.css_code,
                        stencil_code: result.stencil_code,
                        storybook_code: result.storybook_code,
                        image_url: result.image_url,
                        component_name: result.component_name,
                        props: result.props,
                        data: result
                    }));
                    
                    // Mostrar resultados después de un breve retraso para que se vea la barra al 100%
                    setTimeout(() => {
                        showGenerationResults(mappedResults);
                    }, 500);
                    return;
                } else {
                    throw new Error(batchResult.detail || 'Error desconocido en la generación por lotes');
                }
            } catch (error) {
                console.error('Error en la generación por lotes:', error);
                throw error; // Propagar el error para que se muestre en la UI
            }        // Mostrar resultados de la generación
        showGenerationResults(results);
        
    } catch (error) {
        console.error('Error en generación de componentes:', error);
        contentArea.innerHTML = `
            <div class="message-box error">
                <h3>❌ Error al generar componentes</h3>
                <p>${error.message}</p>
                <button onclick="fetchComponents()" class="btn-primary" style="margin-top: 1rem;">
                    🔄 Volver a la selección de componentes
                </button>
            </div>
        `;
    }
}

// Función para mostrar los resultados de la generación
function showGenerationResults(results) {
    const contentArea = document.getElementById('component-selector-content');
    
    // Contar éxitos y errores
    const successCount = results.filter(r => r.success).length;
    const errorCount = results.length - successCount;
    
    let html = `
        <div class="generation-results">
            <h3>Resultados de la Generación</h3>
            <div class="results-summary">
                <div class="summary-item success">
                    <div class="summary-count">${successCount}</div>
                    <div class="summary-label">Exitosos</div>
                </div>
                <div class="summary-item error">
                    <div class="summary-count">${errorCount}</div>
                    <div class="summary-label">Errores</div>
                </div>
                <div class="summary-item total">
                    <div class="summary-count">${results.length}</div>
                    <div class="summary-label">Total</div>
                </div>
            </div>
            
            <div class="results-details">
                <h4>Detalles de la generación:</h4>
                <div class="results-list">
    `;
    
    results.forEach(result => {
        html += `
            <div class="result-item ${result.success ? 'success' : 'error'}">
                <div class="result-status">${result.success ? '✅' : '❌'}</div>
                <div class="result-name">${result.name}</div>
                <div class="result-message">
                    ${result.success 
                        ? 'Generado correctamente' 
                        : `Error: ${result.error || (result.data && result.data.error) || 'Error desconocido'}`
                    }
                </div>
                ${result.success ? `
                <div class="result-actions">
                    <button class="btn-view-code" onclick="toggleCodeView('${result.node_id}')">
                        📝 Ver código
                    </button>
                </div>` : ''}
            </div>
        `;
    });
    
    html += `
                </div>
            </div>
            
            <!-- Contenedor para mostrar el código generado -->
            <div id="code-preview-container" style="display: none;">
                <div class="code-preview-header">
                    <h4 id="code-preview-title">Código Generado para: <span id="component-name">Componente</span></h4>
                    <div class="code-tabs">
                        <button id="tab-html" class="code-tab active" onclick="switchCodeTab('html')">HTML</button>
                        <button id="tab-css" class="code-tab" onclick="switchCodeTab('css')">CSS</button>
                        <button id="tab-tsx" class="code-tab" onclick="switchCodeTab('tsx')">Stencil (TSX)</button>
                        <button id="tab-storybook" class="code-tab" onclick="switchCodeTab('storybook')">Storybook</button>
                    </div>
                </div>
                <div class="preview-component-container">
                    <div class="component-image-container" id="component-image-container">
                        <!-- La imagen del componente se insertará aquí -->
                    </div>
                    <div class="code-preview-content">
                        <pre id="code-preview-html" class="code-block active"><code></code></pre>
                        <pre id="code-preview-css" class="code-block"><code></code></pre>
                        <pre id="code-preview-tsx" class="code-block"><code></code></pre>
                        <pre id="code-preview-storybook" class="code-block"><code></code></pre>
                    </div>
                </div>
                <button class="btn-secondary close-preview" onclick="closeCodePreview()">Cerrar</button>
            </div>
            
            <div class="results-actions">
                <button onclick="fetchComponents()" class="btn-secondary">
                    🔙 Volver a la selección
                </button>
                ${successCount > 0 ? `
                <button onclick="showGeneratedComponentsGallery()" class="btn-primary">
                    📋 Ver Componentes Generados
                </button>` : ''}
            </div>
        </div>
    `;
    
    contentArea.innerHTML = html;
    
    // Almacenamos los resultados para acceder después
    window.generatedResults = {};
    results.forEach(result => {
        if (result.success) {
            window.generatedResults[result.node_id] = {
                name: result.name,
                html_code: result.html_code || 'No se generó código HTML',
                css_code: result.css_code || 'No se generó código CSS',
                stencil_code: result.stencil_code || 'No se generó código Stencil',
                storybook_code: result.storybook_code || 'No se generó código Storybook',
                image_url: result.image_url,
                component_name: result.component_name || result.name
            };
        }
    });
    
    // Añadir estilos para la visualización del código
    const codeStyle = document.createElement('style');
    codeStyle.textContent = `
        .code-preview-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 20px;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }
        .code-tabs {
            display: flex;
            gap: 10px;
        }
        .code-tab {
            padding: 8px 16px;
            border: 1px solid #ddd;
            border-radius: 4px;
            background: #f5f5f5;
            cursor: pointer;
            font-size: 14px;
        }
        .code-tab.active {
            background: #667eea;
            color: white;
            border-color: #5a6acf;
        }
        .preview-component-container {
            display: flex;
            gap: 20px;
            margin-top: 15px;
        }
        .component-image-container {
            flex: 0 0 300px;
            border: 1px solid #eee;
            border-radius: 6px;
            padding: 10px;
            background: #f9f9f9;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .component-image-container img {
            max-width: 100%;
            max-height: 500px;
            object-fit: contain;
        }
        .code-preview-content {
            flex: 1;
            border: 1px solid #eee;
            border-radius: 6px;
            overflow: hidden;
        }
        .code-block {
            display: none;
            margin: 0;
            padding: 15px;
            background-color: #f8f8f8;
            max-height: 500px;
            overflow: auto;
            font-family: monospace;
            white-space: pre-wrap;
            line-height: 1.5;
        }
        .code-block.active {
            display: block;
        }
        .close-preview {
            margin-top: 10px;
        }
        .result-actions {
            margin-left: auto;
        }
        .btn-view-code {
            background: #f0f0f0;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 12px;
            cursor: pointer;
        }
        .btn-view-code:hover {
            background: #e0e0e0;
        }
    `;
    document.head.appendChild(codeStyle);
}

// Función para mostrar el código de un componente
function toggleCodeView(nodeId) {
    const codeContainer = document.getElementById('code-preview-container');
    const componentData = window.generatedResults[nodeId];
    
    if (!componentData) {
        console.error('No se encontraron datos para el componente:', nodeId);
        return;
    }
    
    // Actualizar el título
    document.getElementById('component-name').textContent = componentData.component_name || componentData.name;
    
    // Actualizar el contenido de los bloques de código
    document.querySelector('#code-preview-html code').textContent = componentData.html_code;
    document.querySelector('#code-preview-css code').textContent = componentData.css_code;
    document.querySelector('#code-preview-tsx code').textContent = componentData.stencil_code;
    document.querySelector('#code-preview-storybook code').textContent = componentData.storybook_code;
    
    // Añadir la imagen del componente
    const imageContainer = document.getElementById('component-image-container');
    if (componentData.image_url) {
        imageContainer.innerHTML = `
            <h4>Diseño Original (Figma)</h4>
            <img src="${componentData.image_url}" alt="${componentData.component_name || componentData.name}" />
        `;
    } else {
        imageContainer.innerHTML = `
            <h4>Diseño Original (Figma)</h4>
            <div class="no-image-available">No hay imagen disponible</div>
        `;
    }
    
    // Mostrar el contenedor de código
    codeContainer.style.display = 'block';
    
    // Asegurarse de que la pestaña HTML esté seleccionada por defecto
    switchCodeTab('html');
    
    // Desplazarse hasta el contenedor de código
    codeContainer.scrollIntoView({ behavior: 'smooth' });
}

// Función para cambiar entre pestañas de código
function switchCodeTab(tabName) {
    // Desactivar todas las pestañas y bloques
    document.querySelectorAll('.code-tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.code-block').forEach(block => block.classList.remove('active'));
    
    // Activar la pestaña seleccionada
    document.getElementById(`tab-${tabName}`).classList.add('active');
    document.getElementById(`code-preview-${tabName}`).classList.add('active');
}

// Función para cerrar la vista previa del código
function closeCodePreview() {
    const codeContainer = document.getElementById('code-preview-container');
    codeContainer.style.display = 'none';
}

// Función para mostrar la galería de componentes generados
function showGeneratedComponentsGallery() {
    // Si no hay resultados generados, no hacer nada
    if (!window.generatedResults || Object.keys(window.generatedResults).length === 0) {
        alert("No hay componentes generados para mostrar");
        return;
    }

    const contentArea = document.getElementById('component-selector-content');
    contentArea.style.display = 'block';
    document.getElementById('component-selector-grid').style.display = 'none';
    
    let html = `
        <div class="components-gallery">
            <h3>🎉 Componentes Generados</h3>
            
            <div class="gallery-grid">
    `;
    
    // Crear un panel para cada componente generado exitosamente
    Object.entries(window.generatedResults).forEach(([nodeId, component]) => {
        html += `
            <div class="gallery-item">
                <div class="gallery-header">
                    <h4>${component.component_name || component.name}</h4>
                </div>
                <div class="gallery-preview">
                    <div class="preview-tabs">
                        <button class="preview-tab active" onclick="switchPreviewTab('${nodeId}', 'figma')">Figma</button>
                        <button class="preview-tab" onclick="switchPreviewTab('${nodeId}', 'preview')">Preview HTML</button>
                        <button class="preview-tab" onclick="switchPreviewTab('${nodeId}', 'html')">HTML</button>
                        <button class="preview-tab" onclick="switchPreviewTab('${nodeId}', 'css')">CSS</button>
                        <button class="preview-tab" onclick="switchPreviewTab('${nodeId}', 'tsx')">TSX</button>
                        <button class="preview-tab" onclick="switchPreviewTab('${nodeId}', 'storybook')">Storybook</button>
                    </div>
                    <div class="preview-content">
                        <div class="preview-panel active" id="preview-${nodeId}-figma">
                            <div class="component-preview-container">
                                <h4>Imagen original de Figma</h4>
                                <div class="figma-image-container">
                                    ${component.image_url ? 
                                        `<img src="${component.image_url}" alt="${component.name}" class="figma-component-image" />` : 
                                        '<div class="no-image-available">No hay imagen disponible</div>'}
                                </div>
                            </div>
                        </div>
                        <div class="preview-panel" id="preview-${nodeId}-preview">
                            <div class="component-preview-container">
                                <h4>Vista previa del componente HTML</h4>
                                <div class="component-preview-iframe">
                                    <iframe srcdoc="${generatePreviewHTML(component)}" frameborder="0" width="100%" height="300"></iframe>
                                </div>
                            </div>
                        </div>
                        <pre class="preview-panel code-block" id="preview-${nodeId}-html"><code>${escapeHTML(component.html_code)}</code></pre>
                        <pre class="preview-panel code-block" id="preview-${nodeId}-css"><code>${escapeHTML(component.css_code)}</code></pre>
                        <pre class="preview-panel code-block" id="preview-${nodeId}-tsx"><code>${escapeHTML(component.stencil_code)}</code></pre>
                        <pre class="preview-panel code-block" id="preview-${nodeId}-storybook"><code>${escapeHTML(component.storybook_code)}</code></pre>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += `
            </div>
            
            <div class="gallery-actions">
                <button onclick="fetchComponents()" class="btn-secondary">
                    🔙 Volver a la selección
                </button>
            </div>
        </div>
    `;
    
    contentArea.innerHTML = html;
    
    // Añadir estilos para la galería
    const galleryStyle = document.createElement('style');
    galleryStyle.textContent = `
        .components-gallery {
            padding: 20px 0;
        }
        
        .gallery-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 30px;
            margin-top: 20px;
        }
        
        .gallery-item {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
            background: white;
        }
        
        .gallery-header {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 15px;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .gallery-header h4 {
            margin: 0;
            font-size: 16px;
        }
        
        .preview-tabs {
            display: flex;
            background: #f5f5f5;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .preview-tab {
            padding: 10px 15px;
            border: none;
            background: none;
            cursor: pointer;
            font-size: 14px;
            flex: 1;
        }
        
        .preview-tab.active {
            background: white;
            font-weight: bold;
            border-bottom: 3px solid #667eea;
        }
        
        .preview-content {
            position: relative;
            height: 350px;
        }
        
        .preview-panel {
            display: none;
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            overflow: auto;
            margin: 0;
            padding: 15px;
            background: #f8f8f8;
        }
        
        .preview-panel.active {
            display: block;
        }
        
        .component-preview-container {
            height: 100%;
            display: flex;
            flex-direction: column;
        }
        
        .component-preview-container h4 {
            margin-top: 0;
            margin-bottom: 10px;
            font-size: 14px;
            color: #666;
            text-align: center;
        }
        
        .component-preview-iframe {
            flex: 1;
            height: 100%;
            width: 100%;
            overflow: auto;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            background: white;
        }
        
        .component-preview-iframe iframe {
            height: 100%;
            background: white;
        }
        
        .figma-image-container {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
            width: 100%;
            background-color: #f0f0f0;
            overflow: hidden;
            padding: 15px;
        }
        
        .figma-component-image {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-radius: 4px;
            background-color: white;
        }
        
        .no-image-available {
            padding: 30px;
            text-align: center;
            color: #999;
            border: 2px dashed #ddd;
            border-radius: 8px;
            width: 100%;
        }
        
        .gallery-actions {
            margin-top: 30px;
            display: flex;
            justify-content: flex-end;
        }
    `;
    document.head.appendChild(galleryStyle);
}

// Función para cambiar entre las pestañas de la vista previa
function switchPreviewTab(nodeId, tabName) {
    // Encontrar el panel de vista previa
    const targetPanel = document.getElementById(`preview-${nodeId}-${tabName}`);
    if (!targetPanel) return;
    
    // Encontrar el elemento padre (gallery-item) navegando hacia arriba en el DOM
    let parentElement = targetPanel.closest('.gallery-item');
    if (!parentElement) return;
    
    // Desactivar todas las pestañas y paneles para este componente
    parentElement.querySelectorAll('.preview-tab').forEach(tab => tab.classList.remove('active'));
    parentElement.querySelectorAll('.preview-panel').forEach(panel => panel.classList.remove('active'));
    
    // Activar la pestaña y panel seleccionados
    parentElement.querySelector(`.preview-tab:nth-child(${getTabIndex(tabName)})`).classList.add('active');
    targetPanel.classList.add('active');
}

// Función auxiliar para obtener el índice de la pestaña
function getTabIndex(tabName) {
    switch(tabName) {
        case 'figma': return 1;
        case 'preview': return 2;
        case 'html': return 3;
        case 'css': return 4;
        case 'tsx': return 5;
        case 'storybook': return 6;
        default: return 1;
    }
}

// Función para generar el HTML para la vista previa del componente
function generatePreviewHTML(component) {
    // Escapar las comillas para que no rompan el atributo srcdoc
    const escapedHTML = component.html_code.replace(/"/g, '&quot;');
    const escapedCSS = component.css_code.replace(/"/g, '&quot;');
    
    // Obtener el nombre del componente para mostrar en la vista previa
    const componentName = component.component_name || component.name;
    
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {
                    margin: 0;
                    padding: 0;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                    background-color: #f9f9f9;
                    display: flex;
                    flex-direction: column;
                    height: 100vh;
                }
                
                .preview-header {
                    background: #f0f0f0;
                    padding: 8px;
                    text-align: center;
                    border-bottom: 1px solid #ddd;
                    font-size: 12px;
                    color: #666;
                }
                
                .preview-container {
                    flex: 1;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 20px;
                    position: relative;
                }
                
                .preview-container::before {
                    content: "";
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: 
                        linear-gradient(45deg, #f0f0f0 25%, transparent 25%),
                        linear-gradient(-45deg, #f0f0f0 25%, transparent 25%),
                        linear-gradient(45deg, transparent 75%, #f0f0f0 75%),
                        linear-gradient(-45deg, transparent 75%, #f0f0f0 75%);
                    background-size: 20px 20px;
                    background-position: 0 0, 0 10px, 10px -10px, -10px 0px;
                    opacity: 0.3;
                    z-index: -1;
                }
                
                .component-wrapper {
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    border-radius: 4px;
                    background: white;
                    max-width: 100%;
                    overflow: auto;
                    padding: 20px;
                }
                
                /* Estilos del componente */
                ${escapedCSS}
            </style>
        </head>
        <body>
            <div class="preview-container">
                <div class="component-wrapper">
                    <!-- Componente HTML -->
                    ${escapedHTML}
                </div>
            </div>
        </body>
        </html>
    `;
}

// Función para escapar HTML y evitar inyección de código
function escapeHTML(str) {
    if (!str) return 'No se generó código';
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

// Agregar filtro para componentes
document.addEventListener('DOMContentLoaded', function() {
    const filterInput = document.getElementById('component-filter');
    if (filterInput) {
        filterInput.addEventListener('input', function() {
            const filterValue = this.value.toLowerCase();
            
            // Si no hay componentes, no hacer nada
            if (!fileComponents || fileComponents.length === 0) return;
            
            // Si el filtro está vacío, mostrar todos los componentes
            if (!filterValue) {
                displayComponents(fileComponents);
                return;
            }
            
            // Filtrar componentes
            const filteredComponents = fileComponents.filter(component => {
                const name = component.name.toLowerCase();
                return name.includes(filterValue);
            });
            
            // Mostrar componentes filtrados
            displayComponents(filteredComponents);
        });
    }
});

// Estilos adicionales para el selector de componentes
const style = document.createElement('style');
style.textContent = `
    .component-grid {
        display: flex;
        flex-direction: column;
        gap: 20px;
    }
    
    .component-group {
        background-color: #f7f7f7;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .component-group-header {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        padding: 10px 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .component-group-items {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
        gap: 15px;
        padding: 15px;
        background-color: white;
    }
    
    .component-item {
        border: 1px solid #ddd;
        border-radius: 6px;
        overflow: hidden;
        transition: all 0.2s ease;
        position: relative;
    }
    
    .component-item:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .component-item.selected {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.3);
    }
    
    .component-checkbox {
        position: absolute;
        top: 8px;
        right: 8px;
        z-index: 2;
        background-color: white;
        border-radius: 50%;
        width: 22px;
        height: 22px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .component-preview {
        height: 150px;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: #f0f0f0;
        overflow: hidden;
        cursor: pointer;
    }
    
    .component-preview img {
        max-width: 100%;
        max-height: 100%;
        object-fit: contain;
    }
    
    .no-preview {
        color: #999;
        font-size: 12px;
    }
    
    .component-info {
        padding: 10px;
    }
    
    .component-name {
        font-size: 14px;
        font-weight: 500;
        margin-bottom: 2px;
        word-break: break-word;
    }
    
    .component-page-name {
        font-size: 11px;
        color: #666;
        margin-bottom: 4px;
        font-style: italic;
    }
    
    .component-variant-badge {
        display: inline-block;
        background-color: #e6e6ff;
        color: #6366f1;
        font-size: 11px;
        padding: 2px 6px;
        border-radius: 4px;
    }
    
    .message-box {
        padding: 20px;
        border-radius: 8px;
        text-align: center;
        margin: 20px 0;
    }
    
    .message-box.warning {
        background-color: #fff8e6;
        color: #b45309;
        border: 1px solid #fef3c7;
    }
    
    .message-box.error {
        background-color: #fee2e2;
        color: #b91c1c;
        border: 1px solid #fecaca;
    }
    
    .actions-bar {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        margin-bottom: 20px;
    }
    
    /* Estilos para la barra de progreso */
    #generation-progress {
        margin-top: 20px;
        width: 100%;
    }
    
    .progress-label {
        margin-bottom: 5px;
        font-size: 14px;
        color: #666;
    }
    
    .progress-bar {
        height: 10px;
        background-color: #f0f0f0;
        border-radius: 5px;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(45deg, #667eea, #764ba2);
        width: 0;
        transition: width 0.3s ease;
    }
    
    /* Estilos para los resultados de generación */
    .generation-results {
        padding: 20px;
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .results-summary {
        display: flex;
        gap: 15px;
        margin: 20px 0;
    }
    
    .summary-item {
        flex: 1;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        color: white;
    }
    
    .summary-item.success {
        background-color: #10b981;
    }
    
    .summary-item.error {
        background-color: #ef4444;
    }
    
    .summary-item.total {
        background-color: #6366f1;
    }
    
    .summary-count {
        font-size: 24px;
        font-weight: bold;
    }
    
    .summary-label {
        font-size: 14px;
        opacity: 0.9;
    }
    
    .results-details {
        margin-top: 20px;
    }
    
    .results-list {
        max-height: 300px;
        overflow-y: auto;
        border: 1px solid #eee;
        border-radius: 5px;
    }
    
    .result-item {
        display: flex;
        padding: 10px;
        border-bottom: 1px solid #eee;
        align-items: center;
    }
    
    .result-item:last-child {
        border-bottom: none;
    }
    
    .result-item.success {
        background-color: #f0fdf4;
    }
    
    .result-item.error {
        background-color: #fef2f2;
    }
    
    .result-status {
        margin-right: 10px;
        font-size: 18px;
    }
    
    .result-name {
        font-weight: 500;
        flex: 1;
    }
    
    .result-message {
        font-size: 13px;
        color: #666;
    }
    
    .results-actions {
        margin-top: 20px;
        display: flex;
        gap: 10px;
        justify-content: flex-end;
    }
    
    /* Estilos para la visualización de código */
    #code-preview-container {
        background-color: #fff;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 20px 0;
        padding: 15px;
        border: 1px solid #e0e0e0;
    }
    
    .code-block {
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 14px;
        line-height: 1.4;
    }
    
    .code-block code {
        color: #333;
    }
    
    /* Colores de sintaxis básicos */
    .code-block .keyword {
        color: #0000ff;
    }
    
    .code-block .string {
        color: #a31515;
    }
    
    .code-block .comment {
        color: #008000;
    }
    
    .code-block .function {
        color: #795e26;
    }
    
    .code-block .tag {
        color: #800000;
    }
    
    .code-block .attribute {
        color: #ff0000;
    }
`;

document.head.appendChild(style);
