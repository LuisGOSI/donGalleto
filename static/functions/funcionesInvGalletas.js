
document.addEventListener("DOMContentLoaded", function () { 
    var modalCafe = document.getElementById('alertaGalletasCafe');
    var modalAmarillo = document.getElementById('alertaGalletasAmarilla');
    var modalRojo = document.getElementById('alertaGalletasRoja');
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
    function asignarEventosMermas() {
        document.querySelectorAll(".mermas-btn, .enviMerma-btn").forEach(button => {
            button.addEventListener("click", function () {
                let row = this.closest("tr");
                let idGalleta = row.querySelectorAll("td")[0].textContent.trim();
                let cantidadActual = row.querySelectorAll("td")[4].textContent.trim();
                let textoBoton = this.querySelector("span");

                // Check the current state
                const statusSwitch = document.getElementById("statusSwitch");
                const estado = statusSwitch.checked ? "Caducado" : "Disponible";

                // Determine which modal and form action to use
                const modalType = estado === "Caducado" ? "enviarMerma" : "registroMermaModal";
                const formAction = estado === "Caducado" ? "/enviarMerma" : "/registrarMermaGalleta";

                // Selector for the modal
                let modal = document.getElementById(modalType);

                if (modal) {
                    // Populate hidden inputs in the modal
                    let idInput = modal.querySelector("#idInventarioGalletaFK");
                    let cantidadInput = modal.querySelector("#cantidadActual");

                    if (idInput) idInput.value = idGalleta;
                    if (cantidadInput) cantidadInput.value = cantidadActual;

                    // Set form action dynamically
                    let form = modal.querySelector("form");
                    if (form) {
                        form.action = formAction;
                        form.method = "POST";
                    }

                    // Trigger the modal
                    new bootstrap.Modal(modal).show();
                }
            });
        });
    }


    const statusSwitch = document.getElementById("statusSwitch");
    const statusLabel = document.getElementById("statusLabel");

    statusSwitch.addEventListener("change", function () {
        const estado = statusSwitch.checked ? "Caducado" : "Disponible";
        statusLabel.textContent = estado;

        // Actualizar encabezados
        actualizarEncabezados(estado);

        fetch(`/actualizar_tabla?estado=${estado}`)
            .then(response => response.json())
            .then(data => {
                actualizarTabla(data, estado);
            })
            .catch(error => console.error("Error al actualizar la tabla:", error));
    });

    function actualizarEncabezados(estado) {
        const thead = document.querySelector("thead tr");
        thead.innerHTML = estado === "Caducado"
            ? `<th>Lote</th><th>Nombre</th><th>Fecha Caducada</th><th>Cantidad</th><th>Acciones</th>`
            : `<th>Lote</th><th>Nombre</th><th>Mermas</th><th>Fecha de Caducidad</th><th>Cantidad</th><th>Acciones</th>`;
    }

    function actualizarTabla(data, estado) {
        const tbody = document.querySelector("tbody");
        tbody.innerHTML = ""; 

        data.forEach(galleta => {
            // Convierte la fecha a un objeto Date
            let fechaCaducidad = new Date(galleta.fechaCaducidad);
            
            // Suma un día a la fecha
            fechaCaducidad.setDate(fechaCaducidad.getDate() + 1);
            
            // Formatea la fecha en 'DD/MM/YYYY'
            const fechaFormateada = fechaCaducidad.toLocaleDateString("es-MX", {
                day: "2-digit",
                month: "2-digit",
                year: "numeric"
            });
            

            const esCaducado = estado === "Caducado";
            const claseBoton = esCaducado ? "enviMerma-btn" : "mermas-btn";
            const textoBoton = esCaducado ? "Enviar a merma" : "Mermas";

            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${galleta.idInvGalleta}</td>
                <td>${galleta.nombreGalleta}</td>
                ${esCaducado ? `<td>${fechaFormateada}</td>` : `<td>${parseInt(galleta.mermas)}</td><td>${fechaFormateada}</td>`}
                <td>${galleta.cantidad}</td>
                <td>
                    <button class="${claseBoton}">
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-graph-down-arrow" viewBox="0 0 16 16">
        <path fill-rule="evenodd" d="M0 0h1v15h15v1H0V0Zm10 11.5a.5.5 0 0 0 .5.5h4a.5.5 0 0 0 .5-.5v-4a.5.5 0 0 0-1 0v2.6l-3.613-4.417a.5.5 0 0 0-.74-.037L7.06 8.233 3.404 3.206a.5.5 0 0 0-.808.588l4 5.5a.5.5 0 0 0 .758.06l2.609-2.61L13.445 11H10.5a.5.5 0 0 0-.5.5Z"/>
    </svg>
    <span>${textoBoton}</span>
</button>
                </td>
            `;

            tbody.appendChild(row);
        });

        asignarEventosMermas();
    }

    // Al cargar la página, asegurarse de que los encabezados y botones estén correctos
    const estadoInicial = statusSwitch.checked ? "Caducado" : "Disponible";
    actualizarEncabezados(estadoInicial);
    fetch(`/actualizar_tabla?estado=${estadoInicial}`)
        .then(response => response.json())
        .then(data => {
            actualizarTabla(data, estadoInicial);
        })
        .catch(error => console.error("Error al cargar la tabla inicial:", error));
});
