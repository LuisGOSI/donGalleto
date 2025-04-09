document.addEventListener("DOMContentLoaded", function () {
    const modalRegistro = document.getElementById("registroModal");
    const btnAgregarInsumo = document.getElementById("btnAgregarInsumo");
    const contenedorInsumos = document.getElementById("insumosContainer");
    const proveedorSelectPrincipal = document.getElementById("proveedor-select");
    let contadorInsumos = 1;

    // Cargar insumos
    function cargarInsumos(selectElement) {
        fetch("/getInsumos")
            .then(response => response.json())
            .then(data => {
                selectElement.innerHTML = "<option value='' selected disabled>Seleccione un insumo</option>";
                data.forEach(insumo => {
                    let option = document.createElement("option");
                    option.value = insumo.idInsumo;
                    option.textContent = insumo.nombreInsumo;
                    option.dataset.unidadMedida = insumo.unidadMedida;
                    selectElement.appendChild(option);
                });
            })
            .catch(error => console.error("Error al obtener los insumos:", error));
    }

    // Cargar presentaciones basadas en proveedor e insumo
    function cargarPresentaciones(selectPresentacion, idInsumo, idProveedor) {
        if (!idProveedor) {
            selectPresentacion.innerHTML = "<option value='' selected disabled>Seleccione proveedor primero</option>";
            return;
        }

        let url = idInsumo 
            ? `/getPresentacionesPorInsumoYProveedor/${idInsumo}/${idProveedor}`
            : `/getPresentacionesPorProveedor/${idProveedor}`;

        fetch(url)
            .then(response => response.json())
            .then(data => {
                selectPresentacion.innerHTML = "<option value='' selected disabled>Seleccione presentación</option>";
                
                if (data.length === 0) {
                    selectPresentacion.innerHTML += "<option value=''>No hay presentaciones disponibles</option>";
                } else {
                    data.forEach(presentacion => {
                        let option = document.createElement("option");
                        option.value = presentacion.idPresentacion;
                        option.textContent = presentacion.nombrePresentacion;
                        selectPresentacion.appendChild(option);
                    });
                }
            })
            .catch(error => console.error("Error al obtener las presentaciones:", error));
    }

    // Cargar proveedores cuando el modal se muestra
    modalRegistro.addEventListener("show.bs.modal", function () {
        fetch("/getProveedores")
            .then(response => response.json())
            .then(data => {
                proveedorSelectPrincipal.innerHTML = "<option value='' selected disabled>Seleccione un proveedor</option>";
                
                if (Array.isArray(data.proveedores)) {
                    data.proveedores.forEach(proveedor => {
                        let option = document.createElement("option");
                        option.value = proveedor.idProveedor;
                        option.textContent = proveedor.nombreProveedor;
                        proveedorSelectPrincipal.appendChild(option);
                    });
                }
            })
            .catch(error => console.error("Error al obtener los proveedores:", error));

        // Cargar insumos para el primer ítem
        cargarInsumos(document.querySelector(".insumo-select"));
    });

    // Cuando cambia el proveedor principal, actualizar todas las presentaciones
    proveedorSelectPrincipal.addEventListener("change", function () {
        const idProveedor = this.value;
        
        // Actualizar presentaciones en todos los ítems de insumo
        document.querySelectorAll(".insumo-item").forEach(item => {
            const selectInsumo = item.querySelector(".insumo-select");
            const selectPresentacion = item.querySelector(".presentacion-select");
            const idInsumo = selectInsumo.value;
            
            cargarPresentaciones(selectPresentacion, idInsumo, idProveedor);
        });
    });

    // Cuando cambia un insumo, actualizar sus presentaciones
    contenedorInsumos.addEventListener("change", function (event) {
        if (event.target.classList.contains("insumo-select")) {
            const idProveedor = proveedorSelectPrincipal.value;
            const selectInsumo = event.target;
            const idInsumo = selectInsumo.value;
            const selectPresentacion = selectInsumo.closest(".insumo-item").querySelector(".presentacion-select");
            
            cargarPresentaciones(selectPresentacion, idInsumo, idProveedor);
        }
    });

    // Evento para agregar un nuevo insumo
    btnAgregarInsumo.addEventListener("click", function () {
        const idProveedor = proveedorSelectPrincipal.value;
        const nuevoInsumoHTML = `
            <div class="insumo-item mb-3 border p-3 rounded">
                <div class="row">
                    <div class="col-md-3">
                        <label class="form-label">Insumo</label>
                        <select class="form-select insumo-select" name="insumos[${contadorInsumos}][idInsumo]" required></select>
                    </div>
                    <div class="col-md-3">
                        <label class="form-label">Presentación</label>
                        <select class="form-select presentacion-select" name="insumos[${contadorInsumos}][idPresentacionFK]" required>
                            <option value="" selected disabled>${idProveedor ? "Seleccione presentación" : "Seleccione proveedor primero"}</option>
                        </select>
                    </div>
                    <div class="col-md-3">
                        <label class="form-label">Cantidad</label>
                        <input type="number" step="0.01" min="0.01" class="form-control" name="insumos[${contadorInsumos}][cantidadCompra]" required>
                    </div>
                </div>
                <div class="row mt-2">
                    <div class="col-md-3">
                        <label class="form-label">Fecha Caducidad</label>
                        <input type="date" class="form-control" name="insumos[${contadorInsumos}][fechaCaducidad]" required>
                    </div>
                    <div class="col-md-1 d-flex align-items-end">
                        <button type="button" class="btn btn-danger btn-eliminar-insumo">Eliminar insumo</button>
                    </div>
                </div>
            </div>`;

        contenedorInsumos.insertAdjacentHTML("beforeend", nuevoInsumoHTML);
        const nuevoSelectInsumo = contenedorInsumos.lastElementChild.querySelector(".insumo-select");
        cargarInsumos(nuevoSelectInsumo);
        
        // Si ya hay un proveedor seleccionado, cargar presentaciones vacías
        if (idProveedor) {
            const selectPresentacion = contenedorInsumos.lastElementChild.querySelector(".presentacion-select");
            selectPresentacion.innerHTML = "<option value='' selected disabled>Seleccione un insumo primero</option>";
        }
        
        contadorInsumos++;
    });

    // Eliminar insumo
    contenedorInsumos.addEventListener("click", function (event) {
        if (event.target.classList.contains("btn-eliminar-insumo")) {
            event.target.closest(".insumo-item").remove();
        }
    });
});


