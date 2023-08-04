// script for add.html

// DOMPurify - sanitizes HTML and prevents XSS attacks
const formFields = [
  document.getElementById("first_name"),
  document.getElementById("last_name"),
  document.getElementById("email"),
  document.getElementById("other_animal"),
];

// function to sanitize input using DOMPurify
function sanitizeInput() {
  const field = this;
  field.value = DOMPurify.sanitize(field.value);
}

formFields.forEach((field) => {
  field.addEventListener("input", sanitizeInput);
});

const emailInput = document.getElementById("email");
emailInput.addEventListener("input", checkEmailAvailability);

// email validation and check if email is unique
function checkEmailAvailability() {
  const email = emailInput.value.trim();
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  if (emailRegex.test(email)) {
    fetch("/check_email_availability", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email: email }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.available) {
          emailInput.setCustomValidity("");
        } else {
          emailInput.setCustomValidity("This email is already used.");
          document.getElementById("emailFeedback").textContent =
            "This email address has already been used to submit information. You can add information only once with one email address.";
        }
      })
      .catch((error) => {
        console.error("Error checking email availability:", error);
      });
  } else {
    emailInput.setCustomValidity("Please enter a valid email address.");
    document.getElementById("emailFeedback").textContent =
      "Please enter a valid email address in the format name@example.com.";
  }
}

// validation for others
(function () {
  "use strict";
  window.addEventListener(
    "load",
    function () {
      var forms = document.getElementsByClassName("needs-validation");
      Array.prototype.filter.call(forms, function (form) {
        form.addEventListener(
          "submit",
          function (event) {
            if (form.checkValidity() === false) {
              event.preventDefault();
              event.stopPropagation();
            }
            form.classList.add("was-validated");
          },
          false
        );
      });
    },
    false
  );
})();
