// Performance tests for various intersection algorithms
// Can be run in node.js
// "node intersect-perf.js"
// On PC, Cosines & Haversine seem to be the best performing, and pre-screening makes perf worse not better.
// Desirable to run this on target hardware (smartphones) to see what impact it has on performance.
// correctly labelling variables with const vs let vs var is observed to have major perf impacts.

var events = require('events');
var eventEmitter = new events.EventEmitter();
var math = require('math');
var heading = require('geolocation-utils')

//Create an event handler:
var myEventHandler = function () {
  var start_time
  var end_time
  var i
  var j
  var lat1 = {}  
  var lat2 = {}
  var long1 = {}
  var long2 = {}
  
  const base_lat = (Math.random() * 90)
  const base_long = (Math.random() * 180)
  console.log(base_lat, base_long);

  for (i = 0; i < 10000	; i++) {
  	  lat1[i] = base_lat + Math.random();
	  lat2[i] = base_lat + Math.random();
	  long1[i] = base_long + Math.random();
	  long2[i] = base_long + Math.random();
  }

 
  console.log("Pythagoras");
 
  start_time = Date.now()
  for (j = 0; j < 10000	; j++) {
	  for (i = 0; i < 10000	; i++) {
		  areLocationsNearby_pythagoras(lat1[i], long1[i], lat2[i], long2[i]);
	  }
  }		  
  end_time = Date.now()
  console.log(end_time - start_time);

  console.log("Haversine");
 
  start_time = Date.now()
  for (j = 0; j < 10000	; j++) {
	  for (i = 0; i < 10000	; i++) {
		  areLocationsNearby_haversine(lat1[i], long1[i], lat2[i], long2[i]);
	  }
  }		  
  end_time = Date.now()
  console.log(end_time - start_time);

  console.log("Cosines");
 
  start_time = Date.now()
  for (j = 0; j < 10000	; j++) {
	  for (i = 0; i < 10000	; i++) {
		  areLocationsNearby_cosines(lat1[i], long1[i], lat2[i], long2[i]);
	  }
  }		  
  end_time = Date.now()
  console.log(end_time - start_time);

  console.log("Cosines w/ pre-screening");
 
  start_time = Date.now()
  for (j = 0; j < 10000	; j++) {
	  for (i = 0; i < 10000	; i++) {
		  areLocationsNearby_cosines_screened(lat1[i], long1[i], lat2[i], long2[i]);
	  }
  }		  
  end_time = Date.now()
  console.log(end_time - start_time);

  console.log("Pre-screening only");
 
  start_time = Date.now()
  for (j = 0; j < 10000	; j++) {
	  for (i = 0; i < 10000	; i++) {
		  areLocationsNearby_prescreen_only(lat1[i], long1[i], lat2[i], long2[i]);
	  }
  }		  
  end_time = Date.now()
  console.log(end_time - start_time);

  console.log("Original code");
 
  start_time = Date.now()
  
  for (j = 0; j < 10000	; j++) {
	  for (i = 0; i < 10000	; i++) {
		  areLocationsNearby_original(lat1[i], long1[i], lat2[i], long2[i]);
	  }
  }		  
  end_time = Date.now()
  console.log(end_time - start_time);

  console.log("geolocation-utils (10% of load)");
 
  start_time = Date.now()
  for (j = 0; j < 1000 ; j++) {
    for (i = 0; i < 10000 ; i++) {
      areLocationsNearby_geolocation(lat1[i], long1[i], lat2[i], long2[i]);
    }
  }     
  end_time = Date.now()
  console.log(end_time - start_time);

}

//Assign the event handler to an event:
eventEmitter.on('scream', myEventHandler);

//Fire the 'scream' event:
eventEmitter.emit('scream');

/**
 * Function to determine if two location points are "nearby".
 * Uses shortcuts when possible, then the exact calculation.
 *
 * @param {number} lat1 - location 1 latitude
 * @param {number} lon1 - location 1 longitude
 * @param {number} lat2 - location 2 latitude
 * @param {number} lon2 - location 2 longitude
 * @return {boolean} true if the two locations meet the criteria for nearby
 */
