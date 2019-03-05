// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

function sortObject(obj) {
    return Object.keys(obj).sort().reduce(function (result, key) {
        result[key] = obj[key];
        return result;
    }, {});
}

function number_format(number, decimals, dec_point, thousands_sep) {
  // *     example: number_format(1234.56, 2, ',', ' ');
  // *     return: '1 234,56'
  number = (number + '').replace(',', '').replace(' ', '');
  var n = !isFinite(+number) ? 0 : +number,
    prec = !isFinite(+decimals) ? 0 : Math.abs(decimals),
    sep = (typeof thousands_sep === 'undefined') ? ',' : thousands_sep,
    dec = (typeof dec_point === 'undefined') ? '.' : dec_point,
    s = '',
    toFixedFix = function(n, prec) {
      var k = Math.pow(10, prec);
      return '' + Math.round(n * k) / k;
    };
  // Fix for IE parseFloat(0.55).toFixed(0) = 0;
  s = (prec ? toFixedFix(n, prec) : '' + Math.round(n)).split('.');
  if (s[0].length > 3) {
    s[0] = s[0].replace(/\B(?=(?:\d{3})+(?!\d))/g, sep);
  }
  if ((s[1] || '').length < prec) {
    s[1] = s[1] || '';
    s[1] += new Array(prec - s[1].length + 1).join('0');
  }
  return s.join(dec);
}

// Bar Chart Example
var ctx = document.getElementById("dailyErrorCounts");

var totalDays = Object.keys(error_results['daily_count']).length
var data_points = Object.entries(sortObject(error_results['daily_count']))
var barchart_labels = []
var barchart_data = []
for (var entry in data_points){
  barchart_labels.push(moment.unix(data_points[entry][0]).format("MM-DD-YYYY")) 
  barchart_data.push(data_points[entry][1].length)
}

var dailyErrorCount = new Chart(ctx, {
  type: 'bar',
  data: {
    labels: barchart_labels,
    datasets: [{
      label: "Tracebacks",
      backgroundColor: "#4e73df",
      hoverBackgroundColor: "#2e59d9",
      borderColor: "#4e73df",
      data: barchart_data,
    }],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    pan: {
      enabled: true,
      mode: 'x',
      rangeMin: {y:0},
      rangeMax: {y:Math.max.apply(Math, barchart_data)*1.2}
    },
    zoom: {
      enabled: true,
      drag: false,
      mode: 'x',
      speed: 10,
      threshold: 10,
      rangeMin: {y:0,x:'02-01-2018'},
      rangeMax: {y:Math.max.apply(Math, barchart_data)*1.2},
      onZoom: function() { 
        debugger
       }

    },
    layout: {
      padding: {
        left: 10,
        right: 25,
        top: 25,
        bottom: 0
      }
    },
    scales: {
      xAxes: [{

        type: 'time',
       time: {
          
          parser: "MM-DD-YYYY",
          unit: 'month'
        },
        gridLines: {
          display: false,
          drawBorder: false
        },
        scaleLabel: {
            display: true,
            labelString: 'Date'
        },
        ticks: {
          maxTicksLimit: 6,
          maxRotation: 0
        },
        maxBarThickness: 25,
      }],
      yAxes: [{
        type: 'logarithmic',
        min:0,
        ticks: {
          min: 0,
          max:  Math.max.apply(Math, barchart_data)*1.2,
          maxTicksLimit: 5,
          padding: 10,
          // Include a dollar sign in the ticks
          callback: function(value, index, values) {
            if (Math.log10(value).toString().length===1 && value.toString().substring(0,1)==='1'){
                return number_format(value)
            }}
        },
        gridLines: {
          color: "rgb(234, 236, 244)",
          zeroLineColor: "rgb(234, 236, 244)",
          drawBorder: false,
          borderDash: [2],
          zeroLineBorderDash: [2]
        }
      }],
    },

    legend: {
      display: false
    },
    tooltips: {
      titleMarginBottom: 10,
      titleFontColor: '#6e707e',
      titleFontSize: 14,
      backgroundColor: "rgb(255,255,255)",
      bodyFontColor: "#858796",
      borderColor: '#dddfeb',
      borderWidth: 1,
      xPadding: 15,
      yPadding: 15,
      displayColors: false,
      caretPadding: 10,
      callbacks: {
        label: function(tooltipItem, chart) {
          var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
          var label = {}
          for (var i = 0; i < data_points[tooltipItem.index][1].length; i++){
            var key = data_points[tooltipItem.index][1][i][0]
            
            if (Object.keys(label).indexOf(key.toString()) === -1){
              label[key] = 1
            } else {
              label[key] ++
            } 
          } 
          var label_text = []
          for (entry in  Object.entries(label)){
              label_text.push( ' #' + Object.entries(label)[entry][0] + ": " + Object.entries(label)[entry][1] + " case(s)\n" )
          }
          return datasetLabel + ' : ' + label_text.join('\n');
        }
      }
    },
  }
});


