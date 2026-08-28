"""Task-local M05 evidence retention. Never edits an input or an existing output."""
import argparse
import datetime as dt
import gzip
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import tarfile

BUILD = "09a15e686a4e7581e362175f4aa99d6bde80de55"
VERIFIER = "6f0123839ba1fe01e18c29858b15fefc1cc7b12c"
BASELINE = "M05-Baseline-v6"


def require(value, message):
    if not value:
        raise RuntimeError(message)


def digest(stream):
    h = hashlib.sha256()
    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
        h.update(chunk)
    return h.hexdigest()


def sha(path):
    require(path.is_file() and not path.is_symlink(), "Not a regular input: " + str(path))
    with path.open("rb") as stream:
        return digest(stream)


def write_json(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def safe_name(name):
    p = PurePosixPath(name)
    require(not p.is_absolute() and ".." not in p.parts and str(p) == name,
            "Unsafe or noncanonical archive name: " + name)


def main(root, destination):
    require(root.is_absolute() and root.resolve() == root, "Canonical project path required")
    require(destination == root / "Docs/AssemblyShadow/M05/Evidence", "Only the new M05 evidence directory is authorized")
    require(not destination.exists() and not destination.is_symlink(), "Evidence destination already exists")
    tmp = root / "_temp/AssemblyShadow"
    players = tmp / "M05V6Execution-FlFy78z1/Players"
    offline = tmp / "M05OfflineVerifier-q5F4xoSu"
    integration = tmp / "M05Integration-8IdZleUf"
    native = tmp / "M05FinalNative-FOgff7G2"
    fixtures = tmp / "M05Fixtures-71857c4c1550462ab50b27cb2d4ab1d2"
    on = tmp / "M05PlayerInputs-97d90c0db2c74f71b59e69b5e7191124"
    off = tmp / "M05PlayerInputs-e2dfc5d856e74e439891f92930601711"
    editor = tmp / "EditorTests-10f9de99885d4bec8f700a946d9cd553"
    launch = json.loads((players / "player-launches.json").read_text())
    require(launch["completedModes"] == 19 and len(launch["processLaunches"]) == 19,
            "Incomplete Player launch inventory")
    require(len({p["processId"] for p in launch["processLaunches"]}) == 19,
            "Player cases must use distinct actual processes")
    require(launch["inputsUnchanged"] and launch["inputHashesBefore"] == launch["inputHashesAfter"],
            "Player inputs changed during execution")
    for process in launch["processLaunches"]:
        require(process["passed"] and process["exitCode"] == 0 and not process["timedOut"], "Failed Player process")
        require(sha(Path(process["resultPath"])) == process["resultSha256"], "Player result changed")
    files = []
    for path in sorted(players.rglob("*")):
        require(not path.is_symlink(), "Symlink in Player evidence")
        if path.is_dir():
            continue
        name = path.relative_to(players).as_posix()
        safe_name(name)
        files.append(dict(name=name, size=path.stat().st_size, sha256=sha(path)))
    require(len(files) == 76, "Expected exactly 76 actual Player files")
    require(sum(p["name"].startswith("Results/") and p["name"].endswith(".json") for p in files) == 37,
            "Expected 19 results plus 18 native diagnostics")
    plan = []

    def add(source, name, category, expected=None):
        safe_name(name)
        source = Path(source)
        require(source.is_relative_to(root), "Copy input must remain in the isolated project")
        require(source.resolve() == source, "Symlinked input path")
        value = sha(source)
        require(expected is None or value == expected, "Unexpected input hash: " + str(source))
        plan.append(dict(originalPath=str(source), name=name, category=category,
                         size=source.stat().st_size, sha256=value))

    add(root / "HybridCLRData/AssemblyShadow/Baselines/StandaloneOSX/M05-Baseline-v6/baseline-manifest.json",
        "baseline-manifest-v6.json", "frozen-build", "adde5a69362a79e7e51358bab6c65b89e0405ae90ea293753fb40b857e7c3f8d")
    add(fixtures / "m05-fixtures.json", "fixture-manifest-v6.json", "frozen-build",
        "11f5e31780c006ec541517c39689cea9bd5428e3e0e120e04fddf59f51344af7")
    add(fixtures / "m05-editor-replay.json", "editor-replay-v6.json", "editor-proof",
        "f39178e5a1ff7986faa62e1113f4bb20b9eaec06dfd1f40d3f0eefb53e5f984c")
    for label, path in (("on", on), ("off", off)):
        for source, target in (("m05-player-build.json", "build"), ("m05-type-proof.json", "type-proof"),
                               ("assembly-snapshot.json", "assembly-snapshot"),
                               ("LinkedPlayer/linked-player-receipt.json", "linked-player-receipt")):
            add(path / source, "native-" + label + "-" + target + "-v6.json", "frozen-build")
        add(path / "m05-placeholder-AssemblyManifest.cpp", "native-" + label + "-placeholder-v6.cpp", "frozen-build")
    add(editor / "results.xml", "editor-tests-v6.xml", "editor-proof",
        "8c5302d4f1ff60fc39f7c130bd74e10f4714ea1d70e21d30d7cc723712e095da")
    add(editor / "unity.log", "editor-tests-v6.unity.log", "editor-proof",
        "7c490d014f819dcc6f204cb70099d7ad0c2ea9af53c00f0c16ae4dde46fdcbf3")
    for name in ("corrective-validation.json", "m05-verification.json", "final-native-validation.json",
                 "source-equivalence-before-install.json", "source-equivalence-after-install.json",
                 "source-equivalence-final.json", "tooling-install-validation.json", "preservation-review.json",
                 "frozen-build-install-receipt.json", "frozen-build-install-repeatability.json"):
        add(offline / name, name, "verification-and-provenance")
    add(tmp / "m00-install-receipt.json", "tooling-install-receipt.json", "current-tooling-only",
        "d943c2051ac8573a10cfa95b16dd0e2bff28893b45766cdbd1e29f40b3f0410e")
    add(tmp / "m00-install-repeatability.json", "tooling-install-repeatability.json", "current-tooling-only")
    add(root / "ProjectSettings/AssemblyShadowSourcePins.json", "current-tooling-source-pins.json", "current-tooling-only")
    add(root / "ProjectSettings/AssemblyShadowRawTypeAdmissions.json", "raw-type-admission-configuration.json", "frozen-build",
        "d47806dc47b699aa3fb0ece4f285a158e4677e4b40c9ae23fb448929a7bed8a8")
    for name in ("m05-native-tests.json", "m03-native-tests.json", "visibility-native-tests.json", "m04-native-tests-ready.json"):
        require(json.loads((native / name).read_text())["success"], "Failed final native receipt")
        add(native / name, name, "final-native-proof")
    add(native / "m04-native-tests.json", "history/m04-native-ungenerated-header-failure.json", "preserved-failure")
    for name in ("v6-prebuild-validation.json", "v6-on-build-complete.json", "v6-off-build-complete.json",
                 "v6-fixture-build-complete.json", "v6-on-input-replay.json", "v6-on-off-pre-runtime-replay.json",
                 "v6-editor-replay-verification.json", "historical-preservation-during-v6-build.json"):
        add(integration / name, name, "build-and-replay-proof")
    for name in ("allocation-guard-source-review.json", "public-image-native-source-review.json",
                 "public-image-tooling-source-review.json", "v6-scene-source-review.json",
                 "v6-source-provenance-review.json", "namespace-source-review.json"):
        add(integration / name, "source-reviews/" + name, "bounded-source-readiness-only")
    add(integration / "v6-initial-strict-diagnostic.json", "history/v6-initial-strict-diagnostic.json", "preserved-failure")
    for folder, name in (("M05V5NestedAdmission-D0i51rDO", "v5-nested-admission.json"),
                         ("M05V5SerializationTrace-vewuQXGD", "v5-serialization-observations.json")):
        add(tmp / folder / "serialization-observations.json", "history/" + name, "preserved-failure-diagnosis")
    for stamp in ("064455", "064902", "065019", "065201", "065948", "070612", "072217", "080706", "081052"):
        name = "UnityExec_20260828_" + stamp + ".log"
        add(root / "_temp" / name, "build-logs/" + name, "guarded-unity-log")
    add(tmp / "M05Execution-kxsgu5Wq/run_players.py", "capture-run-players.py", "task-local-capture-script")
    add(offline / "audit_equivalence.py", "audit-source-equivalence.py", "task-local-capture-script")
    add(Path(__file__).resolve(), "archive-evidence.py", "task-local-capture-script")
    require(len({p["name"] for p in plan}) == len(plan), "Duplicate copy target")
    destination.mkdir()
    archive_path = destination / "player-results-v6-09a15e6.tar.gz"
    with archive_path.open("xb") as raw:
        with gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as archive:
                for entry in files:
                    archive.add(players / entry["name"], arcname=entry["name"], recursive=False)
    by_name = {entry["name"]: entry for entry in files}
    seen = set()
    with tarfile.open(archive_path, "r:gz") as archive:
        for member in archive:
            require(member.isfile() and member.name in by_name and member.name not in seen, "Unexpected archive member")
            expected = by_name[member.name]
            with archive.extractfile(member) as stream:
                require(member.size == expected["size"] and digest(stream) == expected["sha256"], "Archived bytes differ")
            seen.add(member.name)
    require(seen == set(by_name), "Incomplete archive")
    for entry in files:
        require(sha(players / entry["name"]) == entry["sha256"], "Original Player bytes changed during archive")
    archive_index = dict(schemaVersion=1, milestone="M05", baselineBuildId=BASELINE,
                         demoExecutableSourceCommit=BUILD, offlineVerifierRevision=VERIFIER,
                         sourceRoot=str(players), archivePath=str(archive_path), archiveSha256=sha(archive_path),
                         files=files, allArchivedBytesMatch=True)
    write_json(destination / "player-results-v6-09a15e6.index.json", archive_index)
    for entry in plan:
        source, target = Path(entry["originalPath"]), destination / entry["name"]
        target.parent.mkdir(parents=True, exist_ok=True)
        with source.open("rb") as incoming, target.open("xb") as outgoing:
            shutil.copyfileobj(incoming, outgoing)
        require(sha(source) == sha(target) == entry["sha256"] and target.stat().st_size == entry["size"],
                "Input/copy bytes changed: " + entry["name"])
        entry["path"] = str(target)
    index = dict(schemaVersion=1, milestone="M05", kind="LosslessEvidenceRetention", runtimeAcceptance=False,
                 recordedUtc=dt.datetime.now(dt.timezone.utc).isoformat(), baselineBuildId=BASELINE,
                 demoExecutableSourceCommit=BUILD, offlineVerifierRevision=VERIFIER,
                 archiveIndexPath=str(destination / "player-results-v6-09a15e6.index.json"),
                 archiveIndexSha256=sha(destination / "player-results-v6-09a15e6.index.json"),
                 archiveSha256=sha(archive_path), copiedArtifacts=plan, allCopiedBytesMatch=True,
                 limitation="Byte-identical retention, not relocated acceptance inputs or a portable deployment. Canonical DLL/native/snapshot graphs remain in their original immutable local roots. Independent gates are still required.")
    write_json(destination / "artifact-index-v6.json", index)
    print(json.dumps(dict(success=True, archiveFiles=len(files), copiedArtifacts=len(plan),
                          archiveBytes=archive_path.stat().st_size, archiveSha256=index["archiveSha256"],
                          indexSha256=sha(destination / "artifact-index-v6.json"), destination=str(destination))))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True)
    args = parser.parse_args()
    main(args.project_root, args.project_root / "Docs/AssemblyShadow/M05/Evidence")
