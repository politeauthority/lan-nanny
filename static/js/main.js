function register_favorite_button(favorite_selector, base_ajax_uri){
  /*
  Registers a div as favorite button, which will star or unstar an item and send an ajax request.

  */
  $( device_selector ).click(function(){
    $.ajax({
      url: uri + device_id,
      context: document.body
    }).done(function() {

      var icon = $(this).find('i');
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


function register_toggle_ajax(input_selector, starting_value, base_ajax_uri){
  // Set initial device states
  if(starting_value == 'True'){
    $(input_selector).bootstrapToggle('on');
  }

  $(function(){
    $(input_selector).change(function() {
      update_alert('online', $(this).prop('checked'));
    })
  });
}

function convert_str_bool(bool_str){
  /*
  Returns a javascript bool from a string bool.

  */
  if(bool_str == 'True'){
    return true;
  } else if (bool_str == 'None'){
    return false;
  } else {
    return false;
  }
}