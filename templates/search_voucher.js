
  $(document).ready(function() {
    document.getElementById('message_modal').classList.toggle("tiny")
    document.getElementById('message_modal').classList.toggle("medium")
    $('#datepicker').calendar({
      monthFirst: false,
      type: 'month',
      formatter: {
        date: function(date, settings) {
          if (!date) return '';
          var day = date.getDate();
          var month = date.getMonth();
          var year = date.getFullYear();
          //console.log(date, settings);
          //return date;
          monthList = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
          return monthList[month] + '-' + year;
        },
      },
      onChange: function(date, text, mode) {
        getVoucherData(text);
        //console.log(date, text, mode);
      }
    });
  });

  function getVoucherData(text) {
    if(!text) {
      return
    }
    var target = text.split("-");
    var month = target[0];
    var year = target[1];
    //console.log(month,year);
    var headers = new Headers();
    var init = {
      method: 'GET',
      headers: headers,
      mode: 'cors',
      credentials: 'same-origin',
    };
    fetch('/{{view_type}}/search/bymonth/' + year + '/' + month, init).then(function(response) {
      if (response.ok) {
        return response.json();
      }
    }).then(function(json_data) {
      updateVoucherData(json_data)
      //console.log(json_data);
    });
  }

  function updateVoucherData(json_data) {
    var data = "";
    var filters = []
    for(let i = 0; i < document.getElementsByName('display_filter')[0].options.length; i++) {
	    filters[document.getElementsByName('display_filter')[0].options[i].value] = document.getElementsByName('display_filter')[0].options[i].selected
    }
    //console.log(filters);

    let t_amt = 0.00
    let t_tax = 0.00
    let t_twa = 0.00

    for (var i = 0; i < json_data.length; i++) {
      if(!filters.c && json_data[i].comp === "True") {
        continue;
      }
      if(!filters.s && json_data[i].sez === "True") {
        continue;
      }
      if(!filters.r && json_data[i].un_reg === "False" && json_data[i].comp === "False" && json_data[i].sez === "False") {
        continue;
      }
      if(!filters.ur && json_data[i].un_reg === "True") {
        continue;
      }
      if(!filters.hs && json_data[i].pos === "19") {
        continue;
      }
      if(!filters.os && json_data[i].pos !== "19") {
        continue;
      }
      t_amt += parseFloat(json_data[i].invoice_taxable_value)
      t_tax += parseFloat(json_data[i].invoice_tax)
      t_twa += parseFloat(json_data[i].invoice_value)

      data += `<tr>
        <td>${json_data[i].name}</td>
        <td>${json_data[i].inv_no}</td>
        <td>${json_data[i].day}-${json_data[i].month}-${json_data[i].year}</td>
        <td>${statecodes[json_data[i].pos]}</td>
        <td>${parseFloat(json_data[i].invoice_taxable_value).toFixed(2)}</td>
        <td>${parseFloat(json_data[i].invoice_tax).toFixed(2)}</td>
        <td>${parseFloat(json_data[i].invoice_value).toFixed(2)}</td>
        <td>
          <div class="ui primary button" onclick="getVoucher('${json_data[i].inv_no}')">
          <i class="eye icon"></i>View
          </div>
        </td>
      </tr>`
    }
    innerHTML =
      `<table class="ui celled padded table">
          <thead>
            <tr>
              <th>Ledger Name</th>
              <th>Invoice No</th>
              <th>Date</th>
              <th>Place of Supply</th>
              <th>Taxable Amount</th>
              <th>GST</th>
              <th>Invoice Value</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            ${data}
          </tbody>
          <tfoot>
            <tr>
              <td></td>
              <td></td>
              <td></td>
              <th>Total:</th>
              <th>${t_amt.toFixed(2)}</th>
              <th>${t_tax.toFixed(2)}</th>
              <th>${t_twa.toFixed(2)}</th>
              <th></th>
            </tr>
          </tfoot>
        </table>`
      if(json_data.length === 0) {
        innerHTML = `<div class="ui red center">No voucher found for given period.</div>`
      }

      document.getElementById('content').innerHTML = innerHTML;
  }
  function getVoucher(inv_no) {
    var headers = new Headers();
    var fd = new FormData();
    fd.append('inv_no',inv_no);
    var init = {
      method: 'POST',
      headers: headers,
      mode: 'cors',
      body: fd,
      credentials: 'same-origin',
    };
    fetch('/{{view_type}}/search/byinv/', init).then(function(response) {
      if (response.ok) {
        return response.json();
      }
    }).then(function(json_data) {
      viewVoucher(json_data);
    });
  }
  function viewVoucher(json_data) {
    document.getElementById('message_modal_header').innerHTML = "View Voucher";
    innerHTML = `
      <div class="ui container">
      <table class="ui padded table">
        <tbody>
          <tr>
            <td><p><b>Ledger Name: </b>${json_data.name}</p></td>
            <td><p><b>Date: </b>${json_data.day}-${json_data.month}-${json_data.year}</p></td>

          </tr>
          <tr>
            <td><p><b>GSTIN: </b>${json_data.gstin}</p></td>
            <td><p><b>Invoice No: </b>${json_data.inv_no}</p></td>

          </tr>
          <tr>
          <td><p><b>Place of Supply: </b>${statecodes[json_data.pos]}</p></td>
          <td><p><b>Supply Type: </b>${ ((json_data.sez === 'True')?"SEZ":"") }
                 ${((json_data.comp === 'True')?"Composition":"") }
                 ${((json_data.comp === 'False') && (json_data.sez === 'False'))?"Regular":""}
           </p></td>
          </tr>
        </tbody>
      </table>
      </div>
    `
    data = ""
    let t_amt = 0.00
    let t_tax = 0.00
    let t_twa = 0.00
    for (var i = 0; i < json_data.tax_data.length; i++) {
      t_amt += parseFloat(json_data.tax_data[i].amount)
      t_tax += (parseFloat(json_data.tax_data[i].rate)*parseFloat(json_data.tax_data[i].amount))
      t_twa += ((parseFloat(json_data.tax_data[i].rate)+1)*parseFloat(json_data.tax_data[i].amount))
      data += `<tr>
                <td>
                  ${parseFloat(json_data.tax_data[i].rate*100).toFixed(2)}%
                </td>
                <td>
                  ${json_data.tax_data[i].amount}
                </td>
                <td>
                  ${(parseFloat(json_data.tax_data[i].rate)*parseFloat(json_data.tax_data[i].amount)).toFixed(2)}
                </td>
                <td>
                  ${((parseFloat(json_data.tax_data[i].rate)+1)*parseFloat(json_data.tax_data[i].amount)).toFixed(2)}
                </td>
              </tr>`//json_data.tax_data[i]
    }
    innerHTML += `<div class="ui container">
      <table class="ui celled padded table">
        <thead>
          <tr>
            <th>Tax Rate</th>
            <th>Amount</th>
            <th>GST</th>
            <th>Amount with Tax</th>
          </tr>
        </thead>
        <tbody>
          ${data}
        </tbody>
        <tfoot>
          <tr>
            <th>Total:</th>
            <th>${t_amt.toFixed(2)}</th>
            <th>${t_tax.toFixed(2)}</th>
            <th>${t_twa.toFixed(2)}</th>
          </tr>
          <tr>
            <td></td>
            <td></td>
            <th>Round off:</th>
            <th>${json_data.roundoff}</th>
          </tr>
          <tr>
            <td></td>
            <td></td>
            <th>Invoice Value:</th>
            <th>${(parseFloat(json_data.roundoff) + t_twa).toFixed(2)}</th>
          </tr>
        </tfoot>
      </table>
    </div>`
    document.getElementById('message_modal_content').innerHTML = innerHTML
    $('#message_modal').modal('show');

    document.getElementById('message_modal_actions').innerHTML = `
      <div class="ui">
        <button type="button" class='ui red button' onclick="deleteVoucher('${json_data.id}')" id="modaldeletebutton">Delete</button>
        <a class='ui teal button'>Edit</a>
      </div>
    `;

  }
  function deleteVoucher(master_id) {
    document.getElementById('modaldeletebutton').classList.toggle("disabled");
    document.getElementById('modaldeletebutton').classList.toggle("loading");
    var headers = new Headers();
    var init = {
      method: 'GET',
      headers: headers,
      mode: 'cors',
      credentials: 'same-origin',
    };
    fetch('/{{view_type}}/delete/'+master_id, init).then(function(response) {
      if (response.ok) {
        var text = document.getElementsByName('date')[0].value
        getVoucherData(text)
        return response.json();
      }
    }).then(function(json_data) {
        setTimeout(function(){
          $('#message_modal').modal('hide');
        }, 1000);
    });

  }
