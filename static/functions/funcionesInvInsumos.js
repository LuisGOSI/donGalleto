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