//! Modal de alerta de insumos ============================================================================

document.addEventListener("DOMContentLoaded", function () { 
    var modalCafe = document.getElementById('alertaInsumosCafe');
    var modalAmarillo = document.getElementById('alertaInsumosAmarilla');
    var modalRojo = document.getElementById('alertaInsumosRoja');
    if (modalCafe && modalCafe.querySelector('.modal-body').textContent.trim() !== "") {
        new bootstrap.Modal(modalCafe).show();
    } else if (modalAmarillo && modalAmarillo.querySelector('.modal-body').textContent.trim() !== "") {
        new bootstrap.Modal(modalAmarillo).show();
        modalAmarillo.addEventListener('hidden.bs.modal', function () {
            if (modalRojo && modalRojo.querySelector('.modal-body').textContent.trim() !== "") {
                new bootstrap.Modal(modalRojo).show();
            }
        });
    } else if (modalRojo && modalRojo.querySelector('.modal-body').textContent.trim() !== "") {
        new bootstrap.Modal(modalRojo).show();
    }
});


document.addEventListener("DOMContentLoaded", function () { 
    document.querySelectorAll(".mermas-btn").forEach(button => {
        button.addEventListener("click", function () {
            let row = this.closest("tr");
            let idInsumo = row.querySelectorAll("td")[0].textContent.trim();
            let cantidadActual = row.querySelectorAll("td")[2].textContent.trim();
            document.getElementById("idInventarioInsumoFK").value = idInsumo;
            document.getElementById("cantidadActual").value = cantidadActual;
            
        });
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const modalMermaLote = document.getElementById("modalMermaLote");
    modalMermaLote.addEventListener("show.bs.modal", function (event) {
        const button = event.relatedTarget;
        const idLote = button.getAttribute("data-id-lote");
        const inputIdLoteMerma = modalMermaLote.querySelector("#idLoteMerma");
        inputIdLoteMerma.value = idLote;
    });
});

// Funciones de sanitización y validación para modales de merma y compra de insumos
(function() {
    'use strict';
    
    function sanitizeInput(input) {
        if (input.value) {
            if (input.type !== 'password' && input.type !== 'hidden' && input.type !== 'number' && input.type !== 'date') {
                input.value = input.value
                    .replace(/&/g, '&amp;')
                    .replace(/</g, '&lt;')
                    .replace(/>/g, '&gt;')
                    .replace(/"/g, '&quot;')
                    .replace(/'/g, '&#039;');
            }
        }
    }
    
    function validateField(input) {
        const isValid = input.checkValidity();
        
        if (input.type === 'hidden') return true;
        
        if (isValid) {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
        } else {
            input.classList.remove('is-valid');
            input.classList.add('is-invalid');
        }
        
        return isValid;
    }
    
    function showTemporaryMessage(element, message) {
        let msgElement = element.nextElementSibling;
        if (!msgElement || !msgElement.classList.contains('temp-message')) {
            msgElement = document.createElement('div');
            msgElement.className = 'temp-message text-danger small mt-1';
            element.parentNode.insertBefore(msgElement, element.nextElementSibling);
        }
        
        msgElement.textContent = message;
        setTimeout(() => {
            if (msgElement.parentNode) {
                msgElement.parentNode.removeChild(msgElement);
            }
        }, 3000);
    }
    
    function setupMermaModal() {
        const form = document.getElementById('registroMermaForm');
        if (!form) return;
        
        const inputs = form.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                if (this.type === 'hidden') return;
                
                clearTimeout(this.debounceTimer);
                this.debounceTimer = setTimeout(() => {
                    validateField(this);
                    if (this.id === 'cantidad') {
                        const cantidad = parseFloat(this.value);
                        const cantidadActual = parseFloat(document.getElementById('cantidadActual').value || 0);
                        
                        if (isNaN(cantidad) || cantidad <= 0) {
                            this.classList.add('is-invalid');
                            showTemporaryMessage(this, 'La cantidad debe ser un número positivo');
                        } else if (cantidad > cantidadActual) {
                            this.classList.add('is-invalid');
                            showTemporaryMessage(this, 'La cantidad no puede ser mayor al stock actual');
                        }
                    }
                    
                    if (this.id === 'observaciones') {
                        const maxLength = 500;
                        if (this.value.length > maxLength) {
                            this.value = this.value.substring(0, maxLength);
                            showTemporaryMessage(this, `Limitado a ${maxLength} caracteres`);
                        }
                    }
                }, 500);
            });
            input.addEventListener('blur', function() {
                if (this.type === 'hidden') return;
                
                sanitizeInput(this);
                validateField(this);
            });
        });
        
        form.addEventListener('submit', function(event) {
            let isFormValid = true;
            
            inputs.forEach(input => {
                sanitizeInput(input);
                if (!validateField(input)) {
                    isFormValid = false;
                }
            });
            
            const cantidad = parseFloat(document.getElementById('cantidad').value);
            const cantidadActual = parseFloat(document.getElementById('cantidadActual').value || 0);
            
            if (cantidad > cantidadActual) {
                const cantidadInput = document.getElementById('cantidad');
                cantidadInput.classList.add('is-invalid');
                showTemporaryMessage(cantidadInput, 'La cantidad no puede ser mayor al stock actual');
                isFormValid = false;
            }
            
            if (!isFormValid) {
                event.preventDefault();
                event.stopPropagation();
                
                const firstInvalidField = form.querySelector('.is-invalid');
                if (firstInvalidField) {
                    firstInvalidField.focus();
                }
                
                const errorAlertId = 'registroMermaFormErrorAlert';
                const errorAlert = document.getElementById(errorAlertId);
                if (!errorAlert) {
                    const alert = document.createElement('div');
                    alert.id = errorAlertId;
                    alert.className = 'alert alert-danger mt-3';
                    alert.role = 'alert';
                    alert.innerHTML = 'Por favor, corrige los errores marcados en el formulario.';
                    form.prepend(alert);
                    
                    setTimeout(() => {
                        if (alert.parentNode) {
                            alert.parentNode.removeChild(alert);
                        }
                    }, 5000);
                }
            }
            
            form.classList.add('was-validated');
        }, false);
    }
    function setupCompraInsumosModal() {
        const form = document.getElementById('formCompraInsumos');
        if (!form) return;
        
        function setupInsumoValidation(insumoItem, index) {
            const inputs = insumoItem.querySelectorAll('input, select');
            
            inputs.forEach(input => {
                input.addEventListener('input', function() {
                    if (this.type === 'hidden') return;
                    
                    clearTimeout(this.debounceTimer);
                    this.debounceTimer = setTimeout(() => {
                        validateField(this);
                        if (this.name.includes('cantidadCompra')) {
                            const cantidad = parseFloat(this.value);
                            if (isNaN(cantidad) || cantidad <= 0) {
                                this.classList.add('is-invalid');
                                showTemporaryMessage(this, 'La cantidad debe ser un número positivo');
                            }
                        }
                        if (this.name.includes('fechaCaducidad')) {
                            const fechaSeleccionada = new Date(this.value);
                            const hoy = new Date();
                            
                            if (fechaSeleccionada < hoy) {
                                this.classList.add('is-invalid');
                                showTemporaryMessage(this, 'La fecha de caducidad no puede ser anterior a hoy');
                            }
                        }
                    }, 500);
                });
                
                input.addEventListener('blur', function() {
                    if (this.type === 'hidden') return;
                    
                    sanitizeInput(this);
                    validateField(this);
                });
            });
        }
        
        const insumosItems = form.querySelectorAll('.insumo-item');
        insumosItems.forEach((item, index) => {
            setupInsumoValidation(item, index);
        });
        const btnAgregarInsumo = document.getElementById('btnAgregarInsumo');
        if (btnAgregarInsumo) {
            btnAgregarInsumo.addEventListener('click', function() {
                const insumosContainer = document.getElementById('insumosContainer');
                
                const insumoCount = insumosContainer.querySelectorAll('.insumo-item').length;
                
                const primerInsumo = insumosContainer.querySelector('.insumo-item');
                const nuevoInsumo = primerInsumo.cloneNode(true);
                
                const inputs = nuevoInsumo.querySelectorAll('input, select');
                inputs.forEach(input => {
                    if (input.name) {
                        input.name = input.name.replace(/\[\d+\]/, `[${insumoCount}]`);
                    }
                    
                    if (input.tagName === 'SELECT') {
                        input.selectedIndex = 0;
                    } else {
                        input.value = '';
                    }
                    
                    input.classList.remove('is-valid', 'is-invalid');
                });
                
                const btnEliminar = nuevoInsumo.querySelector('.btn-eliminar-insumo');
                if (btnEliminar) {
                    btnEliminar.disabled = false;
                    
                    btnEliminar.addEventListener('click', function() {
                        insumosContainer.removeChild(nuevoInsumo);
                    });
                }
                
                insumosContainer.appendChild(nuevoInsumo);
                setupInsumoValidation(nuevoInsumo, insumoCount);
            });
        }
        
        form.addEventListener('submit', function(event) {
            let isFormValid = true;
            
            const allInputs = form.querySelectorAll('input, select');
            allInputs.forEach(input => {
                sanitizeInput(input);
                if (!validateField(input)) {
                    isFormValid = false;
                }
            });
            const insumosItems = form.querySelectorAll('.insumo-item');
            if (insumosItems.length === 0) {
                isFormValid = false;
                
                const insumosContainer = document.getElementById('insumosContainer');
                showTemporaryMessage(insumosContainer, 'Debe agregar al menos un insumo');
            }
            
            if (!isFormValid) {
                event.preventDefault();
                event.stopPropagation();
                
                const firstInvalidField = form.querySelector('.is-invalid');
                if (firstInvalidField) {
                    firstInvalidField.focus();
                }
                
                const errorAlertId = 'formCompraInsumosErrorAlert';
                const errorAlert = document.getElementById(errorAlertId);
                if (!errorAlert) {
                    const alert = document.createElement('div');
                    alert.id = errorAlertId;
                    alert.className = 'alert alert-danger mt-3';
                    alert.role = 'alert';
                    alert.innerHTML = 'Por favor, corrige los errores marcados en el formulario.';
                    form.prepend(alert);
                    
                    setTimeout(() => {
                        if (alert.parentNode) {
                            alert.parentNode.removeChild(alert);
                        }
                    }, 5000);
                }
            }
            
            form.classList.add('was-validated');
        }, false);
    }
    document.addEventListener('DOMContentLoaded', function() {
        setupMermaModal();
        setupCompraInsumosModal();
    });
})();