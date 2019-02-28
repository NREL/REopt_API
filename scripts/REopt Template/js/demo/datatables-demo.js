// Call the dataTables jQuery plugin
$(document).ready(function() {
  $.fn.dataTable.moment( "MM-DD-YYYY HH:mm:ss" )
  $('#dataTable_URDB').DataTable();
  $('#dataTable_BadPost').DataTable();
  $('#dataTable_Errors').DataTable();
  
});
