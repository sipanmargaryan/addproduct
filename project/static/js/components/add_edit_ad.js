$(document).ready(function () {

  var carMake = $('.js-cars-container').data('make');
  var carModel = $('.js-cars-container').data('model');

  if (carMake) {
    $('.js-cars-make').data('locked', '1').val(carMake).data('locked', '');
  }

  var mobileBrand = $('.js-mobile-container').data('brand');
  var mobileModel = $('.js-mobile-container').data('model');

  if (mobileBrand) {
    $('.js-mobile-brand').data('locked', '1').val(mobileBrand).data('locked', '');
  }

  var estatePurpose = $('.js-real-estate-container').data('purpose');
  // default is for_sell
  if(estatePurpose === 'for_rent') {
    $('.js-real-estate-container input#rental').prop('checked', true);
  }

  if (mobileBrand) {
    $('.js-mobile-brand').data('locked', '1').val(mobileBrand).data('locked', '');
  }

  var initialCategory = $('#id_category').parent('div').data('initial');
  if (initialCategory) {
    $('#id_category').data('locked', '1').val(initialCategory).data('locked', '').trigger('change.select2');
  }
  var categoryName = getCategoryName();
  getSubCategories();

  calculatePrice();

  $('#id_category').on('change', function () {
    if($(this).data('locked') !== '1') {
      categoryName = getCategoryName();
      getSubCategories();
    }
  });

  $('.js-ad-image-file').on('change', function () {
    var imageWrap = '<div class="imgWrap"><img /></div>';
    $parent = $(this).parent('.element');
    $parent.remove('.imgWrap');
    $parent.append(imageWrap);
    readURL(this, $parent.find('.imgWrap img'));
    $('#ad-image-required').hide();
  });

  $(document).on('click', '.imgWrap', function () {
    $parent = $(this).parent('.element');
    $(this).remove();
    $parent.find('input[type="file"]').val(null);
  });

  $('.js-submit-ad').on('click', function () {
    $('.errorlist').hide();

    var images = [];
    var existingImages = $('.js-existing-image');
    var formData = new FormData();

    $('input[type="file"]').map(function (index, input) {
      if (input.value) {
        images.push(input.files[0])
      }
    });

    if ($('.js-premium-package').is(':checked')) {
      var premiumDays = $('.js-day').val();
      formData.append('premium_days', premiumDays);
    }

    if (!images.length && !existingImages.length) {
      $('#ad-image-required').show();
    } else {
      $('input[type="file"]').map(function (index, input) {
        if (input.value) {
          formData.append('image-' + index, input.files[0], input.files[0].name);
        } else {
          var img = $(input).parent('.element').find('img');
          if (img.length) {
            formData.append('image-' + index, img.data('id'));
          }
        }
      });

      $.each(
        $('.js-ads-container').find('input[id^="id_"], select[id^="id_"], textarea[id^="id_"]'),
        function (index, input) {
          var name = input.getAttribute('name');
          if (name === 'state' && !$(input).prop('checked')) {
            return true;
          }
          formData.append(name, input.value);
        }
      );

      if (categoryName.toLowerCase() === 'cars') {
        formData.append('make', $('.js-cars-make').val());
        formData.append('model', $('.js-cars-models').val());
        formData.append('mileage', $('#id_mileage').val());
        formData.append('year', $('#id_year').val());
        formData.append('body_style', $('#id_body_style').val());
      } else if (categoryName.toLowerCase() === 'mobile') {
        formData.append('brand', $('.js-mobile-brand').val());
        formData.append('model', $('.js-mobile-models').val());
      } else if (categoryName.toLowerCase() === 'real estate') {
        formData.append('estate_type', $('#id_estate_type').val());
        formData.append('bedrooms', $('#id_bedrooms').val());
        formData.append('bathrooms', $('#id_bathrooms').val());
        if ($('.js-real-estate-container input[name="purpose"]').prop('checked')) {
          formData.append('purpose', 'for_sell');
        } else {
          formData.append('purpose', 'for_rent');
        }
      }

      saveAd(formData, $(this).data('url'));
    }
  });

  $(document).on('change', '.js-cars-make, .js-mobile-brand', function(){
    if($(this).data('locked') !== '1') {
      categoryName = getCategoryName();
      getSubCategories();
    }
  });

  $('.js-day').on('change', function(){
    calculatePrice();
  });

  function saveAd(formData, url) {
    loading();
    hideErrors($('.js-ads-container'), true);
    $.ajax({
      url: url,
      method: 'POST',
      data: formData,
      processData: false,
      contentType: false,
    }).done(function (response) {
      window.location = response.next_url;
    }).fail(function (response) {
      if (response.status === 400) {
        showAdErrors($('.js-ads-container'), response.responseJSON);
      }
    }).always(function () {
      loaded();
    });
  }

  function showAdErrors($form, errors) {
    hideErrors($form, true);
    $.each(errors, function (item, value) {
      $item = $('#id_' + item);
      if ($item.length) {
        var messages = [];
        for (var i = 0; i < value.length; i++) {
          messages.push('<li>' + value[i] + '</li>');
        }
        $item.next('.errorlist').show().html(messages.join(' '));
      }
    });
  }

  function getCategoryName() {
    return $('#id_category option[value="' + $('#id_category').val() + '"]').text();
  }

  function getSubCategories() {
    $('.js-first-row .rightSide>div').removeClass('active');
    var carFields = $('.js-cars-extra-fields');
    var estateFields = $('.js-estate-extra-fields');
    carFields.hide();
    estateFields.hide();
    var activeContainer = null;
    if (categoryName.toLowerCase() === 'cars') {
      activeContainer = $('.js-cars-container');
      carFields.show();
      getCarModels(activeContainer.data('model-url') + '?make=' + $('.js-cars-make').val());
    } else if (categoryName.toLowerCase() === 'mobile') {
      activeContainer = $('.js-mobile-container');
      getMobileModels(activeContainer.data('model-url') + '?brand=' + $('.js-mobile-brand').val());
    } else if (categoryName.toLowerCase() === 'real estate') {
      activeContainer = $('.js-real-estate-container');
      estateFields.show();
    }

    if (activeContainer) {
      activeContainer.children('div').addClass('active');
    }

    select2Init();
  }

  function select2Init() {
    $('.js-select2-sub').select2({
      minimumResultsForSearch: -1
    });
  }

  function getMobileModels(url) {
    $.ajax({
      url: url,
    }).done(function (response) {
      $('.js-mobile-models').select2('destroy');
      var options = '';
      $.each(response.models, function(i, model){
        options += '<option value="'+ model.pk +'">' + model.name + '</option>';
      });
      $('.js-mobile-models').html(options);
      if(mobileModel) {
        $('.js-mobile-models').val(mobileModel);
        mobileModel = null;
      }
      select2Init();
    }).always(function () {
      loaded();
    });
  }

  function getCarModels(url) {
    $.ajax({
      url: url,
    }).done(function (response) {
      $('.js-cars-models').select2('destroy');
      var options = '';
      $.each(response.models, function(i, model){
        options += '<option value="'+ model.pk +'">' + model.name + '</option>';
      });
      $('.js-cars-models').html(options);
      if(carModel) {
        $('.js-cars-models').val(carModel);
        carModel = null;
      }
      select2Init();
    }).always(function () {
      loaded();
    });
  }

  function calculatePrice() {
    $('#price').text($('#price').data('day') * $('.js-day').val() + ' KWD');
  }

});