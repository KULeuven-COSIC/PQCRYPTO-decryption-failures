#include <string.h>
#include "api.h"

// encryption with seed
int fake_enc(const unsigned char *pk, unsigned char mlen, unsigned char *c, int pos, int offset)
{
    //generate zero vector c and c2
    memset(c, 0, DIM_N);
    memset(c+DIM_N, 0, C2_VEC_NUM);

    if (offset==1)
    {
        c[DIM_N]=61;
        if (pos==0) {
            c[0]=250;
        }
        else
        {
            c[DIM_N-pos]=1;
        }
    }
    else
    {
        c[DIM_N]=61;
        if (pos==0) {
            c[0]=1;
        }
        else
        {
            c[DIM_N-pos]=250;
        }
    }

    

    return 0;
}