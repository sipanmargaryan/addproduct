from .utils import send_email


def test_send_email(mailoutbox, monkeypatch):

    monkeypatch.setattr('core.email.utils.render_body', lambda *args, **kwargs: 'spam')

    send_email(
        subject='Test subject',
        template_name='blank.html',
        context={
            'recipient_name': 'Davit',
        },
        to='davitovmasyan@gmail.com',
    )

    assert len(mailoutbox) == 1

    email = mailoutbox[0]

    assert email.subject == 'Test subject'
    assert email.to == ['davitovmasyan@gmail.com']
    assert email.body == 'spam'
