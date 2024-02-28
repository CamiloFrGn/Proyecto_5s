var allElement = 0;
var elements = [];
$(document).ready(function () {
 
  
  $(".create").on("click", function () {
    const name = $(this).attr("name");
    $("#input_id").val(name);
    const ruta = $(this).attr("id");
  
    $("#ruta_nombre").val(ruta);
    $('#familia').val("")
        $('#cantidad').val("")
        $('#trabajador').val("")
        test = $("#total").val(allElement);
        elements = $(".body_form").toArray();
  });
  $("#Agregar_marbete").on("click", function () {
    var newElement = $(".body_form").last().clone().appendTo(".formulario");
    newElement.addClass("Clonado");
    allElement = $(".body_form").toArray().length;
    test = $("#total").val(allElement);
    
    elements = $(".body_form").toArray();
    familiaArray = $(".familia").toArray();
    cantidadArray = $(".cantidad").toArray();
    trabajadorArray = $(".trabajador").toArray();

    $(".Clonado").each(function (index) {
      $(".familia").each(function (index2) {
     
        
        $(familiaArray[index + 1]).attr("name", "familia" + (index + 1));
   
        $(familiaArray[index + 1]).prop("required", true);
        $(cantidadArray[index + 1]).attr("name", "cantidad" + (index + 1));
    
        $(cantidadArray[index + 1]).prop("required", true);
        $(trabajadorArray[index + 1]).attr("name", "trabajador" + (index + 1));
        
        $(trabajadorArray[index + 1]).prop("required", true);
      });
      $('.familia').last().val("");
      $('.cantidad').last().val("");
      $('.trabajador').last().val("")

    });
  });

  $("#Eliminar_marbete").on("click", function () {
    for (let i = allElement; i >= 2; i--) {
      if (i === allElement && allElement>1) {        
       $(".body_form").last().remove(); 
      }
    }
    allElement--;   
  });

  $("#modal_").on("hidden.bs.modal", function () {
    for (let i = allElement; i >= 2; i--) {
      elements[i] = $(".body_form").last().remove();
      allElement = 1;
      
    }
  });

  $(document).ready(function () {
 
    $('#table').DataTable({
      "responsive": true,
      "ordering": false,
      "columnDefs": [
        { "targets": [0,1,2,4], "searchable": false }
    ],
      "language": {                                                               
        "url": "//cdn.datatables.net/plug-ins/1.10.15/i18n/Spanish.json",
        "info": "Página  _PAGE_ De _PAGES_",
        "search":"Buscar Ruta :"
      }
    });
});
});




