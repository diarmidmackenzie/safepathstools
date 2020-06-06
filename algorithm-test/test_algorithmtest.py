# Skeleton beginnings of some test cases.
# Run pytest in the main directory to run these.
# Need some refactoring of main code to be able to use main code in constructing GPS sets etc.

import algorithmutils
import math
import pytest

gps_set_a = [{'latitude': 6.61e-05, 'longitude': 6.61e-05, 'geohash_centre': 's0000000',
              'near_geohashes': ['s0000000'],
              'time': 230.53558941352668}, 
              {'latitude': 3.56e-05, 'longitude': 3.56e-05, 'geohash_centre': 's0000000',
              'near_geohashes': ['s0000000'],
              'time': 530.5355894135266}]
gps_set_b = [{'latitude': 6.61e-05, 'longitude': 6.61e-05, 'geohash_centre': 's0000000',
              'near_geohashes': ['s0000000'],
              'time': 230.53558941352668}, 
              {'latitude': 3.56e-05, 'longitude': 3.56e-05, 'geohash_centre': 's0000000',
              'near_geohashes': ['s0000000'],
              'time': 530.5355894135266}]

def test_gps_intersection():
	intersections = algorithmutils.check_gps_data_for_intersection(gps_set_a,
					                                               gps_set_b,
					                                               300,
					                                               20)
	assert(len(intersections) == 2)

def test_geohash_intersection():

	intersections = algorithmutils.check_gps_data_for_geohash_intersection(gps_set_a,
					                                                       gps_set_b,
					                                                       300)
	assert(len(intersections) == 2)


def test_rotation():

    # check basic rotations of (0,1)
    movement_set = [{'longitude': 1, 'latitude': 0}]
    algorithmutils.rotate_movement_set(movement_set, 0)   
    assert(movement_set[0]['longitude'] == pytest.approx(1))
    assert(movement_set[0]['latitude'] == pytest.approx(0))

    movement_set = [{'longitude': 1, 'latitude': 0}]
    algorithmutils.rotate_movement_set(movement_set, math.pi / 2)   
    assert(movement_set[0]['longitude'] == pytest.approx(0))
    assert(movement_set[0]['latitude'] == pytest.approx(1))
        
    movement_set = [{'longitude': 1, 'latitude': 0}]
    algorithmutils.rotate_movement_set(movement_set, math.pi)   
    assert(movement_set[0]['longitude'] == pytest.approx(-1))
    assert(movement_set[0]['latitude'] == pytest.approx(0))
    
    movement_set = [{'longitude': 1, 'latitude': 0}]
    algorithmutils.rotate_movement_set(movement_set, 3 * math.pi / 2)   
    assert(movement_set[0]['longitude'] == pytest.approx(0))
    assert(movement_set[0]['latitude'] == pytest.approx(-1))
    
    movement_set = [{'longitude': 1, 'latitude': 0}]
    algorithmutils.rotate_movement_set(movement_set, 2 * math.pi)   
    assert(movement_set[0]['longitude'] == pytest.approx(1))
    assert(movement_set[0]['latitude'] == pytest.approx(0))

    # Now check a few rotations of (1,1), (2,2)

    movement_set = [{'longitude': 1, 'latitude': 1},
                    {'longitude': 2, 'latitude': 2}]

    algorithmutils.rotate_movement_set(movement_set, 0)   
    assert(movement_set[0]['longitude'] == pytest.approx(1))
    assert(movement_set[0]['latitude'] == pytest.approx(1))
    assert(movement_set[1]['longitude'] == pytest.approx(2))
    assert(movement_set[1]['latitude'] == pytest.approx(2))

    movement_set = [{'longitude': 1, 'latitude': 1},
                    {'longitude': 2, 'latitude': 2}]

    algorithmutils.rotate_movement_set(movement_set, math.pi / 2)   
    assert(movement_set[0]['longitude'] == pytest.approx(-1))
    assert(movement_set[0]['latitude'] == pytest.approx(1))
    assert(movement_set[1]['longitude'] == pytest.approx(-2))
    assert(movement_set[1]['latitude'] == pytest.approx(2))

    movement_set = [{'longitude': 1, 'latitude': 1},
                    {'longitude': 2, 'latitude': 2}]
    
    algorithmutils.rotate_movement_set(movement_set, math.pi)   
    assert(movement_set[0]['longitude'] == pytest.approx(-1))
    assert(movement_set[0]['latitude'] == pytest.approx(-1))
    assert(movement_set[1]['longitude'] == pytest.approx(-2))
    assert(movement_set[1]['latitude'] == pytest.approx(-2))
    

