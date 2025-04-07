document.addEventListener("DOMContentLoaded", function () {
    // Evento para editar usuarios
    document.querySelectorAll(".btnEditUsuarios").forEach(button => {
        button.addEventListener("click", function () {
            document.getElementById("IdUsuario").value = this.getAttribute("idUsuario");
            document.getElementById("NombreEmpleado").value = this.getAttribute("nombreEmpleado");
            document.getElementById("apellidoPaterno").value = this.getAttribute("apellidoP");
            document.getElementById("apellidoMaterno").value = this.getAttribute("apellidoM");
            document.getElementById("puesto").value = this.getAttribute("puesto");
            document.getElementById("telefono").value = this.getAttribute("telefono");
            document.getElementById("correo").value = this.getAttribute("email");
            document.getElementById("rol").value = this.getAttribute("rol");
        });
    });

    // Evento para eliminar proveedor
    document.querySelectorAll(".btnEliminarUsuarios").forEach(button => {
        button.addEventListener("click", function () {
            document.getElementById("deleteIdUsuario").value = this.getAttribute("data-id");
            document.getElementById("deleteNombreEmpleado").textContent = this.getAttribute("nombreEmpleado");
            document.getElementById("deleteEmail").textContent = this.getAttribute("email");
            document.getElementById("deleteTel").textContent = this.getAttribute("telefono");
            document.getElementById("deleteRol").textContent = this.getAttribute("rol");
        });
    });

    document.getElementById('statusSwitch').addEventListener('change', function () {
        const estado = this.checked ? 0 : 1;
        document.getElementById('statusLabel').textContent = this.checked ? 'Inactivos' : 'Activos';

        fetch(`/getUsuarios?estado=${estado}`)
            .then(response => response.json())
            .then(data => {
                const tbody = document.querySelector('table tbody');
                tbody.innerHTML = '';

                data.usuarios.forEach(usuario => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                    <td>${usuario.nombreEmpleado}</td>
                    <td>${usuario.apellidoP}</td>
                    <td>${usuario.apellidoM}</td>
                    <td>${usuario.email}</td>
                    <td>${usuario.puesto}</td>
                    <td>${usuario.rol}</td>
                    <td>${usuario.telefono}</td>
                    <td class="acciones">
                        
                        ${estado === 1 ? `
                            <!-- Si el estado está activo, mostramos el botón de Activar -->
                            <button class="btnEditUsuarios" data-bs-toggle="modal"
                            data-bs-target="#editUsuarioModal"
                            idUsuario="${usuario.idUsuario}"
                            nombreEmpleado="${usuario.nombreEmpleado}"
                            apellidoP = "${usuario.apellidoP}"
                            apellidoM = "${usuario.apellidoM}"
                            email="${usuario.email}"
                            puesto="${usuario.puesto}"
                            rol="${usuario.rol}"
                            telefono="${usuario.telefono}">
                            <i class="icon fas fa-edit"></i>
                            Modificar
                        </button>
                            <button class="btnEliminarUsuarios" data-bs-toggle="modal"
                                data-bs-target="#deleteUsuarioModal" 
                                data-id="${usuario.idUsuario}"
                                nombreEmpleado="${usuario.nombreEmpleado}"
                                apellidoP="${usuario.apellidoP}"
                                apellidoM="${usuario.apellidoM}"
                                email="${usuario.email}"
                                puesto="${usuario.puesto}"
                                rol="${usuario.rol}"
                                telefono="${usuario.telefono}">
                                <i class="icon fas fa-trash"></i>
                                Eliminar
                            </button>
                            
                        ` : `
                            
                            <form method="POST" action="/activarUsuario" style="display: inline;">
                            <input type="hidden" name="idUsuario" value="${usuario.idUsuario}">
                            <button type="submit" class="btnActivarUsuarios" data-id="${usuario.idUsuario}">
                            <i class='fas fa-check-circle fa-fw'></i>
                            Activar
                            </button>
                            </form>

                            <form method="POST" action="/eliminarDefUsuario" style="display: inline;">
                            <input type="hidden" name="idUsuario" value="${usuario.idUsuario}">
                            <button class="btnEliminarUsuarios">
                                <i class="icon fas fa-trash"></i>
                            Eliminar definitivamente
                            </button>
                            </form>
                        `}
                    </td>
                `;
                    tbody.appendChild(row);
                });

                document.querySelectorAll(".btnEditUsuarios").forEach(button => {
                    button.addEventListener("click", function () {
                        document.getElementById("IdUsuario").value = this.getAttribute("idUsuario");
                        document.getElementById("NombreEmpleado").value = this.getAttribute("nombreEmpleado");
                        document.getElementById("apellidoPaterno").value = this.getAttribute("apellidoP");
                        document.getElementById("apellidoMaterno").value = this.getAttribute("apellidoM");
                        document.getElementById("puesto").value = this.getAttribute("puesto");
                        document.getElementById("telefono").value = this.getAttribute("telefono");
                        document.getElementById("correo").value = this.getAttribute("email");
                        document.getElementById("rol").value = this.getAttribute("rol");
                    });
                });

                document.querySelectorAll(".btnEliminarUsuarios").forEach(button => {
                    button.addEventListener("click", function () {
                        document.getElementById("deleteIdUsuario").value = this.getAttribute("data-id");
                        document.getElementById("deleteNombreEmpleado").textContent = this.getAttribute("nombreEmpleado");
                        document.getElementById("deleteEmail").textContent = this.getAttribute("email");
                        document.getElementById("deleteRol").textContent = this.getAttribute("rol");
                        document.getElementById("deleteTel").textContent = this.getAttribute("telefono");
                    });
                });

                document.querySelectorAll(".btnActivarUsuarios").forEach(button => {
                    button.addEventListener("click", function () {
                        const idProveedor = this.getAttribute("data-id");
                        console.log(`Activando usuario con ID: ${idProveedor}`);
                    });
                });
            });
    });
});

// Función para cargar los proveedores
function cargarUsuarios(estado = 1) {
    fetch(`/getUsuarios?estado=${estado}`)
        .then(response => response.json())
        .then(data => {
            const tbody = document.querySelector('table tbody');
            tbody.innerHTML = '';

            data.usuarios.forEach(usuario => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${usuario.nombreEmpleado}</td>
                    <td>${usuario.apellidoP}</td>
                    <td>${usuario.apellidoM}</td>
                    <td>${usuario.email}</td>
                    <td>${usuario.puesto}</td>
                    <td>${usuario.rol}</td>
                    <td>${usuario.telefono}</td>
                    <td class="acciones">
                        
                        ${estado === 1 ? `
                            <!-- Si el estado está activo, mostramos el botón de Activar -->
                            <button class="btnEditUsuarios" data-bs-toggle="modal"
                            data-bs-target="#editUsuarioModal"
                            idUsuario="${usuario.idUsuario}"
                            nombreEmpleado="${usuario.nombreEmpleado}"
                            apellidoP="${usuario.apellidoP}"
                            apellidoM="${usuario.apellidoM}"
                            puesto="${usuario.puesto}"
                            telefono="${usuario.telefono}"
                            email="${usuario.email}"
                            rol="${usuario.rol}">
                            <i class="icon fas fa-edit"></i>
                            Modificar
                        </button>
                            <button class="btnEliminarUsuarios" data-bs-toggle="modal"
                                data-bs-target="#deleteUsuarioModal" 
                                data-id="${usuario.idUsuario}"
                                nombreEmpleado="${usuario.nombreEmpleado}"
                                apellidoP="${usuario.nombreEmpleado}"
                                apellidoM="${usuario.nombreEmpleado}"
                                puesto="${usuario.puesto}"
                                telefono="${usuario.telefono}"
                                email="${usuario.email}"
                                rol="${usuario.rol}">
                                <i class="icon fas fa-trash"></i>
                                Eliminar
                            </button>
                            
                        ` : `
                            
                            <form method="POST" action="/activarUsuario" style="display: inline;">
                            <input type="hidden" name="idUsuario" value="${usuario.idUsuario}">
                            <button type="submit" class="btnActivarProveedores" data-id="${usuario.idUsuario}">
                            <i class='fas fa-check-circle fa-fw'></i>
                            Activar
                            </button>
                            </form>

                            <form method="POST" action="/eliminarDefUsuario" style="display: inline;">
                            <input type="hidden" name="idUsuario" value="${usuario.idUsuario}">
                            <button class="btnEliminarUsuarios">
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
    document.querySelectorAll(".btnEditUsuarios").forEach(button => {
        button.addEventListener("click", function () {
            document.getElementById("IdUsuario").value = this.getAttribute("idUsuario");
            document.getElementById("nombre").value = this.getAttribute("nombreEmpleado");
            document.getElementById("apellidoPaterno").value = this.getAttribute("apellidoP");
            document.getElementById("apellidoMaterno").value = this.getAttribute("apellidoM");
            document.getElementById("pues").value = this.getAttribute("puesto");
            document.getElementById("telefono").value = this.getAttribute("telefono");
            document.getElementById("correo").value = this.getAttribute("email");
            document.getElementById("funcion").value = this.getAttribute("rol");
        });
    });

    document.querySelectorAll(".btnEliminarUsuarios").forEach(button => {
        button.addEventListener("click", function () {
            document.getElementById("deleteIdUsuario").value = this.getAttribute("data-id");
            document.getElementById("deleteNombreEmpleado").textContent = this.getAttribute("nombreEmpleado");
            document.getElementById("deleteEmail").textContent = this.getAttribute("email");
            document.getElementById("deleteRol").textContent = this.getAttribute("rol");
            document.getElementById("deleteTel").textContent = this.getAttribute("telefono");
        });
    });

    document.querySelectorAll(".btnActivarProveedores").forEach(button => {
        button.addEventListener("click", function () {
            const idProveedor = this.getAttribute("data-id");
            console.log(`Activando usuario con ID: ${idProveedor}`);
        });
    });
}

document.addEventListener("DOMContentLoaded", function () {
    cargarUsuarios();
    setTimeout(() => {
        document.querySelectorAll(".alert").forEach(alert => {
            alert.style.opacity = "0";
            setTimeout(() => alert.remove(), 500);
        });
    }, 4000);
});


//////// // Funciones para la sanitización de formulario /////////////
(function() {
    'use strict';
    const form = document.getElementById('registroForm');
    
    function sanitizeInput(input) {
        if (input.value) {
            if (input.type !== 'password') {
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
        
        if (isValid) {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
        } else {
            input.classList.remove('is-valid');
            input.classList.add('is-invalid');
        }
        
        return isValid;
    }
    
    const inputs = form.querySelectorAll('input, select');
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            clearTimeout(this.debounceTimer);
            this.debounceTimer = setTimeout(() => {
                validateField(this);
            }, 500);
        });
        
        input.addEventListener('blur', function() {
            sanitizeInput(this);
            validateField(this);
        });
        
        input.addEventListener('focus', function() {
            if (this.title) {
                this.setAttribute('data-original-title', this.title);
            }
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
        
        if (!isFormValid) {
            event.preventDefault();
            event.stopPropagation();
            
            const firstInvalidField = form.querySelector('.is-invalid');
            if (firstInvalidField) {
                firstInvalidField.focus();
            }
            const errorAlert = document.getElementById('formErrorAlert');
            if (!errorAlert) {
                const alert = document.createElement('div');
                alert.id = 'formErrorAlert';
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
    
    const nombreFields = form.querySelectorAll('#nombreEmpleado, #apellidoP, #apellidoM');
    nombreFields.forEach(field => {
        field.addEventListener('input', function(e) {
            const invalidChars = /[^A-Za-zÁÉÍÓÚáéíóúÑñ\s]/g;
            if (invalidChars.test(this.value)) {
                this.classList.add('is-invalid');
                this.value = this.value.replace(invalidChars, '');
                const fieldName = this.previousElementSibling.textContent;
                showTemporaryMessage(this, `Caracteres no válidos eliminados en "${fieldName}"`);
            }
        });
    });
    
    const telField = form.querySelector('#tel');
    telField.addEventListener('input', function(e) {
        const invalidChars = /[^0-9]/g;
        if (invalidChars.test(this.value)) {
            this.classList.add('is-invalid');
            this.value = this.value.replace(invalidChars, '');
            showTemporaryMessage(this, 'Solo se permiten números en el teléfono');
        }
    });
    
    function showTemporaryMessage(element, message) {
        let msgElement = element.nextElementSibling.nextElementSibling;
        if (!msgElement || !msgElement.classList.contains('temp-message')) {
            msgElement = document.createElement('div');
            msgElement.className = 'temp-message text-danger small mt-1';
            element.parentNode.insertBefore(msgElement, element.nextElementSibling.nextElementSibling);
        }
        msgElement.textContent = message;
        
        setTimeout(() => {
            if (msgElement.parentNode) {
                msgElement.parentNode.removeChild(msgElement);
            }
        }, 3000);
    }
})();

// Función para validar el formulario para editar usuarios
(function() {
    'use strict';
    const form = document.getElementById('editUsuarioForm');
    function sanitizeInput(input) {
        if (input.value) {
            if (input.type !== 'password' && input.type !== 'hidden') {
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
    
    const inputs = form.querySelectorAll('input, select');
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            if (this.type === 'hidden') return;
            
            clearTimeout(this.debounceTimer);
            this.debounceTimer = setTimeout(() => {
                validateField(this);
            }, 500);
        });
        
        input.addEventListener('blur', function() {
            if (this.type === 'hidden') return;
            
            sanitizeInput(this);
            validateField(this);
        });
        
        input.addEventListener('focus', function() {
            if (this.type === 'hidden') return;
            
            if (this.title) {
                this.setAttribute('data-original-title', this.title);
            }
        });
    });
    
    form.addEventListener('submit', function(event) {
        let isFormValid = true;
        inputs.forEach(input => {
            if (input.type === 'hidden') return;
            
            sanitizeInput(input);
            if (!validateField(input)) {
                isFormValid = false;
            }
        });
        
        if (!isFormValid) {
            event.preventDefault();
            event.stopPropagation();
            
            const firstInvalidField = form.querySelector('.is-invalid');
            if (firstInvalidField) {
                firstInvalidField.focus();
            }
            
            const errorAlert = document.getElementById('formEditErrorAlert');
            if (!errorAlert) {
                const alert = document.createElement('div');
                alert.id = 'formEditErrorAlert';
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
    
    const nombreFields = form.querySelectorAll('#nombre, #apellidoPaterno, #apellidoMaterno');
    nombreFields.forEach(field => {
        field.addEventListener('input', function(e) {
            const invalidChars = /[^A-Za-zÁÉÍÓÚáéíóúÑñ\s]/g;
            if (invalidChars.test(this.value)) {
                this.classList.add('is-invalid');
                this.value = this.value.replace(invalidChars, '');
                const fieldName = this.previousElementSibling.textContent;
                showTemporaryMessage(this, `Caracteres no válidos eliminados en "${fieldName}"`);
            }
        });
    });
    
    const telField = form.querySelector('#telefono');
    telField.addEventListener('input', function(e) {
        const invalidChars = /[^0-9]/g;
        if (invalidChars.test(this.value)) {
            this.classList.add('is-invalid');
            this.value = this.value.replace(invalidChars, '');
            showTemporaryMessage(this, 'Solo se permiten números en el teléfono');
        }
    });
    
    function showTemporaryMessage(element, message) {
        let msgElement = element.nextElementSibling.nextElementSibling;
        if (!msgElement || !msgElement.classList.contains('temp-message')) {
            msgElement = document.createElement('div');
            msgElement.className = 'temp-message text-danger small mt-1';
            element.parentNode.insertBefore(msgElement, element.nextElementSibling.nextElementSibling);
        }
        
        msgElement.textContent = message;
        setTimeout(() => {
            if (msgElement.parentNode) {
                msgElement.parentNode.removeChild(msgElement);
            }
        }, 3000);
    }
})();