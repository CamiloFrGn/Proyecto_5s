$(document).ready(function () {
    $("#sidebarCollapse").on("click", function () {
      $("#sidebar").toggleClass("active");
    });
  });
  
  $(document).ready(function () {
    $("#VerticalSidebarNavigation").load("/navbar");
  });