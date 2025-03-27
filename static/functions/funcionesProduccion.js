// ---------------------------------------------------- Funcion para modal de recetas ----------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
    const modalContainer = document.createElement('div');
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

    function openModal(receta) {
        modalContent.innerHTML = `
            <h2>${receta.nombre}</h2>
            <h3>Ingredientes:</h3>
            <ul>
                ${receta.ingredientes.map(ingrediente => `<li>${ingrediente}</li>`).join('')}
            </ul>
            <h3>Instrucciones:</h3>
            <ol>
                ${receta.instrucciones.map(instruccion => `<li>${instruccion}</li>`).join('')}
            </ol>
        `;
        modal.classList.add('show-modal');
    }
    function closeModal() {
        modal.classList.remove('show-modal');
    }

    // Lista de recetas
    const recetas = [
        {
            nombre: "Galleta Chispas de Chocolate",
            ingredientes: [
                "2 1/4 tazas de harina",
                "1 cucharadita de bicarbonato de sodio",
                "1 cucharadita de sal",
                "1 taza de mantequilla",
                "3/4 taza de azúcar",
                "3/4 taza de azúcar morena",
                "2 huevos",
                "2 cucharaditas de extracto de vainilla",
                "2 tazas de chispas de chocolate"
            ],
            instrucciones: [
                "Precalentar el horno a 375°F (190°C)",
                "Mezclar harina, bicarbonato y sal",
                "En otro bowl, batir mantequilla y azúcares",
                "Agregar huevos y vainilla a la mezcla de mantequilla",
                "Incorporar ingredientes secos",
                "Añadir chispas de chocolate",
                "Formar bolitas y colocar en bandeja",
                "Hornear por 9-11 minutos",
                "Dejar enfriar en rejilla"
            ]
        }
        // Agregar las demás recetas aquí
    ];
    function escucharRecetas() {
        const recetaButtons = document.querySelectorAll('.custom-buttonReceta');
        
        recetaButtons.forEach((button, index) => {
            button.removeEventListener('click', recipeClickHandler);
            button.addEventListener('click', recipeClickHandler);
        });

        function recipeClickHandler(event) {
            const index = Array.from(recetaButtons).indexOf(event.target);
            
            if (recetas[index]) {
                openModal(recetas[index]);
            } else {
                console.error('Receta no encontrada');
            }
        }
    }
    escucharRecetas();
    closeButton.addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });
});

// ---------------------------------------------------- Funciones para estados de producción ----------------------------------------------------

let produccionesEnCurso = 0;
var galletaEncontrada = null;
var estado = "Listas";

