#include "mem_avx2.h"

#include <immintrin.h>


inline void copy_256(void *d, const void *s) {
    // d, s -> size of 256 * sizeof(char)
      
    __m256i *dVec = (__m256i *) d;
    const __m256i *sVec = (__m256i*) s;

    _mm256_stream_si256(dVec, _mm256_load_si256(sVec));
    _mm256_stream_si256(dVec + 1, _mm256_load_si256(sVec + 1));
    _mm256_stream_si256(dVec + 2, _mm256_load_si256(sVec + 2));
    _mm256_stream_si256(dVec + 3, _mm256_load_si256(sVec + 3));
    _mm256_stream_si256(dVec + 4, _mm256_load_si256(sVec + 4));
    _mm256_stream_si256(dVec + 5, _mm256_load_si256(sVec + 5));
    _mm256_stream_si256(dVec + 6, _mm256_load_si256(sVec + 6));
    _mm256_stream_si256(dVec + 7, _mm256_load_si256(sVec + 7));
}

inline void coeff_copy_400(void *d, const void *s) {
    // d, s -> size of 400 * sizeof(short)
      
    __m256i *dVec = (__m256i *) d;
    const __m256i *sVec = (__m256i*) s;
    int nVec = sizeof(short) >> 1;

    //loop unroll (25 times, 400 * sizeof(short) / 32)
    for (; nVec > 0; nVec--, sVec += 25, dVec += 25) {
    _mm256_stream_si256(dVec, _mm256_load_si256(sVec));
    _mm256_stream_si256(dVec + 1, _mm256_load_si256(sVec + 1));
    _mm256_stream_si256(dVec + 2, _mm256_load_si256(sVec + 2));
    _mm256_stream_si256(dVec + 3, _mm256_load_si256(sVec + 3));
    _mm256_stream_si256(dVec + 4, _mm256_load_si256(sVec + 4));
    _mm256_stream_si256(dVec + 5, _mm256_load_si256(sVec + 5));
    _mm256_stream_si256(dVec + 6, _mm256_load_si256(sVec + 6));
    _mm256_stream_si256(dVec + 7, _mm256_load_si256(sVec + 7));
    _mm256_stream_si256(dVec + 8, _mm256_load_si256(sVec + 8));
    _mm256_stream_si256(dVec + 9, _mm256_load_si256(sVec + 9));
    _mm256_stream_si256(dVec + 10, _mm256_load_si256(sVec + 10));
    _mm256_stream_si256(dVec + 11, _mm256_load_si256(sVec + 11));
    _mm256_stream_si256(dVec + 12, _mm256_load_si256(sVec + 12));
    _mm256_stream_si256(dVec + 13, _mm256_load_si256(sVec + 13));
    _mm256_stream_si256(dVec + 14, _mm256_load_si256(sVec + 14));
    _mm256_stream_si256(dVec + 15, _mm256_load_si256(sVec + 15));
    _mm256_stream_si256(dVec + 16, _mm256_load_si256(sVec + 16));
    _mm256_stream_si256(dVec + 17, _mm256_load_si256(sVec + 17));
    _mm256_stream_si256(dVec + 18, _mm256_load_si256(sVec + 18));
    _mm256_stream_si256(dVec + 19, _mm256_load_si256(sVec + 19));
    _mm256_stream_si256(dVec + 20, _mm256_load_si256(sVec + 20));
    _mm256_stream_si256(dVec + 21, _mm256_load_si256(sVec + 21));
    _mm256_stream_si256(dVec + 22, _mm256_load_si256(sVec + 22));
    _mm256_stream_si256(dVec + 23, _mm256_load_si256(sVec + 23));
    _mm256_stream_si256(dVec + 24, _mm256_load_si256(sVec + 24));
    }
    
}

inline void eobs_copy_32(void *d, const void *s) {
    __m256i *dVec = (__m256i *) d;
    const __m256i *sVec = (__m256i*) s;
    _mm256_stream_si256(dVec, _mm256_load_si256(sVec));
}