function areLocationsNearby_pythagoras(lat1, lon1, lat2, lon2) {
  const nearbyDistancesq = 400; // in meters, anything closer is "nearby"
  
  // a lookup table for metres in a degree of longitude at various latitudes
  // values aren't accurate, but that won't matter for perf testing.
  // If we were going to use this approach we'd fix up.
  // Values from here: http://www.csgnetwork.com/degreelenllavcalc.html
  const lon_multiplier = [111000, //0
  	                      111000,
  	                      111000,
  	                      111000,
  	                      111000,
  	                      111000,
  	                      111000,
  	                      111000,
  	                      111000,
  	                      110600,
  	                      104600, //10
  	                      104600,
  	                      104600,
  	                      104600,
  	                      104600,
  	                      104600,
  	                      104600,
  	                      104600,
  	                      104600,
  	                      104600,
  	                      96500, //20
  	                      96500, //21
  	                      96500, //22
  	                      96500, //23
  	                      96500, //24
  	                      96500, //25
  	                      96500, //26
  	                      96500, //27
  	                      96500, //28
  	                      96500, //29
  	                      85400, //30
  	                      85400, //30
  	                      85400, //30
  	                      85400, //30
  	                      85400, //30
  	                      85400, //30
  	                      85400, //30
  	                      85400, //30
  	                      85400, //30
  	                      85400, //30
  	                      71700,
  	                      71700,
  	                      71700,
  	                      71700,
  	                      71700,
  	                      71700,
  	                      71700,
  	                      71700,
  	                      71700,
  	                      71700,
  	                      55800,
  	                      55800,
  	                      55800,
  	                      55800,
  	                      55800,
  	                      55800,
  	                      55800,
  	                      55800,
  	                      55800,
  	                      55800,
  	                      38200,
  	                      38200,
  	                      38200,
  	                      38200,
  	                      38200,
  	                      38200,
  	                      38200,
  	                      38200,
  	                      38200,
  	                      38200,
  	                      19400,
  	                      19400,
  	                      19400,
  	                      19400,
  	                      19400,
  	                      19400,
  	                      19400,
  	                      19400,
  	                      19400,
  	                      19400,
  	                      0] // 90
    
    const long_metres = lon_multiplier[Math.floor(lat1)]
    const lonm = (lon2 - lon1) * long_metres
    const latm = (lat2 - lat1) * 111320
    const dsq = lonm*lonm + latm*latm
    if (dsq < nearbyDistancesq) return true;
  
  // nope
  return false;
}

function areLocationsNearby_cosines(lat1, lon1, lat2, lon2) {
  const nearbyDistance = 20; // in meters, anything closer is "nearby"
  const deltaLon = lon2 - lon1;
  
  // Using the the Spherical Law of Cosines method.
  //    https://www.movable-type.co.uk/scripts/latlong.html
  //    https://en.wikipedia.org/wiki/Spherical_law_of_cosines
  //
  // Calculates the distance in meters
  const p1 = (lat1 * Math.PI) / 180;
  const p2 = (lat2 * Math.PI) / 180;
  const deltaLambda = (deltaLon * Math.PI) / 180;
  const R = 6371e3; // gives d in metres
  // let, not const, because we may need to reassign cos_d
  let cos_d = Math.sin(p1) * Math.sin(p2) +
        Math.cos(p1) * Math.cos(p2) * Math.cos(deltaLambda)

  // We have seen Floating Point rounding errors where cod_d > 1
  // When this happens, we can assume distance is 0.
  if (cos_d > 1){
    cos_d = 1
  }
  let d = Math.acos(cos_d) * R;

  if (d < nearbyDistance) return true;
    
  // nope
  return false;
}

function areLocationsNearby_haversine(lat1, lon1, lat2, lon2) {
  
  // Haversine calculation described here: https://www.movable-type.co.uk/scripts/latlong.html 
  const nearbyDistance = 20; // in meters, anything closer is "nearby"
  const deltaLon = lon2 - lon1;
  
  const R = 6371e3; // metres
  const p1 = lat1 * Math.PI/180; // φ, λ in radians
  const p2 = lat2 * Math.PI/180;
  const dp = (lat2-lat1) * Math.PI/180;
  const dlambda = (lon2-lon1) * Math.PI/180;
 
  const a = Math.sin(dp/2) * Math.sin(dp/2) +
	          Math.cos(p1) * Math.cos(p2) *
	          Math.sin(dlambda/2) * Math.sin(dlambda/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));

  const d = R * c; // in metres

  // closer than the "nearby" distance?
  if (d < nearbyDistance) return true;

  // nope
  return false;
}


function areLocationsNearby_cosines_screened(lat1, lon1, lat2, lon2) {
  // This is the original code, as of 4 May 2020
  // but with some tweaks for performance (e.g. let --> const)
  const nearbyDistance = 20; // in meters, anything closer is "nearby"

  // these numbers from https://en.wikipedia.org/wiki/Decimal_degrees
  const notNearbyInLatitude = 0.00017966; // = nearbyDistance / 111320
  const notNearbyInLongitude_23Lat = 0.00019518; // = nearbyDistance / 102470
  const notNearbyInLongitude_45Lat = 0.0002541; // = nearbyDistance / 78710
  const notNearbyInLongitude_67Lat = 0.00045981; // = nearbyDistance / 43496

  
  // Initial checks we can do quickly.  The idea is to filter out any cases where the
  //   difference in latitude or the difference in longitude must be larger than the
  //   nearby distance, since this can be calculated trivially.
  if (Math.abs(lat2 - lat1) > notNearbyInLatitude) return false;
  const deltaLon = lon2 - lon1;

  if (Math.abs(lat1) < 23) {
    if (Math.abs(deltaLon) > notNearbyInLongitude_23Lat) return false;
  } else if (Math.abs(lat1) < 45) {
    if (Math.abs(deltaLon) > notNearbyInLongitude_45Lat) return false;
  } else if (Math.abs(lat1) < 67) {
    if (Math.abs(deltaLon) > notNearbyInLongitude_67Lat) return false;
  }

  // Close enough to do a detailed calculation.  Using the the Spherical Law of Cosines method.
  //    https://www.movable-type.co.uk/scripts/latlong.html
  //    https://en.wikipedia.org/wiki/Spherical_law_of_cosines
  //
  // Calculates the distance in meters
  const p1 = (lat1 * Math.PI) / 180;
  const p2 = (lat2 * Math.PI) / 180;
  const deltaLambda = (deltaLon * Math.PI) / 180;
  const R = 6371e3; // gives d in metres
  let cos_d = Math.sin(p1) * Math.sin(p2) +
        Math.cos(p1) * Math.cos(p2) * Math.cos(deltaLambda)

  // We have seen Floating Point rounding errors where cod_d > 1
  // When this happens, we can assume distance is 0.
  if (cos_d > 1){
    cos_d = 1
  }
  let d = Math.acos(cos_d) * R;
  
  if (d < nearbyDistance) return true;
  
  // nope
  return false;
}

