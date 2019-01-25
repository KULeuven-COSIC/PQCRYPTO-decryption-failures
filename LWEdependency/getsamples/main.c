#include "test_correctness.h"
#include "test_speed.h"
#include "test_cpucycles.h"
#include "rand.h"
#include "api.h"
#include <stdio.h>
#include <string.h>

int main(int argc, char **argv)
{

	printf("============== test %s ==============\n",STRENGTH);
	{
		test_kem_fo_correctness();
	}
	printf("============================================\n");

	return 0;
}
