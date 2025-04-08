// Modal setup 
document.addEventListener('DOMContentLoaded', () => {
    const buttonReceta = document.querySelectorAll('.custom-buttonReceta');
    const modalContainer = document.createElement('div');
    const barraSolicitudes = document.getElementById('ordenesProduccion')
    modalContainer.id = 'recipeModal';
    modalContainer.innerHTML = `
        <div class="modal-content">
            <span class="close-button">&times;</span>
            <div id="recipe-content"></div>
        </div>
    `;
    modalContainer.classList.add('modal');
    document.body.appendChild(modalContainer);

    const modal = document.getElementById('recipeModal');
    const modalContent = document.getElementById('recipe-content');
    const closeButton = modal.querySelector('.close-button');

    // Función para buscar recetas 
    buttonReceta.forEach(button => {
        button.addEventListener('click', async function () {
            const galletaId = this.getAttribute('data-galleta-id');
            try {
                modalContent.innerHTML = `<p>Cargando recetas...</p>`;
                modal.classList.add('show-modal');

                const response = await fetch(`/buscarRecetasPorId/${galletaId}`);
                const data = await response.json();

                if (data.error) {
                    modalContent.innerHTML = `<p>${data.error}</p>`;
                    return;
                }

                let html = `<h2>Recetas para ${data.galleta}</h2>`;

                if (data.recetas.length === 0) {
                    html += `<p>No hay recetas disponibles para esta galleta.</p>`;
                } else {
                    let index = 1;
                    data.recetas.forEach(receta => {
                        html += `
                    <div class="receta">
                        <br>
                        <h3>${index++}-${receta.nombre}</h3>
                        <h4>Ingredientes:</h4>
                        <ul>
                            ${receta.ingredientes.map(ing => {
                            // Mostrar de diferente forma según si tiene conversión o no
                            if (ing.tiene_conversion) {
                                return `<li>${ing.cantidad_formato} ${ing.formato}${ing.cantidad_formato > 1 ? 's' : ''} de ${ing.nombre} | ${ing.cantidad_exacta} ${ing.unidad}${ing.cantidad_exacta > 1 ? 's' : ''}</li>`;
                            } else {
                                return `<li>${ing.cantidad_formato} ${ing.formato}${ing.cantidad_formato > 1 ? 's' : ''} de ${ing.nombre} | No cuenta con presentacion de receta, favor de registrar</li>`;
                            }
                        }).join('')}
                        </ul>
                    </div>
                `;
                    });
                }

                modalContent.innerHTML = html;

            } catch (error) {
                console.error('Error al cargar recetas:', error);
                modalContent.innerHTML = `<p>Error al cargar las recetas. Intente nuevamente.</p>`;
            }
        });

        // Cerrar modal
        closeButton.onclick = closeModal;
        window.onclick = function (event) {
            if (event.target == modal) {
                closeModal();
            }
        };

        function closeModal() {
            modal.classList.remove('show-modal');
        }
    });
});

// ---------------------------------------------------- Funciones para estados de producción ----------------------------------------------------

let produccionesEnCurso = 0;
var galletaEncontrada = null;
var estado = "Listas";

async function traerTodasLasProducciones() {
    const url = '/producciones-en-curso';
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Error al obtener producciones en curso');
        }
        const data = await response.json();
        if (data.error) {
            console.error(data.error);
            return []
        }
        return data.producciones;
    } catch (error) {
        console.error('Error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'No se pudo cargar las producciones en curso.',
            confirmButtonColor: '#009E0F',
            background: '#fff'
        });
    }
}


