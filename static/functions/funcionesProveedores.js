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
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                                    class="bi bi-pencil-square" viewBox="0 0 16 16">
                                    <path
                                        d="M15.502 1.94a.5.5 0 0 1 0 .706L14.459 3.69l-2-2L13.502.646a.5.5 0 0 1 .707 0l1.293 1.293zm-1.75 2.456-2-2L4.939 9.21a.5.5 0 0 0-.121.196l-.805 2.414a.25.25 0 0 0 .316.316l2.414-.805a.5.5 0 0 0 .196-.12l6.813-6.814z" />
                                    <path fill-rule="evenodd"
                                        d="M1 13.5A1.5 1.5 0 0 0 2.5 15h11a1.5 1.5 0 0 0 1.5-1.5v-6a.5.5 0 0 0-1 0v6a.5.5 0 0 1-.5.5h-11a.5.5 0 0 1-.5-.5v-11a.5.5 0 0 1 .5-.5H9a.5.5 0 0 0 0-1H2.5A1.5 1.5 0 0 0 1 2.5v11z" />
                                </svg>
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
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                                    class="bi bi-trash" viewBox="0 0 16 16">
                                    <path
                                        d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z" />
                                    <path fill-rule="evenodd"
                                        d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z" />
                                </svg>
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
