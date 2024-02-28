$(document).ready(function () {
 
    $('#table').DataTable({
      "responsive": true,
      "ordering": false,
      "language": {                                                               
        "url": "//cdn.datatables.net/plug-ins/1.10.15/i18n/Spanish.json",
        "info": "Página  _PAGE_ De _PAGES_",
        "search":"Buscar Usuario :"
      }
    });
});