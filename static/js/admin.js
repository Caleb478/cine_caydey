document.addEventListener("DOMContentLoaded", function () {
    const peliculasTable = document.getElementById("peliculasTable");
    const modal = new bootstrap.Modal(document.getElementById("modalPelicula"));
    const formPelicula = document.getElementById("formPelicula");

    const loadPeliculas = () => {
        fetch("/api/peliculas")
            .then(response => response.json())
            .then(data => {
                peliculasTable.innerHTML = data.map(pelicula => `
                    <tr>
                        <td>${pelicula.idPelicula}</td>
                        <td>${pelicula.Titulo}</td>
                        <td>${pelicula.Genero}</td>
                        <td>${pelicula.Clasificacion}</td>
                        <td>${pelicula.Duracion}</td>
                        <td>
                            <button class="btn btn-warning btn-sm" onclick="editPelicula(${pelicula.idPelicula})">Editar</button>
                            <button class="btn btn-danger btn-sm" onclick="deletePelicula(${pelicula.idPelicula})">Eliminar</button>
                        </td>
                    </tr>
                `).join("");
            });
    };

    window.editPelicula = (idPelicula) => {
        fetch(`/api/peliculas/${idPelicula}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById("idPelicula").value = data.idPelicula;
                document.getElementById("titulo").value = data.Titulo;
                document.getElementById("genero").value = data.Genero;
                document.getElementById("clasificacion").value = data.Clasificacion;
                document.getElementById("duracion").value = data.Duracion;
                modal.show();
            });
    };

    window.deletePelicula = (idPelicula) => {
        if (confirm("¿Estás seguro de eliminar esta película?")) {
            fetch(`/api/peliculas/${idPelicula}`, { method: "DELETE" })
                .then(() => loadPeliculas());
        }
    };

    document.getElementById("btnAgregarPelicula").addEventListener("click", () => {
        document.getElementById("idPelicula").value = ""; // Vaciar ID (nueva película)
        document.getElementById("titulo").value = "";
        document.getElementById("genero").value = "";
        document.getElementById("clasificacion").value = "";
        document.getElementById("duracion").value = "";
    });
    
    formPelicula.addEventListener("submit", (e) => {
        e.preventDefault();
        const idPelicula = document.getElementById("idPelicula").value;
        const pelicula = {
            Titulo: document.getElementById("titulo").value,
            Genero: document.getElementById("genero").value,
            Clasificacion: document.getElementById("clasificacion").value,
            Duracion: document.getElementById("duracion").value,
        };

        const method = idPelicula ? "PUT" : "POST";
        const url = idPelicula ? `/api/peliculas/${idPelicula}` : "/api/peliculas";

        fetch(url, {
            method,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(pelicula),
        }).then(() => {
            modal.hide();
            loadPeliculas();
        });
    });

    loadPeliculas();
});
