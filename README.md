# BlenderAssist

Based on [AnimAssist](https://github.com/lmcintyre/AnimAssist), but much more scuffed.

## Requirements
- [VC++2012 32-bit Redist](https://www.microsoft.com/en-us/download/details.aspx?id=30679#) (`VSU_4\vcredist_x86.exe`)
- [Blender](https://www.blender.org/)
- A way to replace an existing `.pap` file like Textools, Penumbra, or VFXEditor 

## Usage
First, find the `.pap` file of an animation that you want to replace (using a tool like [FFXIVExplorer](https://github.com/goaaats/ffxiv-explorer-fork/tree/index2), as well as the corresponding `.sklb` skeleton file. For example:

```
chara/human/c1101/skeleton/base/b0001/skl_c1101b0001.sklb
chara/human/c1101/animation/a0001/bt_common/emote/joy.pap
```
Make sure that the ids of the skeleton and the animation match up (in this case `c1101`), and extract both of these files using Textools, FFXIVExplorer, etc.

## Custom Animations in Blender

## TMB and PAP Files

## Notes on Building

This is taken verbatim from [AnimAssist](https://github.com/lmcintyre/AnimAssist#building):

> Building animassist.exe requires the Havok 2014 SDK and an env var of HAVOK_SDK_ROOT set to the directory, as well as the Visual C++ Platform Toolset v110. This is included in any install of VS2012, including the Community edition. You can find the Havok SDK to compile with in the description of [this video](https://www.youtube.com/watch?v=U88C9K-mSHs). Please note that is NOT a download I control, just a random one from online.

Make sure to set your `HAVOK_SDK_ROOT` like this:

![image](https://user-images.githubusercontent.com/18051158/162323294-f6eacc56-7efc-4cf4-9247-ac3888ee865a.png)
