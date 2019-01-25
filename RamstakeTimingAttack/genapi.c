#include <stdio.h>

#include "ramstake.h"

int main( int argc, char ** argv )
{

    printf("#define CRYPTO_SECRETKEYBYTES %i\n", RAMSTAKE_SECRET_KEY_LENGTH);
    printf("#define CRYPTO_PUBLICKEYBYTES %i\n", RAMSTAKE_PUBLIC_KEY_LENGTH);
    printf("#define CRYPTO_BYTES %i\n", RAMSTAKE_SEED_LENGTH);
    printf("#define CRYPTO_CIPHERTEXTBYTES %i\n", RAMSTAKE_CIPHERTEXT_LENGTH);
    printf("\n");
    printf("#define CRYPTO_ALGNAME \"Ramstake RS %i\"\n", RAMSTAKE_MODULUS_BITSIZE);
    printf("\n");
    printf("int crypto_kem_keypair( unsigned char *pk, unsigned char *sk );\n");
    printf("int crypto_kem_enc( unsigned char *ct, unsigned char *ss, const unsigned char *pk );\n");
    printf("int crypto_kem_dec( unsigned char *ss, const unsigned char *ct, const unsigned char *sk );\n");

    return 0;

}
