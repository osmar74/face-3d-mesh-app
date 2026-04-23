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

    const uploadStatus = document.getElementById("uploadStatus");
    const backendResponse = document.getElementById("backendResponse");

    const badgeReal = document.getElementById("badgeReal");
    const badgeLandmarksOverlay = document.getElementById("badgeLandmarksOverlay");
    const badgeLandmarksOnly = document.getElementById("badgeLandmarksOnly");
    const badgeDelaunayOverlay = document.getElementById("badgeDelaunayOverlay");
    const badgeDelaunayClean = document.getElementById("badgeDelaunayClean");
    const badgeProjection3D = document.getElementById("badgeProjection3D");

    const realCanvas = document.getElementById("realCanvas");
    const overlayLandmarksCanvas = document.getElementById("overlayLandmarksCanvas");
    const landmarksOnlyCanvas = document.getElementById("landmarksOnlyCanvas");
    const delaunayOverlayCanvas = document.getElementById("delaunayOverlayCanvas");
    const delaunayCleanCanvas = document.getElementById("delaunayCleanCanvas");
    const projectionCanvas = document.getElementById("projectionCanvas");

    const realContext = realCanvas.getContext("2d");
    const overlayLandmarksContext = overlayLandmarksCanvas.getContext("2d");
    const landmarksOnlyContext = landmarksOnlyCanvas.getContext("2d");
    const delaunayOverlayContext = delaunayOverlayCanvas.getContext("2d");
    const delaunayCleanContext = delaunayCleanCanvas.getContext("2d");
    const projectionContext = projectionCanvas.getContext("2d");

    let selectedFile = null;
    let loadedImage = null;
    let currentLandmarksResult = null;
    let currentMesh2DResult = null;
    let currentProjectionResult = null;

    initializeSavedFiles();
    prepareAllCanvases();

    window.addEventListener("resize", () => {
        prepareAllCanvases();
        redrawAllPanels();
    });

    imageInput.addEventListener("change", (event) => {
        const file = event.target.files[0];
        clearAllCanvases();

        if (!file) {
            selectedFile = null;
            loadedImage = null;
            currentLandmarksResult = null;
            currentMesh2DResult = null;
            currentProjectionResult = null;
            resetBadges();
            uploadStatus.textContent = "No se seleccionó ninguna imagen.";
            backendResponse.textContent = "Esperando acción...";
            return;
        }

        selectedFile = file;
        currentLandmarksResult = null;
        currentMesh2DResult = null;
        currentProjectionResult = null;

        const objectUrl = URL.createObjectURL(file);
        const img = new Image();

        img.onload = () => {
            loadedImage = img;
            prepareAllCanvases();
            drawImageFittedToCanvas(realContext, realCanvas, loadedImage);
            badgeReal.textContent = `${img.width}x${img.height}`;
        };

        img.src = objectUrl;

        uploadStatus.textContent =
            `Imagen seleccionada:\n${file.name}\nTamaño: ${Math.round(file.size / 1024)} KB`;

        backendResponse.textContent = "Lista para enviar al backend.";
        resetProcessingBadges();
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

            badgeReal.textContent = `${result.width}x${result.height}`;
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

        uploadStatus.textContent = "Detectando landmarks y generando malla 2D...";

        try {
            const landmarksResult = await detectLandmarksInBackend(selectedFile);
            const meshResult = await triangulateMesh(selectedFile);

            currentLandmarksResult = landmarksResult;
            currentMesh2DResult = meshResult;

            uploadStatus.textContent = "Landmarks y malla 2D generados correctamente.";

            backendResponse.textContent = JSON.stringify(
                {
                    landmark_count: landmarksResult.landmark_count,
                    mesh_vertices: meshResult.vertices.length,
                    mesh_triangles: meshResult.triangles.length,
                    landmarks_message: landmarksResult.message,
                    mesh_message: meshResult.message
                },
                null,
                2
            );

            redrawAllPanels();
            updateLandmarkAndMeshBadges();
        } catch (error) {
            uploadStatus.textContent = "Error en landmarks o triangulación 2D.";
            backendResponse.textContent = error.message;
        }
    });

    projectButton.addEventListener("click", async () => {
        await renderProjection();
    });

    saveButton.addEventListener("click", async () => {
        if (!currentMesh2DResult && !currentProjectionResult && !currentLandmarksResult) {
            uploadStatus.textContent = "Primero genera información para guardar.";
            return;
        }

        try {
            const payload = {
                landmarks: currentLandmarksResult,
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

            currentLandmarksResult = data.landmarks || null;
            currentMesh2DResult = data.mesh2d || null;
            currentProjectionResult = data.projection3d || null;

            if (data.scene) {
                rotationAInput.value = data.scene.rotation_a ?? 0;
                rotationBInput.value = data.scene.rotation_b ?? 0;
                distanceInput.value = data.scene.distance ?? 500;
            }

            redrawAllPanels();
            updateAllBadgesAfterLoad();

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

            redrawProjectionPanel();
            badgeProjection3D.textContent = "3D";
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

    function prepareAllCanvases() {
        prepareCanvasToDisplaySize(realCanvas, realContext);
        prepareCanvasToDisplaySize(overlayLandmarksCanvas, overlayLandmarksContext);
        prepareCanvasToDisplaySize(landmarksOnlyCanvas, landmarksOnlyContext);
        prepareCanvasToDisplaySize(delaunayOverlayCanvas, delaunayOverlayContext);
        prepareCanvasToDisplaySize(delaunayCleanCanvas, delaunayCleanContext);
        prepareCanvasToDisplaySize(projectionCanvas, projectionContext);
    }

    function redrawAllPanels() {
        clearAllCanvases();

        if (loadedImage) {
            drawImageFittedToCanvas(realContext, realCanvas, loadedImage);
        }

        if (loadedImage && currentLandmarksResult) {
            drawImageFittedToCanvas(overlayLandmarksContext, overlayLandmarksCanvas, loadedImage);
            drawLandmarksOverlayOnImage(
                overlayLandmarksContext,
                overlayLandmarksCanvas,
                currentLandmarksResult.landmarks
            );
        }

        if (currentLandmarksResult) {
            drawLandmarksOnlyPanel(
                landmarksOnlyContext,
                landmarksOnlyCanvas,
                currentLandmarksResult.landmarks
            );
        }

        if (loadedImage && currentMesh2DResult) {
            drawImageFittedToCanvas(delaunayOverlayContext, delaunayOverlayCanvas, loadedImage);
            drawTrianglesOverlayOnImage(
                delaunayOverlayContext,
                delaunayOverlayCanvas,
                currentMesh2DResult.vertices,
                currentMesh2DResult.triangles
            );
            drawVerticesOverlayOnImage(
                delaunayOverlayContext,
                delaunayOverlayCanvas,
                currentMesh2DResult.vertices
            );
        }

        if (currentMesh2DResult) {
            drawCenteredMesh2D(
                delaunayCleanContext,
                delaunayCleanCanvas,
                currentMesh2DResult.vertices,
                currentMesh2DResult.triangles
            );
        }

        redrawProjectionPanel();
    }

    function redrawProjectionPanel() {
        clearCanvas(projectionContext, projectionCanvas);

        if (currentProjectionResult) {
            drawProjectedMeshCentered(
                projectionContext,
                projectionCanvas,
                currentProjectionResult.projected_vertices,
                currentProjectionResult.triangles,
                parseFloat(rotationAInput.value),
                parseFloat(rotationBInput.value)
            );
        }
    }

    function updateLandmarkAndMeshBadges() {
        if (loadedImage) {
            badgeReal.textContent = `${loadedImage.width}x${loadedImage.height}`;
        }

        if (currentLandmarksResult) {
            badgeLandmarksOverlay.textContent = `${currentLandmarksResult.landmark_count} PTS`;
            badgeLandmarksOnly.textContent = `${currentLandmarksResult.landmark_count} PTS`;
        }

        if (currentMesh2DResult) {
            badgeDelaunayOverlay.textContent = `${currentMesh2DResult.triangles.length} TRI`;
            badgeDelaunayClean.textContent = `${currentMesh2DResult.triangles.length} TRI`;
        }
    }

    function updateAllBadgesAfterLoad() {
        if (loadedImage) {
            badgeReal.textContent = `${loadedImage.width}x${loadedImage.height}`;
        }

        if (currentLandmarksResult) {
            badgeLandmarksOverlay.textContent = `${currentLandmarksResult.landmark_count} PTS`;
            badgeLandmarksOnly.textContent = `${currentLandmarksResult.landmark_count} PTS`;
        } else {
            badgeLandmarksOverlay.textContent = "--";
            badgeLandmarksOnly.textContent = "--";
        }

        if (currentMesh2DResult) {
            badgeDelaunayOverlay.textContent = `${currentMesh2DResult.triangles.length} TRI`;
            badgeDelaunayClean.textContent = `${currentMesh2DResult.triangles.length} TRI`;
        } else {
            badgeDelaunayOverlay.textContent = "--";
            badgeDelaunayClean.textContent = "--";
        }

        badgeProjection3D.textContent = currentProjectionResult ? "3D" : "--";
    }

    function resetBadges() {
        badgeReal.textContent = "--";
        badgeLandmarksOverlay.textContent = "--";
        badgeLandmarksOnly.textContent = "--";
        badgeDelaunayOverlay.textContent = "--";
        badgeDelaunayClean.textContent = "--";
        badgeProjection3D.textContent = "--";
    }

    function resetProcessingBadges() {
        badgeLandmarksOverlay.textContent = "--";
        badgeLandmarksOnly.textContent = "--";
        badgeDelaunayOverlay.textContent = "--";
        badgeDelaunayClean.textContent = "--";
        badgeProjection3D.textContent = "--";
    }

    function clearAllCanvases() {
        clearCanvas(realContext, realCanvas);
        clearCanvas(overlayLandmarksContext, overlayLandmarksCanvas);
        clearCanvas(landmarksOnlyContext, landmarksOnlyCanvas);
        clearCanvas(delaunayOverlayContext, delaunayOverlayCanvas);
        clearCanvas(delaunayCleanContext, delaunayCleanCanvas);
        clearCanvas(projectionContext, projectionCanvas);
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
        context.fillStyle = "#000814";
        context.fillRect(0, 0, rect.width, rect.height);
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

    function drawLandmarksOverlayOnImage(context, canvas, landmarks) {
        if (!loadedImage || !landmarks) return;

        const { offsetX, offsetY, scaleX, scaleY } = getImageFitTransform(canvas, loadedImage);

        for (const point of landmarks) {
            context.beginPath();
            context.fillStyle = point.source === "synthetic" ? "#f59e0b" : "#2cff88";
            context.arc(
                offsetX + point.x * scaleX,
                offsetY + point.y * scaleY,
                point.source === "synthetic" ? 2.2 : 1.4,
                0,
                Math.PI * 2
            );
            context.fill();
        }
    }

    function drawLandmarksOnlyPanel(context, canvas, landmarks) {
        if (!landmarks || !landmarks.length) return;

        const transformed = fitPointsToCanvas(landmarks, canvas, 35);

        for (let index = 0; index < transformed.length; index += 1) {
            const point = transformed[index];
            const sourcePoint = landmarks[index];

            context.beginPath();
            context.fillStyle = sourcePoint.source === "synthetic" ? "#f59e0b" : "#2cff88";
            context.arc(
                point.x,
                point.y,
                sourcePoint.source === "synthetic" ? 2.2 : 1.4,
                0,
                Math.PI * 2
            );
            context.fill();
        }
    }

    function drawTrianglesOverlayOnImage(context, canvas, vertices, triangles) {
        if (!loadedImage || !vertices || !triangles) return;

        const { offsetX, offsetY, scaleX, scaleY } = getImageFitTransform(canvas, loadedImage);

        context.strokeStyle = "#2cff88";
        context.lineWidth = 0.8;

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
        if (!loadedImage || !vertices) return;

        const { offsetX, offsetY, scaleX, scaleY } = getImageFitTransform(canvas, loadedImage);

        context.fillStyle = "#2cff88";

        for (const point of vertices) {
            context.beginPath();
            context.arc(
                offsetX + point.x * scaleX,
                offsetY + point.y * scaleY,
                1.1,
                0,
                Math.PI * 2
            );
            context.fill();
        }
    }

    function drawCenteredMesh2D(context, canvas, vertices, triangles) {
        const transformed = fitPointsToCanvas(vertices, canvas, 28);

        context.strokeStyle = "#2cff88";
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

        context.fillStyle = "#2cff88";
        for (const point of transformed) {
            context.beginPath();
            context.arc(point.x, point.y, 1.1, 0, Math.PI * 2);
            context.fill();
        }
    }

    function drawProjectedMeshCentered(context, canvas, projectedVertices, triangles, rotationA = 0, rotationB = 0) {
        const transformed = fitPointsToCanvas(projectedVertices, canvas, 42);

        context.strokeStyle = "#ff5b6e";
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
            context.arc(point.x, point.y, 1.0, 0, Math.PI * 2);
            context.fill();
        }

        drawMiniAxis(context, canvas, rotationA, rotationB);
    }

    function drawMiniAxis(context, canvas, rotationA, rotationB) {
        const rect = canvas.getBoundingClientRect();
        const baseX = 52;
        const baseY = rect.height - 42;
        const axisLength = 28;

        const projectedX = projectAxisPoint(axisLength, 0, 0, rotationA, rotationB);
        const projectedY = projectAxisPoint(0, -axisLength, 0, rotationA, rotationB);
        const projectedZ = projectAxisPoint(0, 0, axisLength, rotationA, rotationB);

        context.beginPath();
        context.strokeStyle = "#23364f";
        context.lineWidth = 1;
        context.arc(baseX, baseY, 34, 0, Math.PI * 2);
        context.stroke();

        drawAxisLine(context, baseX, baseY, projectedX.x, projectedX.y, "#ff5b6e", "X");
        drawAxisLine(context, baseX, baseY, projectedY.x, projectedY.y, "#2cff88", "Y");
        drawAxisLine(context, baseX, baseY, projectedZ.x, projectedZ.y, "#38bdf8", "Z");

        context.beginPath();
        context.fillStyle = "#ffffff";
        context.arc(baseX, baseY, 3, 0, Math.PI * 2);
        context.fill();
    }

    function drawAxisLine(context, originX, originY, dx, dy, color, label) {
        const endX = originX + dx;
        const endY = originY + dy;

        context.beginPath();
        context.strokeStyle = color;
        context.lineWidth = 2;
        context.moveTo(originX, originY);
        context.lineTo(endX, endY);
        context.stroke();

        context.fillStyle = color;
        context.font = '12px Consolas';
        context.fillText(label, endX + 4, endY + 2);
    }

    function projectAxisPoint(x, y, z, a, b) {
        const cosA = Math.cos(a);
        const sinA = Math.sin(a);
        const cosB = Math.cos(b);
        const sinB = Math.sin(b);

        const xt = x * cosA - z * sinA;
        const yt = y * cosB - z * cosA * sinB - x * sinA * sinB;

        return { x: xt * 0.6, y: yt * 0.6 };
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