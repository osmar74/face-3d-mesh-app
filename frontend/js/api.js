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

async function detectLandmarksInBackend(file, detectorMode = "mediapipe") {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("detector_mode", detectorMode);

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

async function triangulateMesh(file, detectorMode = "mediapipe") {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("detector_mode", detectorMode);

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

async function projectMesh3D(file, rotationA, rotationB, distance, detectorMode = "mediapipe") {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("rotation_a", rotationA);
    formData.append("rotation_b", rotationB);
    formData.append("distance", distance);
    formData.append("detector_mode", detectorMode);

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

async function saveMeshResult(data, filenamePrefix = "mesh_result") {
    const response = await fetch(`${API_BASE_URL}/storage/save`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            data: data,
            filename_prefix: filenamePrefix
        })
    });

    const result = await response.json();

    if (!response.ok) {
        throw new Error(result.detail || "Error guardando el resultado");
    }

    return result;
}

async function listSavedResults() {
    const response = await fetch(`${API_BASE_URL}/storage/list`);
    const result = await response.json();

    if (!response.ok) {
        throw new Error(result.detail || "Error listando resultados guardados");
    }

    return result;
}

async function loadSavedResult(filename) {
    const response = await fetch(`${API_BASE_URL}/storage/load/${encodeURIComponent(filename)}`);
    const result = await response.json();

    if (!response.ok) {
        throw new Error(result.detail || "Error cargando resultado guardado");
    }

    return result;
}