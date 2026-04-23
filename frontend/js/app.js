const imageInput = document.getElementById("imageInput");
const uploadButton = document.getElementById("uploadButton");
const imagePreview = document.getElementById("imagePreview");
const uploadStatus = document.getElementById("uploadStatus");
const backendResponse = document.getElementById("backendResponse");

let selectedFile = null;

imageInput.addEventListener("change", (event) => {
    const file = event.target.files[0];

    if (!file) {
        selectedFile = null;
        imagePreview.removeAttribute("src");
        uploadStatus.textContent = "No se seleccionó ninguna imagen.";
        return;
    }

    selectedFile = file;

    const objectUrl = URL.createObjectURL(file);
    imagePreview.src = objectUrl;

    uploadStatus.textContent =
        `Imagen seleccionada:\n${file.name}\nTamaño: ${Math.round(file.size / 1024)} KB`;

    backendResponse.textContent = "Lista para enviar al backend.";
});

uploadButton.addEventListener("click", async () => {
    if (!selectedFile) {
        uploadStatus.textContent = "Primero selecciona una imagen.";
        return;
    }

    uploadStatus.textContent = "Enviando imagen al backend...";

    try {
        const result = await uploadImageToBackend(selectedFile);

        uploadStatus.textContent = "Imagen enviada correctamente.";
        backendResponse.textContent = JSON.stringify(result, null, 2);
    } catch (error) {
        uploadStatus.textContent = "Error al enviar la imagen.";
        backendResponse.textContent = error.message;
    }
});