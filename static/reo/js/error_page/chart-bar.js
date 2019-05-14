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


var totalDays = Object.keys(scenario_results.data).length - 2
var daily_data_points = Object.entries(sortObject(scenario_results.data))
var daily_barchart_labels = []
var daily_barchart_data = []
var resilience_data = []
var error_barchart_data = []
var error_data_points = []

for (var entry in daily_data_points){
  
  if (daily_data_points[entry][0].substring(0,5)!="count"){  
    daily_barchart_labels.push(moment.unix(daily_data_points[entry][0]).format("MM-DD-YYYY")) 
    daily_barchart_data.push(daily_data_points[entry][1]['count'])
    resilience_data.push(daily_data_points[entry][1]['count_resilience'])
    var daily_errors = error_results.data['daily_count'][parseInt(daily_data_points[entry][0])]
    if (daily_errors===undefined){
      error_data_points.push(undefined)
      error_barchart_data.push(0)
    } else {
      error_data_points.push(daily_errors)
      error_barchart_data.push(  daily_errors.length)
    }
  }
  }

var dailyErrorCount = new Chart(ctx, {
  type: 'bar',
  data: {
    labels: daily_barchart_labels,
    datasets: [{
      label: "Total Errors",
      fillColor: "rgba(220,220,220,0)",
      hoverBackgroundColor: "#D3D3D3",
      borderColor: "#e74a3b",
      borderWidth:2,
      data: error_barchart_data,
    }, {
      label: "Resilience Runs",
      backgroundColor: "#0000ff",
      hoverBackgroundColor: "#D3D3D3",
      borderColor: "#4e73df",
      data: resilience_data,
    },
    {
      label: "Finacial Runs",
      backgroundColor: "#1cc88a",
      hoverBackgroundColor: "#D3D3D3",
      borderColor: "#4e73df",
      data: daily_barchart_data,
    },
   ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    pan: {
      enabled: true,
      mode: 'x',
      rangeMin: {y:0},
      rangeMax: {y:Math.max.apply(Math, daily_barchart_data)*1.2}
    },
    zoom: {
      enabled: true,
      drag: false,
      mode: 'x',
      speed: 10,
      threshold: 10,
      rangeMin: {y:0,x:'02-01-2018'},
      rangeMax: {y:Math.max.apply(Math, daily_barchart_data)*1.2},
      onZoom: function() { 
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
        stacked: true,
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
        stacked: false,
        type: 'logarithmic',
        min:0,
        ticks: {
          min: 0,
          max:  Math.max.apply(Math, daily_barchart_data)*1.2,
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
      display: true
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
          var label = {}
          if (error_data_points[tooltipItem.index]===undefined){
            return 'Total Runs: ' + daily_data_points[tooltipItem.index][1]['count'] +'  Resilience Runs: ' + (resilience_data[tooltipItem.index]) +'  Errors: 0 '
          } else {

          for (var i = 0; i < error_data_points[tooltipItem.index].length; i++){
            var key = error_data_points[tooltipItem.index][i][0]
            
            if (Object.keys(label).indexOf(key.toString()) === -1){
              label[key] = 1
            } else {
              label[key] ++
            } 
          } 
          var label_text = []
          for (entry in  Object.entries(label)){
              label_text.push( '#' + Object.entries(label)[entry][0] + ": " + Object.entries(label)[entry][1] + " case(s)\n" )
          }
          return 'Total Runs: ' + (daily_data_points[tooltipItem.index][1]['count']) +'  Resilience Runs: ' + (resilience_data[tooltipItem.index]) +  '  Errors: '+ error_data_points[tooltipItem.index].length +' {' + label_text + "}";
          }
        }
      }
    },
  }
});


var ctx2 = document.getElementById("URDBBreakdown");
var notURDB = urdb_results.data["count_blended_monthly"] + urdb_results.data["count_urdb_plus_blended"] + urdb_results.data["count_blended_annual"]
var URDBbarchart_labels = ["URDB Rate", "Blended Monthly", "Blended Monthly + URDB", "Blended Annual"]
var URDBbarchart_data = [urdb_results.data["count_total_uses"] - notURDB,urdb_results.data["count_blended_monthly"],urdb_results.data["count_urdb_plus_blended"],urdb_results.data["count_blended_annual"]]
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