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
        // Guardar el precio base original si no está definido
        if (!item.basePrice) {
            item.basePrice = item.price;
        }
        // Resetear al precio base antes de aplicar cualquier cálculo
        item.price = item.basePrice;
        switch (item.type) {
            case "Unidad":
                item.unidades = item.quantity;
                break;
            case "Paquete 1kg":
                fetch("/revisarGramajePorNombre1kg", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(item)
                })
                    .then(response => response.json())
                    .then(data => {
                        item.unidades = data.cantidadPara1kg;
                        item.price = (item.unidades * item.basePrice) * 0.93;
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
                        item.unidades = data.cantidadPara700gr;
                        item.price = (item.unidades * item.basePrice) * 0.93;
                        renderCart();
                    })
                    .catch(error => console.error("Error:", error));
                break;
            case "Gramaje":
                fetch("/revisarGramajePorNombre", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(item)
                })
                    .then(response => response.json())
                    .then(data => {
                        const gramosPorUnidad = data.pesoGalleta;
                        item.unidades = Math.round(item.quantity / gramosPorUnidad);
                        item.price = item.basePrice * item.unidades;
                        renderCart();
                    })
                    .catch(error => console.error("Error:", error));
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
        item.basePrice = item.price; // Guardar el precio base original
        item.unidades = 1; // Inicializar unidades
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
                        <option value="Gramaje" ${item.type === "Gramaje" ? "selected" : ""}>Gramaje</option>
                    </select>
                    ${item.type === "Gramaje" ? `<div class="small-text">(${item.unidades} unidades)</div>` : ''}
                </td>
                <td>
                    ${item.type === "Gramaje" ? 
                        `<input type="number" class="quantity-input" data-index="${index}" value="${item.quantity}" min="1" step="1">` : 
                        `<input type="number" class="quantity-input" data-index="${index}" value="${item.quantity}" min="1">`}
                </td>
                <td class="price-column">$${item.type === "Gramaje" ? item.price.toFixed(2) : (item.price * item.quantity).toFixed(2)}</td>
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
            // Si es gramaje, recalcular el precio
            if (cart[index].type === "Gramaje") {
                PAQUETE_CANTIDAD(cart[index]);
            }
        } else if (event.target.classList.contains("type-select")) {
            cart[index].type = event.target.value;
            // Resetear cantidad a 1 si cambia de gramaje a otro tipo o viceversa
            if ((event.target.value === "Gramaje" && cart[index].quantity === 1) || 
                (event.target.value !== "Gramaje" && cart[index].type === "Gramaje")) {
                cart[index].quantity = 1;
            }
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
        let subtotal = cart.reduce((acc, item) => {
            if (item.type === "Gramaje") {
                return acc + item.price; // Ya está calculado el precio total para gramaje
            } else {
                return acc + (item.price * item.quantity);
            }
        }, 0);
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
        // =============== FUNCIONALIDAD PARA VENTAS ONLINE ==========

    // Elementos del modal
    const modal = document.getElementById("ventaOnlineModal");
    const closeModal = document.querySelector(".close-modal");
    const confirmarVentaBtn = document.getElementById("confirmarVentaBtn");
    const cancelarVentaBtn = document.getElementById("cancelarVentaBtn");
    const ventaIdSpan = document.getElementById("ventaId");
    const ventaInfoDiv = document.getElementById("ventaInfo");

    // Función para formatear la fecha
    function formatearFecha(fechaStr) {
        if (!fechaStr) return '';
        try {
            const fecha = new Date(fechaStr);
            return fecha.toLocaleDateString();
        } catch (e) {
            return fechaStr;
        }
    }

    // Función para mostrar el modal con animación
    function showModal() {
        modal.classList.add('active');
    }

    // Función para cerrar el modal con animación
    function closeModalWithAnimation() {
        modal.classList.add('closing');
        
        setTimeout(() => {
            modal.classList.remove('active');
            modal.classList.remove('closing');
        }, 300);
    }

    // Crear efecto de confeti al confirmar la venta
    function createConfettiEffect() {
        const confettiCount = 80;
        const colors = ['#2ecc71', '#3498db', '#f1c40f', '#e74c3c', '#9b59b6'];
        
        for (let i = 0; i < confettiCount; i++) {
            const confetti = document.createElement('div');
            confetti.style.position = 'absolute';
            confetti.style.width = `${Math.random() * 10 + 5}px`;
            confetti.style.height = `${Math.random() * 10 + 5}px`;
            confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
            confetti.style.borderRadius = '50%';
            confetti.style.left = `${Math.random() * 100}%`;
            confetti.style.top = `-10px`;
            confetti.style.opacity = '1';
            confetti.style.zIndex = '9999';
            
            modal.appendChild(confetti);
            
            // Animar cada confeti
            const animation = confetti.animate([
                { 
                    transform: `translate(0, 0) rotate(0deg)`, 
                    opacity: 1 
                },
                { 
                    transform: `translate(${Math.random() * 300 - 150}px, ${Math.random() * 600 + 400}px) rotate(${Math.random() * 360}deg)`, 
                    opacity: 0 
                }
            ], {
                duration: Math.random() * 1500 + 1500,
                easing: 'cubic-bezier(0.25, 1, 0.5, 1)'
            });
            
            animation.onfinish = () => {
                confetti.remove();
            };
        }
    }

    // Buscar venta online
    if (buscarVentaBtn) {
        buscarVentaBtn.addEventListener("click", async function() {
            const codigoVenta = codigoVentaInput.value.trim();
            
            if (!codigoVenta) {
                Swal.fire({
                    icon: 'warning',
                    title: 'Atención',
                    text: 'Por favor ingrese un código de venta',
                    confirmButtonText: 'Entendido',
                    confirmButtonColor: '#3085d6'
                  });
                return;
            }

            try {
                buscarVentaBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Buscando...';
                buscarVentaBtn.disabled = true;
                
                const response = await fetch(`/obtenerVentaOnline/${codigoVenta}`);
                const data = await response.json();
                
                if (response.ok) {
                    currentOnlineOrder = data;
                    
                    // Mostrar información de la venta en el modal
                    ventaIdSpan.textContent = codigoVenta;
                    ventaInfoDiv.innerHTML = `
                        <p><strong>Fecha:</strong> ${formatearFecha(data.venta.fechaVenta)}</p>
                        <p><strong>Estado:</strong> ${data.venta.estadoVenta}</p>
                        <p><strong>Total:</strong> $${data.venta.totalVenta.toFixed(2)}</p>
                        <h4>Productos:</h4>
                        <ul>
                            ${data.detalles.map(p => `
                                <li>${p.nombre} - ${p.cantidadVendida} ${p.tipoVenta}/es - $${p.precioUnitarioVendido.toFixed(2)} - C/U </li>
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
                    
                    showModal();
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
    }

    // Cerrar modal
    if (closeModal) {
        closeModal.addEventListener('click', function() {
            closeModalWithAnimation();
        });
    }

    // Confirmar venta
    if (confirmarVentaBtn) {
        confirmarVentaBtn.addEventListener('click', async function() {
            if (!currentOnlineOrder) return;
            
            confirmarVentaBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Confirmando...';
            confirmarVentaBtn.disabled = true;
            
            try {
                const response = await fetch(`/confirmarVentaOnline/${currentOnlineOrder.venta.idVenta}`, {
                    method: 'POST'
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    // Efecto visual de confirmación
                    createConfettiEffect();
                    
                    // Actualizar la interfaz
                    const estadoElements = ventaInfoDiv.querySelectorAll('p');
                    estadoElements.forEach(p => {
                        if (p.innerHTML.includes('<strong>Estado:</strong>')) {
                            p.innerHTML = '<strong>Estado:</strong> confirmada';
                            p.style.color = '#2ecc71';
                            p.style.fontWeight = '700';
                        }
                    });
                    
                    // Ocultar los botones
                    confirmarVentaBtn.style.display = 'none';
                    cancelarVentaBtn.style.display = 'none';
                    
                    // Mostrar mensaje de éxito
                    setTimeout(() => {
                        closeModalWithAnimation();
                        codigoVentaInput.value = '';
                        currentOnlineOrder = null;
                    }, 2000);
                } else {
                    alert(data.error || 'Error al confirmar la venta');
                    confirmarVentaBtn.innerHTML = 'Confirmar Venta';
                    confirmarVentaBtn.disabled = false;
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error al conectar con el servidor');
                confirmarVentaBtn.innerHTML = 'Confirmar Venta';
                confirmarVentaBtn.disabled = false;
            }
        });
    }

    // Cancelar venta
    if (cancelarVentaBtn) {
        cancelarVentaBtn.addEventListener('click', async function () {
            if (!currentOnlineOrder) return;
    
            // Mostrar confirmación con SweetAlert2
            const result = await Swal.fire({
                title: '¿Cancelar venta?',
                text: '¿Estás seguro de que deseas cancelar esta venta?',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#3085d6',
                confirmButtonText: 'Sí, cancelar',
                cancelButtonText: 'No'
            });
    
            // Si el usuario cancela
            if (!result.isConfirmed) return;
    
            // Esperar un par de segundos antes de continuar
            await new Promise(resolve => setTimeout(resolve, 2000));
    
            cancelarVentaBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Cancelando...';
            cancelarVentaBtn.disabled = true;
    
            try {
                const response = await fetch(`/cancelarVentaOnline/${currentOnlineOrder.venta.idVenta}`, {
                    method: 'POST'
                });
    
                const data = await response.json();
    
                if (response.ok) {
                    const estadoElements = ventaInfoDiv.querySelectorAll('p');
                    estadoElements.forEach(p => {
                        if (p.innerHTML.includes('<strong>Estado:</strong>')) {
                            p.innerHTML = '<strong>Estado:</strong> cancelada';
                            p.style.color = '#e74c3c';
                            p.style.fontWeight = '700';
                        }
                    });
    
                    ventaInfoDiv.style.transition = 'all 0.3s ease';
                    ventaInfoDiv.style.backgroundColor = '#ffebee';
                    ventaInfoDiv.style.borderLeft = '4px solid #e74c3c';
    
                    confirmarVentaBtn.style.display = 'none';
                    cancelarVentaBtn.style.display = 'none';
    
                    setTimeout(() => {
                        closeModalWithAnimation();
                        codigoVentaInput.value = '';
                        currentOnlineOrder = null;
                    }, 2000);
                } else {
                    Swal.fire('Error', data.error || 'Error al cancelar la venta', 'error');
                    cancelarVentaBtn.innerHTML = 'Cancelar Venta';
                    cancelarVentaBtn.disabled = false;
                }
            } catch (error) {
                console.error('Error:', error);
                Swal.fire('Error', 'Error al conectar con el servidor', 'error');
                cancelarVentaBtn.innerHTML = 'Cancelar Venta';
                cancelarVentaBtn.disabled = false;
            }
        });
    }
    

    // Cerrar modal al hacer clic fuera
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            closeModalWithAnimation();
        }
    });

    // Validación del input de código
    if (codigoVentaInput) {
        codigoVentaInput.addEventListener('input', function() {
            this.value = this.value.replace(/[^0-9]/g, '');
        });
    }
});