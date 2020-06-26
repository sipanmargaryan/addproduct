$(document).ready(function () {

  $('.js-switch-ad').on('change', function () {
    $el = $(this);
    $.ajax({
      url: $el.data('url'),
      method: 'post',
      data: {ad_id: $el.data('id')},
    }).done(function() {
      var active = $('#active-ads').prop('checked');
      var inactive = $('#inactive-ads').prop('checked');
      if (active !== inactive) {
        $('.js-ad-column-' + $el.data('id')).remove();
      }
    });
  });

  $('.js-remove-ad').on('click', function () {
    $el = $(this);
    $.ajax({
      url: $el.data('url'),
      method: 'post',
      data: {ad_id: $el.data('id')},
    }).done(function () {
      $('.js-ad-column-' + $el.data('id')).remove();
    });
  });

  $('.js-filter-my-ads').on('change', function () {
    $el = $(this);
    var active = $('#active-ads').prop('checked');
    var inactive = $('#inactive-ads').prop('checked');
    var url = $el.data('url');

    if (active !== inactive) {
      url += '?filter_by=';
      url += active ? 'active' : 'inactive';
    }

    window.location.href = url
  });

  $('.js-republish-ad').on('click', function(){
    $el = $(this);
    $.ajax({
      url: $el.data('url'),
      method: 'post',
      data: {ad_id: $el.data('id')},
    }).done(function (response) {
      $('.js-ad-column-' + $el.data('id') + '.js-date-column span').text(response.publish_date);
    });
  });

});