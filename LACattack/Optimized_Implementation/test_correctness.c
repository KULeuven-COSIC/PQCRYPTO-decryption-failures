#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include "api.h"
#include "ecc.h"
#include "rand.h"

#define CTESTS 10000
uint64_t loop=1;

static void print_uint64(unsigned long long num)
{
	if(num>=10)
		print_uint64(num/10);
	printf("%u",(unsigned int)(num%10));
}

int error_bit_num(unsigned char *k1, unsigned char *k2, int num)
{
	int i,sum=0;
	unsigned char temp;
	for(i=0;i<num;i++)
	{
		temp=k1[i]^k2[i];
		if(temp>0)
		{
			sum+=(temp&0x1);
			sum+=((temp>>1)&0x1);
			sum+=((temp>>2)&0x1);
			sum+=((temp>>3)&0x1);
			sum+=((temp>>4)&0x1);
			sum+=((temp>>5)&0x1);
			sum+=((temp>>6)&0x1);
			sum+=((temp>>7)&0x1);
		}
	}
	
	return sum;
}
int print_error_bit(unsigned char *k1, unsigned char *k2, int num)
{
	int i,sum=0;
	unsigned char temp;
	printf("\nerror bit:\n");
	for(i=0;i<num;i++)
	{
		temp=k1[i]^k2[i];
		printf("%d%d%d%d%d%d%d%d",temp&0x1,((temp>>1)&0x1),((temp>>2)&0x1),((temp>>3)&0x1),((temp>>4)&0x1),((temp>>5)&0x1),((temp>>6)&0x1),((temp>>7)&0x1));
	}
	printf("\n");
	
	return sum;
}

//print bytes
int print_bytes(unsigned char *buf, int len)
{
	int i;
	for(i=0;i<len;i++)
	{
		printf("%d ",buf[i]);
	}
	printf("\n");
	
	return 0;
}

//test correctness of pke
int test_pke_correctness()
{

	unsigned char pk[CRYPTO_PUBLICKEYBYTES];
	unsigned char sk[CRYPTO_SECRETKEYBYTES];
	unsigned char k1[CRYPTO_BYTES],k2[CRYPTO_BYTES],c[CRYPTO_CIPHERTEXTBYTES];
	int i,j;
	long long int  error_bit,sum=0;
	long long int  error_num=0,sum_bits;
	unsigned long long mlen=CRYPTO_BYTES,clen=CRYPTO_CIPHERTEXTBYTES;
	
	printf("correctness test of pke:\n");
	for(j=0;j<loop;j++)
	{
		crypto_encrypt_keypair(pk,sk);
		random_bytes(k1,CRYPTO_BYTES);
		for(i=0;i<CTESTS;i++)
		{
			crypto_encrypt(c,&clen,k1,mlen,pk);
			crypto_encrypt_open(k2,&mlen,c,clen,sk);
			//printf("i=%d\n",i);
			if(memcmp(k1,k2,CRYPTO_BYTES)!=0)
			{
				error_num++;
				error_bit=error_bit_num(k1,k2,CRYPTO_BYTES);
				sum+=error_bit;
				if(error_bit>0)
				{
					printf("error bit num:");
					print_uint64(error_bit);
					printf("\n");
					print_error_bit(k1,k2,CRYPTO_BYTES);
				}
			}
		}
		printf("test %d error block:",j+1);
		print_uint64(error_num);
		printf(" error bit:");
		print_uint64(sum);
		printf("\n");

	}
    sum_bits=CTESTS*loop*CRYPTO_BYTES*8;
	printf("total error bit:");
	print_uint64(sum);
	printf("/");
	print_uint64(sum_bits);
	printf("\n\n");
	
	return error_num;
}

//test kem fo correctness
int test_kem_fo_correctness()
{
	unsigned char pk[CRYPTO_PUBLICKEYBYTES];
	unsigned char sk[CRYPTO_SECRETKEYBYTES];
	unsigned char k1[CRYPTO_BYTES],k2[CRYPTO_BYTES],c[CRYPTO_CIPHERTEXTBYTES];
	int i,j;
	long long int  error_num=0;
	
	printf("correctness test of kem_fo:\n");
	for(j=0;j<loop;j++)
	{
		crypto_kem_keypair(pk,sk);
		random_bytes(k1,CRYPTO_BYTES);
		for(i=0;i<CTESTS;i++)
		{
			crypto_kem_enc(c,k1,pk);
			crypto_kem_dec(k2,c,sk);
			if(memcmp(k1,k2,CRYPTO_BYTES)!=0)
			{
				error_num++;
			}
		}
		printf("test %d error block:",j+1);
		print_uint64(error_num);
		printf("\n");
	}
	printf("\n");

	return error_num;
}

//test  ke correctness
int test_ke_correctness()
{
	unsigned char pk[CRYPTO_PUBLICKEYBYTES];
	unsigned char sk[CRYPTO_SECRETKEYBYTES];
	unsigned char k1[CRYPTO_BYTES],k2[CRYPTO_BYTES],c[CRYPTO_CIPHERTEXTBYTES];
	int i,j;
	long long int  error_num=0;
	
	printf("correctness test of ke:\n");
	for(j=0;j<loop;j++)
	{
		for(i=0;i<CTESTS;i++)
		{
			crypto_ke_alice_send(pk,sk);
			crypto_ke_bob_receive(pk,c,k1);
			crypto_ke_alice_receive(pk,sk,c,k2);
			if(memcmp(k1,k2,CRYPTO_BYTES)!=0)
			{
				error_num++;
			}
		}
		printf("test %d error block:",j+1);
		print_uint64(error_num);
		printf("\n");
	}
	printf("\n");
	
	return error_num;
}

//test  ake correctness
int test_ake_correctness()
{
	unsigned char pk_a[CRYPTO_PUBLICKEYBYTES],pk_b[CRYPTO_PUBLICKEYBYTES],pk[CRYPTO_PUBLICKEYBYTES];
	unsigned char sk[CRYPTO_SECRETKEYBYTES],sk_a[CRYPTO_SECRETKEYBYTES],sk_b[CRYPTO_SECRETKEYBYTES];
	unsigned char k_a[CRYPTO_BYTES],k_b[CRYPTO_BYTES],c_a[CRYPTO_CIPHERTEXTBYTES],c_b[2*CRYPTO_CIPHERTEXTBYTES],k1[CRYPTO_BYTES];
	int i,j;
	long long int  error_num=0;
	
	// generate public parameter  a and the key pair of alice and bob
	crypto_encrypt_keypair(pk_a,sk_a);
	crypto_encrypt_keypair(pk_b,sk_b);
	printf("correctness test of ake:\n");
	for(j=0;j<loop;j++)
	{
		for(i=0;i<CTESTS;i++)
		{
			crypto_ake_alice_send(pk,sk,pk_b,sk_a,c_a,k1);
			crypto_ake_bob_receive(pk_b,sk_b,pk_a,pk,c_a,c_b,k_b);
			crypto_ake_alice_receive(pk_a,sk_a,pk_b,pk,sk,c_a,c_b,k1,k_a);
			if(memcmp(k_b,k_a,CRYPTO_BYTES)!=0)
			{
				error_num++;
			}
		}
		printf("test %d error block:",j+1);
		print_uint64(error_num);
		printf("\n");
	}
	printf("\n");

	return error_num;
}