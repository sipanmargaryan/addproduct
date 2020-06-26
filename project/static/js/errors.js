var errorClassSelector = 'errorlist';

function hideErrors($form, keepElement) {
  keepElement = keepElement || false;
  if (keepElement) {
    $form.find('.' + errorClassSelector).not('.js-error-hustle').html('');
  } else {
    $form.find('.' + errorClassSelector).not('.js-error-hustle').remove('');
  }
}

function showErrors($form, errors) {
  hideErrors($form);
  $.each(errors, function (item, value) {
    $item = $('#id_' + item);
    if ($item.length) {
      var messages = [];
      for (var i = 0; i < value.length; i++) {
        messages.push('<li>' + value[i] + '</li>');
      }

      $errorContainer = $('<ul></ul>').addClass(errorClassSelector);
      $errorContainer.html(messages.join(' '));
      $errorContainer.insertAfter($item.parent('.element'));
    }
  });
}