document.addEventListener("DOMContentLoaded", () => {
    const cartTableBody = document.querySelector(".sales-table tbody");
    const subtotalInput = document.getElementById("subtotal");
    const descuentoInput = document.getElementById("descuento");
    const totalInput = document.getElementById("total");
    const clearButton = document.getElementById("clear-btn");
    const addButtons = document.querySelectorAll(".add-btn");
    const sellButton = document.querySelector(".btn-primary");
    const buscarVentaBtn = document.getElementById("buscaVentaBtn");
    const codigoVentaInput = document.getElementById("codigoVentaOnline");


    let cart = [];
    let currentOnlineOrder = null;

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
                        item.price = (data.cantidadPara1kg * item.price) * 0.93;
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
                        item.price = (data.cantidadPara700gr * item.price) * 0.93;
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
            total: parseFloat(totalInput.value),
            tipoVenta: "local"
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
                if (data.pdf_url) {
                    window.open(data.pdf_url, '_blank');
                }
            })
            .catch(error => {
                alert("Error al registrar la venta: " + (error.error || error.message || "Error desconocido"));
            });
    });
        // ========== NUEVA FUNCIONALIDAD PARA VENTAS ONLINE ==========

    // Elementos del modal
    const modal = document.getElementById("ventaOnlineModal");
    const closeModal = document.querySelector(".close-modal");
    const confirmarVentaBtn = document.getElementById("confirmarVentaBtn");
    const cancelarVentaBtn = document.getElementById("cancelarVentaBtn");
    const ventaIdSpan = document.getElementById("ventaId");
    const ventaInfoDiv = document.getElementById("ventaInfo");

    // Buscar venta online
    buscarVentaBtn.addEventListener("click", async function() {
        const codigoVenta = codigoVentaInput.value.trim();        
        
        if (!codigoVenta) {
            alert('Por favor ingrese un código de venta');
            return;
        }

        try {
            buscarVentaBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Buscando...';
            buscarVentaBtn.disabled = true;
            
            const response = await fetch(`/obtenerVentaOnline/${codigoVenta}`);
            const data = await response.json();
            
            if (response.ok) {
                currentOnlineOrder = data;
                console.log('Venta encontrada:', data);
                
                
                // Mostrar información de la venta en el modal
                ventaIdSpan.textContent = codigoVenta;
                ventaInfoDiv.innerHTML = `
                    <p><strong>Fecha:</strong> ${(data.venta.fechaVenta)}</p>
                    <p><strong>Estado:</strong> ${data.venta.estadoVenta}</p>
                    <p><strong>Total:</strong> $${data.venta.totalVenta.toFixed(2)}</p>
                    <h4>Productos:</h4>
                    <ul>
                        ${data.detalles.map(p => `
                            <li>${p.nombre} - ${p.cantidadVendida} ${p.tipoVenta}/es - $${p.precioUnitarioVendido} - C/U </li>
                        `).join('')}
                    </ul>
                `;
                
                // Mostrar u ocultar botones según el estado
                if (data.venta.estadoVenta === 'pendiente') {
                    confirmarVentaBtn.style.display = 'block';
                    cancelarVentaBtn.style.display = 'block';
                } else {
                    confirmarVentaBtn.style.display = 'none';
                    cancelarVentaBtn.style.display = 'none';
                    ventaInfoDiv.innerHTML += `<p class="alert">Esta venta ya ha sido ${data.venta.estadoVenta}</p>`;
                }
                
                modal.style.display = 'block';
            } else {
                alert(data.error || 'Error al buscar la venta');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error al conectar con el servidor');
        } finally {
            buscarVentaBtn.innerHTML = 'Buscar';
            buscarVentaBtn.disabled = false;
        }
    });

    // Cerrar modal
    closeModal.addEventListener('click', function() {
        modal.style.display = 'none';
    });

    // Confirmar venta
    confirmarVentaBtn.addEventListener('click', async function() {
        console.log('Confirmar venta:', currentOnlineOrder);
        
        if (!currentOnlineOrder) return;
        
        confirmarVentaBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Confirmando...';
        confirmarVentaBtn.disabled = true;
        
        try {
            const response = await fetch(`/confirmarVentaOnline/${currentOnlineOrder.venta.idVenta}`, {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (response.ok) {
                alert('Venta confirmada con éxito');
                modal.style.display = 'none';
                codigoVentaInput.value = '';
                currentOnlineOrder = null;
            } else {
                alert(data.error || 'Error al confirmar la venta');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error al conectar con el servidor');
        } finally {
            confirmarVentaBtn.innerHTML = 'Confirmar Venta';
            confirmarVentaBtn.disabled = false;
        }
    });

    // Cancelar venta
    cancelarVentaBtn.addEventListener('click', async function() {
        if (!currentOnlineOrder) return;
        
        if (!confirm('¿Estás seguro de que deseas cancelar esta venta?')) {
            return;
        }
        
        cancelarVentaBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Cancelando...';
        cancelarVentaBtn.disabled = true;
        
        try {
            const response = await fetch(`/cancelarVentaOnline/${currentOnlineOrder.venta.idVenta}`, {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (response.ok) {
                alert('Venta cancelada con éxito');
                modal.style.display = 'none';
                codigoVentaInput.value = '';
                currentOnlineOrder = null;
            } else {
                alert(data.error || 'Error al cancelar la venta');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error al conectar con el servidor');
        } finally {
            cancelarVentaBtn.innerHTML = 'Cancelar Venta';
            cancelarVentaBtn.disabled = false;
        }
    });

    // Cerrar modal al hacer clic fuera
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });

    // Validación del input de código
    codigoVentaInput.addEventListener('input', function() {
        this.value = this.value.replace(/[^0-9]/g, '');
    });
});


