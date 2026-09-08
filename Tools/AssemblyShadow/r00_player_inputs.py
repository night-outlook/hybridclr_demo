"""Bind fresh R00 observations to the actual current four-repository pairing."""
from pathlib import Path

import m07_results as m07
from shadow_tools import PINS, read_json, require, verify


def require_current_pairing(expected, captured, label):
    # Demo is deliberately included: RuntimeAbiHash excludes it and therefore
    # cannot by itself establish the source that produced the Player.
    m07.prior._pins(captured, label, expected)
    m07.exact(captured, expected, label + ".sourcePins")


def verify_inputs(project, fixture_manifest, on_path, off_path, replay_path):
    project = Path(project).resolve(strict=True)
    installed = verify(project, expected_shadow="on")
    pins = read_json(project / PINS)
    manifest, baseline, fixtures, rejected, resources = m07.verify_inputs(fixture_manifest)
    require_current_pairing(pins, baseline["sourcePins"], "R00 baseline")
    on = m07.verify_player(on_path, manifest, baseline, resources, "NativeOn")
    off = m07.verify_player(off_path, manifest, baseline, resources, "NativeOff")
    for name, build in (("NativeOn", on), ("NativeOff", off)):
        require_current_pairing(pins, build["snapshot"]["sourcePins"], "R00 " + name)
        require(build["output"].is_relative_to(project / "Builds/AssemblyShadow/M07"),
                "R00 Player is outside the current integration project")
    for key in ("inputSnapshotHash", "nativeLibrarySha256", "buildGuid"):
        require(on["player"][key] != off["player"][key], "R00 ON/OFF must be distinct: " + key)
    m07.exact(m07.managed_player_inputs(on["snapshot"], on["path"]),
              m07.managed_player_inputs(off["snapshot"], off["path"]), "R00 ON/OFF managed inputs")
    m07.exact(on["path"], Path(manifest["playerBuildReceiptPath"]), "R00 manifest ON receipt")
    m07.exact(m07.digest(on["path"]), manifest["playerBuildReceiptSha256"], "R00 manifest ON receipt hash")
    m07.verify_replay(replay_path, manifest, baseline, fixtures, rejected, on, resources)
    replay = read_json(Path(replay_path))
    require_current_pairing(pins, replay["validatorSourcePins"], "R00 Editor replay")
    return {"manifest": manifest, "baseline": baseline, "fixtures": fixtures,
            "on": on, "off": off, "sourcePins": pins, "installed": installed}
