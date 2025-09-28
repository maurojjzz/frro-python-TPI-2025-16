document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("upload-form");
  const fileInput = document.getElementById("file-input");
  const uploadBox = document.querySelector(".upload-box");
  const spinner = document.getElementById("upload-spinner");
  const label = document.querySelector(".label-formulario");
  const API_URL = window.API_URL;

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

      const response = await fetch(`${API_URL}/subir-imagen`, {
        method: "POST",
        body: formData,
      });
      const data = await response.json();

      console.log(data);

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

        // aca la logica del cuadro analisis nutricional
        updateAnalysisBox(data);
      } else {
        alert("Error al subir la imagen", data?.error);
      }
    } catch (error) {
      console.error("Error en la solicitud:", error);
    } finally {
      spinner.classList.add("d-none");
    }
  });

  function updateAnalysisBox(data) {
    const secondBox = document.querySelector(".second-analisis-box");
    secondBox.classList.add("position-relative");
    
    // Ocultar todo el contenido actual
    const allContent = secondBox.querySelectorAll("*:not(#analysis-spinner)");
    allContent.forEach(element => {
      element.style.display = "none";
    });
    
    // Remover cualquier spinner previo
    const existingSpinner = secondBox.querySelector("#analysis-spinner");
    if (existingSpinner) {
      existingSpinner.remove();
    }
    
    // Crear nuevo spinner
    const analysisSpinner = document.createElement("div");
    analysisSpinner.id = "analysis-spinner";
    analysisSpinner.classList.add("position-absolute", "top-50", "start-50", "translate-middle");
    analysisSpinner.innerHTML =
      '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Analizando...</span></div>';

    secondBox.appendChild(analysisSpinner);

    setTimeout(() => {
      // Remover el spinner
      const spinnerToRemove = secondBox.querySelector("#analysis-spinner");
      if (spinnerToRemove) {
        spinnerToRemove.remove();
      }
      
      // Actualizar el contenido completo del cuadro
      secondBox.innerHTML = `
       <div class="d-flex flex-column flex-grow w-100 h-100">
          <h4 class="mt-2 mb-3 fs-4 text-start">Analisis Nutricional</h4>
          <h5 class="fs-6 fw-normal text-start">Alimento detectado:</h5>
          <div class="analisis-nutrientes d-flex flex-column flex-grow-1 border border-success">
            <h4 class="fs-5 text-start">${data?.titulo_atractivo || "Plato de comida detectado"}</h4>
            <div class="d-flex flex-grow-1 align-items-center border border-danger">
              
            </div>
          </div>
        </div>
      `;
    }, 3000);
  }
});

// Función auxiliar para resetear el cuadro de análisis
function resetAnalysisBox() {
  const secondBox = document.querySelector(".second-analisis-box");
  secondBox.innerHTML = `
    <div class="analisis_nutricional">
      <h4 class="mt-5 mb-4 fs-4">Analisis Nutricional</h4>
      <div>
        <i class="fa-solid fa-magnifying-glass-chart analisis"></i>
        <p class="mt-2 subt">No hay datos</p>
        <p class="aclaracion">Sube una imagen para obtener análisis</p>
      </div>
    </div>
  `;
}
