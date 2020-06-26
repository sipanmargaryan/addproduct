var loadingContainerId = 'loading-container';
var loadingMessageId = 'loading-message';

function loading(message) {
  $('#' + loadingContainerId).show();
  $('#' + loadingMessageId).html(message);
}

function loaded() {
  $('#' + loadingContainerId).hide();
  $('#' + loadingMessageId).html('');
}