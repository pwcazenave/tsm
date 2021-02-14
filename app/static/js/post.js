var coll = document.getElementsByClassName("collapsible");
var i;

for (i = 0; i < coll.length; i++) {
  coll[i].addEventListener("click", function () {
    this.classList.toggle("active");
    var content = this.nextElementSibling;
    if (content.style.display !== "none") {
      content.style.display = "none";
    } else {
      content.style.display = "block";
    }
  });
}

// // Hide good hosts by default
// var tables = document.getElementsByClassName('pretty-table');
// console.log(tables);
// for (t=0; t<tables.length; t++) {
//   console.log(tables[0])
//   var rows = tables[t].rows;
//   for (r=0; r<rows.length; r++) {
//     let paths = rows[r].cells;
//     console.log(paths[0].className)

//     var showHost = 0;
//     if (paths[0].className === "bad") {
//       showHost = 1;
//     }
//     console.log('showHost: ' + showHost);
//     if (showHost === 0) {
//       rows[r].style.display = "none";
//     }
//   }
// }

