$(document).ready(function () {
  $mapContainer = $('#googleMap');

  $("#share").jsSocials({
    showLabel: false,
    showCount: false,
    shares: [
      'facebook', 'twitter', 'pinterest'
    ]
  });

  initMap();

  function initMap() {
    var eventLatLng = {lat: $mapContainer.data('latitude'), lng: $mapContainer.data('longitude')};

    var map = new google.maps.Map(document.getElementById('googleMap'), {
      zoom: 19,
      center: eventLatLng
    });

    new google.maps.Marker({
      position: eventLatLng,
      map: map,
      title: $mapContainer.data('title')
    });
  }
});