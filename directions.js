var directionsService = new google.maps.DirectionsService();

var request = {
  origin      : 'Melbourne VIC', // a city, full address, landmark etc
  destination : 'Sydney NSW',
  travelMode  : google.maps.DirectionsTravelMode.DRIVING
};

directionsService.route(request, function(response, status) {
  if ( status == google.maps.DirectionsStatus.OK ) {
    alert( response.routes[0].legs[0].distance.value ); // the distance in metres
  }
  else {
    // oops, there's no route between these two locations
    // every time this happens, a kitten dies
    // so please, ensure your address is formatted properly
  }
});