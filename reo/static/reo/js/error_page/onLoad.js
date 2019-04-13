// Call the dataTables jQuery plugin

function create_generic_popup(link_text,header, text, id){
		
		return '<br><span title="'+header+'" class="text-info" data-toggle="popover"  data-content="'+text.replace(/"/g, '\'')+'" style="margin:20px;">'+link_text+'</span>'
	}


function create_run_uuid_popup(recent_uuids){
		
		if (recent_uuids===undefined){recent_uuids={}}
	
		var base = $('<div class ="popoverList"></div>')
		var list = $('<ul style="list-style: none;" class ="popoverList"></ul>')
		for (var i = 0; i < recent_uuids.length; i++){
			var uuid = $('<li class ="popoverList"></li>')
			uuid.html(recent_uuids[i])
			list.append(uuid)
		}
		base.append(list)
		return "<span title='UUID\'s' class='uuid_popover text-info'  data-toggle='popover' data-html='true' data-content='"+ base.prop('outerHTML') +"''>UUID\'s</span>"
	}

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
  $('body').on('click', function (e) {
    if ($(e.target).attr('class')===undefined){
		$('[data-toggle="popover"]').popover('hide');
    }
    else if ($(e.target).attr('class').includes('popover')===false) { 
        $('[data-toggle="popover"]').popover('hide');
    }
});
  error_results_lookup = []
  for (var i = 0; i < Object.entries(error_results['daily_count']).length; i++){
  	error_results_lookup.push(moment.unix(Object.entries(error_results['daily_count'])[i][0]).format('YYYY-MM-DD'))
  }  
  $('[data-toggle="popover"]').popover();
  $.fn.dataTable.moment( "MM-DD-YYYY HH:mm:ss" )
  $.fn.dataTable.moment( "MM-DD-YYYY" )
  
  $('#dataTable_URDB').DataTable();
  $('#dataTable_BadPost').DataTable();
  $('#dataTable_Errors').DataTable();
  $('#dataTable_queryErrors').DataTable();
  $('#filterURDBbyErrors').click( function() {
        $('#dataTable_URDB').DataTable().draw();
    } );

	$('#errorQueryByDate').change( function() {
		
		$('#dataTable_queryErrors').dataTable().fnClearTable();
		$('#errorQueryByID').val(undefined)
		
		
		var ts = error_results_lookup.indexOf(moment($('#errorQueryByDate').val()).format('YYYY-MM-DD'))
		
		var tracebacks = Object.entries(error_results['daily_count'])[ts][1]
		
		if (tracebacks !== undefined){
			
			var label = {}
			
	          for (var i = 0; i < tracebacks.length; i++){
	            var tb_id = tracebacks[i][0]
	            var run_uuid = tracebacks[i][1]
	            
	            if (Object.keys(label).indexOf(tb_id.toString())===-1){
	              label[tb_id] = [1,[run_uuid]]
	            } else {
	              
	              label[tb_id][0] = label[tb_id][0] +1
	              
	              if (label[tb_id][1].indexOf(run_uuid) === -1){
	              		label[tb_id][1].push(run_uuid)
	              	}
	              
	            } 
	          } 
	          
	          
	          for (entry in  Object.entries(label)){
	          		

	          		var tb_text = common_lookup[Object.entries(label)[entry][0]] || ''
	          		if ( tb_text.length > 249 ){
	          			tb_text = tb_text.substring(0,249) + create_generic_popup('...see full','Traceback', tb_text, 'queryTB'+ entry.toString())
	          		}

	          		
	          		$('#dataTable_queryErrors').DataTable().row.add(
					[
						tb_text,
						'#' + Object.entries(label)[entry][0],
						Object.entries(label)[entry][1][0],
						create_run_uuid_popup(Object.entries(label)[entry][1][1]),
						moment($('#errorQueryByDate').val()).format('MM-DD-YYYY')
					]).draw();

	          }
		
			}	
		$('[data-toggle="popover"]').popover();

	} )


  $('#errorQueryByID').on('input', function() {
  		$('#dataTable_queryErrors').dataTable().fnClearTable();
  		$('#errorQueryByDate').val(undefined)
		
		
		var tb_id = parseInt($('#errorQueryByID').val())
		
		var day_entries = Object.entries(error_results['daily_count'])
		
		for (var i = 0; i < day_entries.length; i++){
				var tracebacks = []

				for (var idx = 0; idx < day_entries[i][1].length; idx++){
					if (day_entries[i][1][idx].indexOf(tb_id) !== -1 ){
						
								tracebacks.push(day_entries[i][1][idx])
							}
							}
				
				if (tracebacks.length > 0 ){
				
					var label = {}
					for (var iii = 0; iii < tracebacks.length; iii++){
			            var tbid = tracebacks[iii][0]
			            var run_uuid = tracebacks[iii][1]
			            if (!(tbid in label)){
			              label[tbid] = [1,[run_uuid]]
			            } else {
			              label[tbid][0] ++
			              
			              	if (label[tbid][1].indexOf(run_uuid) === -1){
			              		label[tbid][1].push(run_uuid)
			              	}

			            } 
			          } 

	          		var tb_text = common_lookup[tb_id]
	          		if ( tb_text.length > 249 ){
	          			tb_text = tb_text.substring(0,249) + create_generic_popup('...see full','Traceback', tb_text, 'queryTB'+ entry.toString())
	          		}
	          		
	          		$('#dataTable_queryErrors').DataTable().row.add([
						tb_text,
						'#' + tb_id,
						label[tb_id][0],
						create_run_uuid_popup(label[tb_id][1]),
						moment.unix(day_entries[i][0]).format('MM-DD-YYYY')
					]).draw();
			     	     
				}
				}
		
	$('[data-toggle="popover"]').popover();	
} )
});
