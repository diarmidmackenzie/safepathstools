import geohashutils
import time

print(geohashutils.geohashes_from_gps(0,13,9))
print(geohashutils.geohashes_from_gps(30,13,9))
print(geohashutils.geohashes_from_gps(45,13,9))
print(geohashutils.geohashes_from_gps(60,13,9))

print(geohashutils.geohashes_from_gps(0,13,8))
print(geohashutils.geohashes_from_gps(30,13,8))
print(geohashutils.geohashes_from_gps(45,13,8))
print(geohashutils.geohashes_from_gps(60,13,8))

#print(geohashutils.scrypt_hashes(42,13,time.time(),12,8))
#print(geohashutils.scrypt_hashes(42,13,time.time(),12,9))
#print(geohashutils.scrypt_hashes(0,13,time.time(),12,9))
#print(geohashutils.scrypt_hashes(75,13,time.time(),12,9))