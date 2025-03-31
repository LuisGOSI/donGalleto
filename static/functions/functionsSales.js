document.addEventListener('DOMContentLoaded', () => {
    const addButtons = document.querySelectorAll('.add-btn');
    const salesTableBody = document.querySelector('.sales-table tbody');
    const subtotalInput = document.getElementById('subtotal');
    const totalInput = document.getElementById('total');
    const clearBtn = document.getElementById('clear-btn');

    let subtotal = 0;

    addButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            const productCard = e.target.closest('.product-card');
            const productName = productCard.querySelector('p').textContent;
            const productPrice = parseFloat(productCard.querySelector('p:nth-child(2)').textContent.replace('Precio: $', ''));

            const newRow = salesTableBody.insertRow();
            newRow.innerHTML = `
                <td>${productName}</td>
                <td>
                    <select>
                        <option value="piezas">Piezas</option>
                        <option value="gramos">Gramos</option>
                        <option value="paquete">Paquete</option>
                    </select>
                </td>
                <td><input type="number" min="1" value="1"></td>
                <td>$${productPrice}</td>
                <td>
                    <button class="action-btn">❌</button>
                </td>
            `;

            subtotal += productPrice;
            subtotalInput.value = subtotal.toFixed(2);
            totalInput.value = subtotal.toFixed(2);

            // Evento para eliminar fila
            newRow.querySelector('.action-btn').addEventListener('click', () => {
                const rowPrice = parseFloat(newRow.querySelector('td:nth-child(4)').textContent.replace('$', ''));
                subtotal -= rowPrice;
                subtotalInput.value = subtotal.toFixed(2);
                totalInput.value = subtotal.toFixed(2);
                newRow.remove();
            });
        });
    });

    // Evento para limpiar toda la tabla
    clearBtn.addEventListener('click', () => {
        // Eliminar todas las filas excepto la primera (inicial)
        while (salesTableBody.rows.length > 1) {
            salesTableBody.deleteRow(1);
        }
        
        // Reiniciar valores financieros
        subtotal = 0;
        subtotalInput.value = '0';
        totalInput.value = '0';
    });
});