document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById('nuevaProduccionModal');
    const closeModalButton = modal.querySelector('.close-modal');
    const botonesProducir = document.querySelectorAll(".custom-buttonProducir");
    const recetaSelect = document.getElementById("receta-select");
    const recetaInfo = document.getElementById("receta-info");
    const cantidadHorneadaSpan = document.getElementById("cantidad-horneada");
    const modalGalletaName = document.getElementById("modal-galleta-name");
    const totalInventarioSpan = document.getElementById("total-inventario");
    const btnAgregarSolicitud = document.querySelector(".btnAgregarSolicitud");

    let currentRecetaId = null;
    let currentCantidad = 0;

    botonesProducir.forEach(boton => {
        boton.addEventListener("click", async function () {
            const productCard = boton.closest(".product-card");
            const idGalleta = productCard.getAttribute("data-galleta-id");
            const nombreGalleta = productCard.getAttribute("data-galleta-nombre");

            // Mostrar modal
            modalGalletaName.textContent = nombreGalleta
            modal.style.display = "block";

            try {
                const [inventarioResponse, recetasResponse] = await Promise.all([
                    fetch(`/api/inventario-galleta/${idGalleta}`),
                    fetch(`/api/recetas-galleta/${idGalleta}`)
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
                console.error("Error al buscar recetas:", error);
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'No se pudo buscar recetas para esta galleta.',
                    confirmButtonColor: '#009E0F',
                    background: '#fff'
                });
            }
        });
    });

    recetaSelect.addEventListener('change', function () {
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

    btnAgregarSolicitud.addEventListener("click", async function () {
        if (!currentRecetaId) {
            Swal.fire({
                icon: 'warning',
                title: 'Seleccionar receta',
                text: 'Por favor, seleccione una receta antes de continuar.',
                confirmButtonColor: '#009E0F',
                background: '#fff'
            });
            return;
        }

        try {
            const response = await fetch(`revisarDisponibilidadRecetaPorId/${currentRecetaId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ cantidadHorneada: currentCantidad })
            });

            const data = await response.json();

            if (!data.success) {
                console.error(data.error);
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: data.error,
                    confirmButtonColor: '#009E0F',
                    background: '#fff'
                });
                return;
            }

            const todosDisponibles = data.ingredientes.every(ing => ing.estado === "Suficiente");

            if (todosDisponibles) {
                const result = await Swal.fire({
                    icon: 'success',
                    title: 'Ingredientes disponibles',
                    text: 'Todos los ingredientes están disponibles. ¿Quieres continuar con la producción?',
                    confirmButtonColor: '#009E0F',
                    cancelButtonColor: '#d33',
                    showCloseButton: true,
                    showCancelButton: true,
                    cancelButtonText: 'Cancelar',
                    confirmButtonText: 'Continuar',
                    background: '#fff'
                });

                if (result.isConfirmed) {
                    const solicitudResponse = await fetch(`/agregarProduccionPorReceta/${currentRecetaId}`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({data}),
                    });
                    const solicitudData = await solicitudResponse.json();

                    if (solicitudData.error) {
                        console.error(solicitudData.error);
                        Swal.fire({
                            icon: 'error',
                            title: 'Error',
                            text: solicitudData.error,
                            confirmButtonColor: '#009E0F',
                            background: '#fff'
                        });
                        return;
                    }

                    Swal.fire({
                        icon: 'success',
                        title: 'Éxito',
                        text: 'Solicitud de producción agregada con éxito.',
                        confirmButtonColor: '#009E0F',
                        background: '#fff'
                    });
                    modal.style.display = "none";
                    window.location.reload(); // Recargar la página para mostrar la nueva producción
                }
            } else {
                const faltantes = data.ingredientes
                    .filter(ing => ing.estado !== "Suficiente")
                    .map(ing => `- ${ing.nombreInsumo}: necesitas ${ing.cantidadNecesaria} ${ing.unidadMedida}s, tienes ${ing.totalDisponible}`)
                    .join('\n');

                Swal.fire({
                    icon: 'warning',
                    title: 'Ingredientes insuficientes',
                    html: `<p>No hay suficiente stock para algunos ingredientes:</p><pre style="text-align:left;">${faltantes}</pre>`,
                    confirmButtonColor: '#009E0F',
                    background: '#fff'
                });
            }
        } catch (error) {
            console.error('Error al revisar disponibilidad:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Ocurrió un error al revisar la disponibilidad de los ingredientes.',
                confirmButtonColor: '#009E0F',
                background: '#fff'
            });
        }
    });

    // Cerrar modal
    closeModalButton.addEventListener("click", () => {
        modal.style.display = "none";
        recetaSelect.value = "";
        recetaInfo.style.display = "none";
        cantidadHorneadaSpan.textContent = "0";
    });
});


function actualizarControlesSwiper() {
    const swiperWrapper = document.querySelector(".swiper-wrapper");
    const slides = swiperWrapper.querySelectorAll(".swiper-slide");

    let nextButton = document.querySelector(".swiper-button-next");
    let prevButton = document.querySelector(".swiper-button-prev");

    if (!nextButton) {
        nextButton = document.createElement("div");
        nextButton.classList.add("swiper-button-next");
        document.querySelector(".swiper-container").appendChild(nextButton);
    }
    if (!prevButton) {
        prevButton = document.createElement("div");
        prevButton.classList.add("swiper-button-prev");
        document.querySelector(".swiper-container").appendChild(prevButton);
    }
    if (slides.length > 2) {
        nextButton.style.display = "block";
        prevButton.style.display = "block";
    } else {
        nextButton.style.display = "none";
        prevButton.style.display = "none";
    }
    if (window.mySwiper) {
        window.mySwiper.params.navigation.nextEl = nextButton;
        window.mySwiper.params.navigation.prevEl = prevButton;
        window.mySwiper.navigation.init();
        window.mySwiper.navigation.update();
    }
}

// ---------------------------------------------------- Función para desplegar y producir galletas ----------------------------------------------------

async function cargarProduccionesIniciales() {
    const producciones = await traerTodasLasProducciones()
    const produccionesAMostrar = producciones.filter(prod =>
        prod.estadoProduccion !== 'Solicitud' && prod.estadoProduccion !== 'Listo'
    );

    if (produccionesAMostrar.length > 0) {
        const estadoProduccion = document.getElementById("estado-produccion");
        estadoProduccion.style.display = "block";

        let swiperContainer = document.querySelector(".swiper-container");
        if (!swiperContainer) {
            swiperContainer = crearSwiperContainer();
            estadoProduccion.appendChild(swiperContainer);
        }

        const swiperWrapper = swiperContainer.querySelector(".swiper-wrapper");
        swiperWrapper.innerHTML = ''; // Limpiar antes de agregar

        produccionesAMostrar.forEach(produccion => {
            const card = crearCardProduccion(
                produccion.nombreGalleta,
                produccion.imgGalleta,
                produccion.estadoProduccion,
                produccion.idProduccion
            );
            swiperWrapper.appendChild(card);
        });

        inicializarSwiper();
    }
}

// Función para crear el contenedor Swiper
function crearSwiperContainer() {
    const swiperContainer = document.createElement("div");
    swiperContainer.classList.add("swiper-container");
    swiperContainer.innerHTML = `
        <div class="swiper-wrapper"></div>
        <div class="swiper-button-next"></div>
        <div class="swiper-button-prev"></div>
        <div class="swiper-pagination"></div>
    `;
    return swiperContainer;
}

// Función para crear una card de producción
function crearCardProduccion(nombre, rutaImagen, estadoInicial, idProduccion) {
    const cardView = document.createElement("div");
    cardView.classList.add("swiper-slide", "card", "text-center", "p-1");
    cardView.style.display = "flex";
    cardView.style.flexDirection = "column";
    cardView.style.alignItems = "center";
    cardView.style.padding = "20px";
    cardView.style.backgroundColor = "#EED8C5";
    cardView.style.margin = "10px";
    cardView.style.boxSizing = "border-box";
    cardView.style.flexShrink = "0"; // esto evita que se achique
    cardView.style.maxWidth = "300px"; // ancho máximo
    cardView.style.height = "350px";
    cardView.style.borderRadius = "15px";
    cardView.dataset.idProduccion = idProduccion; // Guardar el ID de producción en el elemento

    const columna1 = document.createElement("div");
    columna1.style.display = "flex";
    columna1.style.flexDirection = "column";
    columna1.style.alignItems = "center";
    columna1.style.marginBottom = "10px";

    const imagenGalleta = document.createElement("img");
    imagenGalleta.src = rutaImagen;
    imagenGalleta.alt = nombre;
    imagenGalleta.style.width = "100px";
    imagenGalleta.style.height = "100px";
    imagenGalleta.style.borderRadius = "50%";
    columna1.appendChild(imagenGalleta);

    const nombreGalleta = document.createElement("h3");
    nombreGalleta.textContent = nombre;
    nombreGalleta.classList.add("card-title");
    nombreGalleta.style.fontSize = "16px";
    columna1.appendChild(nombreGalleta);

    const imagenEstado = document.createElement("img");
    imagenEstado.src = "/static/img/preparacion.webp";
    imagenEstado.alt = "Estado de producción";
    imagenEstado.style.width = "70px";
    imagenEstado.style.height = "70px";

    const botonEstadoProduccion = document.createElement("button");
    botonEstadoProduccion.textContent = estadoInicial;
    botonEstadoProduccion.style.backgroundColor = "#FEE498";
    botonEstadoProduccion.style.borderRadius = "20px";
    botonEstadoProduccion.style.border = "none";
    botonEstadoProduccion.style.padding = "10px 20px";
    botonEstadoProduccion.style.fontSize = "16px";
    botonEstadoProduccion.style.margin = "15px";
    botonEstadoProduccion.style.cursor = "pointer";

    // Configurar según estado inicial

    configurarEstado(estadoInicial, imagenEstado);

    botonEstadoProduccion.addEventListener("click", () => {
        manejarCambioEstado(botonEstadoProduccion, imagenEstado, idProduccion);
    });

    cardView.appendChild(columna1);
    cardView.appendChild(imagenEstado);
    cardView.appendChild(botonEstadoProduccion);

    return cardView;
}

// Función para configurar el estado inicial
function configurarEstado(estado, imagenEstado) {
    switch (estado) {
        case "Preparación":
            imagenEstado.src = "/static/img/preparacion.webp";
            imagenEstado.alt = "Estado de preparación";
            break;
        case "Horneado":
            imagenEstado.src = "/static/img/horneado.webp";
            imagenEstado.alt = "Estado de horneado";
            break;
        case "Enfriado":
            imagenEstado.src = "/static/img/enfriado.webp";
            imagenEstado.alt = "Estado de enfriado";
            break;
    }


}

// Función para manejar el cambio de estado
function manejarCambioEstado(boton, imagenEstado, idProduccion) {
    const estadoActual = boton.textContent;

    if (estadoActual === "Preparación") {
        Swal.fire({
            title: '¡Es hora de hornear!',
            icon: 'question',
            text: '¿Ha culminado la preparación de las galletas?',
            showCancelButton: true,
            confirmButtonText: 'Sí',
            cancelButtonText: 'No',
            customClass: {
                confirmButton: 'btn-confirm',
                cancelButton: 'btn-cancel'
            },
            buttonsStyling: false
        }).then(result => {
            if (result.isConfirmed) {
                actualizarEstadoEnBackend(idProduccion, 'Horneado', () => {
                    imagenEstado.src = "/static/img/horneado.webp";
                    imagenEstado.alt = "Horneado";
                    boton.textContent = "Horneado";
                    boton.style.backgroundColor = "#FF0000";
                });
            }
        });
    } else if (estadoActual === "Horneado") {
        Swal.fire({
            title: '¡Vamos a reposar esas galletas!',
            icon: 'question',
            text: '¿Ha terminado el tiempo de horneado de las galletas?',
            showCancelButton: true,
            confirmButtonText: 'Sí',
            cancelButtonText: 'No',
            customClass: {
                confirmButton: 'btn-confirm',
                cancelButton: 'btn-cancel'
            },
            buttonsStyling: false
        }).then(result => {
            if (result.isConfirmed) {
                actualizarEstadoEnBackend(idProduccion, 'Enfriado', () => {
                    imagenEstado.src = "/static/img/enfriado.webp";
                    imagenEstado.alt = "Enfriado";
                    boton.textContent = "Enfriado";
                    boton.style.backgroundColor = "#6FA8DC";
                });
            }
        });
    } else if (estadoActual === "Enfriado") {
        Swal.fire({
            title: '¡La galleta está Lista!',
            icon: 'success',
            confirmButtonText: 'Aceptar',
            customClass: { confirmButton: 'btn-confirm' },
            buttonsStyling: false
        }).then(result => {
            if (result.isConfirmed) {
                    imagenEstado.src = "/static/img/listas.webp";
                    imagenEstado.alt = "Listas";
                    boton.textContent = "Listas";
                    boton.style.backgroundColor = "#00FF00";
                    boton.disabled = true;
                
                    // Ocultar después de un tiempo
                    setTimeout(() => {
                        const card = boton.closest('.swiper-slide');
                        card.style.display = 'none';
                        verificarProduccionesVisibles();
                    }, 2000);
                fetch(`/agregarLotePorProduccion/${idProduccion}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ idProduccion })
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.error) {
                            console.error(data.error);
                            Swal.fire({
                                icon: 'error',
                                title: 'Error',
                                text: 'No se pudo agregar el lote de producción.',
                                confirmButtonColor: '#009E0F',
                                background: '#fff'
                            });
                            return;
                        }
                        actualizarEstadoEnBackend(idProduccion, 'Listo');
                        Swal.fire({
                            icon: 'success',
                            title: 'Éxito',
                            text: 'Lote de producción agregado con éxito.',
                            confirmButtonColor: '#009E0F',
                            background: '#fff'
                        });
                        console.log(`Lote agregado con éxito`);
                    })
                    .catch(error => {
                        console.error('Error al agregar lote:', error);
                        Swal.fire({
                            icon: 'error',
                            title: 'Error',
                            text: 'No se pudo agregar el lote de producción.',
                            confirmButtonColor: '#009E0F',
                            background: '#fff'
                        });
                    });
            }
        });
    }
}

