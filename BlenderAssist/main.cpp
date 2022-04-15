#include <cstdio>
#include <vector>

#include <Common/Base/hkBase.h>
#include <Common/Base/Memory/System/Util/hkMemoryInitUtil.h>
#include <Common/Base/Reflection/Registry/hkDefaultClassNameRegistry.h>
#include <Common/Serialize/Version/hkVersionPatchManager.h>
#include <Common/Base/Reflection/hkInternalClassMember.h>
#include <Common/Serialize/Util/hkSerializeDeprecated.h>

#include <shellapi.h>
#include <locale>
#include <codecvt>

#include "Common/Base/System/Init/PlatformInit.cxx"
#include "pack_anim.h"
#include "extract.h"

static void HK_CALL errorReport(const char* msg, void* userContext) {
    using namespace std;
    printf("%s", msg);
}

void init() {
    PlatformInit();
    hkMemoryRouter* memoryRouter = hkMemoryInitUtil::initDefault(hkMallocAllocator::m_defaultMallocAllocator, hkMemorySystem::FrameInfo(1024 * 1024));
    hkBaseSystem::init(memoryRouter, errorReport);
    PlatformFileSystemInit();
    hkSerializeDeprecatedInit::initDeprecated();
}

inline std::string convert_from_wstring(const std::wstring &wstr) {
    std::wstring_convert<std::codecvt_utf8_utf16<wchar_t>, wchar_t> conv;
    return conv.to_bytes(wstr);
}

int main(int argc, const char** argv) {
    int nargc = 0;
    wchar_t** nargv;

    auto command_line = GetCommandLineW();
    if (command_line == nullptr) {
        printf("Fatal error.");
        return 1;
    }
    nargv = CommandLineToArgvW(command_line, &nargc);
    if (nargv == nullptr) {
        printf("Fatal error.");
        return 1;
    }

    // ===========================

    init();

    std::string operation(convert_from_wstring(nargv[1]).c_str());

    // blenderassist.exe pack anim_idx .bin sklb pap out.pap
    if (operation.compare("pack_anim") == 0) {
        hkStringBuf anim_idx; // animation index
        hkStringBuf bin_in; // .bin from blender
        hkStringBuf skl_in; // original skeleton
        hkStringBuf anim_in; // original animation
        hkStringBuf anim_out; // pap animation out
        hkStringBuf check_if_bound;

        anim_idx = convert_from_wstring(nargv[2]).c_str();
        bin_in = convert_from_wstring(nargv[3]).c_str();
        skl_in = convert_from_wstring(nargv[4]).c_str();
        anim_in = convert_from_wstring(nargv[5]).c_str();
        anim_out = convert_from_wstring(nargv[6]).c_str();
        check_if_bound = convert_from_wstring(nargv[7]).c_str();

        return pack_anim(anim_idx, bin_in, skl_in, anim_in, anim_out, check_if_bound);
    }
    else if (operation.compare("extract") == 0) {
        hkStringBuf skl_in_sklb;
        hkStringBuf anim_in_pap;
        hkStringBuf sklb_out;
        hkStringBuf pap_out;

        skl_in_sklb = convert_from_wstring(nargv[2]).c_str();
        anim_in_pap = convert_from_wstring(nargv[3]).c_str();
        sklb_out = convert_from_wstring(nargv[4]).c_str();
        pap_out = convert_from_wstring(nargv[5]).c_str();

        return extract(skl_in_sklb, anim_in_pap, sklb_out, pap_out);
    }

    printf("No operation given\n");
    return 0;
}

#include <Common/Base/keycode.cxx>

#undef HK_FEATURE_PRODUCT_AI
//#undef HK_FEATURE_PRODUCT_ANIMATION
#undef HK_FEATURE_PRODUCT_CLOTH
#undef HK_FEATURE_PRODUCT_DESTRUCTION_2012
#undef HK_FEATURE_PRODUCT_DESTRUCTION
#undef HK_FEATURE_PRODUCT_BEHAVIOR
#undef HK_FEATURE_PRODUCT_PHYSICS_2012
#undef HK_FEATURE_PRODUCT_SIMULATION
#undef HK_FEATURE_PRODUCT_PHYSICS

#define HK_SERIALIZE_MIN_COMPATIBLE_VERSION 201130r1

#include <Common/Base/Config/hkProductFeatures.cxx>