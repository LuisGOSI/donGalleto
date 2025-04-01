// --------------------------------------------------------- Funcion js para modal ---------------------------------------------------------  //
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('nuevaOrdenModal');
    const closeModalBtn = modal.querySelector('.close-modal');
    const produceButtons = document.querySelectorAll('.custom-botonProducir');

    produceButtons.forEach(button => {
        button.addEventListener('click', function() {
            const productName = this.getAttribute('data-product');
            modal.style.display = 'block';
        });
    });

    closeModalBtn.addEventListener('click', function() {
        modal.style.display = 'none';
    });

    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
});