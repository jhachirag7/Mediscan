const sign_in_btn = document.querySelector("#sign-in-btn");
const sign_up_btn = document.querySelector("#sign-up-btn");
const container = document.querySelector(".container");

sign_up_btn.addEventListener("click", () => {
  container.classList.add("sign-up-mode");
});

sign_in_btn.addEventListener("click", () => {
  container.classList.remove("sign-up-mode");
});

// username validate
const username = document.querySelector('#usernameField');

const submitbtn = document.querySelector("#submit");
submitbtn.setAttribute("disabled", 'disabled');

cuser = false;
cmail = false;

function checkSubmit() {
  if (cuser && cmail) {
    submitbtn.removeAttribute('disabled');
  } else {
    submitbtn.setAttribute("disabled", 'disabled');
  }

}

username.addEventListener("keyup", (e) => {
  const usernameVal = e.target.value;
  console.log('username', usernameVal)
  if (usernameVal.length > 0) {
    fetch("/validate-username", {
      body: JSON.stringify({ username: usernameVal }),
      method: "POST",
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.username_error) {
          cuser = false;
          checkSubmit();

        }
        else {
          cuser = true;
          checkSubmit();

        }
      });
  }
  else {
    console.log("hello")
    cuser = false
  }

});
// email validate

const email = document.querySelector('#emailField');
email.addEventListener("keyup", (e) => {
  const emailVal = e.target.value;
  if (emailVal.length > 0) {
    fetch('/validate-email', {
      body: JSON.stringify({ email: emailVal }),
      method: "POST",
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.email_error) {
          cmail = false;
          checkSubmit();
        }
        else {
          cmail = true;
          checkSubmit();

        }
      });
  }
  else {
    cmail = false
  }
});



