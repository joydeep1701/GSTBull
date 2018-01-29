var headers = new Headers();
var init = {
  method: 'GET',
  headers: headers,
  mode: 'cors',
  credentials: 'same-origin',
};

function randomColor() {
    return `rgb(${parseInt(Math.random()*256)},${parseInt(Math.random()*256)},${parseInt(Math.random()*256)})`
}
function min(a,b){
  return a<b?a:b
}

var monthlysdata = [];
var monthlypdata = [];
var monthlabels = [];

fetch("/chart/Sale/monthlytotal", init).then(function(response) {
  if(response.ok) {
    return response.json();
  }
}).then(function(json_data){
  console.log(json_data);
  var labels = [];
  for (var i = 0; i < json_data.length; i++) {
    monthlysdata.push(json_data[i].amount.toFixed(2));
    labels.push(json_data[i].month);
  }
  monthlabels = labels;
  new Chart(document.getElementById('salesChart').getContext('2d'), {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: "Sale",
        borderColor: randomColor(),
        data: monthlysdata,
      }]
    },
  });
}).then(
  function(){
    fetch("/chart/Pur/monthlytotal", init).then(function(response) {
      if(response.ok) {
        return response.json();
      }
    }).then(function(json_data){
      console.log(json_data);
      var labels = [];
      let toptotal = 0;
      for (var i = 0; i < json_data.length; i++) {
        monthlypdata.push(json_data[i].amount.toFixed(2));
        labels.push(json_data[i].month);
      }

      new Chart(document.getElementById('purchaseChart').getContext('2d'), {
        type: 'line',
        data: {
          labels: labels,
          datasets: [{
            label: "Purchase",
            //borderColor: randomColor(),
            data: monthlypdata,
          }]
        },

      });
    });
  }
).then(
  function() {
    //
    // var linechartdata = {
    //   labels:monthlabels,
    //   datasets:[{
    //     label: "Sales",
    //     borderColor: randomColor(),
    //     //backgroundColor: randomColor(),
    //     fill: false,
    //     data: monthlysdata,
    //     yAxisID: "y-axis-3",
    //   },{
    //     label: "Purchase",
    //     borderColor: randomColor(),
    //     //backgroundColor: randomColor(),
    //     fill: false,
    //     data: monthlypdata,
    //     yAxisID: "y-axis-1",
    //   }],
    // };
    // new Chart(document.getElementById("salePurchaseMonthly").getContext("2d"), {
    //         type: 'line',
    //         data: linechartdata,
    //         options: {
    //             responsive: true,
    //             hoverMode: 'index',
    //             stacked: false,
    //             title:{
    //                 display: true,
    //                 text:'{{session['company_name']}} Sale Purchase'
    //             },
    //             scales: {
    //                 yAxes: [{
    //                     type: "linear", // only linear but allow scale type registration. This allows extensions to exist solely for log scale for instance
    //                     display: false,
    //                     position: "left",
    //                     id: "y-axis-1",
    //                 }, {
    //                     type: "linear", // only linear but allow scale type registration. This allows extensions to exist solely for log scale for instance
    //                     display: false,
    //                     position: "left",
    //                     id: "y-axis-3",
    //                     // grid line settings
    //                     gridLines: {
    //                         drawOnChartArea: false, // only want the grid lines for one axis to show up
    //                     },
    //                 }],
    //             }
    //         },
    //     });

  }
);



fetch("/chart/Sale/partytotal", init).then(function(response) {
  if(response.ok) {
    return response.json();
  }
}).then(function(json_data){
  console.log(json_data);
  let total = 0;
  for (var i = 0; i < json_data.length; i++) {
    total += json_data[i].amount;
  }
  var data = [];
  var labels = [];
  var background = [];
  let toptotal = 0;
  for (var i = 0; i < min(10,json_data.length); i++) {
    toptotal += json_data[i].amount;
    data.push(json_data[i].amount.toFixed(2));
    labels.push(json_data[i].name);
    background.push(randomColor());
  }
  data.push((total-toptotal).toFixed(2));
  labels.push("Remaining");
  background.push(randomColor());

  new Chart(document.getElementById("salesPartyChart"), {
    "type": "pie",
    "data": {
      "labels": labels,
      "datasets": [
        {
          "label": "Party Wise Sales Data",
          "data": data,
          "backgroundColor": background
        }
      ]
    },
    options: {
      legend: {
        display: false
      },
    }
  });
});

fetch("/chart/Pur/partytotal", init).then(function(response) {
  if(response.ok) {
    return response.json();
  }
}).then(function(json_data){
  console.log(json_data);
  let total = 0;
  for (var i = 0; i < json_data.length; i++) {
    total += json_data[i].amount;
  }
  var data = [];
  var labels = [];
  var background = [];
  let toptotal = 0;
  for (var i = 0; i < min(10,json_data.length); i++) {
    toptotal += json_data[i].amount;
    data.push(json_data[i].amount.toFixed(2));
    labels.push(json_data[i].name);
    background.push(randomColor());
  }
  data.push((total-toptotal).toFixed(2));
  labels.push("Remaining");
  background.push(randomColor());

  new Chart(document.getElementById("purchasePartyChart"), {
    "type": "pie",
    "data": {
      "labels": labels,
      "datasets": [
        {
          "label": "Party Wise Sales Data",
          "data": data,
          "backgroundColor": background
        }
      ]
    },
    options: {
      legend: {
        display: false
      },
    }
  });
});
