#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <gmp.h>

#include "ramstake.h"
#include "csprng.h"

int main( int argc, char ** argv )
{
    unsigned long randomness;
    unsigned char * seed;
    mpz_t integer;
    csprng rng;
    unsigned char data[RAMSTAKE_SEED_LENGTH];
    int i;
    int equals;
    int num_trials, trial_index;
    int histogram[2+RAMSTAKE_CODEWORD_NUMBER];
    int num_successes;
    int num_failures;
    int decaps_value;
    unsigned char byte;

    ramstake_public_key pk;
    ramstake_secret_key sk;
    ramstake_ciphertext c;
    unsigned char pk_bytes[RAMSTAKE_PUBLIC_KEY_LENGTH];
    unsigned char sk_bytes[RAMSTAKE_SECRET_KEY_LENGTH];
    unsigned char c_bytes[RAMSTAKE_CIPHERTEXT_LENGTH];
    unsigned char key1[RAMSTAKE_KEY_LENGTH];
    unsigned char key2[RAMSTAKE_KEY_LENGTH];

    if( argc != 3 || strlen(argv[2]) % 2 != 0 )
    {
        printf("usage: ./test [num trials, eg 13] [random seed, eg d13d13deadbeef]\n");
        return 0;
    }

    /* grab randomness */
    csprng_init(&rng);

    seed = malloc(strlen(argv[2])/2);
    for( i = 0 ; i < strlen(argv[2])/2 ; ++i )
    {
        sscanf(argv[2] + 2*i, "%2hhx", &seed[i]);
    }
    csprng_seed(&rng, strlen(argv[2])/2, seed);
    free(seed);

    csprng_generate(&rng, 1, &byte);
    printf("randomness byte: %02x\n", byte);

    randomness = csprng_generate_ulong(&rng);

    printf("randomness: %lu\n", randomness);


    /* grab trial number */
    num_trials = atoi(argv[1]);
    printf("num trials: %i\n", num_trials);

    /* run trials */
    for( i = 0 ; i < 2+RAMSTAKE_CODEWORD_NUMBER ; ++i )
    {
        histogram[i] = 0;
    } 
    for( trial_index = 0 ; trial_index < num_trials ; ++trial_index )
    {

        ramstake_public_key_init(&pk);
        ramstake_secret_key_init(&sk);
        ramstake_ciphertext_init(&c);

        seed = malloc(RAMSTAKE_SEED_LENGTH);
        csprng_generate(&rng, RAMSTAKE_SEED_LENGTH, seed);
    
        ramstake_keygen(&sk, &pk, seed, 2*(num_trials == 1));

        free(seed);
        ramstake_export_public_key(pk_bytes, pk);
        ramstake_export_secret_key(sk_bytes, sk);

        ramstake_import_public_key(&pk, pk_bytes);
        seed = malloc(RAMSTAKE_SEED_LENGTH);
        csprng_generate(&rng, RAMSTAKE_SEED_LENGTH, seed);
        ramstake_encaps(&c, key1, pk, seed, 2*(num_trials == 1));
        free(seed);
        ramstake_export_ciphertext(c_bytes, c);

        ramstake_import_ciphertext(&c, c_bytes);
        ramstake_import_secret_key(&sk, sk_bytes);
        decaps_value = ramstake_decaps(key2, c, sk, 2*(num_trials == 1));

        histogram[2+decaps_value] += 1;

        ramstake_public_key_destroy(pk);
        ramstake_secret_key_destroy(sk);
        ramstake_ciphertext_destroy(c);
    }

    /* report on results */
    num_successes = 0;
    for( i = 0 ; i < RAMSTAKE_CODEWORD_NUMBER ; ++i )
    {
        num_successes += histogram[2+i];
    }
    num_failures = 0;
    for( i = 0 ; i < 2 ; ++i )
    {
        num_failures += histogram[i];
    }
    printf("Ran %i trials with %i successes and %i failures.\n", num_trials, num_successes, num_failures);
    printf("Failures:\n");
    printf(" * %i decoding errors\n", histogram[1]);
    printf(" * %i integrity errors\n", histogram[0]);
    printf("Successes:\n");
    printf(" * %i total successes\n", num_successes);

    return 0;
}

