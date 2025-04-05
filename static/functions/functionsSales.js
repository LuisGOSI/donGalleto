document.addEventListener("DOMContentLoaded", () => {
    const cartTableBody = document.querySelector(".sales-table tbody");
    const subtotalInput = document.getElementById("subtotal");
    const descuentoInput = document.getElementById("descuento");
    const totalInput = document.getElementById("total");
    const clearButton = document.getElementById("clear-btn");
    const addButtons = document.querySelectorAll(".add-btn");
    const sellButton = document.querySelector(".btn-primary");

    let cart = [];
    const CANTIDAD_GALLETAS = 0

    function PAQUETE_CANTIDAD(item) {        
        switch (item.type) {
            case "Paquete 1kg":
                fetch("/revisarGramajePorNombre1kg", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(item)
                })
                    .then(response => response.json())
                    .then(data => {
                        item.price = (data.cantidadPara1kg * item.price) * 0.95;
                        renderCart();
                    })
                    .catch(error => console.error("Error:", error));
                break;
            case "Paquete 700gr":
                fetch("/revisarGramajePorNombre700gr", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(item)
                })
                    .then(response => response.json())
                    .then(data => {
                        item.price = (data.cantidadPara700gr * item.price) * 0.95;
                        renderCart();
                    })
                    .catch(error => console.error("Error:", error));
                break;
            default:
                item.price = item.price; // No change for Unidad
                break;
        }
    }

    addButtons.forEach((button, index) => {
    button.addEventListener("click", () => {
        const productCard = button.closest(".product-card");
        const name = productCard.querySelector("p:nth-of-type(1)").textContent;
        const price = parseFloat(productCard.querySelector("p:nth-of-type(2)").textContent.replace("Precio: ", "").replace(" C/U", ""));
        const type = "Unidad";

        addToCart({ name, price, type, quantity: 1 });
    });
});

function addToCart(item) {
    cart.push(item);
    renderCart();
}

function renderCart() {
    cartTableBody.innerHTML = "";
    cart.forEach((item, index) => {
        const row = document.createElement("tr");
        row.innerHTML = `
                <td>${item.name}</td>
                <td>
                    <select class="type-select" data-index="${index}">
                        <option value="Unidad" ${item.type === "Unidad" ? "selected" : ""}>Unidad</option>
                        <option value="Paquete 1kg" ${item.type === "Paquete 1kg" ? "selected" : ""}>Paquete 1kg</option>
                        <option value="Paquete 700gr" ${item.type === "Paquete 700gr" ? "selected" : ""}>Paquete 700gr</option>
                    </select>
                </td>
                <td>
                    <input type="number" class="quantity-input" data-index="${index}" value="${item.quantity}" min="1">
                </td>
                <td class="price-column">$${(item.price * item.quantity).toFixed(2)}</td>
                <td><button class="remove-btn" data-index="${index}">❌</button></td>
            `;
        cartTableBody.appendChild(row);
    });
    updateTotals();
}

cartTableBody.addEventListener("change", (event) => {
    const index = event.target.dataset.index;
    if (event.target.classList.contains("quantity-input")) {
        cart[index].quantity = parseInt(event.target.value) || 1;
    } else if (event.target.classList.contains("type-select")) {
        cart[index].type = event.target.value;
        PAQUETE_CANTIDAD(cart[index]);
        
    }
    renderCart();
});

cartTableBody.addEventListener("click", (event) => {
    if (event.target.classList.contains("remove-btn")) {
        const index = event.target.dataset.index;
        cart.splice(index, 1);
        renderCart();
    }
});

function updateTotals() {
    let subtotal = cart.reduce((acc, item) => acc + item.price * item.quantity, 0);
    subtotalInput.value = subtotal.toFixed(2);
    let descuento = parseFloat(descuentoInput.value) || 0;
    let descuentoAplicado = (subtotal * descuento) / 100;
    totalInput.value = (subtotal - descuentoAplicado).toFixed(2);
}

descuentoInput.addEventListener("input", updateTotals);

clearButton.addEventListener("click", () => {
    cart = [];
    renderCart();
});

sellButton.addEventListener("click", () => {
    const ventaData = {
        productos: cart,
        subtotal: parseFloat(subtotalInput.value),
        descuento: parseFloat(descuentoInput.value),
        total: parseFloat(totalInput.value)
    };

    fetch("/registrarVenta", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(ventaData)
    })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => Promise.reject(err));
            }
            return response.json();
        })
        .then(data => {
            alert("Venta registrada exitosamente: " + data.mensaje);
            cart = [];
            renderCart();
        })
        .catch(error => {
            alert("Error al registrar la venta: " + (error.error || error.message || "Error desconocido"));
        });
});
});
