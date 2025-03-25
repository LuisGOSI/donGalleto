document.addEventListener("DOMContentLoaded", function () {
  // Cargar datos en el modal de editar
  const editClienteModal = document.getElementById("editClienteModal");
  editClienteModal.addEventListener("show.bs.modal", function (event) {
      const button = event.relatedTarget; // Botón que activa el modal
      const idCliente = button.getAttribute("data-id");

      fetch(`/get_cliente/${idCliente}`)
          .then((response) => response.json())
          .then((data) => {
              document.getElementById("IdCliente").value = data.idCliente;
              document.getElementById("Nombre").value = data.nombreCliente;
              document.getElementById("Telefono").value = data.telefono;
              document.getElementById("Email").value = data.email;
          })
          .catch((error) => console.error("Error al obtener los datos del cliente:", error));
  });

  // Configurar el modal de desactivar
  const deleteClienteModal = document.getElementById("deleteClienteModal");
  deleteClienteModal.addEventListener("show.bs.modal", function (event) {
      const button = event.relatedTarget; // Botón que activa el modal
      const idCliente = button.getAttribute("data-id");

      document.getElementById("deleteIdCliente").value = idCliente;
  });
});

document.addEventListener("DOMContentLoaded", function () {
  // Configurar el modal de reactivar
  const activarClienteModal = document.getElementById("activarClienteModal");
  activarClienteModal.addEventListener("show.bs.modal", function (event) {
      const button = event.relatedTarget; // Botón que activa el modal
      const idCliente = button.getAttribute("data-id");

      document.getElementById("activarIdCliente").value = idCliente;
  });
});

//Cambiar contenido con switch
document.addEventListener("DOMContentLoaded", function () {
  const statusSwitch = document.getElementById("statusSwitch");
  const statusLabel = document.getElementById("statusLabel");

  statusSwitch.addEventListener("change", function () {
      const status = this.checked ? 0 : 1; 
      window.location.href = `/clientes?status=${status}`;
  });
});

document.addEventListener("DOMContentLoaded", function () {
  // Tiempo de alerta
  setTimeout(() => {
      document.querySelectorAll(".alert").forEach(alert => {
          alert.style.opacity = "0";
          setTimeout(() => alert.remove(), 500);
      });
  }, 4000);
});

/////////// Función dropdown Menu de cerrar sesión e histórico de compras ///////////
function toggleDropdown(event) {
  event.preventDefault();
  document.getElementById("userDropdownMenu").classList.toggle("show");
}

window.onclick = function(event) {
  if (!event.target.matches('.dropdown-toggle') && !event.target.matches('.header-icon')) {
    var dropdowns = document.getElementsByClassName("dropdown-menu");
    for (var i = 0; i < dropdowns.length; i++) {
      var openDropdown = dropdowns[i];
      if (openDropdown.classList.contains('show')) {
        openDropdown.classList.remove('show');
      }
    }
  }
}

document.addEventListener("DOMContentLoaded", function () {
    const unitBadges = document.querySelectorAll(".unit-badge");
    const unitOptions = ["Unidad", "Paquetes", "Gramaje"];

    unitBadges.forEach((badge) => {
        let currentIndex = 0;

        badge.addEventListener("click", function () {
            currentIndex = (currentIndex + 1) % unitOptions.length;
            badge.textContent = unitOptions[currentIndex];
        });
    });

    // Manejar el aumento y disminución de cantidad
    document.querySelectorAll(".product-card").forEach((card) => {
      const quantityInput = card.querySelector(".quantity-input");
      const increaseBtn = card.querySelector(".quantity-btn:first-of-type"); // Botón "+"
      const decreaseBtn = card.querySelector(".quantity-btn:last-of-type");  // Botón "-"

      increaseBtn.addEventListener("click", function () {
          let currentValue = parseInt(quantityInput.value);
          if (!isNaN(currentValue)) {
              quantityInput.value = currentValue + 1; // Aumenta el valor
          }
      });

      decreaseBtn.addEventListener("click", function () {
          let currentValue = parseInt(quantityInput.value);
          if (!isNaN(currentValue) && currentValue > 1) {
              quantityInput.value = currentValue - 1; // Disminuye el valor, pero no baja de 1
          }
      });
  });
});
