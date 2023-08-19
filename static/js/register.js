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
    usernameField.classList.remove('is-invalid');
    usernameField.classList.remove('is-valid');
    if (usernameVal.length > 0) {
        fetch("/validate-username", {
            body: JSON.stringify({ username: usernameVal }),
            method: "POST",
        })
            .then((res) => res.json())
            .then((data) => {
                if (data.username_error) {
                    usernameField.classList.add('is-invalid');
                    cuser = false;
                    checkSubmit();

                }
                else {
                    usernameField.classList.add('is-valid');
                    cuser = true;
                    checkSubmit();

                }
            });
    }

});
// email validate

const email = document.querySelector('#emailField');
email.addEventListener("keyup", (e) => {
    const emailVal = e.target.value;
    emailField.classList.remove('is-invalid');
    emailField.classList.remove('is-valid');
    if (emailVal.length > 0) {
        fetch('/validate-email', {
            body: JSON.stringify({ email: emailVal }),
            method: "POST",
        })
            .then((res) => res.json())
            .then((data) => {
                if (data.email_error) {
                    emailField.classList.add('is-invalid');
                    cmail = false;
                    checkSubmit();
                }
                else {
                    emailField.classList.add('is-valid');
                    cmail = true;
                    checkSubmit();

                }
            });
    }
});

// passwordtoggle

const passwordtoggle = document.querySelector(".showPasswordToggle");
const passwordField = document.querySelector("#passwordField");
const handleToggleInput = (e) => {
    if (passwordtoggle.textContent === "SHOW") {
        passwordtoggle.textContent = "HIDE";
        passwordField.setAttribute("type", "text");
    } else {
        passwordtoggle.textContent = "SHOW";
        passwordField.setAttribute("type", "password");
    }
}

passwordtoggle.addEventListener("click", handleToggleInput);


