# BlenderAssist

Based on [AnimAssist](https://github.com/lmcintyre/AnimAssist), but much more scuffed.

## Requirements
- [VC++2012 32-bit Redist](https://www.microsoft.com/en-us/download/details.aspx?id=30679#) (`VSU_4\vcredist_x86.exe`)
- [Blender](https://www.blender.org/)
- A way to replace an existing `.pap` files like Textools, Penumbra, or VFXEditor 

## Installation
Download the addon from the [releases](https://github.com/0ceal0t/BlenderAssist/releases). Go to `Edit > Preferences > Add-ons`, press "Install" and select the entire `.zip` file. Make sure to enable the add-on as well.

![image](https://user-images.githubusercontent.com/18051158/162598790-56386e08-6182-4691-90b3-ebfc0f88cf9f.png)

## Usage

First, find the `.pap` file of an animation that you want to replace (using a tool like [FFXIVExplorer](https://github.com/goaaats/ffxiv-explorer-fork/tree/index2)), as well as the corresponding `.sklb` skeleton file. For example:

```
chara/human/c1101/skeleton/base/b0001/skl_c1101b0001.sklb
chara/human/c1101/animation/a0001/bt_common/emote/joy.pap
```
Make sure that the ids of the skeleton and the animation match up (in this case `c1101`), and extract both of these files using Textools, FFXIVExplorer, etc.

Once you have an animation you want to export, select the armature and open the "BlenderAssist" menu in 3D view (default keybind is "N"), or press the left-facing arrow at the top-right of the 3D view.

Configure the parameters to your liking, **making sure to select the original .pap and .sklb files**. Make sure the animation index also matches that of the animation you want to replace. Most `.pap` files only have a single animation, so leaving it at `0` is fine, but make sure to double-check.

![image](https://user-images.githubusercontent.com/18051158/162598885-6a85dc66-ac38-4f3b-8501-ab7abc2f5ed3.png)

And import the outputed `.pap` using your modding tool of choice.

https://user-images.githubusercontent.com/18051158/162326495-ab9ba1c2-fc88-4068-a53d-bf8dd50c83e2.mp4

## Porting Animations
When importing animations from MMD, other games, etc. it's generally a good idea to use a [bone remapping tool](https://github.com/Mwni/blender-animation-retargeting). A small caveat for this specific ones is that it will not work unless just adjust the "Rest alignment" of one of the bones you have mapped. For example, my mapping is:

![image](https://user-images.githubusercontent.com/18051158/162326747-87837006-276d-4436-ba15-6abe2b23652f.png)

So when setting the "Rest alignment", I just wiggled `n_hara` slightly. Also make sure to resize the animation source armature so that is rougly the same size as your target:

![image](https://user-images.githubusercontent.com/18051158/162326875-74f1c72d-999c-4cd8-a882-4d382ec65c92.png)

## TMB and PAP Files
There are parameters in both the `.pap` and `.tmb` files which determine how long an animation is allowed to play, so you may need to adjust them. In addition `.tmb` files often have facial expressions which you may want to remove or adjust using [VFXEditor](https://github.com/0ceal0t/Dalamud-VFXEditor)

## Notes on Building

This is taken verbatim from [AnimAssist](https://github.com/lmcintyre/AnimAssist#building):

> Building animassist.exe requires the Havok 2014 SDK and an env var of HAVOK_SDK_ROOT set to the directory, as well as the Visual C++ Platform Toolset v110. This is included in any install of VS2012, including the Community edition. You can find the Havok SDK to compile with in the description of [this video](https://www.youtube.com/watch?v=U88C9K-mSHs). Please note that is NOT a download I control, just a random one from online.

Make sure to set your `HAVOK_SDK_ROOT` like this:

![image](https://user-images.githubusercontent.com/18051158/162323294-f6eacc56-7efc-4cf4-9247-ac3888ee865a.png)
