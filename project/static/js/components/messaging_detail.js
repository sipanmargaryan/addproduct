$(document).ready(function () {

    var form = $('#message-form');
    var msgInput = $('#id_message');
    var messageList = $('.messages');
    var messageWrap = $('.messageWrap');
    var user = form.data('user');
    var loc = window.location;
    var wsStart = 'ws://';
    if (loc.protocol === 'https:') {
        wsStart = 'wss://';
    }
    var endpoint = wsStart + loc.host + form.data('url');
    var socket = new WebSocket(endpoint);

    scrollDown();

    socket.onmessage = (e) => {
        var messageData = JSON.parse(e.data);

        var $msgForm = $('#msg_form').clone();
        $msgForm.removeAttr('id');

        var messagePosition = messageData.sender === user ? 'leftSide' : 'rightSide';

        $msgForm.addClass(messagePosition);
        $msgForm.find('p').text(messageData.message);
        var sent_at = new Date(messageData.sent_at);
        var day = sent_at.getDate();
        day = day < 10 ? '0' + day : day;
        var month = sent_at.getMonth() + 1;
        month = month < 10 ? '0' + month : month;
        $msgForm.find('span').text(month + '.' + day + '.' + sent_at.getFullYear());
        messageList.append($msgForm);

        scrollDown();
    };

    socket.onopen = () => {
        form.submit((event) => {
            event.preventDefault();
            var message = msgInput.val();
            if (message) {
                socket.send(JSON.stringify({
                    'message': message
                }));
                form[0].reset();
            }
        })
    };

    socket.onclose = () => {
        socket.close();
    };

    function scrollDown() {
        messageWrap.scrollTop(messageWrap[0].scrollHeight);
    }

});