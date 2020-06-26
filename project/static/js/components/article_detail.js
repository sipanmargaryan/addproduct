$(document).ready(function () {

  $("#share").jsSocials({
    showLabel: false,
    showCount: false,
    shares: [
      'facebook', 'twitter', 'pinterest', 'whatsapp'
    ]
  });


  $('.js-show-more-posts').on('click', function(e){
    e.preventDefault();
    $btn = $(this);

    $.ajax({
      url: $btn.data('url'),
      data: {
        page: $btn.data('page'),
      }
    }).done(function (response) {
        if(response) {
          $('.js-recent-posts').append(response);
          $next = $('.js-recent-posts .js-blog-next-page');
          if($next.length) {
            $btn.data('page', $next.data('page'));
            $btn.show();
            $next.remove();
          } else {
            $btn.hide();
          }
        }
    });
  });

  $('.js-article-comment').on('keyup', function (e) {
    $input = $(this);
    var comment = $input.val().trim();
    if (e.keyCode === 13 && comment) {
      $('.js-comment-description').val(comment);
      loading();
      $('#comment-form').submit();
    }
  });

});