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
