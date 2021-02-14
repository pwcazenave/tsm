function uhOh() {
    var rows = document.getElementsByTagName('td');
    for (i=0; i<rows.length; i++) {
        if (rows[i].classList !== "bad") {
            rows[i].style.display = "none";
        }
        console.log(rows[i]);
    }
}