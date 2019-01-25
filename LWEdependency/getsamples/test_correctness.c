#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include "api.h"
#include "ecc.h"
#include "rand.h"

// #define CTESTS 1
uint64_t loop=1000000;

// static void print_uint64(unsigned long long num)
// {
// 	if(num>=10)
// 		print_uint64(num/10);
// 	printf("%u",(unsigned int)(num%10));
// }

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

//test kem fo correctness
int test_kem_fo_correctness()
{
	unsigned char pk[CRYPTO_PUBLICKEYBYTES];
	unsigned char sk[CRYPTO_SECRETKEYBYTES];
	unsigned char k1[CRYPTO_BYTES],k2[CRYPTO_BYTES],c[CRYPTO_CIPHERTEXTBYTES];
	int j;
	long long int  error_num=0;
	
	for(j=0;j<loop;j++)
	{
		crypto_kem_keypair(pk,sk);
		random_bytes(k1,CRYPTO_BYTES);
		crypto_kem_enc(c,k1,pk);
		crypto_kem_dec(k2,c,sk);
		printf("\n");
	}

	return error_num;
}