// Función para actualizar estado en el backend
function actualizarEstadoEnBackend(idProduccion, nuevoEstado, callback) {
    fetch(`/actualizar-estado-porID/${idProduccion}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ nuevoEstado })
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error(data.error);
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'No se pudo actualizar el estado de la producción.',
                    confirmButtonColor: '#009E0F',
                    background: '#fff'
                });
                return;
            }
            console.log(`Estado actualizado a ${nuevoEstado} en el backend`);
            Swal.fire({
                icon: 'success',
                title: 'Éxito',
                text: `Estado actualizado a ${nuevoEstado} con exito.`,
                confirmButtonColor: '#009E0F',
                background: '#fff'
            });
            console.log(`Actualizando estado a ${nuevoEstado} en el backend`);
            if (callback) callback();
        })
        .catch(error => {
            console.error('Error al actualizar estado:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'No se pudo actualizar el estado de la producción.',
                confirmButtonColor: '#009E0F',
                background: '#fff'
            });
        });
}


// Función para inicializar Swiper
function inicializarSwiper() {
    if (!window.mySwiper) { 
        window.mySwiper = new Swiper('.swiper-container', {
            loop: false,
            initialSlide: 0,
            slidesPerView: 'auto',
            centeredSlides: true, // <-- esto es clave para centrar
            spaceBetween: 20,
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev'
            },
            pagination: {
                el: '.swiper-pagination',
                clickable: true
            }
        });
    } else {
        window.mySwiper.update();
    }
    actualizarControlesSwiper();
}

// Función para verificar si quedan producciones visibles
function verificarProduccionesVisibles() {
    const cardsVisibles = document.querySelectorAll('.swiper-slide:not([style*="display: none"])');
    if (cardsVisibles.length === 0) {
        document.getElementById("estado-produccion").style.display = "none";
    }
}

// Llamar a cargar producciones al iniciar
document.addEventListener("DOMContentLoaded", () => {
    cargarProduccionesIniciales();

});




// ---------------------------------------------------- Funciones para ocultar tarjetas de producción ----------------------------------------------------
function ocultarTarjetasListas() {
    const cardsProduccion = document.querySelectorAll("#estado-produccion .card");
    let tarjetasVisibles = 0;

    cardsProduccion.forEach(card => {
        const botonEstadoProduccion = card.querySelector("button");
        if (botonEstadoProduccion && botonEstadoProduccion.textContent === "Listas") {
            console.log(`Ocultando tarjeta con estado "Listas".`);
            card.style.display = "none";
            produccionesEnCurso--;
        } else if (card.style.display !== "none") {
            tarjetasVisibles++;
        }
    });

    const estadoProduccion = document.getElementById("estado-produccion");
    if (tarjetasVisibles === 0) {
        console.log("No quedan tarjetas visibles. Contrayendo el contenedor.");
        estadoProduccion.style.display = "none";
    }
}

function toggleDropdown(event) {
    event.preventDefault();
    const dropdownMenu = document.getElementById('produccionDropdownMenu');
    dropdownMenu.classList.toggle('show');

    // Close dropdown if clicked outside
    function closeDropdown(e) {
        if (!dropdownMenu.contains(e.target) && e.target !== event.target) {
            dropdownMenu.classList.remove('show');
            document.removeEventListener('click', closeDropdown);
        }
    }

    // Add event listener to close dropdown when clicking outside
    document.addEventListener('click', closeDropdown);
}

// ---------------------------------------------------- Funciones para modal de despliegue de ordenes ----------------------------------------------------
// Cargar solicitudes al abrir el panel


