document.addEventListener("DOMContentLoaded", function () {
    const buscador = document.getElementById("buscarAccion");
    const tabla = document.getElementById("tablaAcciones");

    if (buscador && tabla) {
        buscador.addEventListener("input", function () {
            const texto = buscador.value.toLowerCase();
            const filas = tabla.querySelectorAll("tbody tr");

            filas.forEach(function (fila) {
                const contenido = fila.textContent.toLowerCase();
                fila.style.display = contenido.includes(texto) ? "" : "none";
            });
        });
    }

    const botonesEliminar = document.querySelectorAll("[data-confirmar]");

    botonesEliminar.forEach(function (boton) {
        boton.addEventListener("click", function (evento) {
            const mensaje = boton.getAttribute("data-confirmar");

            if (!confirm(mensaje)) {
                evento.preventDefault();
            }
        });
    });

    const formulario = document.getElementById("formAccion");

    if (formulario) {
        formulario.addEventListener("submit", function (evento) {
            const descripcion = document.getElementById("descripcion");
            const impacto = document.getElementById("impacto");

            if (
                !descripcion.value.trim() ||
                Number(impacto.value) < 0 ||
                Number(impacto.value) > 1000000
            ) {
                evento.preventDefault();
                alert("Revisa la descripción y la cantidad del impacto.");
            }
        });
    }
});