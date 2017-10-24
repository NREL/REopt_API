var tableParameterCell = function(name) {
  return $("<td>").append($("<span>").html(name))
}

var tableRequiredCell = function(def) {
  var text

  if ( def.hasOwnProperty("required") ) {
    if ( Boolean(def["required"]) ){
      text="Yes"
    }

  } else if (def.hasOwnProperty("depends_on") || def.hasOwnProperty("replacements")) {
      text="Depends"
  } else {
      text = "No"
  }
  return $("<td>").append($("<em>").html(text))
}

var tableValueCell = function(def) {
  var output = $("<small>")
  if ( def.hasOwnProperty("type") ) {
    var type_string = $("<span>").html(" <b class='text-primary'>Type: </b>"+def["type"])
    output.append(type_string)
  }

  if ( def.hasOwnProperty("min") ) {
    var min_string = $("<span>").html(" <br><b class='text-primary'>Min Value: </b>"+def["min"])
    output.append(min_string)
  }
  
  if ( def.hasOwnProperty("max") ) {
    var max_string = $("<span>").html(" <br><b class='text-primary'>Max Value: </b>"+def["max"])
    output.append(max_string)
  }

  if ( def.hasOwnProperty("default") ) {
    var default_string = $("<span>").html(" <br><b class='text-primary'>Default: </b>"+def["default"])
    output.append(default_string)
  }

  if ( def.hasOwnProperty("restrict_to") ) {
    var options_string = $("<span>").html(" <br><b class='text-primary'>Options:</b> <em>"+def["restrict_to"].join(', ')+"</em>")
    output.append(options_string)
  }


  return $("<td>").append($('<div>').append(output))
}

var tableDescriptionCell = function(def) {
  var text
  if ( def.hasOwnProperty("description") ) {
      text=def['description']
  } else {
    text = ""
  }

  return $("<td>").append($("<span>").html(text))
}


var buildAttributeTableRow = function(name, def,tableColumns){
  var row = $("<tr>")
  
  for (var i=0;i<tableColumns.length;i++){
    if (tableColumns[i]==='Parameter') {
      row.append(tableParameterCell(name))
    }
    else if (tableColumns[i]==='Required') {
      row.append(tableRequiredCell(def))
    }
    else if (tableColumns[i]==='Value') {
      row.append(tableValueCell(def))
    }
    else if (tableColumns[i]==='Description') {
      row.append(tableDescriptionCell(def))
    }
    else {
      row.append($('<td>'))
      alert('No cell template for ' + tableColumns[i])
    }
  }

  return row
}

var buildAttributeTableHeader = function(head, columns){
  for (var i=0;i<columns.length;i++){
      var width
      if (columns[i]==='Value'){
        width = '4%'
      } else if (columns[i]==='Description'){
        width ='8%'
      } else {
        width = '1%'
      }

      var columnName = $("<th width='"+width+"'>").html(columns[i])
      head.append(columnName)
    }
    return head
}


var sortAttributeTableRows = function (def){
  var all_keys = Object.keys(def) 
  var req_keys = []
  var dep_keys = []
  var other_keys = []

  for (var i=0;i<all_keys.length;i++){
    var req = false
    
    if ( def[all_keys[i]].hasOwnProperty("required") ) {
      if (Boolean(def[all_keys[i]]['required'])){
        req_keys.push(all_keys[i])
        req = true
      }
    }

    if ( def[all_keys[i]].hasOwnProperty("depends_on") || def[all_keys[i]].hasOwnProperty("replacements") ) {
        dep_keys.push(all_keys[i])
        req = true      
    }
    
    if (req===false){
      other_keys.push(all_keys[i])
    }
  }
  return req_keys.sort().concat(dep_keys.sort()).concat(other_keys.sort())
}

var buildAttributeTable = function(definition_dictionary) {
  var def_keys = sortAttributeTableRows(definition_dictionary)
  var attributeTable = $('<table>').prop({'class':'table table-striped row'})
  var attributeTableHead = $("<thead>")
  var attributeTableBody = $("<tbody>")

  var tableColumns = ["Parameter","Required","Value","Description"]
  
  attributeTableHead = buildAttributeTableHeader(attributeTableHead,tableColumns)
  attributeTable = attributeTable.append(attributeTableHead)

  for (var i=0;i<def_keys.length;i++){
    if (def_keys[i][0]===def_keys[i][0].toLowerCase()){
      attributeTableBody.append(buildAttributeTableRow( def_keys[i], definition_dictionary[def_keys[i]],tableColumns))
    } 
  }
  attributeTable = attributeTable.append(attributeTableBody)

  return attributeTable
}

