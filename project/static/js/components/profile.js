$(document).ready(function () {

  $('#contact-info-form').on('submit', function (e) {
    e.preventDefault();
    $form = $(this);
    var formData = new FormData(this);
    $.ajax({
      url: $form.data('url'),
      method: 'post',
      data: formData,
      dataType: 'json',
      cache: false,
      contentType: false,
      processData: false
    }).done(function () {
      hideErrors($form);
    }).fail(function (response) {
      if (response.status === 400) {
        showErrors($form, response.responseJSON);
      }
    });
  });

  $('#change-password-form').on('submit', function (e) {
    e.preventDefault();
    $form = $(this);
    $.ajax({
      url: $form.data('url'),
      method: 'post',
      data: $form.serialize(),
      dataType: 'json',
    }).done(function () {
      $form[0].reset();
      $old_password = $form.find('#id_old_password');
      $old_password.removeAttr('readonly');
      $old_password.removeAttr('disabled');
      hideErrors($form);
    }).fail(function (response) {
      if (response.status === 400) {
        showErrors($form, response.responseJSON);
      }
    });
  });

  $('#notification-form').on('submit', function (e) {
    e.preventDefault();
    $form = $(this);
    $.ajax({
      url: $form.data('url'),
      method: 'post',
      data: $form.serialize(),
      dataType: 'json',
    }).done(function () {
      hideErrors($form);
    }).fail(function (response) {
      if (response.status === 400) {
        showErrors($form, response.responseJSON);
      }
    });
  });

  $('.js-select-avatar').on('click', function () {
    $('#id_avatar').trigger('click');
  });

  $('#id_avatar').on('change', function () {
    readURL(this, $('#avatar-preview'));
  });

  if($('.js-profile-section-value').is(':visible')) {
    $('.js-profile-section-change-password').hide();
    $('.js-profile-section-notifications').hide();
  }

  $('.js-profile-section-value').on('change', function(){
    $('.js-profile-section').hide();
    $('.js-profile-section-' + $(this).val()).show();
  });
});