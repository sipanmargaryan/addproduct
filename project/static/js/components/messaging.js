$(document).ready(function () {

  $('.block-thread').on('click', function () {
    $icon = $(this);
    var thread_id = $icon.data('id');
    $.ajax({
      url: $icon.data('url'),
      method: 'post',
      data: {thread_id: thread_id},
      dataType: 'json',
    }).done(function () {
      $icon.remove();
    });
  });

});