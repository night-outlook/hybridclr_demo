#!/usr/bin/env python3
"""Conditional fresh IR terminal Player batch with the existing R03 LQ storage policy.

Default is diagnostics-only. --execute requires fresh admission and is valid
only after a separately published Primary -> Local Validation handoff.
No S/R/Q/P/O/N batch is rerun or modified. Do not retry failed cells.
"""
import argparse
import json
import os
from pathlib import Path
import re
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "R03Storage"))
sys.path.insert(0, str(HERE.parent / "R03"))
import storage_guard as storage
from run_local import identity, git, REPOS
from batch_contract import loads
from run_terminal_local import Batch, execute

EXPECTED_CELLS = 1 + 1 + 1 + 1 + 3 * 2 + 4  # authority, S, tool, target, 3 builds, 4 Players


class ObservedTerminalBatch(Batch):
    def __init__(self, *args, session):
        self.storage_session = session
        self.storage_phase = "constructor"
        super().__init__(*args)

    def cell(self, name, action, dependencies=()):
        def checked():
            self.storage_phase = name
            try:
                self.storage_session.before(name)
                return action()
            except BaseException as error:
                self.storage_session.record_failure(name, error)
                raise
            finally:
                self.storage_session.observe("cell-after")
        return super().cell(name, checked, dependencies)

    def command(self, args, timeout=600):
        phase = self.storage_phase + "/command-" + str(self.command_count + 1)
        try:
            self.storage_session.before(phase)
            return super().command(args, timeout)
        except BaseException as error:
            self.storage_session.record_failure(phase, error)
            raise
        finally:
            self.storage_session.observe("command-after")


def validate_locations(workspace, output, evidence, retained):
    paths = tuple(map(storage.canonical, (workspace, output, evidence, retained)))
    workspace, output, evidence, retained = paths
    storage.require(workspace.is_dir() and retained.is_dir(),
                    "Existing owning workspace and retained Q required")
    for path in (output, evidence):
        storage.require(not path.exists() and path.parent.is_dir(),
                        "Unused immediate output under existing parent required: " + str(path))
        storage.require(not path.is_relative_to(workspace) and
                        not workspace.is_relative_to(path),
                        "External output cannot overlap Git workspace")
        storage.require(not path.is_relative_to(retained) and
                        not retained.is_relative_to(path),
                        "Never nest new outputs in retained Q")
    storage.require(not output.is_relative_to(evidence) and
                    not evidence.is_relative_to(output),
                    "Storage evidence must remain outside sealed IR root")
    storage.require(not retained.is_relative_to(workspace) and
                    not workspace.is_relative_to(retained),
                    "Retained Q is a separate historical root")
    return paths


def source_authority(workspace, expected_demo):
    storage.require(re.fullmatch(r"[0-9a-f]{40}", expected_demo) is not None,
                    "Exact pushed demo SHA required")
    storage.require(HERE == workspace / "hybridclr_demo/Tools/AssemblyShadow/R03IR",
                    "Run this entry point from the original owning demo checkout")
    pins = loads((HERE.parent / "R03/source-pins.json").read_text())
    pins = dict(pins, hybridclr_demo=expected_demo)
    rows = [identity(workspace / name, pins[name]) for name in REPOS]
    files = [
        HERE / "run_terminal_local.py",
        HERE / "run_terminal_storage_checked.py",
        HERE / "ir_original_fixtures.py",
        HERE / "test_ir_original_fixtures.py",
        HERE / "test_terminal_storage_checked.py",
        HERE / "PlayerProject/R03TerminalPlayer.cs",
        HERE / "test_terminal_contract.py",
        HERE.parent / "R03/source-pins.json",
        HERE.parent / "R03/PlayerProject/AssemblyShadowR03Probe.cpp",
        HERE.parent / "R03/PlayerProject/R03Build.cs",
        HERE.parent / "R03/PlayerFixtures/Program.cs",
        HERE.parent / "R03/PlayerFixtures/PlayerFixtures.csproj",
        HERE.parent / "R03/Fixtures/EvolutionFixtureCorpus.cs",
        HERE.parent / "R03/run_local.py",
        HERE.parent / "R03/batch_contract.py",
        HERE.parent / "R03Storage/storage_guard.py",
        workspace / "hybridclr_demo/Docs/AssemblyShadow/History/M07R/R03/local-validation-20261007-batch-s-evidence-ready/batch/host/player-fixtures/inventory.json",
        workspace / "hybridclr_demo/Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md",
    ]
    return {"kind":"R03IRPreflightExactSource","repositories":rows,"sourceFiles":
        [{"path":str(f),"sha256":storage.digest(f)} for f in files],
        "historicalInputsModified":False,"R03Accepted":False,"H2Passed":False}


