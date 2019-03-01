(function($) {
  "use strict"; // Start of use strict
	
	function numberWithCommas(x) {
	    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
	}
	
  	$("#totalRequests").html(numberWithCommas(summary_info['count_all_posts']))
	var goodPosts = (100-(summary_info['count_bad_posts'] *100 / summary_info['count_all_posts'])).toFixed(1)
	$("#pctCorrectlyFormatted").html(goodPosts + '%')
	// $('$progressbar_CorrectlyFormatted').attr({'valuenow':goodPosts})
	$("#recentErrors").html(numberWithCommas(error_results['count_new_errors']))
	$("#uniqueURDB").html(numberWithCommas(Object.keys(urdb_results).length - 8))

	function format_names(names){
		if (names!==undefined) {
		var obj = Object.entries(names) 		
		var list = $('<ul>')
		for (var entry in Object.entries(obj)){
				var key = obj[entry][0]
				var value = obj[entry][1]
				var detail = $("<li>")
				detail.html(key + " (" + value['count'] + ") " + create_run_uuid_popup(value['run_uuids_new'],value['run_uuids_old'],"Recent").html(),key+"nameRunUUIDPopUp"+entry.toString())
				list.append(detail)
			}
		}
		return list
	}

	function create_run_uuid_popup(recent_uuids, older_uuids,text,id){
		if (older_uuids===undefined){older_uuids={}}
		if (recent_uuids===undefined){recent_uuids={}}
		var base = $('<div class="dropdown-menu dropdown-menu-right shadow animated--fade-in" style="height:'+Math.min((39+(30*(recent_uuids.length + older_uuids.length))),150)+'px;overflow:auto;" aria-labelledby="'+ id+'"><div class="dropdown-header">'+text+ ' Run UUID\'s</div></div>')
		for (var i = 0; i < recent_uuids.length; i++){
			var uuid = $('<span class="dropdown-item" href="#"></span>')
			uuid.html(recent_uuids[i])
			base.append(uuid)
		}
		if (older_uuids.length > 0 ) {
			base.append($('<div class="dropdown-divider"></div>'))
			base.append($('<div class="dropdown-header">Other Run UUID\'s</div>'))
			for (var i = 0; i < older_uuids.length; i++){
						var uuid = $('<span class="dropdown-item" href="#"></span>')
						uuid.html(older_uuids[i])
						base.append(uuid)
					}
		}
		var result = $('<div class="dropdown arrow"></div>')
		result.append($('<a class="dropdown-toggle" href="#" role="button" id="'+id+'" data-toggle="dropdown" aria-haspopup="true" ></a>') )
        result.append(base)
		return result
	}


	function create_generic_popup(link_text,header, text, id){
		
		return '<br><span title="'+header+'" class="text-info" data-toggle="popover"  data-content="'+text.replace(/"/g, '\'')+'" style="margin:20px;">'+link_text+'</span>'
	}
	
	
	
	var urdb_entries = Object.entries(urdb_results)

	for (var entry in urdb_entries){
		if (urdb_entries[entry][0].substring(0,5).toLocaleLowerCase() != 'count' && urdb_entries[entry][0].substring(0,4).toLocaleLowerCase() != 'most') {	
			    debugger
				var detail= $('<tr>')
				detail.append($('<td>').append($('<span>').html(urdb_entries[entry][0])).append($('<br><span>Look Up @ </span>')).append($('<a target="blank" href="https://openei.org/apps/USURDB/rate/view/'+urdb_entries[entry][0]+'"><small>USURDB </small></a>"') ).append($('<span> or </span>')).append($('<a target="blank" href="https://openei.org/apps/IURDB/rate/view/'+urdb_entries[entry][0]+'"><small>IURDB </small></a>"') ))
				detail.append($('<td>').html(urdb_entries[entry][1]['count_total_uses']))
				detail.append($('<td>').html(urdb_entries[entry][1]['count_total_errors']))
				var most_recent = urdb_entries[entry][1]['most_recent_error']
				if (most_recent===0 || most_recent===undefined){
					detail.append($('<td>').html(''))	
				} else {
					detail.append($('<td>').html(moment.unix(most_recent).format("MM-DD-YYYY HH:mm:ss")))
				}
				detail.append($('<td>').html((urdb_entries[entry][1]['count_unique_error_run_uuids']*100/(urdb_entries[entry][1]['count_total_uses'])).toFixed(0)))	
				detail.append($('<td>').html(format_names(urdb_entries[entry][1]['name']) ) )
				$('#tableBody_URDB').append(detail)			          
		}

	}

	var error_entries = Object.entries(error_results['traceback'])

	for (var entry in error_entries){
		
		if (error_entries[entry][0].substring(0,5).toLocaleLowerCase() != 'count' && error_entries[entry][0].substring(0,4).toLocaleLowerCase() != 'most') {	
				var errordetail= $('<tr>')
				var errorcontent = $('<div>')
				errorcontent.html(common_lookup[error_entries[entry][0]].substring(0,189))
				if (common_lookup[error_entries[entry][0]].length > 189){
					errorcontent.append(create_generic_popup('...(see full)', 'Traceback', common_lookup[error_entries[entry][0]],"errorPopUp"+entry.toString()))
				}
				errordetail.append($('<td>').html(errorcontent))
				errordetail.append($('<td>').html(create_run_uuid_popup(error_entries[entry][1]['run_uuids_new'],error_entries[entry][1]['run_uuids_old'],"Recent").html(),"errorRunUUIDPopUp"+entry.toString()))
				errordetail.append($('<td>').html(moment.unix(error_entries[entry][1]['most_recent_error']).format("MM-DD-YYYY HH:mm:ss")))
				errordetail.append($('<td>').html(error_entries[entry][1]['count'] ))
				$('#tableBody_Errors').append(errordetail)			          
		}

	}

	
	var bad_posts_entries = Object.entries(bad_posts) 
	for (var entry in bad_posts_entries){
		if (bad_posts_entries[entry][0].substring(0,5).toLocaleLowerCase() != 'count' && bad_posts_entries[entry][0].substring(0,4).toLocaleLowerCase() != 'most') {
				var badPostdetail= $('<tr>')
				var badPostcontent = $('<div>')
				badPostcontent.html(bad_posts_entries[entry][0].substring(0,189))
				if (bad_posts_entries[entry][0].length > 189){
					
					badPostcontent.append(create_generic_popup('...(see full)', 'Error', bad_posts_entries[entry][0],"badPostPopUp"+entry.toString()))
				}
				badPostdetail.append($('<td>').html(badPostcontent))
				badPostdetail.append($('<td>').html(create_run_uuid_popup(bad_posts_entries[entry][1]['run_uuids'],[],"").html(),"badPostRunUUIDPopUp"+entry.toString()))
				badPostdetail.append($('<td>').html(bad_posts_entries[entry][1]['count'] ))
				$('#tableBody_BadPost').append(badPostdetail)			       
		}

	}
})(jQuery); // End of use strict
