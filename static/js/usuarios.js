document.addEventListener("DOMContentLoaded", function () {
    const usuariosTable = document.getElementById("usuariosTable");
    const modal = new bootstrap.Modal(document.getElementById("modalUsuario"));
    const formUsuario = document.getElementById("formUsuario");

    const loadUsuarios = () => {
        fetch("/api/usuarios")
            .then(response => response.json())
            .then(data => {
                usuariosTable.innerHTML = data.map(usuario => `
                    <tr>
                        <td>${usuario.idCliente}</td>
                        <td>${usuario.DNI}</td>
                        <td>${usuario.Nombre}</td>
                        <td>${usuario.Apellidos}</td>
                        <td>${usuario.Fecha_Nac}</td>
                        <td>${usuario.Correo}</td>
                        <td>${usuario.Telefono || ''}</td>
                        <td>${usuario.Usuario}</td>
                        <td>${usuario.Puntos}</td>
                        <td>${usuario.Tarjeta || ''}</td>
                        <td>${usuario.Fecha_Registro}</td>
                        <td>
                            <button class="btn btn-warning btn-sm" onclick="editUsuario(${usuario.idCliente})">Editar</button>
                            <button class="btn btn-danger btn-sm" onclick="deleteUsuario(${usuario.idCliente})">Eliminar</button>
                        </td>
                    </tr>
                `).join("");
            });
    };

    window.editUsuario = (idCliente) => {
        fetch(`/api/usuarios/${idCliente}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById("idCliente").value = data.idCliente;
                document.getElementById("dni").value = data.DNI;
                document.getElementById("nombre").value = data.Nombre;
                document.getElementById("apellidos").value = data.Apellidos;
                document.getElementById("fecha_nac").value = data.Fecha_Nac;
                document.getElementById("correo").value = data.Correo;
                document.getElementById("telefono").value = data.Telefono;
                document.getElementById("usuario").value = data.Usuario;
                document.getElementById("contrasena").value = data.Contrasena;
                document.getElementById("puntos").value = data.Puntos;
                document.getElementById("tarjeta").value = data.Tarjeta;
                document.getElementById("fecha_registro").value = data.Fecha_Registro;
                modal.show();
            });
    };

    window.deleteUsuario = (idCliente) => {
        if (confirm("¿Estás seguro de eliminar este usuario?")) {
            fetch(`/api/usuarios/${idCliente}`, { method: "DELETE" })
                .then(() => loadUsuarios());
        }
    };

    document.getElementById("btnAgregarUsuario").addEventListener("click", () => {
        // Limpiar todos los campos del formulario
        document.getElementById("idCliente").value = "";
        document.getElementById("dni").value = "";
        document.getElementById("nombre").value = "";
        document.getElementById("apellidos").value = "";
        document.getElementById("fecha_nac").value = "";
        document.getElementById("correo").value = "";
        document.getElementById("telefono").value = "";
        document.getElementById("usuario").value = "";
        document.getElementById("contrasena").value = "";
        document.getElementById("puntos").value = "";
        document.getElementById("tarjeta").value = "";
        document.getElementById("fecha_registro").value = "";
        modal.show();
    });
    
    formUsuario.addEventListener("submit", (e) => {
        e.preventDefault();
        const idCliente = document.getElementById("idCliente").value;
        const usuario = {
            DNI: document.getElementById("dni").value,
            Nombre: document.getElementById("nombre").value,
            Apellidos: document.getElementById("apellidos").value,
            Correo: document.getElementById("correo").value,
            Telefono: document.getElementById("telefono").value,
            Usuario: document.getElementById("usuario").value,
            Contrasena: document.getElementById("contrasena").value,
            Puntos: document.getElementById("puntos").value,
            Tarjeta: document.getElementById("tarjeta").value
        };

        const method = idCliente ? "PUT" : "POST";
        const url = idCliente ? `/api/usuarios/${idCliente}` : "/api/usuarios";

        fetch(url, {
            method,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(usuario),
        }).then(() => {
            modal.hide();
            loadUsuarios();
        });
    });

    loadUsuarios();
});