// Call the dataTables jQuery plugin
$.fn.dataTable.ext.search.push(
    function( settings, data, dataIndex ) {
    	
    	if ( settings.nTable.id === 'dataTable_URDB' ) {
	        var filterErrors = $('#filterURDBbyErrors').is(':checked') 
	        var hasError = data[5] !== ''
	        if ( filterErrors )
	        {
	            return hasError;
	        }
	        return true;
	    }
		
		else {
			return true
		}

		}

	);
$(document).ready(function() {
  	
  $('[data-toggle="popover"]').popover();
  $.fn.dataTable.moment( "MM-DD-YYYY HH:mm:ss" )
  
  $('#dataTable_URDB').DataTable();
  $('#dataTable_BadPost').DataTable();
  $('#dataTable_Errors').DataTable();
  $('#dataTable_queryErrors').DataTable();
  $('#filterURDBbyErrors').click( function() {
        $('#dataTable_URDB').DataTable().draw();
    } );

	$('#errorQueryByDate').change( function() {
		debugger
		$('#dataTable_queryErrors').dataTable().fnClearTable();
		$('#errorQueryByID').val(undefined)
		
		
		var ts = moment($('#errorQueryByDate').val()).unix()
		
		var tracebacks = error_results['daily_count'][ts+ 61200]
		if (tracebacks.length !== undefined){
			var label = {}
	          for (var i = 0; i < tracebacks.length; i++){
	            var key = tracebacks[i]
	            if (!(key in label)){
	              label[key] = 1
	            } else {
	              label[key] ++
	            } 
	          } 

	          var label_text = []
	          for (entry in  Object.entries(label)){
	          		$('#dataTable_queryErrors').DataTable().row.add(
					[
						common_lookup[Object.entries(label)[entry][0]],
						Object.entries(label)[entry][0],
						Object.entries(label)[entry][1],
						moment($('#errorQueryByDate').val()).format('MM-DD-YYYY HH:mm:ss')
					]).draw();
	          }
		$('#dataTable_queryErrors').DataTable()
		}} )


  $('#errorQueryByID').on('input', function() {
  		$('#dataTable_queryErrors').dataTable().fnClearTable();
  		$('#errorQueryByDate').val(undefined)
		
		
		var tb_id = parseInt($('#errorQueryByID').val())
		
		var day_entries = Object.entries(error_results['daily_count'])
		for (var i = 0; i < day_entries.length; i++){

				if (day_entries[i][1].indexOf(tb_id) !== -1 ){
					
					var tracebacks = []
					for (var ii = 0; ii < day_entries[i][1].length; ii++) {
						if ( day_entries[i][1][ii] == tb_id){
						tracebacks.push(tb_id)
					}
					}
					
					var label = {}
			        for (var iii = 0; iii  < tracebacks.length; iii ++){
			            var key = tracebacks[iii]
			            if (!(key in label)){
			              label[key] = 1
			            } else {
			              label[key] ++
			            } 
			          } 

			       	
	          		$('#dataTable_queryErrors').DataTable().row.add([
						common_lookup[tb_id],
						tb_id,
						label[tb_id],
						moment.unix(day_entries[i][0]).format('MM-DD-YYYY HH:mm:ss')
					]).draw();
			     	     
				}
				
		}
		$('#dataTable_queryErrors').DataTable()
} )
});
