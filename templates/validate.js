$(document).ready(function() {
  $('.special.cards .image').dimmer({
    on: 'hover'
  });
});
function login_handler(gstin, name) {
  var header = `<i class='sign in icon'></i>
                Authentication Warning!`

  var message = "";
  message += "<p style=\"text-align:center;\">Do you want to Authenticate "+ name + " ?</p>";

  document.getElementById('confirmation_modal_header').innerHTML = header;
  document.getElementById('confirmation_modal_content').innerHTML = message;

  var success_form = `<form class="" action="" method="post">
                        <input type="hidden" name='gstin' value="${ gstin }" />
                        <div class="ui red basic cancel inverted button">
                          <i class="remove icon"></i>
                          No
                        </div>
                        <button type="submit" class="ui green ok inverted button">
                          <i class=\"sign in icon\"></i>
                          Yes
                        </button>
                      </form>`;
  //console.log(success_form);
  document.getElementById('confirmation_modal_actions').innerHTML = success_form;
  $('#confirmation_modal').modal('show');
}
