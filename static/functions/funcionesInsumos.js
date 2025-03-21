
//! Conversion de insumos para el modulo de gestion de insumos

document.addEventListener("DOMContentLoaded", function () {
    const asignarProveedorModal = document.getElementById("asignarProveedorModal");
    asignarProveedorModal.addEventListener("show.bs.modal", function (event) {
        const button = event.relatedTarget; // Boton que activa el modal
        const idInsumo = button.getAttribute("data-insumo-id");
        fetch(`/get_insumo/${idInsumo}`)
            .then((response) => response.json())
            .then((data) => {
                document.getElementById("idInsumo").value = data.idInsumo;
                document.getElementById("unidadMedidaAsignar").value = data.unidadMedida;
                actualizarFormatos();
            })
            .catch((error) =>
                console.error("Error al obtener los datos del insumo:", error)
            );
    });
    // Seccion de conversion
    const formatoSelect = document.getElementById("formato");
    const cantidadInput = document.getElementById("cantidad");
    const cantidadBaseInput = document.getElementById("cantidadBase");
    const formatosPorUnidad = {
        gramo: [
            { value: "bulto", text: "Bulto (50 kg)" },
            { value: "kg", text: "Kilogramo (kg)" },
            { value: "gr", text: "Gramo (gr)" },
        ],
        mililitro: [
            { value: "gal", text: "Galón (gal)" },
            { value: "l", text: "Litro (l)" },
            { value: "ml", text: "Mililitro (ml)" },
        ],
        pieza: [
            { value: "docena", text: "Docena" },
            { value: "media_docena", text: "Media Docena" },
            { value: "pieza", text: "Pieza" },
        ],
    };
    function actualizarFormatos() {
        const unidadMedida = document.getElementById("unidadMedidaAsignar").value;
        const formatos = formatosPorUnidad[unidadMedida];
        // Limpiar opciones
        formatoSelect.innerHTML = "";
        // Agregar opción por defecto
        const defaultOption = document.createElement("option");
        defaultOption.value = "0";
        defaultOption.text = "Selecciona el formato";
        formatoSelect.appendChild(defaultOption);
        // carga de opciones
        formatos.forEach((formato) => {
            const option = document.createElement("option");
            option.value = formato.value;
            option.text = formato.text;
            formatoSelect.appendChild(option);
        });
        calcularCantidadBase();
    }
    function calcularCantidadBase() {
        const cantidad = parseFloat(cantidadInput.value);
        const formato = formatoSelect.value;
        const unidadMedida = document.getElementById("unidadMedidaAsignar").value;
        let cantidadBase = 0;
        if (unidadMedida === "gramo") {
            if (formato === "bulto") {
                cantidadBase = cantidad * 50000;
            } else if (formato === "kg") {
                cantidadBase = cantidad * 1000;
            } else if (formato === "gr") {
                cantidadBase = cantidad;
            }
        } else if (unidadMedida === "mililitro") {
            if (formato === "gal") {
                cantidadBase = cantidad * 3785.41;
            } else if (formato === "l") {
                cantidadBase = cantidad * 1000;
            } else if (formato === "ml") {
                cantidadBase = cantidad;
            }
        } else if (unidadMedida === "pieza") {
            if (formato === "docena") {
                cantidadBase = cantidad * 12;
            } else if (formato === "media_docena") {
                cantidadBase = cantidad * 6;
            } else if (formato === "pieza") {
                cantidadBase = cantidad;
            }
        }
        cantidadBaseInput.value = cantidadBase.toFixed(2);
    }
    formatoSelect.addEventListener("change", calcularCantidadBase);
    cantidadInput.addEventListener("input", calcularCantidadBase);
});

//! Funciones de edicion en la tabla de insumos
document.addEventListener("DOMContentLoaded", function () {
    const editarInsumoModal = document.getElementById("editarInsumoModal");
    editarInsumoModal.addEventListener("show.bs.modal", function (event) {
        const button = event.relatedTarget; // Botón que activa el modal
        const idInsumo = button.getAttribute("data-insumo-id");
        
        fetch(`/get_insumo/${idInsumo}`)
            .then((response) => response.json())
            .then((data) => {
                document.getElementById("idInsumoEditar").value = data.idInsumo;
                document.getElementById("nombreInsumoEditar").value = data.nombreInsumo;
                document.getElementById("unidadMedidaEditar").value = data.unidadMedida;
            })
            .catch((error) => console.error("Error al obtener los datos del insumo:", error));
    });
});

//! Funciones de eliminacion en la tabla de insumos
document.addEventListener("DOMContentLoaded", function () {
    const eliminarInsumoModal = document.getElementById("eliminarInsumoModal");
    eliminarInsumoModal.addEventListener("show.bs.modal", function (event) {
        const button = event.relatedTarget; // Botón que activa el modal
        const idInsumo = button.getAttribute("data-insumo-id");
        document.getElementById("idInsumoEliminar").value = idInsumo;
    });
});


document.addEventListener("DOMContentLoaded", function () {
    // Cargar datos en el modal de editar
    const editarPresentacionModal = document.getElementById("editarPresentacionModal");
    editarPresentacionModal.addEventListener("show.bs.modal", function (event) {
        const button = event.relatedTarget; // Botón que activa el modal
        const idPresentacion = button.getAttribute("data-presentacion-id");
        
        fetch(`/get_presentacion/${idPresentacion}`)
            .then((response) => response.json())
            .then((data) => {
                document.getElementById("idPresentacionEditar").value = data.idPresentacion;
                document.getElementById("idInsumoEditar").value = data.idInsumoFK;
                document.getElementById("nombrePresentacionEditar").value = data.nombrePresentacion;
                document.getElementById("cantidadBaseEditar").value = data.cantidadBase;
                document.getElementById("proveedorEditar").value = data.idProveedorFK;
                document.getElementById("precioProveedorEditar").value = data.precioProveedor;
            })
            .catch((error) => console.error("Error al obtener los datos de la presentación:", error));
    });

    // Cargar datos en el modal de eliminar
    const eliminarPresentacionModal = document.getElementById("eliminarPresentacionModal");
    eliminarPresentacionModal.addEventListener("show.bs.modal", function (event) {
        const button = event.relatedTarget; // Botón que activa el modal
        const idPresentacion = button.getAttribute("data-presentacion-id");
        document.getElementById("idPresentacionEliminar").value = idPresentacion;
    });
});