def run(args):
    storage.require(sys.platform == "darwin", "Local IR storage admission is macOS only")
    workspace, output, evidence, retained = validate_locations(
        args.workspace, args.output, args.storage_evidence, args.retained_q)
    authority = source_authority(workspace, args.demo_commit)
    paths = {
        "batch": output, "workspace": workspace,
        "childTemp": Path("/private/tmp"),
        "pythonTemp": Path(tempfile.gettempdir()).resolve(),
        "sidecar": evidence,
        "irFixture": output / "host/ir-side-effect",
        "historicalSInputs": workspace / "hybridclr_demo/Docs/AssemblyShadow/History/M07R/R03/local-validation-20261007-batch-s-evidence-ready/batch/host/player-fixtures",
    }
    for name in REPOS:
        repo = workspace / name
        common = Path(git(repo, "rev-parse", "--git-common-dir"))
        paths["gitCommon-" + name] = (repo / common).resolve() if not common.is_absolute() else common.resolve()
    session = storage.StorageSession(evidence, paths)
    started, exit_code = False, 2
    try:
        storage.write_new(evidence / "source-authority.json", authority)
        admission = session.admit(retained)
        print(json.dumps({"storageAdmission":admission["state"],
                          "batchStarted":False,
                          "requiredAvailableBytesEachLocation":admission.get("requiredAvailableBytesEachLocation"),
                          "evidence":str(evidence)},sort_keys=True),flush=True)
        if admission["state"] != "Admitted":
            exit_code = 2
        elif not args.execute:
            exit_code = 0
        else:
            sampled = session.observe("immediately-before-constructor")
            storage.require(sampled is not None and session.problem is None,
                            "Storage observations lost before launch")
            storage.capacity_ok(sampled,
                admission["requiredAvailableBytesEachLocation"],session.devices)
            storage.require(not output.exists(), "IR output appeared during admission")
            session.start()
            storage.write_new(evidence / "launch-intent.json", {
                "entryPoint":str(HERE/"run_terminal_storage_checked.py"),
                "coreEntryPoint":str(HERE/"run_terminal_local.py"),
                "demoCommit":args.demo_commit,"workspace":str(workspace),
                "output":str(output),"unity":str(args.unity),
                "retainedQ":str(retained),"pid":os.getpid(),
                "expectedCells":EXPECTED_CELLS,"plannedFreshBuilds":3,
                "plannedFreshPlayers":4,"startedUtc":storage.utc(),
                "runtimeAcceptance":False})
            started=True
            exit_code=execute(workspace,output,args.unity,args.demo_commit,
                batch_type=lambda *v: ObservedTerminalBatch(*v,session=session))
            for f in authority["sourceFiles"]:
                storage.require(storage.digest(f["path"])==f["sha256"],
                                "Source bytes changed during focused execution")
    except BaseException as error:
        exit_code=1 if started else 2
        session.record_failure("entry-point",error)
        raise
    finally:
        report=session.finish(batch_started=started,batch_exit=exit_code if started else None)
        result=output/"LOCAL_BATCH_RESULT.json"
        storage.write_new(evidence/"dispatch.json",{
            "batchStarted":started,"batchExitCode":exit_code if started else None,
            "coreResultPath":str(result) if result.is_file() else None,
            "coreResultSha256":storage.digest(result) if result.is_file() else None,
            "sessionSha256":storage.digest(evidence/"session.json"),
            "storageState":report["state"],
            "originalSBatchReplayed":False,"runtimeAcceptance":False,
            "R03Accepted":False,"H2Passed":False,
            "qualificationApproved":False,"pureInterpreterExpansionEnabled":False})
    return exit_code if not started or report["state"] == "Passed" else 1


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ("workspace","output","unity","demo-commit","storage-evidence","retained-q"):
        parser.add_argument("--"+key,required=True)
    parser.add_argument("--execute",action="store_true",
                        help="Only for an explicitly published, single-use Local assignment")
    try:
        raise SystemExit(run(parser.parse_args()))
    except storage.StorageBlocked as error:
        print("BLOCKED: "+str(error),file=sys.stderr)
        raise SystemExit(2)
