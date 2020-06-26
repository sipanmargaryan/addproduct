$(document).ready(function () {
  $('#arabic').click(function () {
    $('body').addClass('rtl');
  });
  $('#eng').click(function () {
    $('body').removeClass('rtl');
  });
  $('.openDrop').click(function () {
    $('.dropdownWrap').css('display', 'none');
    $(this).find('.dropdownWrap').css('display', 'block');
  });
  $(document).click(function (event) {
    if (!$(event.target).closest('.openDrop').length) {
      $('.dropdownWrap').css('display', 'none');
    }
  });
  $('.js-select2').select2({
    minimumResultsForSearch: -1
  });
  $('.js-switch-menu').on('click', function () {
    $(this).toggleClass('opened');
  });
  $('.listBlock').click(function () {
    var visible = true;
    if ($(this).find('.footerMenuList').is(':hidden')) {
      visible = false;
    }
    $('.footerMenuList').hide();
    visible ? $(this).find('.footerMenuList').hide() : $(this).find('.footerMenuList').show();
  });
  $('.mobileElementWrap').slick({
    centerMode: true,
    slidesToShow: 1,
    dots: true
  });
  $('.js-top-side').on('click', function (e) {
    if (!$(event.target).hasClass('iconsWrap')) {
      e.preventDefault();
    }
  });
});

function csrfSafeMethod(method) {
  // these HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
  beforeSend: function (xhr, settings) {
    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
      xhr.setRequestHeader("X-CSRFToken", csrftoken);
    }
  }
});

function readURL(input, preview) {

  if (input.files && input.files[0]) {
    var reader = new FileReader();

    reader.onload = function (e) {
      preview.removeAttr('hidden');
      preview.attr('src', e.target.result);
    };

    reader.readAsDataURL(input.files[0]);
  }
}

function getUrlParams() {
  var params = {};
  window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function (m, key, value) {
    if (params[key]) {
      params[key] += ',' + value;
    } else {
      params[key] = value;
    }
  });

  return params;
}