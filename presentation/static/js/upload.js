document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("upload-form");
  const fileInput = document.getElementById("file-input");
  const uploadBox = document.querySelector(".upload-box");
  const spinner = document.getElementById("upload-spinner");
  const label = document.querySelector(".label-formulario");

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
      document.querySelector(".titulo-tarjeta-sube").classList.add("d-none");
      document.querySelector(".imagen-subir").classList.add("d-none");
      form.classList.add("d-none");
      label.classList.remove("image-upload");
      const oldPreview = uploadBox.querySelector(".upload-form");
      if (oldPreview) oldPreview.remove();
      spinner.classList.remove("d-none");

      const response = await fetch("http://127.0.0.1:5000/subir-imagen", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();

      if (data.success) {
        const boxImage = document.createElement("div");
        boxImage.classList.add("upload-form", "position-relative", "rounded-3");

        const preview = document.createElement("img");
        preview.src = data.url;
        preview.classList.add("img-fluid");

        boxImage.appendChild(preview);

        label.classList.add("image-upload-other", "mt-2");
        document.querySelector(".subt").textContent = "Haz click para subir otra imagen";
        boxImage.style.overflow = "hidden";
        boxImage.style.position = "relative";
        boxImage.style.marginTop = "10px";
        boxImage.style.minHeight = "270px";

        form.style.height = "190px";
        form.classList.remove("d-none");

        uploadBox.classList.add("justify-content-center");
        uploadBox.prepend(boxImage);
      } else {
        alert("Error al subir la imagen", data?.error);
      }
    } catch (error) {
      console.error("Error en la solicitud:", error);
    } finally {
      spinner.classList.add("d-none");
    }
  });
});
