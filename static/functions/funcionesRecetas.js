 document.addEventListener('DOMContentLoaded', function() {
    const detallesContainer = document.getElementById('detallesContainer');
    const btnAgregarDetalle = document.getElementById('btnAgregarDetalle');
    let contadorDetalles = 0;

    // Función para cargar formatos cuando cambia el insumo
    function cargarFormatos(insumoSelect, formatoSelect) {
        const idInsumo = insumoSelect.value;
        const unidadBase = insumoSelect.options[insumoSelect.selectedIndex].dataset.unidadBase;
        
        formatoSelect.innerHTML = '<option value="" selected disabled>Seleccione formato</option>';
        
        if (idInsumo) {
            fetch(`/api/insumos/${idInsumo}/formatos`)
                .then(response => response.json())
                .then(formatos => {
                    formatos.forEach(formato => {
                        const option = document.createElement('option');
                        option.value = formato.id;
                        option.textContent = `${formato.nombre} (equivale a ${formato.equivalencia} ${unidadBase})`;
                        formatoSelect.appendChild(option);
                    });
                });
        }
    }

    // Event listener para cambios en los selects de insumo
    detallesContainer.addEventListener('change', function(e) {
        if (e.target.classList.contains('insumo-select')) {
            const detalleItem = e.target.closest('.detalle-item');
            const formatoSelect = detalleItem.querySelector('.unidad-select');
            cargarFormatos(e.target, formatoSelect);
        }
    });

    // Función para crear nuevo detalle (versión corregida)
function crearNuevoDetalle(index) {
    const nuevoDetalle = document.createElement('div');
    nuevoDetalle.className = 'detalle-item mb-3 border p-3 rounded';
    
    // Obtener opciones originales del primer select
    const primerInsumoSelect = document.querySelector('.insumo-select');
    const opcionesOriginales = Array.from(primerInsumoSelect.querySelectorAll('option'))
        .filter(opt => opt.value !== "")
        .map(opt => `<option value="${opt.value}" data-unidad-base="${opt.dataset.unidadBase}">${opt.text}</option>`)
        .join('');
    
    nuevoDetalle.innerHTML = `
        <div class="row">
            <div class="col-md-4">
                <label class="form-label">Insumo</label>
                <select class="form-select insumo-select" name="detalles[${index}][idInsumoFK]" required>
                    <option value="" selected disabled>Seleccione un insumo</option>
                    ${opcionesOriginales}
                </select>
            </div>
            <div class="col-md-4">
                <label class="form-label">Formato</label>
                <select class="form-select unidad-select" name="detalles[${index}][idUnidadFK]" required>
                    <option value="" selected disabled>Seleccione formato</option>
                </select>
            </div>
            <div class="col-md-3">
                <label class="form-label">Cantidad</label>
                <input type="number" step="0.01" min="0.01" class="form-control" name="detalles[${index}][cantidadFormato]" required>
            </div>
            <div class="col-md-1 d-flex align-items-end">
                <button type="button" class="btn btn-danger btn-eliminar-detalle">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        </div>
    `;
    
    return nuevoDetalle;
}

    // Agregar nuevo detalle
    btnAgregarDetalle.addEventListener('click', function() {
        contadorDetalles++;
        const nuevoDetalle = crearNuevoDetalle(contadorDetalles);
        detallesContainer.appendChild(nuevoDetalle);
        actualizarBotonesEliminar();
    });

    // Eliminar detalle
    detallesContainer.addEventListener('click', function(e) {
        if (e.target.closest('.btn-eliminar-detalle')) {
            const detalleItem = e.target.closest('.detalle-item');
            if (detalleItem && document.querySelectorAll('.detalle-item').length > 1) {
                detalleItem.remove();
                reindexarDetalles();
                actualizarBotonesEliminar();
            }
        }
    });

    // Función para reindexar los detalles
    function reindexarDetalles() {
        const detalles = document.querySelectorAll('.detalle-item');
        contadorDetalles = detalles.length - 1;
        
        detalles.forEach((detalle, index) => {
            detalle.querySelectorAll('[name]').forEach(element => {
                const name = element.getAttribute('name')
                    .replace(/\[\d+\]/g, `[${index}]`);
                element.setAttribute('name', name);
            });
        });
    }

    // Función para actualizar botones de eliminar
    function actualizarBotonesEliminar() {
        const detalles = document.querySelectorAll('.detalle-item');
        const botones = document.querySelectorAll('.btn-eliminar-detalle');
        
        botones.forEach((btn, index) => {
            btn.disabled = detalles.length <= 1 && index === 0;
        });
    }

    // Inicializar el primer detalle
    const primerInsumoSelect = document.querySelector('.insumo-select');
    const primerFormatoSelect = document.querySelector('.unidad-select');
    
    // Configurar data attribute para unidad base
    Array.from(primerInsumoSelect.options).forEach(option => {
        if (option.value !== "") {
            const unidadBase = option.text.split('(')[1].split(')')[0].trim();
            option.dataset.unidadBase = unidadBase;
        }
    });

    // Cargar formatos si hay un insumo seleccionado inicialmente
    if (primerInsumoSelect.value) {
        cargarFormatos(primerInsumoSelect, primerFormatoSelect);
    }
});




 // Script para cargar los detalles de la receta
 document.querySelectorAll('.btn-detalles').forEach(button => {
    button.addEventListener('click', function() {
        const recetaId = this.getAttribute('data-id');
        
        fetch(`/api/recetas/${recetaId}/detalles`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error al cargar los detalles');
                }
                return response.json();
            })
            .then(data => {
                // Configurar el título y la información básica
                document.getElementById('detallesModalLabel').textContent = data.nombreReceta;
                document.getElementById('infoGalleta').textContent = `Galleta: ${data.nombreGalleta}`;
                document.getElementById('infoHorneadas').textContent = `Horneadas: ${data.cantidadHorneadas} u.`;
                document.getElementById('infoAnaquel').textContent = `Anaquel: ${data.duracionAnaquel} días`;
                
                // Cargar ingredientes
                const detallesBody = document.getElementById('detallesRecetaBody');
                detallesBody.innerHTML = '';
                
                data.ingredientes.forEach(ingrediente => {
                    const li = document.createElement('li');
                    li.className = 'list-group-item ingredient-item d-flex justify-content-between align-items-center';
                    li.innerHTML = `
                        <div>
                            <span class="fw-bold">${ingrediente.nombreInsumo}</span>
                            <small class="text-muted ms-2">${ingrediente.unidadMedida}</small>
                        </div>
                        <span class="quantity-badge badge rounded-pill">
                            ${ingrediente.cantidad} ${ingrediente.formato}
                        </span>
                    `;
                    detallesBody.appendChild(li);
                });
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error al cargar los detalles de la receta');
            });
    });
});





