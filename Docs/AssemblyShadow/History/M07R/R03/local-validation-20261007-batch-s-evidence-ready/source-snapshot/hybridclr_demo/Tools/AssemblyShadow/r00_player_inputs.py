"""Bind R00 observations to the authenticated four-repository pairing."""
from pathlib import Path

import m07_results as m07
from shadow_tools import PINS, read_json, require, verify


REUSE_AUTHORITY_KIND = "H1AuthenticatedGraphReuseAuthority"


def require_current_pairing(expected, captured, label):
    # Demo is deliberately included: RuntimeAbiHash excludes it and therefore
    # cannot by itself establish the source that produced the Player.
    m07.prior._pins(captured, label, expected)
    m07.exact(captured, expected, label + ".sourcePins")


def _verify_inputs(project, fixture_manifest, on_path, off_path, replay_path, expected_pins):
    project = Path(project).resolve(strict=True)
    installed = verify(project, expected_shadow="on")
    current_pins = read_json(project / PINS)
    manifest, baseline, fixtures, rejected, resources = m07.verify_inputs(fixture_manifest)
    require_current_pairing(expected_pins, baseline["sourcePins"], "R00 baseline")
    m07.prepare_fixture_resources(manifest, baseline, fixtures, resources)
    on = m07.verify_player(on_path, manifest, baseline, resources, "NativeOn")
    off = m07.verify_player(off_path, manifest, baseline, resources, "NativeOff")
    for name, build in (("NativeOn", on), ("NativeOff", off)):
        require_current_pairing(expected_pins, build["snapshot"]["sourcePins"], "R00 " + name)
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
    require_current_pairing(expected_pins, replay["validatorSourcePins"], "R00 Editor replay")
    return {"manifest": manifest, "baseline": baseline, "fixtures": fixtures,
            "on": on, "off": off, "sourcePins": expected_pins,
            "currentSourcePins": current_pins, "installed": installed}


def verify_inputs(project, fixture_manifest, on_path, off_path, replay_path):
    """Default R00 contract: graph source pins must equal the current project pins."""
    project = Path(project).resolve(strict=True)
    pins = read_json(project / PINS)
    return _verify_inputs(project, fixture_manifest, on_path, off_path, replay_path, pins)


def verify_inputs_with_reuse(project, fixture_manifest, on_path, off_path, replay_path, authority):
    """Strictly verify a retained graph only under a separately authenticated reuse authority."""
    project = Path(project).resolve(strict=True)
    require(type(authority) is dict and authority.get("kind") == REUSE_AUTHORITY_KIND,
            "R00 retained graph requires an authenticated reuse authority")
    require(authority.get("projectRoot") == str(project),
            "R00 retained graph authority project mismatch")
    graph_pins = authority.get("graphSourcePins")
    current_pins = authority.get("currentSourcePins")
    require(type(graph_pins) is dict and type(current_pins) is dict,
            "R00 retained graph authority source pins are incomplete")
    require(read_json(project / PINS) == current_pins,
            "R00 retained graph authority no longer matches current project pins")
    require(authority.get("bridgeReceipt"),
            "R00 retained graph authority is not bound to a bridge receipt")
    return _verify_inputs(project, fixture_manifest, on_path, off_path, replay_path, graph_pins)
