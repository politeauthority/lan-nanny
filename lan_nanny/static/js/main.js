/* Main

*/

function register_favorite_button(favorite_selector, base_ajax_uri){
  /*
  Registers a div as favorite button, which will star or unstar an item and send an ajax request.

  */
  $( favorite_selector ).click(function(){
    $.ajax({
      url: base_ajax_uri,
      context: document.body
    }).done(function() {

      var icon = $(favorite_selector).children('i');
      console.log($(favorite_selector));
      if(icon.hasClass('fa-star-o')){
        icon.removeClass('fa').removeClass('fa-star-o');
        icon.addClass('fas').addClass('fa-star');
      } else {
        icon.removeClass('fas').removeClass('fa-star');
        icon.addClass('fa').addClass('fa-star-o');
      }
    });
  });
}

function register_toggle_ajax(base_ajax_uri, input_selector, starting_value){
  /*
  Will setup a toggle input for sending values on device change.

  */
  var field_name = input_selector.replace('#','');

  // Set the initial state of the toggle.
  if(starting_value == 'True'){
    $(input_selector).bootstrapToggle('on');
  }

  // On toggle send the data to the ajax api end point.
  $(function(){
    $( input_selector ).change(function() {
      var device_id = $(this).attr('data-entity-id');
      var data = {
          "id": device_id,
          "field_name": field_name,
          "field_value": $(this).prop('checked')
      }
      send_ajax_update(base_ajax_uri, data);
    })
  });
}

function send_ajax_update(base_ajax_uri, data){
  /*
  Creates a generic AJAX POST request to the url with the data containing the id, field_name, and
  field_value.
  @todo: return notification on success, error.

  */
  $.ajax({
    type: 'POST',
    data: data,
    url: base_ajax_uri,
    context: document.body
  }).done(function(){ });
}

function convert_str_bool(bool_str){
  /*
  Returns a javascript bool from a string bool.

  */
  if(bool_str == 'True'){
    return true;
  } else if (bool_str == 'False'){
    return false;
  } else if (bool_str == 'None'){
    return false;
  } else {
    return false;
  }
}