// -------------------------------
// FUNCIONES GLOBALES DE EDICIÓN
// -------------------------------

// Función para actualizar el estado de los botones de eliminar
function actualizarBotonesEliminarEdit() {
    const detalles = document.querySelectorAll('#detallesContainerEdit .detalle-item');
    const botones = document.querySelectorAll('#detallesContainerEdit .btn-eliminar-detalle');
    const totalDetalles = detalles.length;
    
    botones.forEach(btn => {
        if (btn) {
            // Deshabilitar solo si queda un ingrediente
            btn.disabled = totalDetalles <= 1;
            
            // Cambiar apariencia visual
            if (totalDetalles <= 1) {
                btn.classList.add('disabled');
                btn.setAttribute('title', 'Debe haber al menos un ingrediente');
            } else {
                btn.classList.remove('disabled');
                btn.removeAttribute('title');
            }
        }
    });
}

// Función para reindexar los detalles
function reindexarDetallesEdit() {
    const detalles = document.querySelectorAll('#detallesContainerEdit .detalle-item');
    
    detalles.forEach((detalle, index) => {
        detalle.querySelectorAll('[name]').forEach(element => {
            const name = element.getAttribute('name')
                .replace(/\[\d+\]/g, `[${index}]`);
            element.setAttribute('name', name);
        });
    });
}

