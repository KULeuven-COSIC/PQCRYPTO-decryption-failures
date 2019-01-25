#include <stdio.h>
#include <string.h>
#include <time.h>
#include "api.h"
#include "rand.h"
#include "ecc.h"
#include "bin-lwe.h"

#define NTESTS 10000

//test poly_nul
int test_poly_mul_speed()
{
	clock_t start,finish;
    double total_time;
	unsigned char a[DIM_N],pk[DIM_N],seed[SEED_LEN];
	char sk[DIM_N];
	int i;
	
	random_bytes(a,DIM_N);
	random_bytes(seed,SEED_LEN);
	gen_psi(sk,DIM_N,seed);
	
    start=clock();
    for(i=0;i<NTESTS;i++)
	{
		poly_mul(a,sk,pk,DIM_N);
	}
    finish=clock();
    total_time=(double)(finish-start)/CLOCKS_PER_SEC;
    printf("poly_mul time    :%f us\n",(total_time*1000000/NTESTS));
	
	return 0;
}

//test pke
int test_pke_speed()
{
	clock_t start,finish;
    double total_time;
	unsigned char pk[CRYPTO_PUBLICKEYBYTES];
	unsigned char sk[CRYPTO_SECRETKEYBYTES];
	unsigned char k1[CRYPTO_BYTES],k2[CRYPTO_BYTES],c[CRYPTO_CIPHERTEXTBYTES];
	int i;
	unsigned long long mlen=CRYPTO_BYTES,clen=CRYPTO_CIPHERTEXTBYTES;
	
	start=clock();
    for(i=0;i<NTESTS;i++)
	{
		crypto_encrypt_keypair(pk,sk);
	}
    finish=clock();
    total_time=(double)(finish-start)/CLOCKS_PER_SEC;
    printf("key generate time:%f us\n",(total_time*1000000/NTESTS));
	
	crypto_encrypt_keypair(pk,sk);
	random_bytes(k1,CRYPTO_BYTES);
	
    start=clock();
    for(i=0;i<NTESTS;i++)
	{
		crypto_encrypt(c,&clen,k1,mlen,pk);
	}
    finish=clock();
    total_time=(double)(finish-start)/CLOCKS_PER_SEC;
    printf("encryption time  :%f us\n",(total_time*1000000/NTESTS));
	
	crypto_encrypt_keypair(pk,sk);
	random_bytes(k1,CRYPTO_BYTES);
	crypto_encrypt(c,&clen,k1,mlen,pk);
	
    start=clock();
    for(i=0;i<NTESTS;i++)
	{
		crypto_encrypt_open(k2,&mlen,c,clen,sk);
	}
    finish=clock();
    total_time=(double)(finish-start)/CLOCKS_PER_SEC;
    printf("decryption time  :%f us\n",(total_time*1000000/NTESTS));
    printf("\n");
	
	return 0;
}

//test kem fo
int test_kem_fo_speed()
{
	clock_t start,finish;
    double total_time;
	unsigned char pk[CRYPTO_PUBLICKEYBYTES];
	unsigned char sk[CRYPTO_SECRETKEYBYTES];
	unsigned char k1[CRYPTO_BYTES],k2[CRYPTO_BYTES],c[CRYPTO_CIPHERTEXTBYTES];
	int i;
	
	start=clock();
    for(i=0;i<NTESTS;i++)
	{
		crypto_kem_keypair(pk,sk);
	}
    finish=clock();
    total_time=(double)(finish-start)/CLOCKS_PER_SEC;
    printf("key generate time:%f us\n",(total_time*1000000/NTESTS));
	
	crypto_kem_keypair(pk,sk);
	
    start=clock();
    for(i=0;i<NTESTS;i++)
	{
		crypto_kem_enc(c,k1,pk);
	}
    finish=clock();
    total_time=(double)(finish-start)/CLOCKS_PER_SEC;
    printf("kem_fo_enc time  :%f us\n",(total_time*1000000/NTESTS));
	
	crypto_kem_keypair(pk,sk);
	crypto_kem_enc(c,k1,pk);
	
    start=clock();
    for(i=0;i<NTESTS;i++)
	{
		crypto_kem_dec(k2,c,sk);
	}
    finish=clock();
    total_time=(double)(finish-start)/CLOCKS_PER_SEC;
    printf("kem_fo_dec time  :%f us\n",(total_time*1000000/NTESTS));
    printf("\n");
	
	return 0;
}

