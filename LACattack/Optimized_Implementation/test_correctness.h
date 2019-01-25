//test correctness of pke_dec
int test_pke_correctness();

//test kem fo correctness
int test_kem_fo_correctness();

//test  ke correctness
int test_ke_correctness();

//test  ke correctness
int test_ake_correctness();

//calculate error bit number
int error_bit_num(unsigned char *k1, unsigned char *k2, int num);

//print bytes
int print_bytes(unsigned char *buf, int len);