// Función para cargar formatos de insumos
async function cargarFormatosParaSelect(idInsumo, selectElement) {
    if (!idInsumo) return;
    
    try {
        const response = await fetch(`/api/insumos/${idInsumo}/formatos`);
        const formatos = await response.json();
        
        selectElement.innerHTML = '<option value="" disabled>Seleccione formato</option>';
        formatos.forEach(formato => {
            const option = document.createElement('option');
            option.value = formato.id;
            option.textContent = `${formato.nombre} (equivale a ${formato.equivalencia} ${formato.unidadBase})`;
            option.setAttribute('data-equivalencia', formato.equivalencia);
            selectElement.appendChild(option);
        });
    } catch (error) {
        console.error('Error cargando formatos:', error);
    }
}

// -------------------------------
// CONFIGURACIÓN DEL MODAL DE EDICIÓN
// -------------------------------

function setupEditRecipeModal() {
    document.querySelectorAll('.btnEditRecetas').forEach(button => {
        button.addEventListener('click', async function() {
            const recetaId = this.getAttribute('data-id');
            
            // Mostrar el modal
            const editarModal = new bootstrap.Modal(document.getElementById('editarModal'));
            editarModal.show();
            
            try {
                // Obtener datos de la receta
                const response = await fetch(`/api/recetas/${recetaId}/editar`);
                
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || 'Error al cargar los datos de la receta');
                }
                
                const data = await response.json();
                
                if (!data || !data.idReceta) {
                    throw new Error('Datos de receta inválidos recibidos del servidor');
                }
                
                // Llenar campos básicos
                document.getElementById('edit_idReceta').value = data.idReceta;
                document.getElementById('edit_nombreReceta').value = data.nombreReceta;
                document.getElementById('edit_idGalletaFK').value = data.idGalletaFK;
                document.getElementById('edit_cantidadHorneadas').value = data.cantidadHorneadas;
                document.getElementById('edit_duracionAnaquel').value = data.duracionAnaquel;
                
                // Cargar ingredientes
                const detallesContainer = document.getElementById('detallesContainerEdit');
                detallesContainer.innerHTML = '';
                
                if (!data.ingredientes || !Array.isArray(data.ingredientes)) {
                    console.warn('No se recibieron ingredientes o formato incorrecto');
                    return;
                }
                
                // Obtener todos los insumos disponibles
                let todosInsumos = [];
                try {
                    const insumosResponse = await fetch('/api/insumos');
                    if (insumosResponse.ok) {
                        todosInsumos = await insumosResponse.json();
                    }
                } catch (error) {
                    console.error('Error cargando insumos:', error);
                }
                
                // Cargar cada ingrediente
                for (const [index, ingrediente] of data.ingredientes.entries()) {
                    const detalleDiv = document.createElement('div');
                    detalleDiv.className = 'detalle-item mb-3 border p-3 rounded';
                    
                    // Crear opciones de insumo
                    let insumoOptions = '<option value="" disabled>Seleccione un insumo</option>';
                    todosInsumos.forEach(insumo => {
                        const selected = ingrediente.idInsumoFK == insumo.id ? 'selected' : '';
                        insumoOptions += `
                            <option value="${insumo.id}" 
                                data-unidad-base="${insumo.unidadBase}"
                                ${selected}>
                                ${insumo.nombre} (${insumo.unidadBase})
                            </option>`;
                    });
                    
                    detalleDiv.innerHTML = `
                        <div class="row">
                            <div class="col-md-4">
                                <label class="form-label">Insumo</label>
                                <select class="form-select insumo-select" name="detalles[${index}][idInsumoFK]" required>
                                    ${insumoOptions}
                                </select>
                            </div>
                            <div class="col-md-4">
                                <label class="form-label">Formato</label>
                                <select class="form-select unidad-select" name="detalles[${index}][idUnidadFK]" required>
                                    <option value="" disabled>Seleccione formato</option>
                                </select>
                            </div>
                            <div class="col-md-3">
                                <label class="form-label">Cantidad</label>
                                <input type="number" step="0.01" min="0.01" class="form-control" 
                                    name="detalles[${index}][cantidadFormato]" 
                                    value="${ingrediente.cantidadFormato}" required>
                            </div>
                            <div class="col-md-1 d-flex align-items-end">
                                <button type="button" class="btn btn-danger btn-eliminar-detalle">
                                    <i class="bi bi-trash"></i>
                                </button>
                            </div>
                        </div>
                    `;
                    
                    detallesContainer.appendChild(detalleDiv);
                    
                    // Configurar selects
                    const insumoSelect = detalleDiv.querySelector('.insumo-select');
                    const formatoSelect = detalleDiv.querySelector('.unidad-select');
                    
                    if (insumoSelect.value) {
                        try {
                            await cargarFormatosParaSelect(insumoSelect.value, formatoSelect);
                            formatoSelect.value = ingrediente.idUnidadFK;
                        } catch (error) {
                            console.error('Error cargando formatos:', error);
                        }
                    }
                    
                    insumoSelect.addEventListener('change', async function() {
                        try {
                            await cargarFormatosParaSelect(this.value, formatoSelect);
                        } catch (error) {
                            console.error('Error al cambiar insumo:', error);
                        }
                    });
                }

                // Actualizar botones después de cargar
                actualizarBotonesEliminarEdit();
                
            } catch (error) {
                console.error('Error en la carga de receta:', error);
                if (!error.message.includes('Datos de receta inválidos')) {
                    alert(error.message || 'Error al cargar los datos de la receta');
                }
            }
        });
    });
}

