// Create form in parts

//1.To declare the variables
const steps = Array.from(document.querySelectorAll("form .step")); //Select all elementos of form that they have the class step
const nextBtn = document.querySelectorAll("form .next-step "); // Select all buttons next
const prevBtn = document.querySelectorAll("form .prev-step "); // Select all buttons prev

const form = document.querySelector("form"); // Select the element form

nextBtn.forEach((button) => {
  // function for go to next is a arrow function
  button.addEventListener("click", (e) => {
    //When you click it is created a event for
    changeStep("next"); // call the function with the parameter , it is equal in the line 15 -18
  });
});
prevBtn.forEach((button) => {
  button.addEventListener("click", (e) => {
    changeStep("prev");
  });
});

function changeStep(btn) {
  let index = 0;
  var active = document.querySelector("form .step.active"); //Select part active of form
  index = steps.indexOf(active);
  steps[index].classList.remove("active");
  if (btn === "next") {
    index++;
  } else if (btn === "prev") {
    index--;
  }
  steps[index].classList.add("active");
}

$(document).ready(function () {
    var active = Array.from(document.querySelectorAll("form .coments"))
  
  $("input[type=radio]").click(function () {
    const  name = $(this).attr("name");
    const value = $('input[name="' + name + '"]:checked').val();
    
    
    $('.coments').each(function (index) {
       
     if( value  == 0 && index == name    ){
        $(this).addClass("coments-active");
        
     }else if( value == 1 && index == name  ){
        $(this).removeClass("coments-active");
        
     }   
    
    });
  });
  
});
