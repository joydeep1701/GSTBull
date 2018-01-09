function validate_ledger() {
  var ledger_id = document.getElementsByName('ledger_id')[0].value;
  var ledger_name = document.getElementsByName('ledger_name')[0].value;
  if(ledger_id === '') {
    showMessage('Ledger name not given','Please select a name from dropdown');
    console.log('No Name');
    return false;
  }
  var headers = new Headers();
  var init = {
    method: 'GET',
    headers: headers,
    mode: 'cors',
    credentials: 'same-origin',
  };
  fetch('/ledger/data/' + ledger_id, init).then(function(response) {
    if(response.ok) {
      return response.json();
    }
  }).then(function(json_data) {
    if(json_data.name !== ledger_name) {
      showMessage('Ledger name mismatch','Please select a name from dropdown');
      console.log('name Error');
      return;
    }
    validate_taxrates();
  });
  return true;
}
function validate_taxrates() {
  tax_rates = document.getElementsByTagName('select');
  for (var i = 0; i < tax_rates.length; i++) {
   if(tax_rates[i].value === "") {
     showMessage('Tax rate mismatch','Please select a taxrate from dropdown');
     return false;
   }
  }
  validate_rest()
  return true;
}
function validate_rest() {
  var date = document.getElementsByName('date')[0].value;

  var total = calculate(false);
  if(isNaN(total) || total < 1.00) {
    showMessage('Amount Error','Invalid charecter in amount field');
    return;
  }
  if(document.getElementsByName('inv_no')[0].value === '') {
    showMessage('Invoice Number NULL','Please enter a valid invoice number')
    return;
  }
  document.getElementById('message_modal_header').innerHTML = `
    <div class="header">Confirm Submit</div>
  `
  document.getElementById('message_modal_content').innerHTML = `
    <p><b>Invoice Date : </b>${date}</p>
    <p><b>Invoice Value: </b>${total}</p>
  `

  document.getElementById('message_modal_actions').innerHTML = `
    <button class="ui green button" onclick="validate_voucher(true)" id='final_submit'>Submit</button>
  `
  $('#message_modal').modal('show');

}

function validate_voucher(post=false) {
  if(post){
    document.getElementById('final_submit').classList.toggle("disabled")
    document.getElementById('final_submit').classList.toggle("loading")
    document.getElementById('voucher_form').submit()
    console.log('POST');
  }
  else{
    validate_ledger();
  }


}
function deleterows(posCheckBox) {
  var elem = document.getElementById('table_tbody');
  for (var i = 0; i < elem.childElementCount; i++) {
    if (elem.children[i].children[posCheckBox].children[0].children[0].checked) {
      console.log(i);
      elem.deleteRow(i);
      deleterows(4)
    }
  }
}

function addrows() {
  var table = document.getElementById('table_tbody');
  var row = table.insertRow(-1);
  row.insertCell(0).innerHTML =
    `<select class="ui fluid dropdown" name="rate">
        <option value="">Taxrate</option>
        {% for rate in taxrates %}
        <option value="{{rate.taxrate}}">
          {{rate.display}}
        </option>
        {% endfor %}
      </select>`
  row.insertCell(1).innerHTML = `<input type="text" name="amount" value="" autocomplete="off" placeholder="Amount">`
  row.insertCell(2).innerHTML = `<input type="text" name="" value="" disabled>`
  row.insertCell(3).innerHTML = `<input type="text" name="" value="" disabled>`
  row.insertCell(4).innerHTML = `<div class="ui toggle checkbox">
                                  <input type="checkbox" value="True">
                                  <label></label>
                                </div>`
  $('.dropdown')
    .dropdown({
      // you can use any ui transition
      transition: 'drop'
    });
}
function calculate(iterate = true) {
  let total_amountv = 0.00;
  let total_taxv = 0.00;
  var rows = document.getElementById('table_tbody').children;
  for (var i = 0; i < rows.length; i++) {
    columns = rows[i].getElementsByTagName('input');
    let taxrate = rows[i].getElementsByTagName('select')[0].value;
    let amount =  ((columns[0].value) != NaN ? (columns[0].value) : 0);

    let tax = amount * taxrate;
    let amountwt = parseFloat(amount) + parseFloat(amount * taxrate)

    total_amountv = parseFloat(total_amountv) + parseFloat(amount)
    total_taxv = parseFloat(total_taxv) + parseFloat(tax)

    columns[1].value = parseFloat(tax).toFixed(2)
    columns[2].value = isNaN(amountwt) ? 0.00 : parseFloat(amountwt).toFixed(2);
    //console.log(taxrate,amount);
  }
  var roundoff = parseFloat(document.getElementById("roundoff").value)
  isNaN(roundoff)?document.getElementById("roundoff").value = 0:true;
  if (isNaN(total_amountv)) {
    document.getElementById('total_amount_p').innerHTML = 0.00
    document.getElementById('total_tax_p').innerHTML = 0.00
    //console.log(total_taxv);
    document.getElementById('total_amount_wth_tax_p').innerHTML = 0.00
    document.getElementById('final_amount').innerHTML = 0.00
  } else {
    document.getElementById('total_amount_p').innerHTML = parseFloat(total_amountv).toFixed(2)
    document.getElementById('total_tax_p').innerHTML = parseFloat(total_taxv).toFixed(2)
    //console.log(total_taxv);
    document.getElementById('total_amount_wth_tax_p').innerHTML = parseFloat(parseFloat(total_amountv) + parseFloat(total_taxv)).toFixed(2)
    document.getElementById('final_amount').innerHTML = parseFloat(parseFloat(total_amountv) + parseFloat(total_taxv) + roundoff).toFixed(2)
  }
  if(supply_type != "") {
    if(supply_type === 'Inter') {
      var text = `<p><b>IGST: </b>${parseFloat(total_taxv).toFixed(2)}</p>`
    }
    else{
      var text = `<p><b>CGST: </b>${parseFloat(total_taxv/2).toFixed(2)}
                  <br /><b>SGST: </b>${parseFloat(total_taxv/2).toFixed(2)}</p>`
    }
    document.getElementById('voucher_overview').innerHTML = text;
  }

  if (iterate)
    setTimeout(calculate, 250)
  else {
    return parseFloat(parseFloat(total_amountv) + parseFloat(total_taxv) + roundoff).toFixed(2);
  }
}
calculate();
function adjust(type) {
  //console.log(type);
  let ca = calculate(false);
  var roundoff = parseFloat(document.getElementById("roundoff").value)
  if(type == '-') {

    roundoff = parseFloat(roundoff) - 1 - parseFloat(ca - parseInt(ca))

  }
  if(type == '+') {
    roundoff = parseFloat(roundoff) + 1 - parseFloat(ca - parseInt(ca))
  }
  document.getElementById("roundoff").value = parseFloat(roundoff).toFixed(2)
}