// -------------------------------
// EVENTOS DEL MODAL DE EDICIÓN
// -------------------------------

function setupEditModalEvents() {
    const detallesContainerEdit = document.getElementById('detallesContainerEdit');
    const btnAgregarDetalleEdit = document.getElementById('btnAgregarDetalleEdit');

    // Función para obtener el próximo índice disponible
    function getNextIndex() {
        const detalles = document.querySelectorAll('#detallesContainerEdit .detalle-item');
        if (detalles.length === 0) return 0;
        
        // Obtener el máximo índice actual + 1
        const maxIndex = Array.from(detalles).reduce((max, detalle) => {
            const inputs = detalle.querySelectorAll('[name]');
            if (inputs.length > 0) {
                const name = inputs[0].getAttribute('name');
                const match = name.match(/\[(\d+)\]/);
                if (match) {
                    const currentIndex = parseInt(match[1]);
                    return currentIndex > max ? currentIndex : max;
                }
            }
            return max;
        }, -1);
        
        return maxIndex + 1;
    }

    // Función para crear nuevo detalle
    async function crearNuevoDetalleEdit() {
        const index = getNextIndex();
        const nuevoDetalle = document.createElement('div');
        nuevoDetalle.className = 'detalle-item mb-3 border p-3 rounded';
        
        // Obtener insumos disponibles
        let insumoOptions = '<option value="" selected disabled>Seleccione un insumo</option>';
        try {
            const response = await fetch('/api/insumos');
            const todosInsumos = await response.json();
            
            todosInsumos.forEach(insumo => {
                insumoOptions += `
                    <option value="${insumo.id}" 
                        data-unidad-base="${insumo.unidadBase}">
                        ${insumo.nombre} (${insumo.unidadBase})
                    </option>`;
            });
        } catch (error) {
            console.error('Error cargando insumos:', error);
        }
        
        nuevoDetalle.innerHTML = `
            <div class="row">
                <div class="col-md-4">
                    <label class="form-label">Insumo</label>
                    <select class="form-select insumo-select" name="detalles[${index}][idInsumoFK]" required>
                        ${insumoOptions}
                    </select>
                </div>
                <div class="col-md-4">
                    <label class="form-label">Formato</label>
                    <select class="form-select unidad-select" name="detalles[${index}][idUnidadFK]" required>
                        <option value="" selected disabled>Seleccione formato</option>
                    </select>
                </div>
                <div class="col-md-3">
                    <label class="form-label">Cantidad</label>
                    <input type="number" step="0.01" min="0.01" class="form-control" 
                        name="detalles[${index}][cantidadFormato]" required>
                </div>
                <div class="col-md-1 d-flex align-items-end">
                    <button type="button" class="btn btn-danger btn-eliminar-detalle">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
        `;
        
        // Configurar evento change
        const insumoSelect = nuevoDetalle.querySelector('.insumo-select');
        const formatoSelect = nuevoDetalle.querySelector('.unidad-select');
        
        insumoSelect.addEventListener('change', async function() {
            await cargarFormatosParaSelect(this.value, formatoSelect);
        });
        
        return nuevoDetalle;
    }

    // Evento para agregar ingrediente
    if (btnAgregarDetalleEdit) {
        btnAgregarDetalleEdit.addEventListener('click', async function() {
            const nuevoDetalle = await crearNuevoDetalleEdit();
            detallesContainerEdit.appendChild(nuevoDetalle);
            actualizarBotonesEliminarEdit();
        });
    }

    // Evento para eliminar ingrediente
    if (detallesContainerEdit) {
        detallesContainerEdit.addEventListener('click', function(e) {
            if (e.target.closest('.btn-eliminar-detalle')) {
                const detalleItem = e.target.closest('.detalle-item');
                if (detalleItem) {
                    const totalDetalles = document.querySelectorAll('#detallesContainerEdit .detalle-item').length;
                    if (totalDetalles > 1) {
                        detalleItem.remove();
                        reindexarDetallesEdit();
                        actualizarBotonesEliminarEdit();
                    }
                }
            }
        });
    }
}

