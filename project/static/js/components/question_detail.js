$(document).ready(function () {

    $('.js-report').on('click', function () {
        $report = $(this);
        $.ajax({
          url: $report.data('url'),
          method: 'post',
          data: {
            answer_id: $report.data('answer-id'),
          }
        }).done(function (response) {
            if(response) {
            }
        });
    });

    $('.js-reply').on('click', function () {
        var answerId = $(this).data('answer-id');
        $('#id_answer_id').val(answerId);
    });

    $('.category').on('change', function() {
        location.href = $(this).data('url');
    });

});
