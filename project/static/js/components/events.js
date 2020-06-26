$(document).ready(function(){
  $('.js-event-category').on('change', function(){
    $btn = $('.js-show-more').data('page', 1);
    $('.js-events-container').html('');
    getEvents();
  });
  $('.js-event-city').on('change', function(){
    $btn = $('.js-show-more').data('page', 1);
    $('.js-events-container').html('');
    getEvents();
  });
  $('.js-event-search').on('keyup', function(e){
    if (e.keyCode === 13) {
      $btn = $('.js-show-more').data('page', 1);
      $('.js-events-container').html('');
      getEvents();
    }
  });
  $('.js-event-sort').on('change', function(){
    $btn = $('.js-show-more').data('page', 1);
    $('.js-events-container').html('');
    getEvents();
  });

  $(document).on('click', '.js-show-more', function(e){
    e.preventDefault();
    getEvents();
  });

  function getEvents() {
    $btn = $('.js-show-more');
    loading();
    $.ajax({
      url: $('.js-events-container').data('url'),
      data: {
        page: $btn.data('page'),
        filter_by: $btn.data('filter'),
        category: $('.js-event-category').val(),
        city: $('.js-event-city').val(),
        q: $('.js-event-search').val(),
        sort_by: $('.js-event-sort').val(),
      }
    }).done(function (response) {
        if(response) {
          $('.js-events-container').append(response);
          $next = $('.js-events-container .js-event-next-page');
          if($next.length) {
            $btn.data('page', $next.data('page'));
            $btn.show();
            $next.remove();
          } else {
            $btn.hide();
          }
        }
    }).always(function(){
      loaded();
    });
  }
});