document.addEventListener("DOMContentLoaded", function () {
    const botonesProducir = document.querySelectorAll(".custom-buttonProducir");

    botonesProducir.forEach((boton, index) => {
        boton.addEventListener("click", function () {
            const productCard = boton.closest(".product-card");
            const nombreGalleta = productCard.querySelector("h6").textContent;
            const rutaImagen = productCard.querySelector("img").src;
            const idGalleta = index;  // Puedes cambiar esto si tienes un ID real.

            iniciarProduccion(nombreGalleta, rutaImagen, idGalleta);
        });
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
function iniciarProduccion(nombre, rutaImagen, idGalleta) {
    Swal.fire({
        title: 'La galleta está lista para producir',
        text: `¿Confirmas iniciar la producción de ${nombre}?`,
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: 'Sí, iniciar producción',
        cancelButtonText: 'Cancelar',
        customClass: {
            confirmButton: 'btn-confirm',
            cancelButton: 'btn-cancel'
        },
        buttonsStyling: false
    }).then((result) => {
        if (result.isConfirmed) {
            Swal.fire({
                title: '¡La producción de galletas está en marcha!',
                icon: 'success',
                confirmButtonText: 'Aceptar',
                customClass: { confirmButton: 'btn-confirm' },
                buttonsStyling: false
            });

            const estadoProduccion = document.getElementById("estado-produccion");
            estadoProduccion.style.display = "block";
            let swiperContainer = document.querySelector(".swiper-container");
            if (!swiperContainer) {
                swiperContainer = document.createElement("div");
                swiperContainer.classList.add("swiper-container");
                swiperContainer.innerHTML = `
                    <div class="swiper-wrapper"></div>
                    <div class="swiper-button-next"></div>
                    <div class="swiper-button-prev"></div>
                    <div class="swiper-pagination"></div>
                `;
                estadoProduccion.appendChild(swiperContainer);
            }

            const swiperWrapper = swiperContainer.querySelector(".swiper-wrapper");

            const cardView = document.createElement("div");
            cardView.classList.add("swiper-slide", "card", "text-center", "p-3");
            cardView.style.display = "flex";
            cardView.style.flexDirection = "column";
            cardView.style.alignItems = "center";
            cardView.style.padding = "20px";
            cardView.style.backgroundColor = "#EED8C5";
            cardView.style.margin = "10px";
            cardView.style.boxSizing = "border-box";
            cardView.style.width = "300px";
            cardView.style.height = "400px";
            cardView.style.borderRadius = "15px";

            const columna1 = document.createElement("div");
            columna1.style.display = "flex";
            columna1.style.flexDirection = "column";
            columna1.style.alignItems = "center";
            columna1.style.marginBottom = "10px";

            const imagenGalleta = document.createElement("img");
            imagenGalleta.src = rutaImagen;
            imagenGalleta.alt = nombre;
            imagenGalleta.style.width = "120px";
            imagenGalleta.style.height = "120px";
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
            imagenEstado.style.width = "90px";
            imagenEstado.style.height = "90px";

            const botonEstadoProduccion = document.createElement("button");
            botonEstadoProduccion.textContent = "Preparación";
            botonEstadoProduccion.style.backgroundColor = "#FEE498";
            botonEstadoProduccion.style.borderRadius = "20px";
            botonEstadoProduccion.style.border = "none";
            botonEstadoProduccion.style.padding = "10px 20px";
            botonEstadoProduccion.style.fontSize = "16px";
            botonEstadoProduccion.style.margin = "15px";
            botonEstadoProduccion.style.cursor = "pointer";

            let estadoActual = "Preparación";

            botonEstadoProduccion.addEventListener("click", () => {
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
                            estadoActual = "Horneado";
                            imagenEstado.src = "/static/img/horneado.webp";
                            imagenEstado.alt = "Horneado";
                            botonEstadoProduccion.textContent = "Horneado";
                            botonEstadoProduccion.style.backgroundColor = "#FF0000";
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
                            estadoActual = "Enfriado";
                            imagenEstado.src = "/static/img/enfriado.webp";
                            imagenEstado.alt = "Enfriado";
                            botonEstadoProduccion.textContent = "Enfriado";
                            botonEstadoProduccion.style.backgroundColor = "#6FA8DC";
                        }
                    });

                } else if (estadoActual === "Enfriado") {
                    Swal.fire({
                        title: '¡La galleta está Lista!',
                        icon: 'success',
                        confirmButtonText: 'Aceptar',
                        customClass: {confirmButton: 'btn-confirm'},
                        buttonsStyling: false
                    }).then(result => {
                        if (result.isConfirmed) {
                            estadoActual = "Listas";
                            imagenEstado.src = "/static/img/listas.webp";
                            imagenEstado.alt = "Listas";
                            botonEstadoProduccion.textContent = "Listas";
                            botonEstadoProduccion.style.backgroundColor = "#00FF00";
                            botonEstadoProduccion.disabled = true;
                            ocultarTarjetasListas();
                        }
                    });
                }
            });

            cardView.appendChild(columna1);
            cardView.appendChild(imagenEstado);
            cardView.appendChild(botonEstadoProduccion);

            swiperWrapper.appendChild(cardView);

            if (!window.mySwiper) {
                window.mySwiper = new Swiper('.swiper-container', {
                    loop: false,
                    slidesPerView: 1,
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
            estadoProduccion.scrollIntoView({ behavior: "smooth", block: "start" });

        }
    });
}

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

// ---------------------------------------------------- Funciones para modal de despliegue de ordenes ----------------------------------------------------