var ctx2 = document.getElementById("URDBBreakdown");
var notURDB = urdb_results["count_blended_monthly"] + urdb_results["count_urdb_plus_blended"] + urdb_results["count_blended_annual"]
var URDBbarchart_labels = ["URDB Rate", "Blended Monthly", "Blended Monthly + URDB", "Blended Annual"]
var URDBbarchart_data = [urdb_results["count_total_uses"] - notURDB,urdb_results["count_blended_monthly"],urdb_results["count_urdb_plus_blended"],urdb_results["count_blended_annual"]]
var yAxisType 
if (Math.max.apply(Math, URDBbarchart_data)*1.2 > 10000){
  yAxisType = 'logarithmic' 
  yAxisFormatCallback = function(value, index, values) {
            if (Math.log10(value).toString().length===1 && value.toString().substring(0,1)==='1'){
                return number_format(value)
            }}
} else {
  yAxisType = 'linear'
  yAxisFormatCallback = function(value, index, values) {return number_format(value)}
}
console.log(yAxisType)
var URDBBreakdown = new Chart(ctx2, {
  type: 'bar',
  data: {
    labels: URDBbarchart_labels,
    datasets: [{
      label: "Tariff Types",
      backgroundColor: ['#4e73df', '#1cc88a', '#36b9cc','#e74a3b'],
      hoverBackgroundColor: "#2e59d9",
      borderColor: "#4e73df",
      data: URDBbarchart_data,
    }],
  },
  options: {
    maintainAspectRatio: false,
    layout: {
      padding: {
        left: 10,
        right: 25,
        top: 25,
        bottom: 0
      }
    },
    scales: {
      xAxes: [{
        time: {
          unit: 'month'
        },
        gridLines: {
          display: false,
          drawBorder: false
        },
        ticks: {
          maxTicksLimit: 6
        },
        maxBarThickness: 25,
      }],
      yAxes: [{
        type: yAxisType,
        ticks: {
          min: 0,
          max:  Math.max.apply(Math, URDBbarchart_data)*1.2,
          padding: 1,
          autoSkip: true,
          // Include a dollar sign in the ticks
          callback: yAxisFormatCallback
        },
        gridLines: {
          color: "rgb(234, 236, 244)",
          zeroLineColor: "rgb(234, 236, 244)",
          drawBorder: false,
          borderDash: [2],
          zeroLineBorderDash: [2]
        }
      }],
    },
    legend: {
      display: false
    },
    tooltips: {
      titleMarginBottom: 10,
      titleFontColor: '#6e707e',
      titleFontSize: 14,
      backgroundColor: "rgb(255,255,255)",
      bodyFontColor: "#858796",
      borderColor: '#dddfeb',
      borderWidth: 1,
      xPadding: 15,
      yPadding: 15,
      displayColors: false,
      caretPadding: 10,
      callbacks: {
        label: function(tooltipItem, chart) {
          var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
          return datasetLabel + ': ' + number_format(tooltipItem.yLabel);
        }
      }
    },
  }
});