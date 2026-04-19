// ---------------- CONFIGURACIÓN (MODAL) ----------------
document.getElementById("configForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);

    const res = await fetch("/config", {
        method: "POST",
        body: formData
    });

    if (res.ok) {
        // Ocultar modal
        document.getElementById("configModal").style.display = "none";

        // Mostrar sistema
        document.getElementById("mainContent").style.display = "block";
    }
});


// ---------------- UPLOAD ----------------
document.getElementById("uploadForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);

    try {
        const res = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        const data = await res.json();

        document.getElementById("uploadStatus").innerText =
            "✔ Datos cargados: " + data.cantidad;

    } catch (err) {
        document.getElementById("uploadStatus").innerText =
            "❌ Error al cargar archivos";
    }
});


// ---------------- PREGUNTAR ----------------
document.getElementById("questionForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);

    const chat = document.getElementById("chatBox");

    try {
        const res = await fetch("/preguntar", {
            method: "POST",
            body: formData
        });

        const data = await res.json();

        chat.innerHTML += `
            <div class="chat-user">🧑 ${formData.get("pregunta")}</div>
            <div class="chat-ai">🤖 ${data.respuesta}</div>
        `;

        chat.scrollTop = chat.scrollHeight;

        e.target.reset();

    } catch (err) {
        chat.innerHTML += `
            <div class="chat-ai text-danger">❌ Error al consultar</div>
        `;
    }
});


// ---------------- EXCEL ----------------
document.getElementById("excelForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const loading = document.getElementById("loadingExcel");
    loading.classList.remove("d-none");

    try {
        const res = await fetch("/generar_excel", {
            method: "POST"
        });

        if (!res.ok) throw new Error("Error en generación");

        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = url;
        a.download = "anexos.xlsm";
        document.body.appendChild(a);
        a.click();
        a.remove();

    } catch (err) {
        alert("Error generando Excel");
    }

    loading.classList.add("d-none");
});