
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
    document.querySelectorAll(".mermas-btn").forEach(button => {
        button.addEventListener("click", function () {
            let row = this.closest("tr");
            let idGalleta = row.querySelectorAll("td")[0].textContent.trim();
            let cantidadActual = row.querySelectorAll("td")[4].textContent.trim();

            document.getElementById("idInventarioGalletaFK").value = idGalleta;
            document.getElementById("cantidadActual").value = cantidadActual;
            
        });
    });
});