// test ke
int test_ke_speed()
{
	clock_t start,finish;
    double total_time;
	unsigned char pk[CRYPTO_PUBLICKEYBYTES];
	unsigned char sk[CRYPTO_SECRETKEYBYTES];
	unsigned char k1[CRYPTO_BYTES],k2[CRYPTO_BYTES],c[CRYPTO_CIPHERTEXTBYTES];
	int i;

	//test alice send
    start=clock();
    for(i=0;i<NTESTS;i++)
	{
		crypto_ke_alice_send(pk,sk);
	}
    finish=clock();
    total_time=(double)(finish-start)/CLOCKS_PER_SEC;
    printf("ke alice0 time   :%f us\n",(total_time*1000000/NTESTS));
	
	//test bob receive
    start=clock();
    for(i=0;i<NTESTS;i++)
	{
		crypto_ke_bob_receive(pk,c,k1);
	}
    finish=clock();
    total_time=(double)(finish-start)/CLOCKS_PER_SEC;
    printf("ke bob time      :%f us\n",(total_time*1000000/NTESTS));
	
	//test alice receive
    start=clock();
    for(i=0;i<NTESTS;i++)
	{
		crypto_ke_alice_receive(pk,sk,c,k2);
	}
    finish=clock();
    total_time=(double)(finish-start)/CLOCKS_PER_SEC;
    printf("ke alice1 time   :%f us\n",(total_time*1000000/NTESTS));
    printf("\n");
	
	return 0;
}

// test ake
int test_ake_speed()
{
	clock_t start,finish;
    double total_time;
	unsigned char pk_a[CRYPTO_PUBLICKEYBYTES],pk_b[CRYPTO_PUBLICKEYBYTES],pk[CRYPTO_PUBLICKEYBYTES];
	unsigned char sk[CRYPTO_SECRETKEYBYTES],sk_a[CRYPTO_SECRETKEYBYTES],sk_b[CRYPTO_SECRETKEYBYTES];
	unsigned char k_a[CRYPTO_BYTES],k_b[CRYPTO_BYTES],c_a[CRYPTO_CIPHERTEXTBYTES],c_b[2*CRYPTO_CIPHERTEXTBYTES],k1[CRYPTO_BYTES];
	int i;
	
	// generate public parameter  a and the key pair of alice and bob
	crypto_encrypt_keypair(pk_a,sk_a);
	crypto_encrypt_keypair(pk_b,sk_b);
	//test alice send
    start=clock();
    for(i=0;i<NTESTS;i++)
	{
		crypto_ake_alice_send(pk,sk,pk_b,sk_a,c_a,k1);
	}
    finish=clock();
    total_time=(double)(finish-start)/CLOCKS_PER_SEC;
    printf("ake alice0 time  :%f us\n",(total_time*1000000/NTESTS));
	
	//test bob receive
    start=clock();
    for(i=0;i<NTESTS;i++)
	{
		crypto_ake_bob_receive(pk_b,sk_b,pk_a,pk,c_a,c_b,k_b);
	}
    finish=clock();
    total_time=(double)(finish-start)/CLOCKS_PER_SEC;
    printf("ake bob time     :%f us\n",(total_time*1000000/NTESTS));
	
	//test alice receive
    start=clock();
    for(i=0;i<NTESTS;i++)
	{
		crypto_ake_alice_receive(pk_a,sk_a,pk_b,pk,sk,c_a,c_b,k1,k_a);
	}
    finish=clock();
    total_time=(double)(finish-start)/CLOCKS_PER_SEC;
    printf("ake alice1 time  :%f us\n",(total_time*1000000/NTESTS));
    printf("\n");
	
	return 0;
}