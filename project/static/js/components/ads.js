$(document).ready(function () {

  $('#showFilter a').click(function (e) {
    e.preventDefault();
    $('#js-filter-ads').css('top', '0');
    $('body').css('overflow', 'hidden');
  });

  var filterForm = $('#filter-form');

  function getUrl() {
    var selectedCategories = $('input[name=category]', filterForm).serializeArray();
    var url = '?' + $('input[name!=category], select', filterForm).serialize();
    var categoryPath = '&category=';
    if (selectedCategories.length > 0) {
      $.each(selectedCategories, function (index, item) {
        categoryPath += item.value + ',';
      });
      categoryPath = categoryPath.replace(/,\s*$/, "");
      url += categoryPath;
    }
    return url;
  }

  filterForm.on('submit', function (e) {
    e.preventDefault();
    location.href = getUrl();
  });

  $('.js-sort-by').on('change', function (e) {
    var sortBy = $(this).val();
    location.href = getUrl() + '&sort=' + sortBy;
  });

  function setFilterData() {
    var url = window.location.href;
    decodeURI(url).replace(/[?&]+([^=&]+)=([^&]*)/gi, function (m, key, value) {
      if (['seller_type', 'status'].indexOf(key) !== -1) {
        $('input:radio[name=' + key + ']').filter('[value=' + value + ']').attr('checked', true);
      } else if (['category'].indexOf(key) !== -1) {
        var paramList = value.split(',');
        $.each(paramList, function (index, item) {
          $('input:checkbox[name=' + key + ']').filter('[value=' + item + ']').attr('checked', true);
        });
      } else if (['sort'].indexOf(key) !== -1) {
        $('.js-sort-by option').removeAttr('selected');
        $('.js-sort-by option[value=' + value + ']').attr('selected', true);
      } else {
        $('input[name=' + key + '], select[name=' + key + ']').val(value);
      }
    });
  }

  setFilterData();

  $('#notify-me').on('click', function () {
    var redirect = $(this).data('redirect');
    if (redirect) {
      window.location.href = redirect;
    } else {
      var submit = $(this).data('submit');
      loading();
      $.ajax({
        url: submit,
        method: 'POST',
        data: filterForm.serializeArray(),
      }).done(function () {
        loaded();
      });
    }
  });

  //function to remove query params form a url
  function removeURLParameter(url, parameter) {
    //prefer to use l.search if you have a location/link object
    var urlparts = url.split('?');
    if (urlparts.length >= 2) {

      var prefix = encodeURIComponent(parameter) + '=';
      var pars = urlparts[1].split(/[&;]/g);

      //reverse iteration as may be destructive
      for (var i = pars.length; i-- > 0;) {
        //idiom for string.startsWith
        if (pars[i].lastIndexOf(prefix, 0) !== -1) {
          pars.splice(i, 1);
        }
      }

      url = urlparts[0] + (pars.length > 0 ? '?' + pars.join('&') : "");
      return url;
    } else {
      return url;
    }
  }


  function insertParam(key, value) {
    if (history.pushState) {
      // var newurl = window.location.protocol + "//" + window.location.host + search.pathname + '?myNewUrlQuery=1';
      var currentUrl = window.location.href;
      //remove any param for the same key
      currentUrl = removeURLParameter(currentUrl, key);

      //figure out if we need to add the param with a ? or a &
      var queryStart;
      if (currentUrl.indexOf('?') !== -1) {
        queryStart = '&';
      } else {
        queryStart = '?';
      }

      var newurl = currentUrl + queryStart + key + '=' + value;
      window.history.pushState({path: newurl}, '', newurl);
    }
  }

  $('#js-upload-next').on('click', function (e) {
    e.preventDefault();
    loading();
    $btn = $(this);
    var nextPageNumber = $btn.data('page-number') + 1;
    insertParam('page', nextPageNumber);
    $.ajax({
      url: window.location,
      type: 'GET',
      success: function (response) {
        $btn.data('page-number', nextPageNumber);
        $('#ad-content-wrapper').append(response);
      }
    }).always(function () {
      loaded();
    });
  });

});