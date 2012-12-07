$(document).ready(function() {

  // Use bootstrap classes for add portlet dropdown
  $('#gwportletselector a').bind('click', function(event) {
    event.preventDefault();
    event.stopPropagation();
    $a = $(event.target);
    $form = $('#portletselectorform');
    $form.find('input[name=":action"]').val($a.attr('href'));
    $form.submit();
  });

  // Call the ws that stores the span value given a portletManager
  $('.editable').bind('change', function(event) {
    // event.preventDefault()
    // event.stopPropagation()
    data = {'manager': $(this).data()['manager'],
            'contextId': $(this).data()['contextId'],
            'span': $(this).val()};
    $.ajax({
      url: portal_url + "/@@set-portlethomemanager-span",
      data: data,
      type: 'POST',
      success: function(data){
          alertify.success("Configuració guardada.");
      },
      error: function(){
          alertify.error("Error al guardar la configuració.");
      }
    });
  });
});
