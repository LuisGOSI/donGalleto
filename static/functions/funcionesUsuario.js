document.addEventListener("DOMContentLoaded", function () {
    // Evento para editar usuarios
    document.querySelectorAll(".btnEditUsuarios").forEach(button => {
        button.addEventListener("click", function () {
            document.getElementById("IdUsuario").value = this.getAttribute("idUsuario");
            document.getElementById("NombreEmpleado").value = this.getAttribute("nombreEmpleado");
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
                            email="${usuario.email}"
                            puesto="${usuario.puesto}"
                            rol="${usuario.rol}"
                            telefono="${usuario.telefono}">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                                    class="bi bi-pencil-square" viewBox="0 0 16 16">
                                    <path
                                        d="M15.502 1.94a.5.5 0 0 1 0 .706L14.459 3.69l-2-2L13.502.646a.5.5 0 0 1 .707 0l1.293 1.293zm-1.75 2.456-2-2L4.939 9.21a.5.5 0 0 0-.121.196l-.805 2.414a.25.25 0 0 0 .316.316l2.414-.805a.5.5 0 0 0 .196-.12l6.813-6.814z" />
                                    <path fill-rule="evenodd"
                                        d="M1 13.5A1.5 1.5 0 0 0 2.5 15h11a1.5 1.5 0 0 0 1.5-1.5v-6a.5.5 0 0 0-1 0v6a.5.5 0 0 1-.5.5h-11a.5.5 0 0 1-.5-.5v-11a.5.5 0 0 1 .5-.5H9a.5.5 0 0 0 0-1H2.5A1.5 1.5 0 0 0 1 2.5v11z" />
                                </svg>
                            Modificar
                        </button>
                            <button class="btnEliminarUsuarios" data-bs-toggle="modal"
                                data-bs-target="#deleteUsuarioModal" 
                                data-id="${usuario.idUsuario}"
                                nombreEmpleado="${usuario.nombreEmpleado}"
                                email="${usuario.email}"
                                puesto="${usuario.puesto}"
                                rol="${usuario.rol}"
                                telefono="${usuario.telefono}">
                                Eliminar
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                                    class="bi bi-trash" viewBox="0 0 16 16">
                                    <path
                                        d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z" />
                                    <path fill-rule="evenodd"
                                        d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z" />
                                </svg>
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
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                                    class="bi bi-trash" viewBox="0 0 16 16">
                                    <path
                                        d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z" />
                                    <path fill-rule="evenodd"
                                        d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z" />
                                </svg>
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
                            puesto="${usuario.puesto}"
                            telefono="${usuario.telefono}"
                            email="${usuario.email}"
                            rol="${usuario.rol}">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                                    class="bi bi-pencil-square" viewBox="0 0 16 16">
                                    <path
                                        d="M15.502 1.94a.5.5 0 0 1 0 .706L14.459 3.69l-2-2L13.502.646a.5.5 0 0 1 .707 0l1.293 1.293zm-1.75 2.456-2-2L4.939 9.21a.5.5 0 0 0-.121.196l-.805 2.414a.25.25 0 0 0 .316.316l2.414-.805a.5.5 0 0 0 .196-.12l6.813-6.814z" />
                                    <path fill-rule="evenodd"
                                        d="M1 13.5A1.5 1.5 0 0 0 2.5 15h11a1.5 1.5 0 0 0 1.5-1.5v-6a.5.5 0 0 0-1 0v6a.5.5 0 0 1-.5.5h-11a.5.5 0 0 1-.5-.5v-11a.5.5 0 0 1 .5-.5H9a.5.5 0 0 0 0-1H2.5A1.5 1.5 0 0 0 1 2.5v11z" />
                                </svg>
                            Modificar
                        </button>
                            <button class="btnEliminarUsuarios" data-bs-toggle="modal"
                                data-bs-target="#deleteUsuarioModal" 
                                data-id="${usuario.idUsuario}"
                                nombreEmpleado="${usuario.nombreEmpleado}"
                                puesto="${usuario.puesto}"
                                telefono="${usuario.telefono}"
                                email="${usuario.email}"
                                rol="${usuario.rol}">
                                Eliminar
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                                    class="bi bi-trash" viewBox="0 0 16 16">
                                    <path
                                        d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z" />
                                    <path fill-rule="evenodd"
                                        d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z" />
                                </svg>
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
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                                    class="bi bi-trash" viewBox="0 0 16 16">
                                    <path
                                        d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z" />
                                    <path fill-rule="evenodd"
                                        d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z" />
                                </svg>
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