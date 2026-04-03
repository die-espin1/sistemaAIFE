// ---------------- UPLOAD ----------------
document.getElementById("uploadForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);

    const res = await fetch("/upload", {
        method: "POST",
        body: formData
    });

    const data = await res.json();

    document.getElementById("uploadStatus").innerText =
        "✔ Datos cargados: " + data.cantidad;
});


// ---------------- PREGUNTAR ----------------
document.getElementById("questionForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);

    const res = await fetch("/preguntar", {
        method: "POST",
        body: formData
    });

    const data = await res.json();

    const chat = document.getElementById("chatBox");

    chat.innerHTML += `
        <div class="chat-user">🧑 ${formData.get("pregunta")}</div>
        <div class="chat-ai">🤖 ${data.respuesta}</div>
    `;

    chat.scrollTop = chat.scrollHeight;

    e.target.reset();
});


// ---------------- EXCEL ----------------
document.getElementById("excelForm").addEventListener("submit", () => {
    document.getElementById("loadingExcel").classList.remove("d-none");
});