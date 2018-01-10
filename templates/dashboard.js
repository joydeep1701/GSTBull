var ctx = document.getElementById('salesChart').getContext('2d');
var chart = new Chart(ctx, {
  // The type of chart we want to create
  type: 'line',

  // The data for our dataset
  data: {
    labels: ["January", "February", "March", "April", "May", "June", "July"],
    datasets: [{
      label: "Sale",
      //backgroundColor: 'rgb(255, 99, 132)',
      borderColor: 'rgb(255, 99, 132)',
      data: [0, 10, 5, 2, 20, 30, 45, 90],
    }]
  },

  // Configuration options go here
  options: {}
});


new Chart(document.getElementById("salesPartyChart"), {
  "type": "doughnut",
  "data": {
    "labels": ["Red", "Blue", "Yellow","Red", "Blue", "Yellow"],
    "datasets": [{
      "label": "My First Dataset",
      "data": [300, 50, 100,300, 50, 100],
      "backgroundColor": ["rgb(255, 99, 132)", "rgb(54, 162, 235)", "rgb(255, 205, 86)","rgb(255, 99, 132)", "rgb(54, 162, 235)", "rgb(255, 205, 86)"]
    }]
  }
});



var ctx = document.getElementById('purchaseChart').getContext('2d');
var chart = new Chart(ctx, {
  // The type of chart we want to create
  type: 'line',

  // The data for our dataset
  data: {
    labels: ["January", "February", "March", "April", "May", "June", "July", "Aug"],
    datasets: [{
      label: "Purchase",
      //backgroundColor: 'rgb(255, 99, 132)',
      borderColor: 'rgb(76, 175, 82)',
      data: [0, 10, 5, 2, 20, 30, 45, 90],
    }]
  },

  // Configuration options go here
  options: {}
});

new Chart(document.getElementById("purchasePartyChart"), {
  "type": "doughnut",
  "data": {
    "labels": ["Red", "Blue", "Yellow"],
    "datasets": [{
      "label": "My First Dataset",
      "data": [300, 50, 100],
      "backgroundColor": ["rgb(255, 99, 132)", "rgb(54, 162, 235)", "rgb(255, 205, 86)"]
    }]
  }
});
