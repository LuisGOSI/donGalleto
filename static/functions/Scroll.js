let lastScrollY = window.scrollY;
let ticking = false;
const header = document.querySelector("header");

window.addEventListener("scroll", () => {
	if (!ticking) {
		window.requestAnimationFrame(() => {
			if (window.scrollY > lastScrollY + 5) {
				header.style.transform = "translateY(-100%)";
			} else if (window.scrollY < lastScrollY - 15) {
				header.style.transform = "translateY(0)";
			}
			lastScrollY = window.scrollY;
			ticking = false;
		});
		ticking = true;
	}
});

document.addEventListener("DOMContentLoaded", function () {
	document.querySelectorAll(".product-card").forEach(product => {
		const btnIncrease = product.querySelector(".quantity-btn:first-child"); // Botón "+"
		const btnDecrease = product.querySelector(".quantity-btn:last-child");  // Botón "-"
		const quantityInput = product.querySelector(".quantity-input");         // Input de cantidad

		// Aumentar cantidad
		btnIncrease.addEventListener("click", function () {
			let value = parseInt(quantityInput.value, 10);
			quantityInput.value = isNaN(value) ? 1 : value + 1;
		});
		btnDecrease.addEventListener("click", function () {
			let value = parseInt(quantityInput.value, 10);
			quantityInput.value = isNaN(value) || value <= 1 ? 1 : value - 1;
		});
	});
});

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
});

function toggleDropdown(event) {
	event.preventDefault();
	document.getElementById("userDropdownMenu").classList.toggle("show");
}

function cerrarSesion(event) {
	event.preventDefault();
	document.getElementById("logoutForm").submit();
}
window.onclick = function (event) {
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