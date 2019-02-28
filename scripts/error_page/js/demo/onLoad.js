// Call the dataTables jQuery plugin
$.fn.dataTable.ext.search.push(
    function( settings, data, dataIndex ) {
    	
    	if ( settings.nTable.id === 'dataTable_URDB' ) {
	        var filterErrors = $('#filterURDBbyErrors').is(':checked') 
	        var hasError = data[5] !== ''
	 		debugger
	        if ( filterErrors )
	        {
	            return hasError;
	        }
	        return true;
	    }
		
		else {
			return true
		}}
	);
$(document).ready(function() {
  	
  $('[data-toggle="popover"]').popover();
  $.fn.dataTable.moment( "MM-DD-YYYY HH:mm:ss" )
  
  $('#dataTable_URDB').DataTable();
  $('#dataTable_BadPost').DataTable();
  $('#dataTable_Errors').DataTable();
  
  $('#filterURDBbyErrors').click( function() {
        $('#dataTable_URDB').DataTable().draw();
    } );
});
