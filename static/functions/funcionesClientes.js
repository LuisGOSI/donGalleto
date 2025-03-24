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