var subDirectoriesCell = function (definition_dictionary){
  var def_keys = Object.keys(definition_dictionary)
  var subdirectories = []
  for (var i=0;i<def_keys.length;i++){
    if (def_keys[i][0]===def_keys[i][0].toUpperCase()){
      subdirectories.push($('<button type="button" data-target="#'+def_keys[i]+'_panel" class="btn btn-primary btn-sml scroll_button">').html(def_keys[i]).prop('outerHTML'))
    }
  }
  if (subdirectories.length>0){
     return subdirectories.join(' ')
       
  } else {
    return 'None'
  }
}

var objectHeaderRow = function(name){
  var output = $('<div class="panel-heading" role="tab">')
  output.append($('<h5 class="panel-title">').html(
    $('<a data-toggle="collapse" data-parent="'+name+'Row" href="#'+name+'_collapsecontainer" aria-expanded="true" aria-controls="'+name+'_collapsecontainer">').html(name))
  )
  return output
}


var buildObjectRow = function(name, definition_dictionary, indent) {
  output = $('<div class="row">')
  output_col = $('<div class="col col-xs-offset-'+indent.toString()+' col-xs-'+(12-indent).toString()+'">')
  
  var object_panel = $('<div class="panel panel-default" role="tablist" id="'+name+'_panel">')

  var objectTableNameRow = objectHeaderRow(name)
  object_panel.append(objectTableNameRow)

  var collapse_container = $('<div id="'+name+'_collapsecontainer" class="panel-collapse collapse in panel-body" role="tabpanel" aria-labelledby="'+name+'_collapsebutton">')
  
  var objectSubTableAttributeRow = $('<div class="row">')
  var attributeRowName = $('<div class="col col-xs-2">').html('<b><span class="text-secondary">Attributes</span></b>')
  objectSubTableAttributeRow.append(attributeRowName)
  collapse_container.append(objectSubTableAttributeRow)
  
  var attributeTable = buildAttributeTable(definition_dictionary)
  var attributeRowContent = $('<div class="col col-xs-10">').html(attributeTable)
  objectSubTableAttributeRow.append(attributeRowContent)
  collapse_container.append(objectSubTableAttributeRow)


  var objectSubTableSubdirectoryRow = $('<div class="row">')
  var attributeRowName = $('<div class="col col-xs-2">').html('<b><span class="text-secondary">Sub Directories</span></b>')
  objectSubTableSubdirectoryRow.append(attributeRowName)
  
  var subdirectoryRowContent= $('<div class="col col-xs-10">').html(subDirectoriesCell(definition_dictionary))
  objectSubTableSubdirectoryRow.append(subdirectoryRowContent)
  collapse_container.append(objectSubTableSubdirectoryRow)

  object_panel.append(collapse_container)
  
  object_panel.append($('<div class="row">').html("<br>"))

  output.append(output_col.html(object_panel))
  return output
}


var recursiveBuildReadTable = function(input_definitions, indent){
  
  var defKeys = Object.keys(input_definitions)
  var subdirectories = []
    
  for (var i=0;i<defKeys.length;i++){
    var key_name = defKeys[i]
    if (key_name[0]===key_name[0].toUpperCase() && key_name!= 'Wind' ){
      subdirectories.push(key_name)
    }
  }
  
  subdirectories = subdirectories.sort()

  for (var i=0;i<subdirectories.length;i++){
      var key_name = subdirectories[i]
      var next_object_defintion = input_definitions[key_name]
      defTable.append(buildObjectRow(key_name, next_object_defintion, indent))
      recursiveBuildReadTable(next_object_defintion,indent+1)   
  }
}

var defTable = $('<div class="container">')

$(document).ready(function() {
	
    recursiveBuildReadTable(nested_input_definitions,1)
    $('#definition_table').html(defTable.prop('outerHTML'))

     $('.scroll_button').on('click', function(event) {
    var target = $(this.getAttribute('data-target'));
    if( target.length ) {
        event.preventDefault();
        $('html, body').stop().animate({
            scrollTop: target.offset().top
        },1000);
    }
    });
  })