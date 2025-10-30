 document.addEventListener('DOMContentLoaded', function() {
    const botonesFiltro = document.querySelectorAll('.btn-filtro');
    const formularioFechas = document.querySelector('form[action="/buscar"]');
    
    // Manejar clicks en los botones de filtro rápido
    botonesFiltro.forEach(boton => {
      boton.addEventListener('click', function() {
        // Remover la clase 'active' de todos los botones
        botonesFiltro.forEach(btn => btn.classList.remove('active'));
        
        // Agregar la clase 'active' al botón clickeado
        this.classList.add('active');
      });
    });

    // Cuando se envía el formulario de fechas personalizadas
    if (formularioFechas) {
      formularioFechas.addEventListener('submit', function() {
        // Remover la clase 'active' de todos los botones de filtro
        botonesFiltro.forEach(btn => btn.classList.remove('active'));
      });
    }
  });