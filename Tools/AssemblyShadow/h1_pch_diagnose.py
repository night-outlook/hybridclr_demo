#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
import h1_native_capture as n
import h1_pch_provenance as p

def diagnose(request_path, graph_path, output):
    output = Path(output); attempt = n.CaptureAttempt(output, "H1PchDiagnosticReplayAttempt")
    summary = {"kind": "H1PchDiagnosticReplay", "status": "Blocked", "diagnosticOnly": True,
               "freshBuildClaim": False, "humanGatePassed": False, "mayEnterR02": False}
    try:
        attempt.stage("request-and-graph-retention")
        request_path = n.canonical_file(str(request_path)); graph_path = n.canonical_file(str(graph_path))
        request_bytes = request_path.read_bytes(); graph_bytes = graph_path.read_bytes()
        n.write_new(output / "original-request.json", request_bytes); n.write_new(output / "original-graph.json", graph_bytes)
        request = json.loads(request_bytes.decode("utf-8-sig"), object_pairs_hook=n.unique_pairs)
        graph = json.loads(graph_bytes.decode("utf-8-sig"), object_pairs_hook=n.unique_pairs)
        root = Path(request["projectRoot"]); p.a.need(root.is_absolute() and root == root.resolve(strict=True), "Original project root unavailable")
        native = n.canonical_file(request["nativeLibraryPath"]); config = n.canonical_file(request["il2cppConfigPath"]); config_bytes = config.read_bytes()
        n.write_new(output / "il2cpp-config.h", config_bytes); p.a.need(n.digest(native) == request["nativeLibrarySha256"], "Selected failed native output bytes differ")
        attempt.stage("preplan-input-retention"); n._retain_plan_inputs(graph, root, output); responses = n.collect_responses(graph, root)
        for i, (source, data) in enumerate(sorted(responses.items())): n.write_new(output / "response-files" / ("%04d.rsp" % i), data)
        attempt.stage("planning"); blueprint = p.plan(graph, root, native, config_bytes.decode("utf-8"), responses, request["featureEnabled"], p.a.H1_APPLE_BEE_DOMAIN_POLICY)
        binding = {**{k: request[k] for k in p.BINDINGS}, "graphSha256": p.sha(graph_bytes), "projectRoot": str(root),
                   "featureEnabled": request["featureEnabled"], "cppConfiguration": request["cppConfiguration"],
                   "diagnosticOnly": True, "replayedRequestSha256": p.sha(request_bytes),
                   "macroDomainPolicy": p.a.H1_APPLE_BEE_DOMAIN_POLICY}
        attempt.stage("pch-execution", pchReplay="Invoked", macroProbes="Invoked")
        proof = p.capture(blueprint, graph, root, str(config), binding, output / "pch", responses)
        p.verify(proof, graph, root, native, config_bytes.decode("utf-8"), responses, binding)
        summary.update(status="DiagnosticReplayVerifiedNotBuildAccepted", proofPath=str(output / "pch/pch-proof.json"), proofSha256=n.digest(output / "pch/pch-proof.json"))
        attempt.stage("completed", pchReplay="Completed", macroProbes="Completed")
    except (OSError, ValueError, KeyError, TypeError) as error:
        summary.update(error=str(error), errorType=type(error).__name__, failedStage=attempt.state["stage"])
        n.write_new(output / "diagnostic-result.json", (json.dumps(summary, indent=2) + "\n").encode()); attempt.failure(error); raise
    n.write_new(output / "diagnostic-result.json", (json.dumps(summary, indent=2) + "\n").encode()); return summary

def main():
    q=argparse.ArgumentParser(); q.add_argument("--request",type=Path,required=True); q.add_argument("--graph",type=Path,required=True); q.add_argument("--output",type=Path,required=True)
    x=q.parse_args(); print(json.dumps(diagnose(x.request,x.graph,x.output),indent=2)); return 0
if __name__ == "__main__":
    try: raise SystemExit(main())
    except (OSError, ValueError, KeyError, TypeError) as error: print("Blocked diagnostic replay: " + str(error), file=__import__("sys").stderr); raise SystemExit(1)