function areLocationsNearby_prescreen_only(lat1, lon1, lat2, lon2) {
  // This is just our original pre-screeing function, pulled out so we can
  // test it in isolation
  const nearbyDistance = 20; // in meters, anything closer is "nearby"

  // these numbers from https://en.wikipedia.org/wiki/Decimal_degrees
  const notNearbyInLatitude = 0.00017966; // = nearbyDistance / 111320
  const notNearbyInLongitude_23Lat = 0.00019518; // = nearbyDistance / 102470
  const notNearbyInLongitude_45Lat = 0.0002541; // = nearbyDistance / 78710
  const notNearbyInLongitude_67Lat = 0.00045981; // = nearbyDistance / 43496

  
  // Initial checks we can do quickly.  The idea is to filter out any cases where the
  //   difference in latitude or the difference in longitude must be larger than the
  //   nearby distance, since this can be calculated trivially.
  if (Math.abs(lat2 - lat1) > notNearbyInLatitude) return false;
  const deltaLon = lon2 - lon1;

  if (Math.abs(lat1) < 23) {
    if (Math.abs(deltaLon) > notNearbyInLongitude_23Lat) return false;
  } else if (Math.abs(lat1) < 45) {
    if (Math.abs(deltaLon) > notNearbyInLongitude_45Lat) return false;
  } else if (Math.abs(lat1) < 67) {
    if (Math.abs(deltaLon) > notNearbyInLongitude_67Lat) return false;
  }

  return true;
}


function areLocationsNearby_original(lat1, lon1, lat2, lon2) {
  // This is the original code, as of 4 May (with no perf tweask let -> const)
  let nearbyDistance = 20; // in meters, anything closer is "nearby"

  // these numbers from https://en.wikipedia.org/wiki/Decimal_degrees
  let notNearbyInLatitude = 0.00017966; // = nearbyDistance / 111320
  let notNearbyInLongitude_23Lat = 0.00019518; // = nearbyDistance / 102470
  let notNearbyInLongitude_45Lat = 0.0002541; // = nearbyDistance / 78710
  let notNearbyInLongitude_67Lat = 0.00045981; // = nearbyDistance / 43496

  let deltaLon = lon2 - lon1;

  // Initial checks we can do quickly.  The idea is to filter out any cases where the
  //   difference in latitude or the difference in longitude must be larger than the
  //   nearby distance, since this can be calculated trivially.
  if (Math.abs(lat2 - lat1) > notNearbyInLatitude) return false;
  if (Math.abs(lat1) < 23) {
    if (Math.abs(deltaLon) > notNearbyInLongitude_23Lat) return false;
  } else if (Math.abs(lat1) < 45) {
    if (Math.abs(deltaLon) > notNearbyInLongitude_45Lat) return false;
  } else if (Math.abs(lat1) < 67) {
    if (Math.abs(deltaLon) > notNearbyInLongitude_67Lat) return false;
  }

  // Close enough to do a detailed calculation.  Using the the Spherical Law of Cosines method.
  //    https://www.movable-type.co.uk/scripts/latlong.html
  //    https://en.wikipedia.org/wiki/Spherical_law_of_cosines
  //
  // Calculates the distance in meters
  let p1 = (lat1 * Math.PI) / 180;
  let p2 = (lat2 * Math.PI) / 180;
  let deltaLambda = (deltaLon * Math.PI) / 180;
  let R = 6371e3; // gives d in metres
  let d =
    Math.acos(
      Math.sin(p1) * Math.sin(p2) +
        Math.cos(p1) * Math.cos(p2) * Math.cos(deltaLambda),
    ) * R;

  // closer than the "nearby" distance?
  if (d < nearbyDistance) return true;

  // nope
  return false;
}


function areLocationsNearby_geolocation(lat1, lon1, lat2, lon2) {
  const nearbyDistance = 20; // in meters, anything closer is "nearby"
  const location1 = {lat: lat1, lon: lon1}
  const location2 = {lat: lat2, lon: lon2 }
  let d = heading.headingDistanceTo(location1, location2).distance
  //console.log(location1, location2, d)
  // closer than the "nearby" distance?
  if (d < nearbyDistance) return true;

  // nope
  return false;
}