// ---- Funcion para modal de recetas ----
// Crear un modal para mostrar recetas de cocina
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

    // Función para abrir el modal
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

    // Función para cerrar el modal
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
            // Primero, eliminar cualquier listener previo para evitar duplicados
            button.removeEventListener('click', recipeClickHandler);
            
            // Añadir nuevo listener
            button.addEventListener('click', recipeClickHandler);
        });

        function recipeClickHandler(event) {
            // Encontrar el índice del botón clickeado
            const index = Array.from(recetaButtons).indexOf(event.target);
            
            if (recetas[index]) {
                openModal(recetas[index]);
            } else {
                console.error('Receta no encontrada');
            }
        }
    }
    escucharRecetas();

    // Cerrar modal al hacer clic en la X
    closeButton.addEventListener('click', closeModal);
    // Cerrar modal al hacer clic fuera del contenido
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });
});