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
        
        // Actualizar el historial nutricional usando Jinja2
        updateHistorialNutricional();
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
    allContent.forEach((element) => {
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

      let valoresNutricionales = sumarValoresNutricionales(data?.reconocimiento?.food_response);

      let porcentajeCarbs = (valoresNutricionales.carbohidratos / 300) * 100;
      let porcentajeProte = (valoresNutricionales.proteinas / 50) * 100;
      let porcentajeGrasas = (valoresNutricionales.grasas / 70) * 100;
      let porcentajeColest = (valoresNutricionales.colesterol / 300) * 100;

      // Actualizar el contenido completo del cuadro
      secondBox.innerHTML = `
       <div class="d-flex flex-column flex-grow w-100 h-100">
              <h4 class="mt-2 mb-2 fs-4 text-start">Analisis Nutricional</h4>
              <h5 class="fs-6 fw-normal text-start">Alimento detectado:</h5>
              <div class="analisis-nutrientes d-flex flex-column flex-grow-1">
                <h4 class="fs-5 text-start mb-1">${data?.titulo_atractivo || "Plato de comida detectado"}</h4>
                <div class="d-flex flex-column flex-grow-1 align-items-center">
                  <div class="d-flex flex-row datos-nutri-box">
                    <div>
                      <p class="nro-valor fw-bold fs-5 text-success">${valoresNutricionales.calorias || 0}</p>
                      <p class="info-sub-sub">Calorias(kcal)</p>
                    </div>
                    <div>
                      <p class="nro-valor fw-bold fs-5 sgundo-sub">${valoresNutricionales.proteinas || 0}</p>
                      <p class="info-sub-sub">Proteinas(g)</p>
                    </div>
                    <div>
                      <p class="nro-valor fw-bold fs-5 trcer-sub">${valoresNutricionales.grasas || 0}</p>
                      <p class="info-sub-sub">Grasas(g)</p>
                    </div>
                  </div>
                  <div class="progreso-barras-box">

                    <div>
                      <div class=" d-flex flex-row justify-content-between">
                        <p class="m-0 caption-barra">Carbohidratos</p>
                        <p class="m-0 caption-barra">${valoresNutricionales.carbohidratos || 0}g</p>
                      </div>
                      <div class="progress" role="progressbar">
                        <div class="progress-bar bg-success" style="width: ${Math.min(porcentajeCarbs, 100)}%"></div>
                      </div>
                    </div>

                    <div>
                      <div class=" d-flex flex-row justify-content-between">
                        <p class="m-0 caption-barra">Proteinas</p>
                        <p class="m-0 caption-barra">${valoresNutricionales.proteinas || 0}g</p>
                      </div>
                      <div class="progress" role="progressbar">
                        <div class="progress-bar bg-info" style="width: ${Math.min(porcentajeProte, 100)}%"></div>
                      </div>
                    </div>

                    <div>
                      <div class=" d-flex flex-row justify-content-between">
                        <p class="m-0 caption-barra">Grasas</p>
                        <p class="m-0 caption-barra">${valoresNutricionales.grasas || 0}g</p>
                      </div>
                      <div class="progress" role="progressbar">
                        <div class="progress-bar bg-warning" style="width: ${Math.min(porcentajeGrasas, 100)}%"></div>
                      </div>
                    </div>

                    <div>
                      <div class=" d-flex flex-row justify-content-between">
                        <p class="m-0 caption-barra">Colesterol</p>
                        <p class="m-0 caption-barra">${valoresNutricionales.colesterol || 0}mg</p>
                      </div>
                      <div class="progress" role="progressbar">
                        <div class="progress-bar bg-danger" style="width: ${Math.min(porcentajeColest, 100)}%"></div>
                      </div>
                    </div>
                    </div>
                  </div>
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

const sumarValoresNutricionales = (f_data) => {
  let total = {
    calorias: 0,
    proteinas: 0,
    grasas: 0,
    carbohidratos: 0,
    colesterol: 0,
  };
  f_data.map((nut) => {
    if (nut?.eaten?.total_nutritional_content) {
      total.calorias += parseFloat(nut?.eaten?.total_nutritional_content?.calories) || 0;
      total.proteinas += parseFloat(nut?.eaten?.total_nutritional_content?.protein) || 0;
      total.grasas += parseFloat(nut?.eaten?.total_nutritional_content?.fat) || 0;
      total.carbohidratos += parseFloat(nut?.eaten?.total_nutritional_content?.carbohydrate) || 0;
      total.colesterol += parseFloat(nut?.eaten?.total_nutritional_content?.cholesterol) || 0;
    }
  });

  return {
    calorias: Math.round(total.calorias * 10) / 10,
    proteinas: Math.round(total.proteinas * 10) / 10,
    grasas: Math.round(total.grasas * 10) / 10,
    carbohidratos: Math.round(total.carbohidratos * 10) / 10,
    colesterol: Math.round(total.colesterol * 10) / 10,
  };
};

async function updateHistorialNutricional() {
  try {
    const response = await fetch(`${API_URL}/obtener-historial-html`);
    
    if (response.ok) {
      const htmlContent = await response.text();
      const historialContainer = document.getElementById('historial-content');
      
      if (historialContainer) {
        historialContainer.innerHTML = htmlContent;
        
        // Reinicializar tooltips para cualquier nuevo botón
        const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        tooltipTriggerList.forEach((el) => new bootstrap.Tooltip(el));
      }
    } else {
      console.error('Error al obtener el historial:', response.status);
    }
  } catch (error) {
    console.error('Error al actualizar historial nutricional:', error);
  }
}
