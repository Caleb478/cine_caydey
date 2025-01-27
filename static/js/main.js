const fila = document.querySelector('.contenedor-carousel');
const peliculas = document.querySelectorAll('.pelicula');

const flechaIzquierda = document.getElementById('flecha-izquierda');
const flechaDerecha = document.getElementById('flecha-derecha');

// ? ----- ----- Event Listener para la flecha derecha. ----- -----
flechaDerecha.addEventListener('click', () => {
	fila.scrollLeft += fila.offsetWidth;

	const indicadorActivo = document.querySelector('.indicadores .activo');
	if(indicadorActivo.nextSibling){
		indicadorActivo.nextSibling.classList.add('activo');
		indicadorActivo.classList.remove('activo');
	}
});

// ? ----- ----- Event Listener para la flecha izquierda. ----- -----
flechaIzquierda.addEventListener('click', () => {
	fila.scrollLeft -= fila.offsetWidth;

	const indicadorActivo = document.querySelector('.indicadores .activo');
	if(indicadorActivo.previousSibling){
		indicadorActivo.previousSibling.classList.add('activo');
		indicadorActivo.classList.remove('activo');
	}
});

// ? ----- ----- Paginacion ----- -----
const numeroPaginas = Math.ceil(peliculas.length / 5);
for(let i = 0; i < numeroPaginas; i++){
	const indicador = document.createElement('button');

	if(i === 0){
		indicador.classList.add('activo');
	}

	document.querySelector('.indicadores').appendChild(indicador);
	indicador.addEventListener('click', (e) => {
		fila.scrollLeft = i * fila.offsetWidth;

		document.querySelector('.indicadores .activo').classList.remove('activo');
		e.target.classList.add('activo');
	});
}

// ? ----- ----- Hover ----- -----
peliculas.forEach((pelicula) => {
	pelicula.addEventListener('mouseenter', (e) => {
		const elemento = e.currentTarget;
		setTimeout(() => {
			peliculas.forEach(pelicula => pelicula.classList.remove('hover'));
			elemento.classList.add('hover');
		}, 300);
	});
});

