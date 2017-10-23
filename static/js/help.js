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

var objectNameCell = function (name){
  return $('<div class="row">').html('<div class="col col-xs-0.5"></div><div class="col col-xs-12 bg-primary text-white"><h4>'+name+'</h4></div>')
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
        req_keys.push(all_keys[i])
        req = true      
    }
    
    if (req===false){
      other_keys.push(all_keys[i])
    }
  }
  return req_keys.sort().concat(other_keys.sort())
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
      subdirectories.push("<b><span class='text-secondary'>"+def_keys[i]+'</span></b>')
    }
  }
  if (subdirectories.length>0){
    return subdirectories.join(', ')
  } else {
    return 'None'
  }
}

var buildObjectRow = function(name, definition_dictionary) {
  
  var object_row = $('<div class="row">')

  var objectTableNameRow = objectNameCell(name) 
  object_row.append(objectTableNameRow)

  
  var objectSubTableAttributeRow = $('<div class="row">')
  var attributeRowName = $('<div class="col col-xs-2">').html('<b><span class="text-secondary">Attributes</span></b>')
  objectSubTableAttributeRow.append(attributeRowName)
  
  var attributeTable = buildAttributeTable(definition_dictionary)
  var attributeRowContent = $('<div class="col col-xs-10">').html(attributeTable)
  objectSubTableAttributeRow.append(attributeRowContent)
  object_row.append(objectSubTableAttributeRow)


  var objectSubTableSubdirectoryRow = $('<div class="row">')
  var attributeRowName = $('<div class="col col-xs-2">').html('<b><span class="text-secondary">Sub Directories</span></b>')
  objectSubTableSubdirectoryRow.append(attributeRowName)
  
  var subdirectoryRowContent= $('<div class="col col-xs-10">').html(subDirectoriesCell(definition_dictionary))
  objectSubTableSubdirectoryRow.append(subdirectoryRowContent)
  object_row.append(objectSubTableSubdirectoryRow)

  object_row.append($('<div class="row">').html("<br>"))
  
  return object_row
}


var recursiveBuildReadTable = function(input_definitions){
  
  var defKeys = Object.keys(input_definitions)
  
  for (var i=0;i<defKeys.length;i++){

    var key_name = defKeys[i]
    
    if (key_name[0]===key_name[0].toUpperCase()){
      var next_object_defintion = input_definitions[key_name]
      defTable.append(buildObjectRow(key_name, next_object_defintion))
      recursiveBuildReadTable(next_object_defintion)
    }  
  }
}

var defTable = $('<div class="container">')

$(document).ready(function() {
	
    recursiveBuildReadTable(nested_input_definitions)
    $('#definition_table').html(defTable.prop('outerHTML'))
  })