console.log('Hola-ScriptVereficacion ')

function myFunction() {
    $(".create").on("click", function () {
    const name = $(this).attr("name");
    let cantidad=$('#conteo_'+name).val();
    window.location.href = '/guardar_dato_verificacion/valor='+name+'&cantidad='+cantidad;
    })
}

$(document).ready(function () {
 
    $('#table').DataTable({
      "responsive": true,
      "ordering": false,
      "language": {                                                               
        "url": "//cdn.datatables.net/plug-ins/1.10.15/i18n/Spanish.json",
        "info": "Página  _PAGE_ De _PAGES_",
        "search":"Buscar  :"
      }
    });
});