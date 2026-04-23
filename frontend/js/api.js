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

async function detectLandmarksInBackend(file) {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_BASE_URL}/face/detect-landmarks`, {
        method: "POST",
        body: formData
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || "Error desconocido al detectar landmarks");
    }

    return data;
}

async function triangulateMesh(file) {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_BASE_URL}/face/triangulate`, {
        method: "POST",
        body: formData
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || "Error triangulando");
    }

    return data;
}

async function projectMesh3D(file, rotationA, rotationB, distance) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("rotation_a", rotationA);
    formData.append("rotation_b", rotationB);
    formData.append("distance", distance);

    const response = await fetch(`${API_BASE_URL}/face/project-mesh`, {
        method: "POST",
        body: formData
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || "Error proyectando la malla 3D");
    }

    return data;
}