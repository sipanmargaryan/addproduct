$(document).ready(function () {

  $('.js-toggle-favorite').on('click', function (e) {
    e.preventDefault();
    $btn = $(this);
    var ad_id = $btn.data('id');
    $.ajax({
      url: $btn.data('url'),
      method: 'post',
      data: {ad_id: ad_id},
      dataType: 'json',
    }).done(function () {
      $('.js-ad-column-' + ad_id).remove();
    });
  });

});