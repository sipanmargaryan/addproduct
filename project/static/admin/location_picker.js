;(function($) {

  var prev_el_selector = '.form-row.field-registration_url';

  var lat_input_selector = '#id_latitude',
      lon_input_selector = '#id_longitude';

  var address_input_selector = '#id_address';

  // Kuwait city
  var initial_lat = 29.3117,
      initial_lon = 47.4818;

  var initial_zoom = 6;

  // Initial zoom level if input fields have a location.
  var initial_with_loc_zoom = 12;

  // Global variables.
  var geocoder, map, marker, $lat, $lon, $address;

  /**
   * Create HTML elements, display map, set up event listenerss.
   */
  function initMap() {
    var $prevEl = $(prev_el_selector);

    if ($prevEl.length === 0) {
      // Can't find where to put the map.
      return;
    }

    $lat = $(lat_input_selector);
    $lon = $(lon_input_selector);
    $address = $(address_input_selector);

    var has_initial_loc = ($lat.val() && $lon.val());

    if (has_initial_loc) {
      // There is lat/lon in the fields, so centre the map on that.
      initial_lat = parseFloat($lat.val());
      initial_lon = parseFloat($lon.val());
      initial_zoom = initial_with_loc_zoom;
    }

    $prevEl.after( $('<div class="js-setloc-map setloc-map"></div>') );

    var mapEl = document.getElementsByClassName('js-setloc-map')[0];

    map = new google.maps.Map(mapEl, {
      zoom: initial_zoom,
      center: {lat: initial_lat, lng: initial_lon}
    });

    geocoder = new google.maps.Geocoder;

    // Create but don't position the marker:
    marker = new google.maps.Marker({
      map: map,
      draggable: true,
    });

    if (has_initial_loc) {
      // There is lat/lon in the fields, so centre the marker on that.
      setMarkerPosition(initial_lat, initial_lon);
    }

    google.maps.event.addListener(map, 'click', function(ev) {
      setMarkerPosition(ev.latLng.lat(), ev.latLng.lng());
    });

    google.maps.event.addListener(marker, 'dragend', function() {
      setInputValues(marker.getPosition().lat(), marker.getPosition().lng());
    });
  }

  /**
   * Re-position marker and set input values.
   */
  function setMarkerPosition(lat, lon) {
    marker.setPosition({lat: lat, lng: lon});
    setInputValues(lat, lon);
  }

  /**
   * Set the values of all the input fields, including getting the
   * geocoded data for address and country, based on lat and lon.
   */
  function setInputValues(lat, lon) {
    setLatLonInputValue($lat, lat);
    setLatLonInputValue($lon, lon);

    geoCode(lat, lon, function(geocoded) {
      if (geocoded['address']) {
        $address.val(geocoded['address'] + ' ' + geocoded['country']);
      }
    });
  }

  /**
   * Set the value of $input to val, with the correct decimal places.
   * We work out decimal places using the <input>'s step value, if any.
   */
  function setLatLonInputValue($input, val) {
    // step should be like "0.000001".
    var step = $input.prop('step');
    var dec_places = 4;

    if (step) {
      if (step.split('.').length === 2) {
        dec_places = step.split('.')[1].length;
      }

      val = val.toFixed(dec_places);
    }

    $input.val(val);
  }

  /**
   * Get an address and a country code for the given lat and lon.
   * callback is the function to call with the data once ready.
   * Returns an object with 'address' and 'country' elements, like:
   *
   * {address: "Colchester, Essex, England", country: "GB"}
   * {address: "Houston, Harris County, Texas", country: "US"}
   */
  function geoCode(lat, lon, callback) {
    var geocoded = {'address': '', 'country': ''};

    geocoder.geocode({'location': {lat: lat, lng: lon}}, function(results, status) {
      if (status === 'OK') {
        if (results[0]) {
          var components = results[0].address_components;
          var address_parts = [];
          // The elements we want to get from the components:
          var wanted = [
                'postal_town',
                'locality',
                'administrative_area_level_2',
                'administrative_area_level_1',
              ];

          for (var n=0; n<(components.length); n++){
            var name = components[n].long_name;
            var type = components[n].types[0];
            if ($.inArray(type, wanted) >= 0
                &&
                $.inArray(name, address_parts) === -1) {
                  address_parts.push(name);
            }
            if (type === 'country'){
              geocoded['country'] = components[n].short_name;
            }
          }

          geocoded['address'] = address_parts.join(', ');
        } else {
          alert('No geocoding results found');
        }
      } else {
        alert('Geocoding failed due to: ' + status);
      }
      callback(geocoded);
    });
  }

  $(document).ready(function(){
    initMap();
  });

})(django.jQuery);