document.addEventListener("DOMContentLoaded", function () {
    const sesionesTable = document.getElementById("sesionesTable");
    const modal = new bootstrap.Modal(document.getElementById("modalSesion"));
    const formSesion = document.getElementById("formSesion");

    const loadSesiones = () => {
        fetch("/api/sesiones")
            .then(response => response.json())
            .then(data => {
                sesionesTable.innerHTML = data.map(sesion => `
                    <tr>
                        <td>${sesion.idSesion}</td>
                        <td>${sesion.Fecha}</td>
                        <td>${sesion.Hora}</td>
                        <td>${sesion.Idioma}</td>
                        <td>${sesion.idPelicula}</td>
                        <td>${sesion.idSala}</td>
                        <td>
                            <button class="btn btn-warning btn-sm" onclick="editSesion(${sesion.idSesion})">Editar</button>
                            <button class="btn btn-danger btn-sm" onclick="deleteSesion(${sesion.idSesion})">Eliminar</button>
                        </td>
                    </tr>
                `).join("");
            });
    };

    window.editSesion = (idSesion) => {
        fetch(`/api/sesiones/${idSesion}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById("idSesion").value = data.idSesion;
                document.getElementById("fecha").value = data.Fecha;
                document.getElementById("hora").value = data.Hora;
                document.getElementById("idioma").value = data.Idioma;
                document.getElementById("idPelicula").value = data.idPelicula;
                document.getElementById("idSala").value = data.idSala;
                modal.show();
            })
            .catch(error => console.error('Error al obtener la sesión:', error));
    };    

    window.deleteSesion = (idSesion) => {
        if (confirm("¿Estás seguro de eliminar esta sesión?")) {
            fetch(`/api/sesiones/${idSesion}`, { method: "DELETE" })
                .then(() => loadSesiones());
        }
    };

    formSesion.addEventListener("submit", (e) => {
        e.preventDefault();
        const sesion = {
            Fecha: document.getElementById("fecha").value,
            Hora: document.getElementById("hora").value,
            Idioma: document.getElementById("idioma").value,
            idPelicula: document.getElementById("idPelicula").value,
            idSala: document.getElementById("idSala").value,
        };
    
        fetch("/api/sesiones", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(sesion),
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error("Error al agregar sesión. Verifica idPelicula e idSala.");
                }
                return response.json();
            })
            .then(() => {
                modal.hide();
                loadSesiones();
            })
            .catch((error) => alert(error.message));
    });    

    loadSesiones();
});
