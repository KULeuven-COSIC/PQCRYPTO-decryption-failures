CC=gcc
OPTFLAGS=-O3
CFLAGS=-I KeccakCodePackage/bin/generic64/ # point this and the one below to wherever the keccak code package is located
LFLAGS=-L KeccakCodePackage/bin/generic64/ -lgmp -lkeccak -lcrypto
TEST_HEADERS = csprng.h  gf256x.h  ramstake.h  reedsolomon.h 
TEST_SOURCE = csprng.c  gf256x.c  ramstake.c  reedsolomon.c  test.c codec_rs.c 
PERFORM_SOURCE = csprng.c  gf256x.c  ramstake.c  reedsolomon.c  attack.c codec_rs.c 
KAT_HEADERS = csprng.h  gf256x.h  ramstake.h  reedsolomon.h  rng.h 
KAT_SOURCES = csprng.c  gf256x.c  ramstake.c  reedsolomon.c  PQCgenKAT_kem.c  rng.c  kem.c codec_rs.c 

ATTACK_SOURCE = csprng.c  gf256x.c  ramstake.c  reedsolomon.c  timing.c codec_rs.c 

attack: $(PERFORM_SOURCE) $(TEST_HEADERS)
	gcc -o $@ $(PERFORM_SOURCE) $(CFLAGS) $(LFLAGS) $(OPTFLAGS) -Wall -lrt

clean:
	rm -f *.o
	rm -f test
	rm -f perform
	rm -f kat
	rm -f genapi
	rm -f attack

