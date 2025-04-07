document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('nuevaOrdenModal');
    const closeModalBtn = modal.querySelector('.close-modal');
    const produceButtons = document.querySelectorAll('.custom-botonProducir');
    const recetaSelect = document.getElementById('receta-select');
    const recetaInfo = document.getElementById('receta-info');
    const cantidadHorneadaSpan = document.getElementById('cantidad-horneada');
    const modalGalletaName = document.getElementById('modal-galleta-name');
    const totalInventarioSpan = document.getElementById('total-inventario');
    const btnAgregarSolicitud = document.querySelector('.btnAgregarSolicitud');
    let currentGalletaId = null;
    let currentGalletaName = null;
    let currentRecetaId = null;
    let currentCantidad = 0;

    // Función para mostrar error elegante
    const showErrorAlert = (title, text) => {
        return Swal.fire({
            icon: 'error',
            title: title,
            text: text,
            confirmButtonColor: '#009E0F',
            background: '#fff'
        });
    };

    // Función para mostrar éxito
    const showSuccessAlert = (title, html) => {
        return Swal.fire({
            icon: 'success',
            title: title,
            html: html,
            confirmButtonColor: '#009E0F',
            timer: 3000,
            timerProgressBar: true,
            background: '#fff'
        });
    };

    produceButtons.forEach(button => {
        button.addEventListener('click', async function() {
            currentGalletaId = this.getAttribute('data-product-id');
            currentGalletaName = this.getAttribute('data-product-name');
            
            modalGalletaName.textContent = currentGalletaName;
            modal.style.display = 'block';
            
            try {
                // Obtener datos sin mostrar loader
                const [inventarioResponse, recetasResponse] = await Promise.all([
                    fetch(`/api/inventario-galleta/${currentGalletaId}`),
                    fetch(`/api/recetas-galleta/${currentGalletaId}`)
                ]);
                
                const [inventarioData, recetasData] = await Promise.all([
                    inventarioResponse.json(),
                    recetasResponse.json()
                ]);
                
                // Procesar inventario
                if (inventarioData.success) {
                    const total = inventarioData.inventario.reduce((sum, lote) => sum + lote.cantidadGalletas, 0);
                    totalInventarioSpan.textContent = total;
                } else {
                    totalInventarioSpan.textContent = '0';
                    console.error('Error al obtener inventario:', inventarioData.message);
                }
                
                // Procesar recetas
                recetaSelect.innerHTML = '<option value="">Seleccionar receta</option>';
                if (recetasData.success) {
                    recetasData.recetas.forEach(receta => {
                        const option = document.createElement('option');
                        option.value = receta.idReceta;
                        option.textContent = receta.nombreReceta;
                        option.setAttribute('data-cantidad', receta.cantidadHorneadas);
                        recetaSelect.appendChild(option);
                    });
                } else {
                    console.error('Error al obtener recetas:', recetasData.message);
                }
                
            } catch (error) {
                console.error('Error en la solicitud:', error);
                await showErrorAlert('Error', 'Ocurrió un problema al cargar los datos');
                modal.style.display = 'none';
                document.body.style.overflow = 'auto';
            }
        });
    });

    // Evento para mostrar información de la receta seleccionada
    recetaSelect.addEventListener('change', function() {
        const selectedOption = this.options[this.selectedIndex];
        if (selectedOption.value) {
            currentRecetaId = selectedOption.value;
            currentCantidad = selectedOption.getAttribute('data-cantidad');
            cantidadHorneadaSpan.textContent = currentCantidad;
            recetaInfo.style.display = 'block';
        } else {
            currentRecetaId = null;
            currentCantidad = 0;
            recetaInfo.style.display = 'none';
        }
    });

    // Evento para agregar solicitud de producción
    btnAgregarSolicitud.addEventListener('click', async function() {
        if (!currentRecetaId) {
            await showErrorAlert('Receta requerida', 'Por favor selecciona una receta');
            return;
        }

        try {
            // Verificar solicitudes pendientes
            const response = await fetch(`/api/solicitudes-pendientes/${currentGalletaId}`);
            const data = await response.json();
            
            let alertConfig = {
                icon: 'question',
                title: 'Confirmar producción',
                html: `¿Está seguro de hacer la petición de producción para <b>${currentGalletaName}</b> que producirá <b>${currentCantidad}</b> unidades por lote?`,
                showCancelButton: true,
                confirmButtonText: 'Sí, producir',
                cancelButtonText: 'Cancelar',
                confirmButtonColor: '#009E0F',
                cancelButtonColor: '#d33',
                background: '#fff'
            };
            
            if (data.success && data.pendientes > 0) {
                if (data.pendientes >= 2) {
                    await showErrorAlert(
                        'Solicitudes pendientes', 
                        `Ya existen ${data.pendientes} solicitudes pendientes para esta galleta. Debe esperar a que se completen antes de hacer otra.`
                    );
                    return;
                }
                
                alertConfig.html += `<br><br><div style="color: #ff9800; font-weight: bold;">
                    <i class="fas fa-exclamation-triangle"></i> ADVERTENCIA: Ya existe ${data.pendientes} solicitud(es) pendiente(s) para esta galleta.
                </div>`;
                alertConfig.icon = 'warning';
            }

            const result = await Swal.fire(alertConfig);
            
            if (result.isConfirmed) {
                // Mostrar loader mientras se procesa
                Swal.fire({
                    title: 'Procesando solicitud',
                    html: 'Por favor espera mientras creamos la orden de producción...',
                    allowOutsideClick: false,
                    background: '#fff',
                    didOpen: () => {
                        Swal.showLoading();
                    }
                });
                
                // Hacer la solicitud de producción
                const produccionResponse = await fetch('/api/crear-produccion', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        idReceta: currentRecetaId,
                        cantidad: currentCantidad
                    })
                });
                
                const produccionData = await produccionResponse.json();
                
                Swal.close();
                
                if (produccionData.success) {
                    await showSuccessAlert(
                        '¡Producción solicitada!',
                        `La solicitud para <b>${currentGalletaName}</b> ha sido creada exitosamente.`
                    );
                    
                    modal.style.display = 'none';
                    // Resetear el modal
                    recetaSelect.innerHTML = '<option value="">Seleccionar receta</option>';
                    recetaInfo.style.display = 'none';
                    currentGalletaId = null;
                    currentRecetaId = null;
                    currentCantidad = 0;
                } else {
                    await showErrorAlert(
                        'Error al crear solicitud', 
                        produccionData.message || 'Ocurrió un error desconocido al crear la solicitud'
                    );
                }
            }
        } catch (error) {
            Swal.close();
            console.error('Error:', error);
            await showErrorAlert('Error inesperado', 'Ocurrió un error al procesar la solicitud');
        }
    });

    closeModalBtn.addEventListener('click', function() {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto'; // Restaurar scroll
        // Resetear el modal
        recetaSelect.innerHTML = '<option value="">Seleccionar receta</option>';
        recetaInfo.style.display = 'none';
        currentGalletaId = null;
        currentRecetaId = null;
        currentCantidad = 0;
    });

    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto'; // Restaurar scroll
            // Resetear el modal
            recetaSelect.innerHTML = '<option value="">Seleccionar receta</option>';
            recetaInfo.style.display = 'none';
            currentGalletaId = null;
            currentRecetaId = null;
            currentCantidad = 0;
        }
    });
});