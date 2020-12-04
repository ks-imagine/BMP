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

/* Product Requirements Builder */
function addRow() {
  var empTab = document.getElementById('empTable');
  var colCnt = empTab.rows[0].cells.length;
  var rowCnt = empTab.rows.length;
  var tr = empTab.insertRow(rowCnt);

  for (i = 0; i < colCnt; i++) {
      var td = document.createElement('td');
      td = tr.insertCell(i);

      if (i == 0) {
          var button = document.createElement('input');
          button.setAttribute('type', 'button');
          button.setAttribute('value', 'Remove Row');
          button.setAttribute('onclick', 'removeRow(this)');
          button.className= "modal-buttons";
          td.appendChild(button);
      }
      else if (i == 3) {
          var values = ["Pass/Fail", "Number", "Text"];
          var select = document.createElement("select");
          select.name = "data-types";
          select.id = "data-types" + rowCnt;
          select.setAttribute('onchange', 'setDefaults(' + (rowCnt) +')');
          for (const val of values) {
              var option = document.createElement("option");
              option.value = val;
              option.text = val;
              select.appendChild(option);
          }
          td.appendChild(select);
      }
      else if (i ==4) {
          var ele = document.createElement('input');
          ele.id =  "max" + rowCnt;
          ele.className = "max-min";
          ele.setAttribute('type', 'text');
          ele.setAttribute('value', 'Pass');
          ele.setAttribute("disabled", "true");
          td.appendChild(ele);
      }
      else if (i == 5) {
          var ele = document.createElement('input');
          ele.id = "min" + rowCnt;
          ele.className = "max-min";
          ele.setAttribute('type', 'text');
          ele.setAttribute('value', 'Fail');
          ele.setAttribute("disabled", "true");
          td.appendChild(ele);
      }
      else {
          var ele = document.createElement('input');
          ele.setAttribute('type', 'text');
          td.appendChild(ele);
      }
  }
}

// function to delete a row.
function removeRow(oButton) {
  var empTab = document.getElementById('empTable');
  empTab.deleteRow(oButton.parentNode.parentNode.rowIndex);
}

// function to extract and submit table data.
function submit() {
  var myTab = document.getElementById('empTable');
  var arrValues = new Array();
  var reqInput = document.getElementById("requirements");
  var reqFinal = document.getElementById("requirements-final");
  var reqButton = document.getElementById("req-button");
  // loop through each row of the table.
  for (row = 1; row < myTab.rows.length; row ++) {
      // loop through each cell in a row.
      for (c = 0; c < myTab.rows[row].cells.length; c++) {
          var element = myTab.rows.item(row).cells[c];
          if (c != 0) {
              if (checkValues(element.childNodes[0].value)){
                  arrValues.push(customTrim(element.childNodes[0].value));
              }
              else {
                  arrValues.push("");
              }
          }
      }
  }

  var finalRequirements = parseRequirements(arrValues);

  if (arrValues.length > 0) {
    reqInput.value = finalRequirements;

    reqFinal.innerHTML = finalRequirements;
    reqFinal.style.display = "block";
    reqButton.innerHTML = "Edit Requirements";
    launchReqBuilder();
  } else {
    reqInput.value = "";

    reqFinal.innerHTML = "";
    reqFinal.style.display = "none";
    reqButton.innerHTML = "Build Requirements";
    launchReqBuilder();
  }
}

function checkValues(string) {
  const regex = RegExp('[a-zA-Z0-9]+');
  return regex.test(string);
}

function customTrim(string) {
  return string.replace(/^(\s|-|_)+|(\s|-|_)+$/gm,'');
}

function setDefaults(rowNum) {
  var dd = document.getElementById("data-types" + rowNum);
  var ddValues = dd.options[dd.selectedIndex].text;
  var max = document.getElementById("max" + rowNum);
  var min = document.getElementById("min" + rowNum);
  if (ddValues == "Pass/Fail") {
      max.value = "Pass";
      min.value = "Fail";
      max.setAttribute("disabled", "true");
      min.setAttribute("disabled", "true");
  } else if (ddValues == "Number") {
      max.value = "0";
      min.value = "1";
      max.removeAttribute("disabled");
      min.removeAttribute("disabled");
  } else {
      max.value = "ABC";
      min.value = "XYZ";
      max.removeAttribute("disabled");
      min.removeAttribute("disabled");
  }
}

function launchReqBuilder() {
  var reqTable = document.getElementById("req-table");
  var modalContent = document.getElementById("product-modal-content");
  if (reqTable.style.display === "none") {
    reqTable.style.display = "block";
    modalContent.style.top = "0%";
    modalContent.style.bottom = "0%";
  } else {
    reqTable.style.display = "none";
    modalContent.style.top = "initial";
    modalContent.style.bottom = "50%";
  }
}

function parseRequirements(arrValues) {
  var keyIndex = 0;
  const data = {
    reqs: [],
  };
  const values = arrValues;
  const keys = ["s-req", "l-req", "v-typ", "max", "min"];
  for (var i = 0; i < values.length; i++) {
    var obj = {};
    obj[keys[keyIndex]] = values[i];
    data.reqs.push(obj);
    keyIndex++;
    if (keyIndex == 5) {
      keyIndex = 0;
    }
  }
  console.log(JSON.stringify(data));
  return JSON.stringify(data);
}