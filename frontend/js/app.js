const imageInput = document.getElementById("imageInput");
const uploadButton = document.getElementById("uploadButton");
const detectButton = document.getElementById("detectButton");
const imagePreview = document.getElementById("imagePreview");
const uploadStatus = document.getElementById("uploadStatus");
const backendResponse = document.getElementById("backendResponse");
const landmarkCanvas = document.getElementById("landmarkCanvas");
const landmarkContext = landmarkCanvas.getContext("2d");

let selectedFile = null;
let loadedImage = null;

imageInput.addEventListener("change", (event) => {
    const file = event.target.files[0];

    clearCanvas();

    if (!file) {
        selectedFile = null;
        loadedImage = null;
        imagePreview.removeAttribute("src");
        uploadStatus.textContent = "No se seleccionó ninguna imagen.";
        backendResponse.textContent = "Esperando acción...";
        return;
    }

    selectedFile = file;

    const objectUrl = URL.createObjectURL(file);
    imagePreview.src = objectUrl;

    const img = new Image();
    img.onload = () => {
        loadedImage = img;
        prepareCanvas(img.width, img.height);
        drawImageOnCanvas(img);
    };
    img.src = objectUrl;

    uploadStatus.textContent =
        `Imagen seleccionada:\n${file.name}\nTamaño: ${Math.round(file.size / 1024)} KB`;

    backendResponse.textContent = "Lista para enviar al backend.";
});

uploadButton.addEventListener("click", async () => {
    if (!selectedFile) {
        uploadStatus.textContent = "Primero selecciona una imagen.";
        return;
    }

    uploadStatus.textContent = "Validando imagen en backend...";

    try {
        const result = await uploadImageToBackend(selectedFile);
        uploadStatus.textContent = "Imagen validada correctamente.";
        backendResponse.textContent = JSON.stringify(result, null, 2);
    } catch (error) {
        uploadStatus.textContent = "Error al validar la imagen.";
        backendResponse.textContent = error.message;
    }
});

detectButton.addEventListener("click", async () => {
    if (!selectedFile) {
        uploadStatus.textContent = "Primero selecciona una imagen.";
        return;
    }

    uploadStatus.textContent = "Generando malla...";

    try {
        const result = await triangulateMesh(selectedFile);

        uploadStatus.textContent = "Malla generada correctamente.";

        backendResponse.textContent = JSON.stringify(
            {
                vertices: result.vertices.length,
                triangles: result.triangles.length,
                message: result.message
            },
            null,
            2
        );

        if (loadedImage) {
            prepareCanvas(loadedImage.width, loadedImage.height);
            drawImageOnCanvas(loadedImage);
            drawTriangles(result.vertices, result.triangles);
        }

    } catch (error) {
        uploadStatus.textContent = "Error en triangulación.";
        backendResponse.textContent = error.message;
    }
});

function prepareCanvas(width, height) {
    landmarkCanvas.width = width;
    landmarkCanvas.height = height;
}

function clearCanvas() {
    landmarkContext.clearRect(0, 0, landmarkCanvas.width, landmarkCanvas.height);
}

function drawLandmarks(landmarks) {
    for (const point of landmarks) {
        landmarkContext.beginPath();

        if (point.source === "synthetic") {
            landmarkContext.fillStyle = "#f59e0b";
            landmarkContext.arc(point.x, point.y, 2.5, 0, Math.PI * 2);
        } else {
            landmarkContext.fillStyle = "#22c55e";
            landmarkContext.arc(point.x, point.y, 1.5, 0, Math.PI * 2);
        }

        landmarkContext.fill();
    }
}

function drawImageOnCanvas(image) {
    landmarkContext.clearRect(0, 0, landmarkCanvas.width, landmarkCanvas.height);
    landmarkContext.drawImage(image, 0, 0, landmarkCanvas.width, landmarkCanvas.height);
}

function drawTriangles(vertices, triangles) {
    landmarkContext.strokeStyle = "#38bdf8";
    landmarkContext.lineWidth = 0.5;

    for (const tri of triangles) {
        const p1 = vertices[tri.a];
        const p2 = vertices[tri.b];
        const p3 = vertices[tri.c];

        landmarkContext.beginPath();
        landmarkContext.moveTo(p1.x, p1.y);
        landmarkContext.lineTo(p2.x, p2.y);
        landmarkContext.lineTo(p3.x, p3.y);
        landmarkContext.closePath();
        landmarkContext.stroke();
    }
}