/* Main

*/

function register_favorite_button(favorite_selector, load_state, base_ajax_uri){
  /*
  Registers a div as favorite button, which will star or unstar an item and send an ajax request.

  */
  var icon = $(favorite_selector).children('i');

  if(load_state){

    icon.addClass('fas').addClass('fa-star');
  } else {
    icon.addClass('fa').addClass('fa-star-o');
  }

  $( favorite_selector ).click(function(){
    $.ajax({
      url: base_ajax_uri,
      context: document.body,
      success: function(){
        if(icon.hasClass('fa-star-o')){
          create_toast('success', 'Device', 'Favorited device', false);
          icon.removeClass('fa').removeClass('fa-star-o');
          icon.addClass('fas').addClass('fa-star');
        } else {
          create_toast('success', 'Device', 'Unfavorited device', false);
          icon.removeClass('fas').removeClass('fa-star');
          icon.addClass('fa').addClass('fa-star-o');
        }
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
  if(starting_value){
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
    context: document.body, 
    success: function(){
      create_toast('success', 'Saved', 'Successfully saved.', false);
    }
  });
}


function register_toggle_form(setting_name, setting_value){
  /*
  Sets up bootstrap 4 toggle for form submission.
  requires the form to have a hidden #form div
  */

  var toggle_id = '#' + setting_name;
  var toggle = $(toggle_id);
  var form_input_id = 'manage_' + setting_name;
  $('#hidden_forms').append('<input id="' + form_input_id + '" type="hidden" name="' + setting_name + '">');
  var form_obj = $('#' + form_input_id);
  if(setting_value == true){
    toggle.bootstrapToggle('on');
    form_obj.val('true');
  } else {
    form_obj.val('false');
  }
  $( toggle_id ).change(function(){
    if(form_obj.val() == 'false'){
      form_obj.val('true');
    } else {
      form_obj.val('false');
    }
  });
}


function convert_str_bool(bool_str){
  /*
  Returns a javascript bool from a string bool.

  */
  if(bool_str == 'True'){
    return true;
  } else if (bool_str == '1'){
    return true;
  } else if (bool_str == 'False'){
    return false;
  } else if (bool_str == '0'){
    return false;
  } else if (bool_str == 'None'){
    return false;
  } else if (bool_str == 'NULL'){
    return false;
  } else {
    return false;
  }
}


function create_toast(level, title, message, persist=true){
  /*
  Creates a toast via javascript.

  */
  var toast_html =`<div class="toast_template toast hidden" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
              <strong class="mr-auto">Title</strong>
              <button type="button" class="ml-2 mb-1 close" data-dismiss="toast" aria-label="Close">
                <span aria-hidden="true">&times;</span>
              </button>
            </div>
            <div class="toast-body">This is a toast template to be copied</div>
          </div>`;

  $('#toasts').append(toast_html);
  new_toast = $('.toast_template');
  if(persist){
    new_toast.attr("data-autohide", false);
  }
  new_toast.removeClass('toast_template').removeClass('not-toast').removeClass('hidden');
  new_toast.find('.toast-body').html(message);
  new_toast.find('.mr-auto').html(title);
  $('.toast').toast({
    delay: 5000
  });
  new_toast.toast('show');
}


/* Global setup for page loads */
$(document).ready(function(){

  // Show Toasts on page load.
  $('.toast').toast({
    delay: 5000
  });
  $('.toast').toast('show');

  $('.time_switch').css({'cursor': 'pointer'});
  $('.time_switch').hover(function(){
    var icon = $(this).find('i');
    icon.addClass('icon_hover_over');
  });
  $('.time_switch').mouseout(function(){
    var icon = $(this).find('i');
    icon.removeClass('icon_hover_over');
  });
  $('.time_switch').click(function(){
    var time_box = $(this);
    time_box.find('span').each(function( index ) {
      if ($(this).hasClass('hidden')){
        $(this).removeClass('hidden');
      } else {
        $(this).addClass('hidden');
      }
    });
  });
});

