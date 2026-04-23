const API_BASE_URL = "http://127.0.0.1:8000/api";

async function uploadImageToBackend(file) {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_BASE_URL}/face/upload-image`, {
        method: "POST",
        body: formData
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || "Error desconocido al subir la imagen");
    }

    return data;
}