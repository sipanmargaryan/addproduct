$(document).ready(function () {

  $('.js-remove-search').on('click', function () {
    $el = $(this);
    $.ajax({
      url: $el.data('url') + '?pk=' + $el.data('id'),
      method: 'delete'
    }).done(function () {
      $('.js-search-column-' + $el.data('id')).remove();
    });
  });

});