/*
  function ledger_search(keyword) {
    if(keyword == '')
      return
    $('#message_modal').modal('show')

    var headers = new Headers();
    var init = {
      method: 'GET',
      headers: headers,
      mode: 'cors',
      credentials: 'same-origin',
    };
    fetch('/ledger/search/' + keyword, init).then(function(response) {
      if(response.ok) {
        return response.json();
      }
    }).then(function(json_data) {


      console.log(json_data);

    });
  }*/
$(document).ready(function() {
  $('#ledger_input').search({
    type: 'category',
    minCharacters: 1,
    onSelect: function(result, response) {
      updateLedgerInfo(result);
    },
    apiSettings: {
      onResponse: function(jsonResponse) {
        var response = {
          results: {
            'Registered': {
              name: 'Registered',
              results: []
            },
            'Unregistered': {
              name: 'Unregistered',
              results: []
            },
            'SEZ': {
              name: 'SEZ',
              results: []
            },
            'Composition': {
              name: 'Composition',
              results: []
            },
          }
        };
        var maxResults = 5;
        $.each(jsonResponse, function(index, item) {
          if (index >= maxResults) {
            return false;
          }
          //console.log(item);
          var temp = {
            title: item.name,
            description: item.unregistered === 'False' ? item.gstin : item.place_of_supply,
            url: '#',
            registered: item.unregistered === 'False',
            composition: item.composition === 'True',
            sez: item.sez === 'True',
            pos: item.place_of_supply,
            ledger_id : item.id
          };
          if (item.unregistered === 'True') {
            response.results['Unregistered'].results.push(temp);
          } else if (item.composition === 'True') {
            response.results['Composition'].results.push(temp);
          } else if (item.sez === 'True') {
            response.results['SEZ'].results.push(temp);
          } else {
            response.results['Registered'].results.push(temp);
          }
        });

        //console.log(response);
        return response;
      },
      url: '/ledger/search/{query}'
    }
  });
});
var supply_type = "";

function updateLedgerInfo(data) {
  var innerHTML = ""
  if (!data.registered) {
    innerHTML += `<p></p><p class="ui tag label">Unregistered</p>`
  } else {
    innerHTML += `<p><b>GSTIN: </b>${data.description}</p>`
    if (data.sez) {
      innerHTML += `<p class="ui tag label">Special Economic Zone</p>`
    }
    if (data.composition) {
      innerHTML += `<p class="ui tag label">Composition Scheme</p>`
    }
  }
  supply_type = data.pos == '19' ? 'Intra' : 'Inter';
  innerHTML += `<p></p>
                <p><b>POS: </b>${statecodes[data.pos]}</p>
                <p><b>Supply Type: </b>${supply_type}-State</p>`
  //console.log(innerHTML);
  document.getElementById('ledger_overview').innerHTML = innerHTML;
  document.getElementsByName('date')[0].focus()
  document.getElementsByName('ledger_id')[0].value = data.ledger_id;
  //console.log(data);
}


var today = new Date();
var date = new Date(today.getFullYear(), today.getMonth() - 1, 1)
document.getElementsByName('date')[0].value = date;

$(document).ready(function() {
  $('#datepicker').calendar({
    monthFirst: false,
    type: 'date',
    formatter: {
      date: function (date, settings) {
        if (!date) return '';
        var day = date.getDate();
        var month = date.getMonth();
        var year = date.getFullYear();
        //console.log(date, settings);
        //return date;
        monthList = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        return day + '-' + monthList[month] + '-' + year;
      }
    }
  });
});
var statecodes = {}
function updateStateCodes() {
  fetch('/statecodes').then(function(response) {
    if (response.ok) {
      return response.json();
    }
  }).then(function(ret) {
    //console.log(ret);
    statecodes = ret;
  });
}
updateStateCodes();
