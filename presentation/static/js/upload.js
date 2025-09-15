document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("upload-form");
  const fileInput = document.getElementById("file-input");
  const uploadLabel = document.querySelector(".image-upload");

  if (!form || !fileInput) return;

  fileInput.addEventListener("change", async () => {
    const file = fileInput.files[0];

    if (!file) return;

    const validTypes = ["image/jpeg", "image/png"];
    if (!validTypes.includes(file.type)) {
      alert("Solo se permiten imágenes JPG o PNG.");
      fileInput.value = "";
      return;
    }

    const maxSizeMB = 5;
    if (file.size > maxSizeMB * 1024 * 1024) {
      alert(`El archivo no debe superar los ${maxSizeMB} MB.`);
      fileInput.value = "";
      return;
    }

    const formData = new FormData();
    formData.append("imagen", file);

    try {
      const response = await fetch("http://127.0.0.1:5000/subir-imagen", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      console.log("respuesta backend", data);

      if (data.success) {
        alert("Imagen subida con éxito");
        const preview = document.createElement("img");
        preview.src = data.url;
        preview.classList.add("img-fluid", "mt-2");
        document.querySelector(".upload-box").appendChild(preview);
      } else {
        alert("Error al subir la imagen", data?.error);
      }
    } catch (error) {
      console.error("Error en la solicitud:", error);
    }
  });
});
