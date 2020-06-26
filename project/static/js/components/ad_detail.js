$(document).ready(function () {
  $('.js-select-image').on('click', function () {
    $('.js-main-image').attr('src', $(this).data('url'));
  });

  $("#share").jsSocials({
    showLabel: false,
    showCount: false,
    shares: [
      'facebook', 'twitter',
      'pinterest', 'copylink',
    ]
  });

  $(document).on('click', '.jssocials-share-copylink a', function (e) {
    e.preventDefault();
    var copyText = document.getElementById('js-current-url');
    copyText.select();
    document.execCommand('copy');
  });

  $(document).on('click', '.js-detail-favorite-btn', function () {
    $signIn = $('#header-signin');
    if ($signIn.length) {
      window.location = $signIn.attr('href');
    } else {
      $btn = $(this);
      $.ajax({
        url: $btn.data('favorite-url'),
        data: {ad_id: $btn.data('ad-id')},
        type: 'POST',
        dataType: 'json',
      }).done(function () {
        $btn.find('.icon').toggleClass('favorite').toggleClass('empty');
      });
    }
  });

  if($('.recommendations .hotSaleElement').length) {
    $('.recommendations').slick({
      slidesToShow: 3,
      slidesToScroll: 1,
      dots: false,
      centerMode: true,
      focusOnSelect: false,
      prevArrow: $('.eventsPrev'),
      nextArrow: $('.eventsNext')
    });
  }

  $('#send-comment-form').on('submit', function (e) {
    $textBox = $('#ad-comment');
    if(!$textBox.val()) {
      $textBox.focus();
      e.preventDefault();
    } else {
      loading();
    }
  });
});