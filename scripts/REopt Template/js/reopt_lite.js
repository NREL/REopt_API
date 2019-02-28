(function($) {
  "use strict"; // Start of use strict
	
	function numberWithCommas(x) {
	    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
	}
	
  	$("#totalRequests").html(numberWithCommas(bad_posts['count_all_posts']))
	var goodPosts = (100-(bad_posts['count_bad_posts'] *100 / bad_posts['count_all_posts'])).toFixed(1)
	$("#pctCorrectlyFormatted").html(goodPosts + '%')
	// $('$progressbar_CorrectlyFormatted').attr({'valuenow':goodPosts})
	$("#recentErrors").html(numberWithCommas(error_results['count_new']))
	$("#uniqueURDB").html(numberWithCommas(Object.keys(urdb_results).length - 8))

	function format_names(names){
		if (names!==undefined) {
		var obj = Object.entries(names) 		
		var list = $('<ul>')
		for (var entry in Object.entries(obj)){
				var key = obj[entry][0]
				var value = obj[entry][1]
				
				var detail = $("<li>")
				detail.html(key + " (" + value['count'] + ") " + create_urdb_popup(value['run_uuids_new'],value['run_uuids_old'],"Recent").html())
				list.append(detail)

			}
		}
		
		return list
	}

	function create_urdb_popup(recent_uuids, older_uuids,text){
		if (older_uuids===undefined){older_uuids={}}
		if (recent_uuids===undefined){recent_uuids={}}
		var base = $('<div class="dropdown-menu dropdown-menu-right shadow animated--fade-in" style="height:'+Math.min((39+(30*(recent_uuids.length + older_uuids.length))),150)+'px;overflow:auto;" aria-labelledby="dropdownMenuLink"><div class="dropdown-header">'+text+ ' Run UUID\'s</div></div>')

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
		var result = $('<div class="dropdown no-arrow"></div>')
		result.append($('<a class="dropdown-toggle" href="#" role="button" id="dropdownMenuLink" data-toggle="dropdown" aria-haspopup="true" ></a>') )
        result.append(base)
		return result
	}

	var urdb_entries = Object.entries(urdb_results)

	for (var entry in urdb_entries){
		if (urdb_entries[entry][0].substring(0,5).toLocaleLowerCase() != 'count' && urdb_entries[entry][0].substring(0,4).toLocaleLowerCase() != 'most') {	
			      
				var detail= $('<tr>')
				
				detail.append($('<td>').html(urdb_entries[entry][0]) ) 
				detail.append($('<td>').html(urdb_entries[entry][1]['count_total']))

				detail.append($('<td>').html(urdb_entries[entry][1]['count_new']))

				var most_recent = urdb_entries[entry][1]['most_recent']
				if (most_recent===0 || most_recent===undefined){
					detail.append($('<td>').html(''))	
				}else{
					detail.append($('<td>').html(moment.unix(most_recent).format("MM-DD-YYYY HH:mm:ss")))
				}
				
				
				detail.append($('<td>').html((urdb_entries[entry][1]['count_errors']*100/(urdb_entries[entry][1]['count_total'])).toFixed(0)))	

				

				
				
				
				 
				
				detail.append($('<td>').html(format_names(urdb_entries[entry][1]['name']) ) )

				$('#tableBody_URDB').append(detail)			          
		}

	}

	var error_entries = Object.entries(error_results['traceback'])

	for (var entry in error_entries){
		
		if (error_entries[entry][0].substring(0,5).toLocaleLowerCase() != 'count' && error_entries[entry][0].substring(0,4).toLocaleLowerCase() != 'most') {	
				var detail= $('<tr>')
				
				detail.append($('<td>').html(common_lookup[error_entries[entry][0]].substring(0,200)))
				detail.append($('<td>').html(create_urdb_popup(error_entries[entry][1]['run_uuids_new'],error_entries[entry][1]['run_uuids_old'],"Recent").html()))
				detail.append($('<td>').html(moment.unix(error_entries[entry][1]['most_recent']).format("MM-DD-YYYY HH:mm:ss")))
				detail.append($('<td>').html(error_entries[entry][1]['count'] ))

				$('#tableBody_Errors').append(detail)			          
		}

	}

	var bad_posts_entries = Object.entries(bad_posts) 
	for (var entry in bad_posts_entries){
		if (bad_posts_entries[entry][0].substring(0,5).toLocaleLowerCase() != 'count' && bad_posts_entries[entry][0].substring(0,4).toLocaleLowerCase() != 'most') {
				var detail= $('<tr>')
				
				detail.append($('<td>').html(bad_posts_entries[entry][0] ))
				detail.append($('<td>').html(create_urdb_popup(bad_posts_entries[entry][1]['run_uuids'],[],"").html()))
				detail.append($('<td>').html(bad_posts_entries[entry][1]['count'] ))
				
				$('#tableBody_BadPost').append(detail)			          
		}

	}
	

})(jQuery); // End of use strict
