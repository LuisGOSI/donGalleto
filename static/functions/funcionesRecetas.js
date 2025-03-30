document.addEventListener('DOMContentLoaded', function() {
    const detallesContainer = document.getElementById('detallesContainer');
    const btnAgregarDetalle = document.getElementById('btnAgregarDetalle');
    let contadorDetalles = 0;

    // Cargar formatos cuando se selecciona un insumo
    detallesContainer.addEventListener('change', function(e) {
        if (e.target.classList.contains('insumo-select')) {
            const detalleItem = e.target.closest('.detalle-item');
            const idInsumo = e.target.value;
            const formatoSelect = detalleItem.querySelector('.unidad-select');
            
            if (idInsumo) {
                fetch(`/api/insumos/${idInsumo}/formatos`)
                    .then(response => response.json())
                    .then(formatos => {
                        // Limpiar y cargar nuevos formatos
                        formatoSelect.innerHTML = '<option value="" selected disabled>Seleccione formato</option>';
                        formatos.forEach(formato => {
                            const option = document.createElement('option');
                            option.value = formato.id;
                            option.textContent = `${formato.nombre} (equivale a ${formato.equivalencia} ${detalleItem.querySelector('.insumo-select').selectedOptions[0].text.split('(')[1].split(')')[0]})`;
                            formatoSelect.appendChild(option);
                        });
                    });
            } else {
                formatoSelect.innerHTML = '<option value="" selected disabled>Seleccione formato</option>';
            }
        }
    });

    // Agregar nuevo detalle
    btnAgregarDetalle.addEventListener('click', function() {
        contadorDetalles++;
        const nuevoDetalle = document.createElement('div');
        nuevoDetalle.className = 'detalle-item mb-3 border p-3 rounded';
        nuevoDetalle.innerHTML = `
            <div class="row">
                <div class="col-md-5">
                    <label class="form-label">Insumo</label>
                    <select class="form-select insumo-select" name="detalles[${contadorDetalles}][idInsumoFK]" required>
                        <option value="" selected disabled>Seleccione un insumo</option>
                        ${Array.from(document.querySelector('.insumo-select').options)
                            .map(opt => `<option value="${opt.value}">${opt.text}</option>`)
                            .join('')}
                    </select>
                </div>
                <div class="col-md-3">
                    <label class="form-label">Formato</label>
                    <select class="form-select unidad-select" name="detalles[${contadorDetalles}][idUnidadFK]" required>
                        <option value="" selected disabled>Seleccione formato</option>
                    </select>
                </div>
                <div class="col-md-3">
                    <label class="form-label">Cantidad</label>
                    <input type="number" step="0.01" min="0.01" class="form-control" name="detalles[${contadorDetalles}][cantidadFormato]" required>
                </div>
                <div class="col-md-1 d-flex align-items-end">
                    <button type="button" class="btn btn-danger btn-eliminar-detalle">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
        `;
        
        detallesContainer.appendChild(nuevoDetalle);
        actualizarBotonesEliminar();
    });

    // Eliminar detalle
    detallesContainer.addEventListener('click', function(e) {
        if (e.target.classList.contains('btn-eliminar-detalle') || 
            e.target.parentElement.classList.contains('btn-eliminar-detalle')) {
            const detalleItem = e.target.closest('.detalle-item');
            if (detalleItem && document.querySelectorAll('.detalle-item').length > 1) {
                detalleItem.remove();
                reindexarDetalles();
                contadorDetalles--;
                actualizarBotonesEliminar();
            }
        }
    });

    function reindexarDetalles() {
        const detalles = document.querySelectorAll('.detalle-item');
        detalles.forEach((detalle, index) => {
            detalle.querySelectorAll('select, input').forEach(input => {
                const name = input.getAttribute('name');
                if (name) {
                    input.setAttribute('name', name.replace(/\[\d+\]/, `[${index}]`));
                }
            });
        });
        contadorDetalles = detalles.length - 1;
    }

    function actualizarBotonesEliminar() {
        const detalles = document.querySelectorAll('.detalle-item');
        const botones = document.querySelectorAll('.btn-eliminar-detalle');
        
        if (detalles.length > 1) {
            botones.forEach(btn => btn.disabled = false);
        } else {
            botones[0].disabled = true;
        }
    }
});