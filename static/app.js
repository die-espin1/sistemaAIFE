// ---------------- INICIO ----------------
document.addEventListener("DOMContentLoaded", () => {

    // Ocultar sistema hasta configurar
    document.getElementById("mainContent").style.display = "none";
    document.getElementById("configModal").style.display = "block";
});


// ---------------- CONFIGURACIÓN (MODAL) ----------------
document.getElementById("configForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);

    try {
        const res = await fetch("/config", {
            method: "POST",
            body: formData
        });

        const data = await res.json();

        if (!res.ok) {
            alert(data.error || "Error en configuración");
            return;
        }

        // Ocultar modal
        document.getElementById("configModal").style.display = "none";

        // Mostrar sistema
        document.getElementById("mainContent").style.display = "block";

    } catch (err) {
        alert("Error configurando contribuyente");
    }
});


// ---------------- AUTO UPLOAD ----------------
document.querySelector('input[name="files"]').addEventListener("change", async (e) => {

    const files = e.target.files;
    if (!files.length) return;

    const formData = new FormData();
    for (let f of files) {
        formData.append("files", f);
    }

    const status = document.getElementById("uploadStatus");
    status.innerText = "⏳ Subiendo archivos...";

    try {
        const res = await fetch("/upload", {
            method: "POST",
            body: formData,
            credentials: "include"   // 👈 AQUÍ
        });

        let data;

        try {
            data = await res.json();
        } catch {
            throw new Error("Respuesta inválida del servidor");
        }

        if (!res.ok) {
            throw new Error(data.error || "Error en el servidor");
        }

        status.innerText =
            `✔ Datos cargados: ${data.cantidad} | Ignorados: ${data.ignorados}`;

    } catch (err) {
        console.error("UPLOAD ERROR:", err);
        status.innerText = `❌ ${err.message}`;
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


// ---------------- GENERAR EXCEL ----------------
document.getElementById("excelForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const loading = document.getElementById("loadingExcel");
    loading.classList.remove("d-none");

    try {
        const res = await fetch("/generar_excel", {
            method: "POST"
        });

        if (!res.ok) {
            const errorData = await res.json();
            console.error("Error backend:", errorData);
            throw new Error(errorData.detalle || "Error generando Excel");
        }

        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = url;
        a.download = "anexos.xlsm";
        document.body.appendChild(a);
        a.click();
        a.remove();

    } catch (err) {
        alert("❌ " + err.message);
    }

    loading.classList.add("d-none");
});