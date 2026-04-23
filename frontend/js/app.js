document.addEventListener("DOMContentLoaded", () => {
    const imageInput = document.getElementById("imageInput");
    const uploadButton = document.getElementById("uploadButton");
    const detectButton = document.getElementById("detectButton");
    const projectButton = document.getElementById("projectButton");
    const saveButton = document.getElementById("saveButton");
    const refreshSavedButton = document.getElementById("refreshSavedButton");
    const loadButton = document.getElementById("loadButton");

    const savedFilesSelect = document.getElementById("savedFilesSelect");

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
    let currentMesh2DResult = null;
    let currentProjectionResult = null;

    initializeSavedFiles();

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

            prepareCanvasToDisplaySize(landmarkCanvas, landmarkContext);
            clearCanvas(landmarkContext, landmarkCanvas);

            prepareCanvasToDisplaySize(projectionCanvas, projectionContext);
            clearCanvas(projectionContext, projectionCanvas);
        };
        img.src = objectUrl;

        uploadStatus.textContent =
            `Imagen seleccionada:\n${file.name}\nTamaño: ${Math.round(file.size / 1024)} KB`;

        backendResponse.textContent = "Lista para enviar al backend.";
        currentMesh2DResult = null;
        currentProjectionResult = null;
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
            currentMesh2DResult = result;

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

            prepareCanvasToDisplaySize(landmarkCanvas, landmarkContext);
            clearCanvas(landmarkContext, landmarkCanvas);

            drawImageFittedToCanvas(landmarkContext, landmarkCanvas, loadedImage);
            drawTrianglesOverlayOnImage(landmarkContext, landmarkCanvas, result.vertices, result.triangles);
            drawVerticesOverlayOnImage(landmarkContext, landmarkCanvas, result.vertices);

        } catch (error) {
            uploadStatus.textContent = "Error en triangulación 2D.";
            backendResponse.textContent = error.message;
        }
    });

    projectButton.addEventListener("click", async () => {
        await renderProjection();
    });

    saveButton.addEventListener("click", async () => {
        if (!currentMesh2DResult && !currentProjectionResult) {
            uploadStatus.textContent = "Primero genera una malla o proyección para guardar.";
            return;
        }

        try {
            const payload = {
                mesh2d: currentMesh2DResult,
                projection3d: currentProjectionResult,
                scene: {
                    rotation_a: parseFloat(rotationAInput.value),
                    rotation_b: parseFloat(rotationBInput.value),
                    distance: parseFloat(distanceInput.value)
                }
            };

            const result = await saveMeshResult(payload, "face_mesh");
            uploadStatus.textContent = `Resultado guardado: ${result.filename}`;
            backendResponse.textContent = JSON.stringify(result, null, 2);

            await refreshSavedFiles();
        } catch (error) {
            uploadStatus.textContent = "Error al guardar resultado.";
            backendResponse.textContent = error.message;
        }
    });

    refreshSavedButton.addEventListener("click", async () => {
        await refreshSavedFiles();
    });

    loadButton.addEventListener("click", async () => {
        const filename = savedFilesSelect.value;

        if (!filename) {
            uploadStatus.textContent = "No hay archivo seleccionado para cargar.";
            return;
        }

        try {
            const result = await loadSavedResult(filename);
            const data = result.data;

            currentMesh2DResult = data.mesh2d || null;
            currentProjectionResult = data.projection3d || null;

            if (data.scene) {
                rotationAInput.value = data.scene.rotation_a ?? 0;
                rotationBInput.value = data.scene.rotation_b ?? 0;
                distanceInput.value = data.scene.distance ?? 500;
            }

            prepareCanvasToDisplaySize(landmarkCanvas, landmarkContext);
            clearCanvas(landmarkContext, landmarkCanvas);

            if (currentMesh2DResult) {
                if (loadedImage) {
                    drawImageFittedToCanvas(landmarkContext, landmarkCanvas, loadedImage);
                    drawTrianglesOverlayOnImage(
                        landmarkContext,
                        landmarkCanvas,
                        currentMesh2DResult.vertices,
                        currentMesh2DResult.triangles
                    );
                    drawVerticesOverlayOnImage(
                        landmarkContext,
                        landmarkCanvas,
                        currentMesh2DResult.vertices
                    );
                } else {
                    drawCenteredMesh2D(
                        landmarkContext,
                        landmarkCanvas,
                        currentMesh2DResult.vertices,
                        currentMesh2DResult.triangles
                    );
                }
            }

            prepareCanvasToDisplaySize(projectionCanvas, projectionContext);
            clearCanvas(projectionContext, projectionCanvas);

            if (currentProjectionResult) {
                drawProjectedMeshCentered(
                    projectionContext,
                    projectionCanvas,
                    currentProjectionResult.projected_vertices,
                    currentProjectionResult.triangles
                );
            }

            uploadStatus.textContent = `Resultado cargado: ${filename}`;
            backendResponse.textContent = JSON.stringify(result, null, 2);
        } catch (error) {
            uploadStatus.textContent = "Error al cargar resultado.";
            backendResponse.textContent = error.message;
        }
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

            currentProjectionResult = result;

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

            prepareCanvasToDisplaySize(projectionCanvas, projectionContext);
            clearCanvas(projectionContext, projectionCanvas);
            drawProjectedMeshCentered(
                projectionContext,
                projectionCanvas,
                result.projected_vertices,
                result.triangles
            );
        } catch (error) {
            uploadStatus.textContent = "Error en proyección 3D.";
            backendResponse.textContent = error.message;
        }
    }

    async function initializeSavedFiles() {
        await refreshSavedFiles();
    }

    async function refreshSavedFiles() {
        try {
            const result = await listSavedResults();

            savedFilesSelect.innerHTML = "";

            if (!result.files.length) {
                const option = document.createElement("option");
                option.value = "";
                option.textContent = "No hay resultados guardados";
                savedFilesSelect.appendChild(option);
                return;
            }

            for (const fileName of result.files) {
                const option = document.createElement("option");
                option.value = fileName;
                option.textContent = fileName;
                savedFilesSelect.appendChild(option);
            }
        } catch (error) {
            uploadStatus.textContent = "Error al actualizar lista de guardados.";
            backendResponse.textContent = error.message;
        }
    }

    function prepareCanvasToDisplaySize(canvas, context) {
        const rect = canvas.getBoundingClientRect();
        const dpr = window.devicePixelRatio || 1;

        canvas.width = Math.max(1, Math.floor(rect.width * dpr));
        canvas.height = Math.max(1, Math.floor(rect.height * dpr));

        context.setTransform(1, 0, 0, 1, 0, 0);
        context.scale(dpr, dpr);
    }

    function clearCanvas(context, canvas) {
        const rect = canvas.getBoundingClientRect();
        context.clearRect(0, 0, rect.width, rect.height);
    }

    function drawImageFittedToCanvas(context, canvas, image) {
        if (!image) return;

        const canvasWidth = canvas.getBoundingClientRect().width;
        const canvasHeight = canvas.getBoundingClientRect().height;

        const imageAspect = image.width / image.height;
        const canvasAspect = canvasWidth / canvasHeight;

        let drawWidth;
        let drawHeight;
        let offsetX;
        let offsetY;

        if (imageAspect > canvasAspect) {
            drawWidth = canvasWidth;
            drawHeight = drawWidth / imageAspect;
            offsetX = 0;
            offsetY = (canvasHeight - drawHeight) / 2;
        } else {
            drawHeight = canvasHeight;
            drawWidth = drawHeight * imageAspect;
            offsetX = (canvasWidth - drawWidth) / 2;
            offsetY = 0;
        }

        context.drawImage(image, offsetX, offsetY, drawWidth, drawHeight);
    }

    function getImageFitTransform(canvas, image) {
        const canvasWidth = canvas.getBoundingClientRect().width;
        const canvasHeight = canvas.getBoundingClientRect().height;

        const imageAspect = image.width / image.height;
        const canvasAspect = canvasWidth / canvasHeight;

        let drawWidth;
        let drawHeight;
        let offsetX;
        let offsetY;

        if (imageAspect > canvasAspect) {
            drawWidth = canvasWidth;
            drawHeight = drawWidth / imageAspect;
            offsetX = 0;
            offsetY = (canvasHeight - drawHeight) / 2;
        } else {
            drawHeight = canvasHeight;
            drawWidth = drawHeight * imageAspect;
            offsetX = (canvasWidth - drawWidth) / 2;
            offsetY = 0;
        }

        const scaleX = drawWidth / image.width;
        const scaleY = drawHeight / image.height;

        return { offsetX, offsetY, scaleX, scaleY };
    }

    function drawTrianglesOverlayOnImage(context, canvas, vertices, triangles) {
        if (!loadedImage) return;

        const { offsetX, offsetY, scaleX, scaleY } = getImageFitTransform(canvas, loadedImage);

        context.strokeStyle = "#38bdf8";
        context.lineWidth = 0.7;

        for (const tri of triangles) {
            const p1 = vertices[tri.a];
            const p2 = vertices[tri.b];
            const p3 = vertices[tri.c];

            if (!p1 || !p2 || !p3) continue;

            context.beginPath();
            context.moveTo(offsetX + p1.x * scaleX, offsetY + p1.y * scaleY);
            context.lineTo(offsetX + p2.x * scaleX, offsetY + p2.y * scaleY);
            context.lineTo(offsetX + p3.x * scaleX, offsetY + p3.y * scaleY);
            context.closePath();
            context.stroke();
        }
    }

    function drawVerticesOverlayOnImage(context, canvas, vertices) {
        if (!loadedImage) return;

        const { offsetX, offsetY, scaleX, scaleY } = getImageFitTransform(canvas, loadedImage);

        context.fillStyle = "#22c55e";

        for (const point of vertices) {
            context.beginPath();
            context.arc(
                offsetX + point.x * scaleX,
                offsetY + point.y * scaleY,
                1.2,
                0,
                Math.PI * 2
            );
            context.fill();
        }
    }

    function drawCenteredMesh2D(context, canvas, vertices, triangles) {
        const transformed = fitPointsToCanvas(vertices, canvas, 20);

        context.strokeStyle = "#38bdf8";
        context.lineWidth = 0.7;

        for (const tri of triangles) {
            const p1 = transformed[tri.a];
            const p2 = transformed[tri.b];
            const p3 = transformed[tri.c];

            if (!p1 || !p2 || !p3) continue;

            context.beginPath();
            context.moveTo(p1.x, p1.y);
            context.lineTo(p2.x, p2.y);
            context.lineTo(p3.x, p3.y);
            context.closePath();
            context.stroke();
        }

        context.fillStyle = "#22c55e";
        for (const point of transformed) {
            context.beginPath();
            context.arc(point.x, point.y, 1.2, 0, Math.PI * 2);
            context.fill();
        }
    }

    function drawProjectedMeshCentered(context, canvas, projectedVertices, triangles) {
        const transformed = fitPointsToCanvas(projectedVertices, canvas, 40);

        context.strokeStyle = "#f43f5e";
        context.lineWidth = 0.8;

        for (const tri of triangles) {
            const p1 = transformed[tri.a];
            const p2 = transformed[tri.b];
            const p3 = transformed[tri.c];

            if (!p1 || !p2 || !p3) continue;

            context.beginPath();
            context.moveTo(p1.x, p1.y);
            context.lineTo(p2.x, p2.y);
            context.lineTo(p3.x, p3.y);
            context.closePath();
            context.stroke();
        }

        context.fillStyle = "#facc15";
        for (const point of transformed) {
            context.beginPath();
            context.arc(point.x, point.y, 1.1, 0, Math.PI * 2);
            context.fill();
        }
    }

    function fitPointsToCanvas(points, canvas, padding = 20) {
        const canvasWidth = canvas.getBoundingClientRect().width;
        const canvasHeight = canvas.getBoundingClientRect().height;

        if (!points || !points.length) return [];

        const minX = Math.min(...points.map(p => p.x));
        const maxX = Math.max(...points.map(p => p.x));
        const minY = Math.min(...points.map(p => p.y));
        const maxY = Math.max(...points.map(p => p.y));

        const width = Math.max(maxX - minX, 1);
        const height = Math.max(maxY - minY, 1);

        const scale = Math.min(
            (canvasWidth - padding * 2) / width,
            (canvasHeight - padding * 2) / height
        );

        const offsetX = (canvasWidth - width * scale) / 2;
        const offsetY = (canvasHeight - height * scale) / 2;

        return points.map(point => ({
            x: offsetX + (point.x - minX) * scale,
            y: offsetY + (point.y - minY) * scale
        }));
    }
});