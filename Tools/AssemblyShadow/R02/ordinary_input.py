"""Authenticate workspace-generated M00 input without changing its frozen hash."""
from pathlib import Path
from evidence import binding, check_binding, read, require
from h1_witness_contract import IMAGE_PATH, IMAGE_SHA256

SOURCE = "Assets/AssemblyShadowBaseline/HotUpdate"


def preflight(project, output):
    require(project == project.resolve(strict=True), "Canonical ordinary-input project required")
    require(output.parent == project / "_temp/AssemblyShadow" and not output.exists(), "Unused ordinary-input root required")
    for path in (project / SOURCE).rglob("*"):
        if path.suffix in (".cs", ".asmdef"):
            binding(path)
    destination = project / IMAGE_PATH
    for path in (output, destination):
        require(not path.is_symlink() and all(not p.is_symlink() for p in path.parents), "Linked ordinary-input path")
    if destination.exists():
        require(binding(destination)["sha256"] == IMAGE_SHA256, "Existing M00 input differs; preserve it")


def verify(project, output):
    receipt = read(output / "preparation.json")
    require(receipt.get("kind") == "R02OrdinaryInputPreparation" and receipt.get("schemaVersion") == 1 and
            receipt.get("result") == "Passed", "Ordinary-input preparation did not pass")
    require(receipt.get("projectRoot") == str(project) and receipt.get("outputRoot") == str(output), "Wrong workspace/output in ordinary-input receipt")
    require(receipt.get("unityVersion") == "2022.3.62f2" and receipt.get("target") == "StandaloneOSX" and
            receipt.get("development") is True, "Wrong ordinary-input compiler configuration")
    require(receipt.get("classification") == "CurrentWorkspaceCompilerOutput" and
            receipt.get("freshCscExecutionClaimed") is False and receipt.get("runtimeAcceptance") is False,
            "Invalid ordinary-input execution claim")
    require(receipt.get("expectedSha256") == IMAGE_SHA256 and receipt.get("sourcePinsSha256") ==
            binding(project / "ProjectSettings/AssemblyShadowSourcePins.json")["sha256"], "Ordinary-input contract/pins changed")
    expected = {str(p) for p in (project / SOURCE).rglob("*") if p.suffix in (".cs", ".asmdef")}
    rows = receipt.get("sources", [])
    require(expected and len(rows) == len(expected) and {r["path"] for r in rows} == expected, "Ordinary source set incomplete/duplicated")
    for row in rows:
        check_binding(row)
    for key, path in (("compiled", output / "compiled/AssemblyShadowBaseline.HotUpdate.dll"),
                      ("staged", project / IMAGE_PATH)):
        row = receipt[key]
        require(row["path"] == str(path) and row["sha256"] == IMAGE_SHA256, "Wrong ordinary input bytes/path")
        check_binding(row)
    return {"kind": "R02OrdinaryInputAuthentication", "result": "Passed", "projectRoot": str(project),
            "receipt": binding(output / "preparation.json"), "staged": receipt["staged"],
            "runtimeAcceptance": False}
