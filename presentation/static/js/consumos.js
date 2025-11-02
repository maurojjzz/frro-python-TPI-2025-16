document.addEventListener("DOMContentLoaded", function () {
  const botonesFiltro = document.querySelectorAll(".btn-filtro");
  const formularioFechas = document.querySelector('form[action="/buscar"]');
  const plotDiv = document.getElementById("plotly-semanal");

  // Manejar clicks en los botones de filtro rápido
  botonesFiltro.forEach((boton) => {
    boton.addEventListener("click", function () {
      // Remover la clase 'active' de todos los botones
      botonesFiltro.forEach((btn) => btn.classList.remove("active"));

      // Agregar la clase 'active' al botón clickeado
      this.classList.add("active");
    });
  });

  // Cuando se envía el formulario de fechas personalizadas
  if (formularioFechas) {
    formularioFechas.addEventListener("submit", function () {
      // Remover la clase 'active' de todos los botones de filtro
      botonesFiltro.forEach((btn) => btn.classList.remove("active"));
    });
  }

  // Renderizar gráfico de barras si existe graphJSON
  if (plotDiv && window.Plotly && window.graphJSON) {
    Plotly.newPlot('plotly-semanal', window.graphJSON.data, window.graphJSON.layout, {
      responsive: true,
      displayModeBar: true,
      displaylogo: false,
      modeBarButtonsToRemove: [
        'zoom2d', 'pan2d', 'select2d', 'lasso2d',
        'resetScale2d', 'hoverClosestCartesian',
        'hoverCompareCartesian', 'toggleSpikelines'
      ]
    });
  }

  // Renderizar gráfico de dona (pie) si existe graphPieJSON
  const plotPieDiv = document.getElementById("plotly-pie");
  if (plotPieDiv && window.Plotly && window.graphPieJSON) {
    Plotly.newPlot('plotly-pie', window.graphPieJSON.data, window.graphPieJSON.layout, {
      responsive: true,
      displayModeBar: false,
      displaylogo: false,
      modeBarButtonsToRemove: [
        'zoom2d', 'pan2d', 'select2d', 'lasso2d',
        'resetScale2d', 'hoverClosestCartesian',
        'hoverCompareCartesian', 'toggleSpikelines'
      ]
    });
  }
});
