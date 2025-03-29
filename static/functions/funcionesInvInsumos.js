document.addEventListener("DOMContentLoaded", function () {
    const agregarInsumoModal = document.getElementById("registroModal");
    const selectInsumo = document.getElementById("idInsumo");
    const selectPresentacion = document.getElementById("idPresentacionFK");
    const inputCantidadCompra = document.getElementById("cantidadCompra");

    // Cargar insumos al abrir el modal
    agregarInsumoModal.addEventListener("show.bs.modal", function (event) {
        // Primero obtenemos la lista de insumos
        fetch("/getInsumos")
            .then((response) => response.json())
            .then((data) => {
                console.log(data);
                selectInsumo.innerHTML = "<option value=''>Seleccione un insumo</option>";
                data.forEach((insumo) => {
                    let option = document.createElement("option");
                    option.value = insumo.idInsumo;
                    option.text = insumo.nombreInsumo;
                    option.dataset.unidadMedida = insumo.unidadMedida;
                    selectInsumo.appendChild(option);
                });
            })
            .catch((error) => console.error("Error al obtener los insumos:", error));
            
        // Limpiar el select de presentaciones
        selectPresentacion.innerHTML = "<option value=''>Seleccione primero un insumo</option>";
    });

    // Cuando se selecciona un insumo, cargar sus presentaciones
    selectInsumo.addEventListener("change", function() {
        const idInsumo = this.value;
        if (idInsumo) {
            fetch(`/getPresentacionesPorInsumo/${idInsumo}`)
                .then((response) => response.json())
                .then((data) => {
                    selectPresentacion.innerHTML = "";
                    if (data.length === 0) {
                        selectPresentacion.innerHTML = "<option value=''>No hay presentaciones disponibles</option>";
                    } else {
                        data.forEach((presentacion) => {
                            let option = document.createElement("option");
                            option.value = presentacion.idPresentacion;
                            option.text = `${presentacion.nombrePresentacion}`;
                            selectPresentacion.appendChild(option);
                        });
                    }
                })
                .catch((error) => console.error("Error al obtener las presentaciones:", error));
        } else {
            selectPresentacion.innerHTML = "<option value=''>Seleccione primero un insumo</option>";
        }
    });
});