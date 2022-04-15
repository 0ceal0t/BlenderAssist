#ifndef BLENDERASSIST_PACK_ANIM_H
#define BLENDERASSIST_PACK_ANIM_H

#include <Common/Base/hkBase.h>
#include <Common/Base/Container/String/hkStringBuf.h>

int pack_anim(const hkStringBuf anim_idx_str, const hkStringBuf bin_in, const hkStringBuf skl_in, const hkStringBuf anim_in, const hkStringBuf anim_out, const hkStringBuf check_if_bound_str);

#endif //BLENDERASSIST_PACK_ANIM_H
