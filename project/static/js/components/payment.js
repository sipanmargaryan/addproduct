$(document).ready(function () {

  var cardNumber = $('#id_number');
  var cvv = $("#id_cvc");
  var breadcrumb = $('.js-breadcrumb');

  cardNumber.payform('formatCardNumber');
  cvv.payform('formatCardCVC');


  $('#paypal-button').on('click', function () {
    $('#paypal-form').submit();
    loading();
  });

  $('#creditCard-button').on('click', function (e) {
    e.preventDefault();
    var isCardValid = $.payform.validateCardNumber(cardNumber.val());
    var isCvvValid = $.payform.validateCardCVC(cvv.val());

    if (isCardValid && isCvvValid) {
      var $button = $(this);
      $form = $('#creditCard-payment-form');
      var paymentId = $button.data('payment-id');
      var number = cardNumber.val().replace(/\s/g, '');
      var card_cvv = cvv.val();
      var expMonth = $('#id_exp_month').val();
      var expYear = $('#id_exp_year').val();
      loading();
      $.ajax({
        url: $button.data('card-url'),
        method: 'post',
        data: {
          payment_id: paymentId,
          number: number,
          exp_month: expMonth,
          exp_year: expYear,
          cvc: card_cvv,
        },
        dataType: 'json',
      }).done(function (response) {
        location.href = response['url'];
        $form[0].reset();
        hideErrors($form);
      }).fail(function (response) {
        if (response.status === 400) {
          showErrors($form, response.responseJSON);
        }
      }).always(function () {
        loaded();
      });
    }
  });

  $('#knet-button').on('click', function () {
    var $button = $(this);
    var paymentId = $button.data('payment-id');
    $('.loading-popup').show();
    loading();
    $.ajax({
      url: $button.data('knet-url'),
      method: 'post',
      data: {
        payment_id: paymentId,
      },
      dataType: 'json',
    }).done(function (response) {
      location.href = response['url'];
    }).always(function () {
      loaded();
    });
  });

  breadcrumb.on('click', function () {
    var activeClass = 'active';
    var component = $(this).data('component');
    breadcrumb.removeClass(activeClass);
    $(this).addClass(activeClass);
    $('.js-component').attr('hidden', true);
    $('.js-' + component).removeAttr('hidden');
  });
});