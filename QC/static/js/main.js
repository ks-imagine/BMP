function sortTable(n, tableName) {
  var table,
    rows,
    switching,
    i,
    x,
    y,
    shouldSwitch,
    dir,
    switchcount = 0;
  table = document.getElementById(tableName);
  switching = true;
  //Set the sorting direction to ascending:
  dir = "asc";
  /*Make a loop that will continue until
  no switching has been done:*/
  while (switching) {
    //start by saying: no switching is done:
    switching = false;
    rows = table.rows;
    /*Loop through all table rows (except the
    first, which contains table headers):*/
    for (i = 1; i < rows.length - 1; i++) {
      shouldSwitch = false;
      /*Get the two elements you want to compare,
      one from current row and one from the next:*/
      x = rows[i].getElementsByTagName("TD")[n];
      y = rows[i + 1].getElementsByTagName("TD")[n];
      x_value = x.innerText.toLowerCase();
      y_value = y.innerText.toLowerCase();

      var xisnum = /^\d+$/.test(x_value);
      var yisnum =/^\d+$/.test(y_value);
      if (xisnum && yisnum) {
        x_value = parseInt(x_value);
        y_value = parseInt(y_value);
      }
      /*check if the two rows should switch place,
        based on the direction, asc or desc:*/
      if (dir == "asc") {
        if (x_value > y_value) {
          //if so, mark as a switch and break the loop:
          shouldSwitch = true;
          break;
        }
      } else if (dir == "desc") {
        if (x_value < y_value) {
          //if so, mark as a switch and break the loop:
          shouldSwitch = true;
          break;
        }
      }
    }
    if (shouldSwitch) {
      /*If a switch has been marked, make the switch
      and mark that a switch has been done:*/
      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
      switching = true;
      //Each time a switch is done, increase this count by 1:
      switchcount++;
    } else {
      /*If no switching has been done AND the direction is "asc",
      set the direction to "desc" and run the while loop again.*/
      if (switchcount == 0 && dir == "asc") {
        dir = "desc";
        switching = true;
      }
    }
  }
}

function searchTable(search, table) {
  var input, filter, table, tr, td, i, j;
  input = document.getElementById(search);
  filter = input.value.toUpperCase();
  table = document.getElementById(table);
  tr = table.getElementsByTagName("tr");
  for (i = 1; i < tr.length; i++) {
    (td = tr[i].getElementsByTagName("td")), (match = false);
    for (j = 0; j < td.length; j++) {
      if (td[j].innerHTML.toUpperCase().indexOf(filter) > -1) {
        match = true;
        break;
      }
    }
    if (!match) {
      tr[i].style.display = "none";
    } else {
      tr[i].style.display = "";
    }
  }
}

function deleteProduct(productID) {
  var confirmed = confirm("Are you sure you want to delete this entry?");
  if (confirmed) {
    fetch(`products/` + productID, { method: "DELETE" })
    .then((response) => {
      window.location.href = "/products";
    })
    .catch((error) => {
      alert("Error Occured"); //MESSAGE
      window.location.href = "/products";
    });
  }
}

function editProduct(productID) {
  fetch(`products/` + productID, {
    method: "POST"
  })
    .then((response) => {
      window.location.href = "/products";
    })
    .catch((error) => {
      alert("Error Occured"); //MESSAGE
      window.location.href = "/products";
    });
}

function deleteCustomer(customerID) {
  var confirmed = confirm("Are you sure you want to delete this entry?");
  if (confirmed) {
    fetch(`customers/` + customerID, { method: "DELETE" })
    .then((response) => {
      window.location.href = "/customers";
    })
    .catch((error) => {
      alert("Error Occured"); //MESSAGE
      window.location.href = "/customers";
    });
  }
}

function deleteLog(logID) {
  var confirmed = confirm("Are you sure you want to delete this entry?");
  if (confirmed) {
    fetch(`logs/` + logID, { method: "DELETE" })
    .then((response) => {
      window.location.href = "/logs";
    })
    .catch((error) => {
      alert("Error Occured"); //MESSAGE
      window.location.href = "/logs";
    });
  }
}
