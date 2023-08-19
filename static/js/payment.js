var mydata = localStorage.getItem('listCards');
var listCards = JSON.parse(mydata);
console.log(listCards)
var bill = [];


var form = document.getElementById("formid");
function submitForm(event) {
    event.preventDefault();
    var cname = document.getElementById("name").value;
    var email = document.getElementById("email").value;
    var addr = document.getElementById("addr").value;
    var city = document.getElementById("city").value;
    var state = document.getElementById("state").value;
    var zip = document.getElementById("zip").value;
    var namecard = document.getElementById("namecard").value;
    var cardnum = document.getElementById("cardnum").value;
    var month = document.getElementById("month").value;
    var year = document.getElementById("year").value;
    var cvv = document.getElementById("cvv").value;

    bill.push({
        'name': cname, 'email': email, 'addr': addr, 'city': city, 'state': state, 'zip': zip,
        'namecard': namecard, 'cardnum': cardnum, 'month': month, 'year': year, 'cvv': cvv
    });

    fetch('/billing', {
        body: JSON.stringify({ cardbill: bill, Medlist: listCards }),
        method: "POST",
    })
        .then((res) => res.json())
        .then((data) => {
            console.log(data);
            window.location.href = 'http://127.0.0.1:8000/dropbox'
        })

    console.log(bill);
}
form.addEventListener("submit", submitForm);

function submit() {


}





