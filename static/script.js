var passFields = [];

const hamburger = document.querySelector(".hamburger");
const navMenu = document.querySelector(".nav-menu");

hamburger.addEventListener("click", () => {
  hamburger.classList.toggle("active");
  navMenu.classList.toggle("active");
})

document.querySelectorAll(".nav-link").forEach(n => n.addEventListener("click", () => {
  hamburger.classList.remove("active");
  navMenu.classList.remove("active");
}))

function getPwdInputs() {
  var ary = [];
  var inputs = document.getElementsByTagName("input");
  for (var i=0; i<inputs.length; i++) {
    if (inputs[i].type.toLowerCase() === "password") {
      ary.push(inputs[i]);
    }
  }
  return ary;
}

function showPassword() {

  var inputs = document.getElementsByTagName("input");
  for (var i=0; i<inputs.length; i++) {
    if (inputs[i].type.toLowerCase() === "password") {
      passFields.push(inputs[i]);
      inputs[i].type = "text";
    } else if (passFields.includes(inputs[i])) {
      inputs[i].type = "password"
    }
  }

}
