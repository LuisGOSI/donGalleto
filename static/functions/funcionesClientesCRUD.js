/////////////// Funciones para CRUD de Clientes /////////////
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

///////////// Función para santización de modales ///////////
// Función autoejecutable para sanitización de formularios de cliente
(function() {
    'use strict';
    
    // Inicializar los formularios cuando el DOM esté cargado
    document.addEventListener('DOMContentLoaded', function() {
        initFormValidation('registroModal');
        initFormValidation('editClienteModal');
    });
    
    function initFormValidation(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return;
        
        const form = modal.querySelector('form');
        if (!form) return;
        
        // Añadir atributo novalidate para controlar la validación manualmente
        form.setAttribute('novalidate', '');
        
        // Definir patrones de validación para los campos
        setupValidationPatterns(form);
        
        // Configurar listeners para todos los inputs
        setupInputListeners(form);
        
        // Manejar el envío del formulario
        setupFormSubmission(form);
    }
    
    function setupValidationPatterns(form) {
        // Configurar patrones para validación consistente
        const inputs = {
            nombreCliente: form.querySelector('#nombreCliente') || form.querySelector('#Nombre'),
            telefono: form.querySelector('#telefono') || form.querySelector('#Telefono'),
            email: form.querySelector('#email') || form.querySelector('#Email'),
            password: form.querySelector('#password')
        };
        
        // Solo configurar los inputs que existan en el formulario
        if (inputs.nombreCliente) {
            inputs.nombreCliente.setAttribute('pattern', '^[A-Za-zÁÉÍÓÚáéíóúÑñ\\s]{2,50}$');
            inputs.nombreCliente.setAttribute('title', 'Solo letras y espacios permitidos (2-50 caracteres)');
            inputs.nombreCliente.setAttribute('maxlength', '50');
            
            // Añadir mensaje de error si no existe
            addInvalidFeedback(inputs.nombreCliente, 'Por favor ingresa un nombre válido (solo letras y espacios).');
        }
        
        if (inputs.telefono) {
            inputs.telefono.setAttribute('pattern', '^[0-9]{10}$');
            inputs.telefono.setAttribute('title', 'Ingresa un número de 10 dígitos');
            inputs.telefono.setAttribute('maxlength', '10');
            
            addInvalidFeedback(inputs.telefono, 'Por favor ingresa un número telefónico válido (10 dígitos).');
        }
        
        if (inputs.email) {
            inputs.email.setAttribute('pattern', '^[a-zA-Z0-9._%+\\-]+@[a-zA-Z0-9.\\-]+\\.[a-zA-Z]{2,}$');
            inputs.email.setAttribute('maxlength', '100');
            
            addInvalidFeedback(inputs.email, 'Por favor ingresa un correo electrónico válido.');
        }
        
        if (inputs.password) {
            inputs.password.setAttribute('pattern', '^(?=.*[A-Za-z])(?=.*\\d)(?=.*[@$!%*#?&])[A-Za-z\\d@$!%*#?&]{8,}$');
            inputs.password.setAttribute('title', 'La contraseña debe tener al menos 8 caracteres, incluyendo una letra, un número y un carácter especial');
            inputs.password.setAttribute('minlength', '8');
            inputs.password.setAttribute('maxlength', '50');
            
            addInvalidFeedback(inputs.password, 'La contraseña debe tener al menos 8 caracteres, incluyendo una letra, un número y un carácter especial.');
        }
    }
    
    function addInvalidFeedback(input, message) {
        // Verificar si ya existe un div de feedback
        let feedback = input.nextElementSibling;
        if (!feedback || !feedback.classList.contains('invalid-feedback')) {
            feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            feedback.textContent = message;
            input.parentNode.insertBefore(feedback, input.nextElementSibling);
        }
    }
    
    function setupInputListeners(form) {
        const inputs = form.querySelectorAll('input, select');
        
        inputs.forEach(input => {
            // Validación en tiempo real con debounce
            input.addEventListener('input', function() {
                clearTimeout(this.debounceTimer);
                this.debounceTimer = setTimeout(() => {
                    validateField(this);
                }, 500);
                
                // Validación específica según tipo de campo
                handleSpecificFieldValidation(this);
            });
            
            // Sanitización y validación completa al perder el foco
            input.addEventListener('blur', function() {
                sanitizeInput(this);
                validateField(this);
            });
        });
    }
    
    function handleSpecificFieldValidation(input) {
        // Validación específica para campos de nombre (quitar caracteres no permitidos en tiempo real)
        if (input.id === 'nombreCliente' || input.id === 'Nombre') {
            const invalidChars = /[^A-Za-zÁÉÍÓÚáéíóúÑñ\s]/g;
            if (invalidChars.test(input.value)) {
                input.value = input.value.replace(invalidChars, '');
                showTemporaryMessage(input, 'Caracteres no válidos eliminados');
            }
        }
        
        // Validación específica para campos de teléfono
        if (input.id === 'telefono' || input.id === 'Telefono') {
            const invalidChars = /[^0-9]/g;
            if (invalidChars.test(input.value)) {
                input.value = input.value.replace(invalidChars, '');
                showTemporaryMessage(input, 'Solo se permiten números en el teléfono');
            }
        }
    }
    
    function sanitizeInput(input) {
        if (input.value && input.type !== 'password') {
            input.value = input.value
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#039;');
        }
    }
    
    function validateField(input) {
        const isValid = input.checkValidity();
        
        if (isValid) {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
        } else {
            input.classList.remove('is-valid');
            input.classList.add('is-invalid');
        }
        
        return isValid;
    }
    
    function setupFormSubmission(form) {
        form.addEventListener('submit', function(event) {
            let isFormValid = true;
            const inputs = form.querySelectorAll('input, select');
            
            inputs.forEach(input => {
                sanitizeInput(input);
                if (!validateField(input)) {
                    isFormValid = false;
                }
            });
            
            if (!isFormValid) {
                event.preventDefault();
                event.stopPropagation();
                
                // Enfocar el primer campo inválido
                const firstInvalidField = form.querySelector('.is-invalid');
                if (firstInvalidField) {
                    firstInvalidField.focus();
                }
                
                // Mostrar alerta de error si no existe
                showFormErrorAlert(form);
            }
            
            form.classList.add('was-validated');
        }, false);
    }
    
    function showFormErrorAlert(form) {
        const errorAlert = form.querySelector('#formErrorAlert');
        if (!errorAlert) {
            const alert = document.createElement('div');
            alert.id = 'formErrorAlert';
            alert.className = 'alert alert-danger mt-3';
            alert.role = 'alert';
            alert.innerHTML = 'Por favor, corrige los errores marcados en el formulario.';
            form.prepend(alert);
            
            // Remover alerta después de 5 segundos
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.parentNode.removeChild(alert);
                }
            }, 5000);
        }
    }
    
    function showTemporaryMessage(element, message) {
        let msgElement = element.nextElementSibling;
        while (msgElement && !msgElement.classList.contains('temp-message')) {
            msgElement = msgElement.nextElementSibling;
        }
        
        if (!msgElement) {
            msgElement = document.createElement('div');
            msgElement.className = 'temp-message text-danger small mt-1';
            element.parentNode.insertBefore(msgElement, element.nextElementSibling);
        }
        
        msgElement.textContent = message;
        
        setTimeout(() => {
            if (msgElement.parentNode) {
                msgElement.parentNode.removeChild(msgElement);
            }
        }, 3000);
    }
  })();