// -------------------------------
// INICIALIZACIÓN
// -------------------------------

document.addEventListener('DOMContentLoaded', function() {
    setupEditRecipeModal();
    setupEditModalEvents();
});



// Configuración del modal de desactivar receta
document.addEventListener("DOMContentLoaded", function () {
    const eliminarRecetaModal = document.getElementById("eliminarRecetaModal");
    
    eliminarRecetaModal.addEventListener("show.bs.modal", function (event) {
        const button = event.relatedTarget;
        const idReceta = button.getAttribute("data-receta-id");
        document.getElementById("idRecetaEliminar").value = idReceta;
    });
});


// configuración del tiempo de alertas
document.addEventListener("DOMContentLoaded", function () {
    // Tiempo de alerta
    setTimeout(() => {
        document.querySelectorAll(".alert").forEach(alert => {
            alert.style.opacity = "0";
            setTimeout(() => alert.remove(), 500);
        });
    }, 4000);
  });

// -------------------------------
// FUNCIONES PARA SANITIZAR ENTRADAS
// -------------------------------
(function () {
    'use strict';
    const form = document.getElementById('formReceta');

    function sanitizeInput(input) {
        if (input.value && input.type !== 'password') {
            input.value = input.value
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#039;');
        }
    }

    function validateField(input) {
        const isValid = input.checkValidity();

        if (isValid) {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
        } else {
            input.classList.remove('is-valid');
            input.classList.add('is-invalid');
        }

        return isValid;
    }

    // Detectar todos los campos de entrada
    function applyValidationListeners(container) {
        const inputs = container.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.addEventListener('input', function () {
                clearTimeout(this.debounceTimer);
                this.debounceTimer = setTimeout(() => {
                    validateField(this);
                }, 400);
            });

            input.addEventListener('blur', function () {
                sanitizeInput(this);
                validateField(this);
            });

            input.addEventListener('focus', function () {
                if (this.title) {
                    this.setAttribute('data-original-title', this.title);
                }
            });
        });
    }

    applyValidationListeners(form); // Aplicar en los elementos iniciales

    // Formulario completo al enviar
    form.addEventListener('submit', function (event) {
        const allInputs = form.querySelectorAll('input, select');
        let isFormValid = true;

        allInputs.forEach(input => {
            sanitizeInput(input);
            if (!validateField(input)) {
                isFormValid = false;
            }
        });

        if (!isFormValid) {
            event.preventDefault();
            event.stopPropagation();

            const firstInvalid = form.querySelector('.is-invalid');
            if (firstInvalid) firstInvalid.focus();

            const errorAlert = document.getElementById('formRecetaErrorAlert');
            errorAlert.innerHTML = '<div class="alert alert-danger">Por favor, corrige los errores marcados en el formulario.</div>';
        }

        form.classList.add('was-validated');
    }, false);

    // Validar dinámicamente al agregar nuevos ingredientes
    document.getElementById('btnAgregarDetalle').addEventListener('click', () => {
        setTimeout(() => {
            const nuevosDetalles = form.querySelectorAll('.detalle-item');
            const ultimoDetalle = nuevosDetalles[nuevosDetalles.length - 1];
            applyValidationListeners(ultimoDetalle);
        }, 200);
    });

})();

