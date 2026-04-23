document.addEventListener("DOMContentLoaded", () => {
    const imageInput = document.getElementById("imageInput");
    const uploadButton = document.getElementById("uploadButton");
    const detectButton = document.getElementById("detectButton");
    const projectButton = document.getElementById("projectButton");

    const rotationAInput = document.getElementById("rotationA");
    const rotationBInput = document.getElementById("rotationB");
    const distanceInput = document.getElementById("distanceInput");

    const imagePreview = document.getElementById("imagePreview");
    const uploadStatus = document.getElementById("uploadStatus");
    const backendResponse = document.getElementById("backendResponse");

    const landmarkCanvas = document.getElementById("landmarkCanvas");
    const landmarkContext = landmarkCanvas.getContext("2d");

    const projectionCanvas = document.getElementById("projectionCanvas");
    const projectionContext = projectionCanvas.getContext("2d");

    let selectedFile = null;
    let loadedImage = null;
    let lastProjectionResult = null;

    imageInput.addEventListener("change", (event) => {
        const file = event.target.files[0];

        clearCanvas(landmarkContext, landmarkCanvas);
        clearCanvas(projectionContext, projectionCanvas);

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
            prepareCanvas(landmarkCanvas, img.width, img.height);
            drawImageOnCanvas(landmarkContext, landmarkCanvas, img);

            prepareCanvas(projectionCanvas, 700, 700);
            clearCanvas(projectionContext, projectionCanvas);
        };
        img.src = objectUrl;

        uploadStatus.textContent =
            `Imagen seleccionada:\n${file.name}\nTamaño: ${Math.round(file.size / 1024)} KB`;

        backendResponse.textContent = "Lista para enviar al backend.";
        lastProjectionResult = null;
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

        uploadStatus.textContent = "Generando malla 2D...";

        try {
            const result = await triangulateMesh(selectedFile);

            uploadStatus.textContent = "Malla 2D generada correctamente.";

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
                prepareCanvas(landmarkCanvas, loadedImage.width, loadedImage.height);
                drawImageOnCanvas(landmarkContext, landmarkCanvas, loadedImage);
                drawTriangles2D(landmarkContext, result.vertices, result.triangles);
                drawVertices2D(landmarkContext, result.vertices);
            }
        } catch (error) {
            uploadStatus.textContent = "Error en triangulación 2D.";
            backendResponse.textContent = error.message;
        }
    });

    projectButton.addEventListener("click", async () => {
        await renderProjection();
    });

    rotationAInput.addEventListener("input", async () => {
        if (selectedFile) {
            await renderProjection();
        }
    });

    rotationBInput.addEventListener("input", async () => {
        if (selectedFile) {
            await renderProjection();
        }
    });

    distanceInput.addEventListener("input", async () => {
        if (selectedFile) {
            await renderProjection();
        }
    });

    async function renderProjection() {
        if (!selectedFile) {
            uploadStatus.textContent = "Primero selecciona una imagen.";
            return;
        }

        uploadStatus.textContent = "Calculando proyección 3D en backend...";

        const rotationA = parseFloat(rotationAInput.value);
        const rotationB = parseFloat(rotationBInput.value);
        const distance = parseFloat(distanceInput.value);

        try {
            const result = await projectMesh3D(
                selectedFile,
                rotationA,
                rotationB,
                distance
            );

            lastProjectionResult = result;

            uploadStatus.textContent = "Proyección 3D generada correctamente.";

            backendResponse.textContent = JSON.stringify(
                {
                    vertices: result.vertices.length,
                    projected_vertices: result.projected_vertices.length,
                    triangles: result.triangles.length,
                    rotation_a: result.rotation_a,
                    rotation_b: result.rotation_b,
                    distance: result.distance,
                    message: result.message
                },
                null,
                2
            );

            prepareCanvas(projectionCanvas, 700, 700);
            clearCanvas(projectionContext, projectionCanvas);
            drawProjectedMesh(result.projected_vertices, result.triangles);
        } catch (error) {
            uploadStatus.textContent = "Error en proyección 3D.";
            backendResponse.textContent = error.message;
        }
    }

    function prepareCanvas(canvas, width, height) {
        canvas.width = width;
        canvas.height = height;
    }

    function clearCanvas(context, canvas) {
        context.clearRect(0, 0, canvas.width, canvas.height);
    }

    function drawImageOnCanvas(context, canvas, image) {
        context.clearRect(0, 0, canvas.width, canvas.height);
        context.drawImage(image, 0, 0, canvas.width, canvas.height);
    }

    function drawTriangles2D(context, vertices, triangles) {
        context.strokeStyle = "#38bdf8";
        context.lineWidth = 0.5;

        for (const tri of triangles) {
            const p1 = vertices[tri.a];
            const p2 = vertices[tri.b];
            const p3 = vertices[tri.c];

            if (!p1 || !p2 || !p3) {
                continue;
            }

            context.beginPath();
            context.moveTo(p1.x, p1.y);
            context.lineTo(p2.x, p2.y);
            context.lineTo(p3.x, p3.y);
            context.closePath();
            context.stroke();
        }
    }

    function drawVertices2D(context, vertices) {
        context.fillStyle = "#22c55e";

        for (const point of vertices) {
            context.beginPath();
            context.arc(point.x, point.y, 1.2, 0, Math.PI * 2);
            context.fill();
        }
    }

    function drawProjectedMesh(projectedVertices, triangles) {
        const offsetX = projectionCanvas.width / 2;
        const offsetY = projectionCanvas.height / 2;

        projectionContext.strokeStyle = "#f43f5e";
        projectionContext.lineWidth = 0.8;

        for (const tri of triangles) {
            const p1 = projectedVertices[tri.a];
            const p2 = projectedVertices[tri.b];
            const p3 = projectedVertices[tri.c];

            if (!p1 || !p2 || !p3) {
                continue;
            }

            projectionContext.beginPath();
            projectionContext.moveTo(offsetX + p1.x, offsetY + p1.y);
            projectionContext.lineTo(offsetX + p2.x, offsetY + p2.y);
            projectionContext.lineTo(offsetX + p3.x, offsetY + p3.y);
            projectionContext.closePath();
            projectionContext.stroke();
        }

        projectionContext.fillStyle = "#facc15";
        for (const point of projectedVertices) {
            projectionContext.beginPath();
            projectionContext.arc(offsetX + point.x, offsetY + point.y, 1.1, 0, Math.PI * 2);
            projectionContext.fill();
        }
    }
});