fila.addEventListener('mouseleave', () => {
	peliculas.forEach(pelicula => pelicula.classList.remove('hover'));
});
//--Ventana Modal
document.addEventListener("DOMContentLoaded", function () {
    const peliculaImgs = document.querySelectorAll('.pelicula-img');
    
    peliculaImgs.forEach(img => {
        img.addEventListener('click', function() {
            const idPelicula = img.getAttribute('data-id');
            
            fetch(`/pelicula/${idPelicula}`)
                .then(response => response.json())
                .then(data => {
                    // Obtener datos de la película
                    const pelicula = data;
                    document.getElementById('modalTitulo').innerText = pelicula.Titulo;
                    document.getElementById('modalImg').src = pelicula.Cartel;
                    document.getElementById('modalDescripcion').innerText = pelicula.Sinopsis;
                    document.getElementById('modalGenero').innerText = `Género: ${pelicula.Genero}`;
                    document.getElementById('modalDuracion').innerText = `Duración: ${pelicula.Duracion} minutos`;

                    // Mostrar el modal
                    const modal = new bootstrap.Modal(document.getElementById('modalPelicula'));
                    modal.show();

                    // Botón para ver sesiones
                    const btnVerSesiones = document.getElementById('btnVerSesiones');
                    btnVerSesiones.onclick = function() {
                        const sesionesList = document.getElementById('sesionesList');
                        sesionesList.innerHTML = ''; // Limpiar sesiones previas
                        
                        // Llamar a la API para obtener las sesiones de la película
                        fetch(`/sesiones/${idPelicula}`)
                            .then(response => response.json())
                            .then(sesiones => {
                                // Verificamos que estamos obteniendo las sesiones
                                console.log('Sesiones obtenidas:', sesiones);

                                if (sesiones.length === 0) {
                                    // Si no hay sesiones, mostrar un mensaje
                                    sesionesList.innerHTML = '<li>No hay sesiones disponibles para esta película.</li>';
                                } else {
                                    // Agregar las sesiones al modal
                                    sesiones.forEach(sesion => {
                                        const li = document.createElement('li');
                                        li.innerText = `Fecha: ${sesion.Fecha}, Hora: ${sesion.Hora}, Idioma: ${sesion.Idioma}`;
                                        sesionesList.appendChild(li);
                                    });
                                }

                                // Mostrar las sesiones
                                document.getElementById('modalSesiones').style.display = 'block';
                            })
                            .catch(error => {
                                console.error('Error al obtener las sesiones:', error);
                            });
                    };
                })
                .catch(error => {
                    console.error('Error al obtener los datos de la película:', error);
                });
        });
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const selectPelicula = document.getElementById("selectPelicula");
    const selectSesion = document.getElementById("selectSesion");
    const butacasContainer = document.getElementById("butacasContainer");
    const cantidadEntradas = document.getElementById("cantidadEntradas");
    const precioTotal = document.getElementById("precioTotal");
    const precioPorBoleto = 10.00; // Precio fijo por boleto

    // Cargar películas
    fetch("/obtener_peliculas")
        .then(res => res.json())
        .then(peliculas => {
            selectPelicula.innerHTML = peliculas.map(p => `<option value="${p.idPelicula}">${p.Titulo}</option>`).join("");
        });

    // Cargar sesiones al seleccionar una película
    selectPelicula.addEventListener("change", function () {
        fetch(`/obtener_sesiones/${this.value}`)
            .then(res => res.json())
            .then(sesiones => {
                selectSesion.innerHTML = sesiones.map(s => 
                    `<option value="${s.idSesion}" data-idsala="${s.idSala}">${s.Fecha} - ${s.Hora}</option>`
                ).join("");
            });
    });

    // Cargar butacas al seleccionar una sesión
    selectSesion.addEventListener("change", function () {
        const idSala = selectSesion.options[selectSesion.selectedIndex].dataset.idsala;
        fetch(`/obtener_butacas/${idSala}`)
            .then(res => res.json())
            .then(butacas => {
                butacasContainer.innerHTML = butacas.map(b =>
                    `<div>
                        <input type="checkbox" id="butaca${b.idButaca}" value="${b.idButaca}" ${b.Estado === 'Ocupada' ? 'disabled' : ''}>
                        <label for="butaca${b.idButaca}">Fila ${b.Fila}, Número ${b.Numero}</label>
                    </div>`
                ).join("");
                // Agregar evento para actualizar cantidad y precio
                actualizarEventosButacas();
            });
    });

    // Actualizar cantidad y precio al seleccionar butacas
    function actualizarEventosButacas() {
        const butacas = document.querySelectorAll("#butacasContainer input[type='checkbox']");
        butacas.forEach(butaca => {
            butaca.addEventListener("change", function () {
                const seleccionadas = document.querySelectorAll("#butacasContainer input[type='checkbox']:checked").length;
                cantidadEntradas.value = seleccionadas; // Actualizar cantidad
                precioTotal.value = `$${(seleccionadas * precioPorBoleto).toFixed(2)}`; // Actualizar precio total
            });
        });
    }

    // Confirmar compra
    document.getElementById("formCompra").addEventListener("submit", function (e) {
        e.preventDefault();
        const idSesion = selectSesion.value;
        const idButacas = Array.from(document.querySelectorAll("#butacasContainer input:checked")).map(b => b.value);

        if (idButacas.length === 0) {
            alert("Debes seleccionar al menos una butaca.");
            return;
        }

        fetch("/realizar_compra", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ idSesion, idButacas })
        })
            .then(res => res.json())
            .then(data => alert(`Compra realizada con éxito. Precio total: $${data.precio_total}`))
            .catch(err => console.error("Error:", err));
    });
});

// para la propuesta de valor
//temporadas
const body = document.body; // Obtén el elemento <body>
const backgrounds = ['default', 'navidad', 'halloween', 'verano']; // Clases de fondo
let index = 0; // Índice inicial

function changeBackground() {
    // Elimina todas las clases de fondo
    backgrounds.forEach(bg => body.classList.remove(bg));

    // Añade la nueva clase de fondo (según el índice)
    body.classList.add(backgrounds[index]);

    // Incrementa el índice y vuelve a 0 si llega al final
    index = (index + 1) % backgrounds.length;
}

// Cambia el fondo inmediatamente al cargar la página
changeBackground();

// Cambia el fondo cada 60 segundos (1 minuto)
setInterval(changeBackground, 60000);


//codigo agregado 27/1/25
document.addEventListener("DOMContentLoaded", function () {
    // Formulario de Método de Pago
    const formMetodoPago = document.getElementById("formMetodoPago");

    formMetodoPago.addEventListener("submit", function (e) {
        e.preventDefault();

        // Obtener datos del formulario
        const numeroTarjeta = document.getElementById("numeroTarjeta").value;
        const nombreTitular = document.getElementById("nombreTitular").value;
        const fechaExpiracion = document.getElementById("fechaExpiracion").value;
        const cvv = document.getElementById("cvv").value;

        if (!numeroTarjeta || !nombreTitular || !fechaExpiracion || !cvv) {
            alert("Por favor, completa todos los campos.");
            return;
        }

        // Simular confirmación de pago
        alert(`Pago confirmado con la tarjeta terminada en ${numeroTarjeta.slice(-4)}.`);
        const modalMetodoPago = bootstrap.Modal.getInstance(document.getElementById("modalMetodoPago"));
        modalMetodoPago.hide();
    });

    // Generar QR automáticamente (si se requiere en el futuro)
    const qrCode = document.getElementById("qrCode");
    const qrValue = "https://cineapp.com/pago"; // Valor de ejemplo para el QR
    qrCode.src = `https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${encodeURIComponent(qrValue)}`;
});