// -------------------------------
// FUNCIONES PARA SANITIZAR ENTRADAS EN EL MODAL DE EDICIÓN
// -------------------------------
(function () {
    'use strict';
    const form = document.getElementById('formEditarReceta');

    // Función de sanitización
    function sanitizeInput(input) {
        if (input.value && input.type !== 'password') {
            input.value = input.value
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#039;');
        }
    }

    // Función de validación
    function validateField(input) {
        const isValid = input.checkValidity();

        if (isValid) {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
        } else {
            input.classList.remove('is-valid');
            input.classList.add('is-invalid');
        }

        return isValid;
    }

    // Detectar todos los campos de entrada
    function applyValidationListeners(container) {
        const inputs = container.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.addEventListener('input', function () {
                clearTimeout(this.debounceTimer);
                this.debounceTimer = setTimeout(() => {
                    validateField(this);
                }, 400);
            });

            input.addEventListener('blur', function () {
                sanitizeInput(this);
                validateField(this);
            });

            input.addEventListener('focus', function () {
                if (this.title) {
                    this.setAttribute('data-original-title', this.title);
                }
            });
        });
    }

    applyValidationListeners(form); // Aplicar en los elementos iniciales

    // Formulario completo al enviar
    form.addEventListener('submit', function (event) {
        const allInputs = form.querySelectorAll('input, select');
        let isFormValid = true;

        allInputs.forEach(input => {
            sanitizeInput(input);
            if (!validateField(input)) {
                isFormValid = false;
            }
        });

        if (!isFormValid) {
            event.preventDefault();
            event.stopPropagation();

            const firstInvalid = form.querySelector('.is-invalid');
            if (firstInvalid) firstInvalid.focus();

            const errorAlert = document.getElementById('formEditarRecetaErrorAlert');
            errorAlert.innerHTML = '<div class="alert alert-danger">Por favor, corrige los errores marcados en el formulario.</div>';
        }

        form.classList.add('was-validated');
    }, false);

    // Validar dinámicamente al agregar nuevos ingredientes
    document.getElementById('btnAgregarDetalleEdit').addEventListener('click', () => {
        setTimeout(() => {
            const nuevosDetalles = form.querySelectorAll('.detalle-item');
            const ultimoDetalle = nuevosDetalles[nuevosDetalles.length - 1];
            applyValidationListeners(ultimoDetalle);
        }, 200);
    });

})();