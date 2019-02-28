// // Set new default font family and font color to mimic Bootstrap's default styling
// Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
// Chart.defaults.global.defaultFontColor = '#858796';
// function numberWithCommas(x) {
//     return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
// }

// // Pie Chart Example
// var ctx = document.getElementById("URDBBreakdown");
// var notURDB = urdb_results["count_blended_monthly"] + urdb_results["count_urdb_plus_blended"] + urdb_results["count_blended_annual"]
// var myPieChart = new Chart(ctx, {
//   type: 'doughnut',
//   data: {
//     labels: ["URDB Rate", "Blended Monthly", "Blended Monthly + URDB", "Blended Annual"],
//     datasets: [{
//       data: [urdb_results["count"] - notURDB,urdb_results["count_blended_monthly"],urdb_results["count_urdb_plus_blended"],urdb_results["count_blended_annual"]],
//       backgroundColor: ['#4e73df', '#1cc88a', '#36b9cc','#e74a3b'],
//       hoverBackgroundColor: ['#2e59d9', '#17a673', '#2c9faf','#e74a3b'],
//       hoverBorderColor: "rgba(234, 236, 244, 1)",
//     }],
//   },
//   options: {
//     maintainAspectRatio: false,
//     tooltips: {
//       backgroundColor: "rgb(255,255,255)",
//       bodyFontColor: "#858796",
//       borderColor: '#dddfeb',
//       borderWidth: 1,
//       xPadding: 15,
//       yPadding: 15,
//       displayColors: false,
//       caretPadding: 10,
//     },
//     legend: {
//       display: false
//     },
//     cutoutPercentage: 80,
//   },
// });



