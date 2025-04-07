document.addEventListener("DOMContentLoaded", function () {
    // Evento para editar proveedor
    document.querySelectorAll(".btnEditProveedores").forEach(button => {
        button.addEventListener("click", function () {
            document.getElementById("IdProveedor").value = this.getAttribute("idProveedor");
            document.getElementById("Nombre").value = this.getAttribute("nombreProveedor");
            document.getElementById("Contacto").value = this.getAttribute("contacto");
            document.getElementById("Telefono").value = this.getAttribute("telefono");
            document.getElementById("Direccion").value = this.getAttribute("direccion");
        });
    });

    // Evento para eliminar proveedor
    document.querySelectorAll(".btnEliminarProveedores").forEach(button => {
        button.addEventListener("click", function () {
            document.getElementById("deleteIdProveedor").value = this.getAttribute("data-id");
            document.getElementById("deleteNombre").textContent = this.getAttribute("nombreProveedor");
            document.getElementById("deleteContacto").textContent = this.getAttribute("contacto");
            document.getElementById("deleteTelefono").textContent = this.getAttribute("telefono");
            document.getElementById("deleteDireccion").textContent = this.getAttribute("direccion");
        });
    });

    document.getElementById('statusSwitch').addEventListener('change', function () {
        const estado = this.checked ? 0 : 1;
        document.getElementById('statusLabel').textContent = this.checked ? 'Inactivos' : 'Activos';

        fetch(`/getProveedores?estado=${estado}`)
            .then(response => response.json())
            .then(data => {
                const tbody = document.querySelector('table tbody');
                tbody.innerHTML = '';

                data.proveedores.forEach(proveedor => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                    <td>${proveedor.nombreProveedor}</td>
                    <td>${proveedor.contacto}</td>
                    <td>${proveedor.telefono}</td>
                    <td>${proveedor.direccion}</td>
                    <td class="acciones">
                        
                        ${estado === 1 ? `
                            <!-- Si el estado está activo, mostramos el botón de Activar -->
                            <button class="btnEditProveedores" data-bs-toggle="modal"
                            data-bs-target="#editProveedorModal"
                            idProveedor="${proveedor.idProveedor}"
                            nombreProveedor="${proveedor.nombreProveedor}"
                            contacto="${proveedor.contacto}"
                            telefono="${proveedor.telefono}"
                            direccion="${proveedor.direccion}">
                            <i class="icon fas fa-edit"></i>
                            Modificar
                        </button>
                            <button class="btnEliminarProveedores" data-bs-toggle="modal"
                                data-bs-target="#deleteProveedorModal" 
                                data-id="${proveedor.idProveedor}"
                                nombreProveedor="${proveedor.nombreProveedor}"
                                contacto="${proveedor.contacto}"
                                telefono="${proveedor.telefono}"
                                direccion="${proveedor.direccion}">
                                Eliminar
                                <i class="icon fas fa-trash"></i>
                            </button>
                            
                        ` : `
                            
                            <form method="POST" action="/activarProveedor" style="display: inline;">
                            <input type="hidden" name="idProveedor" value="${proveedor.idProveedor}">
                            <button type="submit" class="btnActivarProveedores" data-id="${proveedor.idProveedor}">
                            <i class='fas fa-check-circle fa-fw'></i>
                            Activar
                            </button>
                            </form>

                            <form method="POST" action="/eliminarDefProveedor" style="display: inline;">
                            <input type="hidden" name="idProveedor" value="${proveedor.idProveedor}">
                            <button class="btnEliminarProveedores">
                                <i class="icon fas fa-trash"></i>
                            Eliminar definitivamente
                            </button>
                            </form>
                        `}
                    </td>
                `;
                    tbody.appendChild(row);
                });

                document.querySelectorAll(".btnEditProveedores").forEach(button => {
                    button.addEventListener("click", function () {
                        document.getElementById("IdProveedor").value = this.getAttribute("idProveedor");
                        document.getElementById("Nombre").value = this.getAttribute("nombreProveedor");
                        document.getElementById("Contacto").value = this.getAttribute("contacto");
                        document.getElementById("Telefono").value = this.getAttribute("telefono");
                        document.getElementById("Direccion").value = this.getAttribute("direccion");
                    });
                });

                document.querySelectorAll(".btnEliminarProveedores").forEach(button => {
                    button.addEventListener("click", function () {
                        document.getElementById("deleteIdProveedor").value = this.getAttribute("data-id");
                        document.getElementById("deleteNombre").textContent = this.getAttribute("nombreProveedor");
                        document.getElementById("deleteContacto").textContent = this.getAttribute("contacto");
                        document.getElementById("deleteTelefono").textContent = this.getAttribute("telefono");
                        document.getElementById("deleteDireccion").textContent = this.getAttribute("direccion");
                    });
                });

                document.querySelectorAll(".btnActivarProveedores").forEach(button => {
                    button.addEventListener("click", function () {
                        const idProveedor = this.getAttribute("data-id");
                        console.log(`Activando proveedor con ID: ${idProveedor}`);
                    });
                });
            });
    });
});

// Función para cargar los proveedores
function cargarProveedores(estado = 1) {
    fetch(`/getProveedores?estado=${estado}`)
        .then(response => response.json())
        .then(data => {
            const tbody = document.querySelector('table tbody');
            tbody.innerHTML = '';

            data.proveedores.forEach(proveedor => {
                const row = document.createElement('tr');
                row.innerHTML = `
                <td>${proveedor.nombreProveedor}</td>
                <td>${proveedor.contacto}</td>
                <td>${proveedor.telefono}</td>
                <td>${proveedor.direccion}</td>
                <td class="acciones">
                    
                    ${estado === 1 ? `
                        <!-- Si el estado está activo, mostramos el botón de Activar -->
                        <button class="btnEditProveedores" data-bs-toggle="modal"
                        data-bs-target="#editProveedorModal"
                        idProveedor="${proveedor.idProveedor}"
                        nombreProveedor="${proveedor.nombreProveedor}"
                        contacto="${proveedor.contacto}"
                        telefono="${proveedor.telefono}"
                        direccion="${proveedor.direccion}">
                        <i class="icon fas fa-edit"></i>
                        Modificar
                    </button>
                        <button class="btnEliminarProveedores" data-bs-toggle="modal"
                            data-bs-target="#deleteProveedorModal" 
                            data-id="${proveedor.idProveedor}"
                            nombreProveedor="${proveedor.nombreProveedor}"
                            contacto="${proveedor.contacto}"
                            telefono="${proveedor.telefono}"
                            direccion="${proveedor.direccion}">
                            <i class="icon fas fa-trash"></i>
                            Eliminar
                        </button>
                        
                    ` : `
                        
                        <form method="POST" action="/activarProveedor" style="display: inline;">
                        <input type="hidden" name="idProveedor" value="${proveedor.idProveedor}">
                        <button type="submit" class="btnActivarProveedores" data-id="${proveedor.idProveedor}">
                        <i class='fas fa-check-circle fa-fw'></i>
                        Activar
                        </button>
                        </form>

                        <form method="POST" action="/eliminarDefProveedor" style="display: inline;">
                        <input type="hidden" name="idProveedor" value="${proveedor.idProveedor}">
                        <button class="btnEliminarProveedores">
                            <i class="icon fas fa-trash"></i>
                        Eliminar definitivamente
                        </button>
                        </form>
                    `}
                </td>
            `;
                tbody.appendChild(row);
            });

            // Configurar eventos después de cargar los datos
            configurarEventos();
        });
}

// Función para configurar todos los eventos
function configurarEventos() {
    document.querySelectorAll(".btnEditProveedores").forEach(button => {
        button.addEventListener("click", function () {
            document.getElementById("IdProveedor").value = this.getAttribute("idProveedor");
            document.getElementById("Nombre").value = this.getAttribute("nombreProveedor");
            document.getElementById("Contacto").value = this.getAttribute("contacto");
            document.getElementById("Telefono").value = this.getAttribute("telefono");
            document.getElementById("Direccion").value = this.getAttribute("direccion");
        });
    });

    document.querySelectorAll(".btnEliminarProveedores").forEach(button => {
        button.addEventListener("click", function () {
            document.getElementById("deleteIdProveedor").value = this.getAttribute("data-id");
            document.getElementById("deleteNombre").textContent = this.getAttribute("nombreProveedor");
            document.getElementById("deleteContacto").textContent = this.getAttribute("contacto");
            document.getElementById("deleteTelefono").textContent = this.getAttribute("telefono");
            document.getElementById("deleteDireccion").textContent = this.getAttribute("direccion");
        });
    });

    document.querySelectorAll(".btnActivarProveedores").forEach(button => {
        button.addEventListener("click", function () {
            const idProveedor = this.getAttribute("data-id");
            console.log(`Activando proveedor con ID: ${idProveedor}`);
        });
    });
}

document.addEventListener("DOMContentLoaded", function () {
    cargarProveedores();
    // Tiempo de alerta
    setTimeout(() => {
        document.querySelectorAll(".alert").forEach(alert => {
            alert.style.opacity = "0";
            setTimeout(() => alert.remove(), 500);
        });
    }, 4000);
});

// -------------------------------
// FUNCIONES PARA SANITIZAR ENTRADAS EN EL MODAL DE AGREGACION Y MODIFICACION DE PROVEEDORES
// -------------------------------
(function () {
    'use strict';
    
    // Función para sanitizar entradas
    function sanitizeInput(input) {
        if (input.value && input.type !== 'password') {
            input.value = input.value
                .replace(/&/g, '&amp;')  // Sanitiza el símbolo '&'
                .replace(/</g, '&lt;')   // Sanitiza el símbolo '<'
                .replace(/>/g, '&gt;')   // Sanitiza el símbolo '>'
                .replace(/"/g, '&quot;') // Sanitiza el símbolo '"'
                .replace(/'/g, '&#039;'); // Sanitiza el símbolo "'"
        }
    }

    // Función para validar campos
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

    // Escuchadores de eventos para validar en tiempo real
    function applyValidationListeners(form) {
        const inputs = form.querySelectorAll('input, textarea');
        inputs.forEach(input => {
            input.addEventListener('input', function () {
                sanitizeInput(this); // Sanitiza la entrada en tiempo real
                validateField(this);  // Valida el campo
            });

            input.addEventListener('blur', function () {
                sanitizeInput(this); // Sanitiza la entrada al perder el foco
                validateField(this);  // Valida el campo
            });
        });
    }

    // Validación en la acción de envío del formulario
    function validateForm(event, form) {
        const inputs = form.querySelectorAll('input, textarea');
        let isFormValid = true;

        inputs.forEach(input => {
            sanitizeInput(input); // Sanitiza la entrada
            if (!validateField(input)) {
                isFormValid = false;
            }
        });

        if (!isFormValid) {
            event.preventDefault();
            event.stopPropagation();
            const firstInvalid = form.querySelector('.is-invalid');
            if (firstInvalid) firstInvalid.focus();
        }

        form.classList.add('was-validated');
    }

    // Aplicar validación en los formularios
    const formRegistrarProveedor = document.getElementById('formRegistrarProveedor');
    const editProveedorForm = document.getElementById('editProveedorForm');

    if (formRegistrarProveedor) {
        applyValidationListeners(formRegistrarProveedor);
        formRegistrarProveedor.addEventListener('submit', function (event) {
            validateForm(event, formRegistrarProveedor); // Validación al enviar el formulario
        });
    }

    if (editProveedorForm) {
        applyValidationListeners(editProveedorForm);
        editProveedorForm.addEventListener('submit', function (event) {
            validateForm(event, editProveedorForm); // Validación al enviar el formulario
        });
    }
})();
