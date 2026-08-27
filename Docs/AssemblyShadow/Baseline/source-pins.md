# M00 source baseline

The machine-readable build pairing is
`ProjectSettings/AssemblyShadowSourcePins.json`. Branch names are navigation aids,
not reproducible versions. All tags and commits created by this task are local;
no remote publication is implied.

## Initial inventory, 2026-08-27

| Repository | Initial branch | Initial exact commit | Initial dirty state |
| --- | --- | --- | --- |
| hybridclr_demo | main | 8b8d60e77b998a6dbc0c6a508b8d36a46feec2b3 | Renderer2D.asset modified; .DS_Store and Assets/Editor.meta untracked |
| hybridclr_unity | main | fd32708e7f5106f0ffa375bcfe43342ee594c1e5 | clean |
| hybridclr | main | 210cbe0ecc878a6ab7e392b1ce191a46d509ba25 | clean |
| il2cpp_plus | 2022-3.x | 54db003dc8294524ed21c4b0ebec92b5e9c02b08 | clean |

Initial commit dates respectively: 2026-08-27T02:04:45-07:00,
2026-08-20T08:49:48+08:00, 2026-08-20T09:08:04+08:00,
2023-09-18T23:44:25+08:00.

Each initial origin is `git@github.com:night-outlook/<repository>.git`.
No upstream remote was initially configured. M00 adds
`https://github.com/focus-creative-games/il2cpp_plus.git` as il2cpp_plus upstream.
The package selects upstream tag v2022-8.14.0, exact commit
11251b938d2ce7fa865165130bf257ca239db69f, not the old 2022-3.x checkout.
The runtime main source is byte-identical to v8.13.0
(b33f823982c52587f6c0c909227b2347c88764ff) except for README.md and README_EN.md;
the tag-to-main diff contains no runtime changes.

## Preservation and branch boundaries

The original demo at `/Users/ah/GitHub/hybridclr/hybridclr_demo` and its already-open
Unity Editor are preserved. Its three pre-existing changes were snapshotted in
backup branch `codex/assembly-shadow-preexisting-20260827`, commit
a74182b8ea52c805b24615ae31669e3cc06fc87d. This snapshot
did not change the original index or working files.

Implementation and unattended Unity builds use the clean worktree
`/Users/ah/GitHub/hybridclr/hybridclr_demo_shadow`. M00 uses
`codex/assembly-shadow-m00` in each repository; M01 starts a separate
`codex/assembly-shadow-m01` branch only after the M00 boundary is accepted.

The demo's pin identifies a build-source commit. A subsequent metadata-only
commit can record that pin and its evidence. Requiring a file to contain its own
commit SHA would be circular. The strict verifier compares the actual build
inputs to the source pin while allowing only the pin file and milestone records
to advance; it must not treat arbitrary source changes as metadata.

## Host and target

- Unity: 2022.3.62f2, revision 7670c08855a9.
- Host: macOS 26.5.2 (25F84), ARM64.
- Native compiler: Apple clang 21.0.0 (clang-2100.1.1.101).
- SDK: `/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk`.
- Target: StandaloneOSX, ARM64, IL2CPP, Development, native Debug configuration.
- IL2CPP support for macOS ARM64 is installed. Windows/Android support is not
  installed on this host. Full Xcode is absent; build evidence, not its absence
  alone, decides whether the installed Command Line Tools suffice.

Using macOS as the first executable IL2CPP target is a documented platform
deviation from the recommendation to start on Windows x64. It is not a claim
that Windows or Android has been tested.

## Reproduction and evidence

Run `Tools/AssemblyShadow/print-source-pins.sh` (or .ps1) for live revisions,
branches and working-copy state. The final M00 report records the build-source
pin, installation receipt, Player results, cache rebuild and review evidence.
M00 is not accepted merely because these source pins exist.
