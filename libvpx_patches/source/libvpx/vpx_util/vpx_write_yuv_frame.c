/*
 *  Copyright (c) 2015 The WebM project authors. All Rights Reserved.
 *
 *  Use of this source code is governed by a BSD-style license
 *  that can be found in the LICENSE file in the root of the source
 *  tree. An additional intellectual property rights grant can be found
 *  in the file PATENTS.  All contributing project authors may
 *  be found in the AUTHORS file in the root of the source tree.
 */

#include "vpx_dsp/skin_detection.h"
#include "vpx_util/vpx_write_yuv_frame.h"

//Stegozoa
#include "vp8/common/stegozoa_hooks/macros.h"


void vpx_write_yuv_frame(FILE *yuv_file, YV12_BUFFER_CONFIG *s) {

//Stegozoa
#if defined(OUTPUT_YUV_SRC) || defined(OUTPUT_YUV_DENOISED) || \
    defined(OUTPUT_YUV_SKINMAP) || defined(OUTPUT_YUV_SVC_SRC) || \
    IMAGE_QUALITY

  fwrite(&s->y_crop_height, sizeof(int), 1, yuv_file);
  fwrite(&s->uv_crop_height, sizeof(int), 1, yuv_file);
  fwrite(&s->y_width, sizeof(int), 1, yuv_file);
  fwrite(&s->uv_width, sizeof(int), 1, yuv_file);
  fwrite(&s->y_stride, sizeof(int), 1, yuv_file);
  fwrite(&s->uv_stride, sizeof(int), 1, yuv_file);

  unsigned char *src = s->y_buffer;
  int h = s->y_crop_height;

  do {
    fwrite(src, s->y_width, 1, yuv_file);
    src += s->y_stride;
  } while (--h);

  src = s->u_buffer;
  h = s->uv_crop_height;

  do {
    fwrite(src, s->uv_width, 1, yuv_file);
    src += s->uv_stride;
  } while (--h);

  src = s->v_buffer;
  h = s->uv_crop_height;

  do {
    fwrite(src, s->uv_width, 1, yuv_file);
    src += s->uv_stride;
  } while (--h);


#else
  (void)yuv_file;
  (void)s;
#endif
}

#if IMAGE_QUALITY
void vpx_read_yuv_frame(FILE *yuv_file, YV12_BUFFER_CONFIG *s) {
  
  fread(&s->y_crop_height, sizeof(int), 1, yuv_file);
  fread(&s->uv_crop_height, sizeof(int), 1, yuv_file);
  fread(&s->y_width, sizeof(int), 1, yuv_file);
  fread(&s->uv_width, sizeof(int), 1, yuv_file);
  fread(&s->y_stride, sizeof(int), 1, yuv_file);
  fread(&s->uv_stride, sizeof(int), 1, yuv_file);

  unsigned char *src = s->y_buffer;
  int h = s->y_crop_height;

  do {
    fread(src, s->y_width, 1, yuv_file);
    src += s->y_stride;
  } while (--h);

  src = s->u_buffer;
  h = s->uv_crop_height;

  do {
    fread(src, s->uv_width, 1, yuv_file);
    src += s->uv_stride;
  } while (--h);

  src = s->v_buffer;
  h = s->uv_crop_height;

  do {
    fread(src, s->uv_width, 1, yuv_file);
    src += s->uv_stride;
  } while (--h);

}

#endif
