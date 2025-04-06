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