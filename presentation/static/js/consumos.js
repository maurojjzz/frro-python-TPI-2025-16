document.addEventListener("DOMContentLoaded", function () {
  const botonesFiltro = document.querySelectorAll(".btn-filtro");
  const formularioFechas = document.getElementById('form-filtro-fechas');
  const plotDiv = document.getElementById("plotly-semanal");
  const loadingSpinner = document.getElementById('loading-spinner');
  const graficosContainer = document.getElementById('graficos-container');
  let spinnerStartTime = 0;

  // Función para mostrar el spinner
  function mostrarSpinner() {
    spinnerStartTime = performance.now();
    if (loadingSpinner) loadingSpinner.classList.remove('d-none');
    if (graficosContainer) graficosContainer.classList.add('d-none');
  }

  // Función para ocultar el spinner
  function ocultarSpinner() {
    if (loadingSpinner) loadingSpinner.classList.add('d-none');
    if (graficosContainer) graficosContainer.classList.remove('d-none');
  }

  // Oculta el spinner asegurando un tiempo mínimo visible (ms)
  function ocultarSpinnerMin(minMs = 1500) {
    const elapsed = performance.now() - spinnerStartTime;
    const restante = Math.max(0, minMs - elapsed);
    setTimeout(() => ocultarSpinner(), restante);
  }


  // Manejar clicks en los botones de filtro rápido
  botonesFiltro.forEach((boton) => {
    boton.addEventListener("click", async function () {
      // Remover la clase 'active' de todos los botones
      botonesFiltro.forEach((btn) => btn.classList.remove("active"));

      // Agregar la clase 'active' al botón clickeado
      this.classList.add("active");
      
      // Limpiar inputs de fecha
      const inputFechaInicio = document.getElementById('fecha_inicio');
      const inputFechaFin = document.getElementById('fecha_fin');
      if (inputFechaInicio) inputFechaInicio.value = '';
      if (inputFechaFin) inputFechaFin.value = '';
      
      // Obtener el tipo de filtro
      const filtro = this.getAttribute('data-filtro');
      
      // Calcular fechas según el filtro
      const hoy = new Date();
      let fechaInicio, fechaFin;
      
      if (filtro === 'semana-actual') {
        // Recargar la página para mostrar la semana actual
        window.location.reload();
        return;
      } else if (filtro === '7dias') {
        // Últimos 7 días
        fechaFin = new Date(hoy);
        fechaInicio = new Date(hoy);
        fechaInicio.setDate(fechaInicio.getDate() - 7);
      } else if (filtro === '30dias') {
        // Últimos 30 días
        fechaFin = new Date(hoy);
        fechaInicio = new Date(hoy);
        fechaInicio.setDate(fechaInicio.getDate() - 30);
      }
      
      // Formatear fechas a YYYY-MM-DD para el backend
      const fechaInicioStr = fechaInicio.toISOString().split('T')[0];
      const fechaFinStr = fechaFin.toISOString().split('T')[0];
      
        // Mostrar spinner
        mostrarSpinner();
      
      // Llamar a la API para filtrar
      try {
        const response = await fetch('/api/consumos/filtrar', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            fecha_inicio: fechaInicioStr,
            fecha_fin: fechaFinStr
          })
        });
        
        const data = await response.json();
        
        if (data.success) {
          // Actualizar gráficos y tabla
          actualizarGraficos(data);
          actualizarTabla(data.tabla_data);
            ocultarSpinnerMin(1500);
          console.log(`✅ Filtro aplicado: ${filtro} (${fechaInicioStr} a ${fechaFinStr})`);
        } else {
            ocultarSpinnerMin(1500);
          alert(data.error || 'Error al filtrar datos');
          // Si hay error, recargar para volver a semana actual
          window.location.reload();
        }
      } catch (error) {
          ocultarSpinnerMin(1500);
        console.error('Error al aplicar filtro rápido:', error);
        alert('Error al conectar con el servidor');
      }
    });
  });

  // Manejar submit del formulario de fechas con AJAX
  if (formularioFechas) {
    formularioFechas.addEventListener("submit", async function (e) {
      e.preventDefault(); // Prevenir submit tradicional
      
      // Remover la clase 'active' de todos los botones de filtro
      botonesFiltro.forEach((btn) => btn.classList.remove("active"));
      
      const fechaInicio = document.getElementById('fecha_inicio').value;
      const fechaFin = document.getElementById('fecha_fin').value;
      
      if (!fechaInicio || !fechaFin) {
        alert('Por favor selecciona ambas fechas');
        return;
      }
      
      try {
        // Mostrar loading (opcional)
        const btnSubmit = formularioFechas.querySelector('button[type="submit"]');
        const textoOriginal = btnSubmit.textContent;
        btnSubmit.disabled = true;
        btnSubmit.textContent = 'Cargando...';
        
          // Mostrar spinner
          mostrarSpinner();
        
  // Hacer request a la API
        const response = await fetch('/api/consumos/filtrar', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            fecha_inicio: fechaInicio,
            fecha_fin: fechaFin
          })
        });
        
        const data = await response.json();
        
        if (data.success) {
          // Actualizar gráficos
          actualizarGraficos(data);
          
          // Actualizar tabla
          actualizarTabla(data.tabla_data);
          
            // Ocultar spinner con tiempo mínimo visible
            ocultarSpinnerMin(1500);
        } else {
            ocultarSpinnerMin(1500);
          alert(data.error || 'Error al filtrar datos');
        }
        
        // Restaurar botón
        btnSubmit.disabled = false;
        btnSubmit.textContent = textoOriginal;
        
      } catch (error) {
          ocultarSpinnerMin(1500);
        console.error('Error al filtrar consumos:', error);
        alert('Error al conectar con el servidor');
        formularioFechas.querySelector('button[type="submit"]').disabled = false;
      }
    });
  }
  
  // Función para actualizar los gráficos
  function actualizarGraficos(data) {
    const graphJSON = JSON.parse(data.graphJSON);
    const graphPieJSON = JSON.parse(data.graphPieJSON);
    
    // Actualizar gráfico de barras semanal
    if (plotDiv) {
      Plotly.react('plotly-semanal', graphJSON.data, graphJSON.layout, {
        responsive: true,
        displayModeBar: true,
        displaylogo: false,
        modeBarButtonsToRemove: ['zoom2d', 'pan2d', 'select2d', 'lasso2d',
          'resetScale2d', 'hoverClosestCartesian', 'hoverCompareCartesian', 'toggleSpikelines']
      });
    }
    
    // Actualizar gráfico de torta
    const plotPieDiv = document.getElementById("plotly-pie");
    if (plotPieDiv) {
      Plotly.react('plotly-pie', graphPieJSON.data, graphPieJSON.layout, {
        responsive: true,
        displayModeBar: false,
        displaylogo: false
      });
    }
  }
  
  // Función para actualizar la tabla
  function actualizarTabla(tablaData) {
    const tbody = document.querySelector('.table tbody');
    if (!tbody) return;
    
    const diasEspanol = {
      'Monday': 'Lunes',
      'Tuesday': 'Martes',
      'Wednesday': 'Miércoles',
      'Thursday': 'Jueves',
      'Friday': 'Viernes',
      'Saturday': 'Sábado',
      'Sunday': 'Domingo'
    };
    
    if (tablaData.length === 0) {
      tbody.innerHTML = '<tr><td colspan="8" class="text-center text-muted">No hay datos en el rango seleccionado</td></tr>';
      return;
    }
    
    tbody.innerHTML = tablaData.map(row => {
      const fecha = new Date(row.fecha_consumo + 'T00:00:00');
      const fechaFormateada = fecha.toLocaleDateString('es-AR', { day: '2-digit', month: '2-digit', year: 'numeric' });
      const diaSemana = diasEspanol[fecha.toLocaleDateString('en-US', { weekday: 'long' })];
      
      return `
        <tr>
          <td>${fechaFormateada}</td>
          <td>${diaSemana}</td>
          <td class="fw-bold">${row.nombre}</td>
          <td>${Math.round(row.proteinas)}</td>
          <td>${Math.round(row.carbohidratos)}</td>
          <td>${Math.round(row.grasas)}</td>
          <td>${Math.round(row.colesterol)}</td>
          <td class="fw-bold">${Math.round(row.calorias)}</td>
        </tr>
      `;
    }).join('');
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

  // Renderizar histograma comparativo si existe graphHistJSON
  const plotHistDiv = document.getElementById("plotly-hist");
  if (plotHistDiv && window.Plotly && window.graphHistJSON) {
    Plotly.newPlot('plotly-hist', window.graphHistJSON.data, window.graphHistJSON.layout, {
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

  // Renderizar gráfico de líneas 30 días si existe graphLineJSON
  const plotLineaDiv = document.getElementById("plotly-linea");
  if (plotLineaDiv && window.Plotly && window.graphLineJSON) {
    Plotly.newPlot('plotly-linea', window.graphLineJSON.data, window.graphLineJSON.layout, {
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

  // Renderizar gráfico diario si existe graphHoyJSON
  const plotHoyDiv = document.getElementById("plotly-hoy");
  if (plotHoyDiv && window.Plotly && window.graphHoyJSON) {
    Plotly.newPlot('plotly-hoy', window.graphHoyJSON.data, window.graphHoyJSON.layout, {
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
});
