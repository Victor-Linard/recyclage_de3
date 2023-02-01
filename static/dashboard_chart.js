const chart = document.getElementById('chart_plastique');
new Chart(chart, {
type: 'line',
options: {
  scales: {
    y: {
      display: false
    },
    x: {
      display: false
    }
  },
  elements: {
    line: {
      borderWidth: 2,
      borderColor: '#D2DDEC'
    },
    point: {
      hoverRadius: 0
    }
  },
  plugins: {
    tooltip: {
      external: function() {
        return false;
      }
    }
  }
},
data: {
  labels: new Array(6).fill('Label'),
  datasets: [{
    data: [50, 50, 50 ,65, 10, 0]
  }]
}
});