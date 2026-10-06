using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using HybridCLR;
using UnityEngine;
using UnityEngine.Scripting;
using Process = System.Diagnostics.Process;
using UnityDebug = UnityEngine.Debug;

namespace AssemblyShadowDemo
{
    /// <summary>Fresh-process H1 parameter and nested-count diagnostic runner.</summary>
    [Preserve]
    public sealed class H1CountDiagnosticRunner : MonoBehaviour
    {
        [SerializeField] public string expectedBaselineBuildId;
        [SerializeField] public string expectedRuntimeAbiHash;
        [SerializeField] public bool expectedFeatureEnabled;
        [SerializeField] public string expectedCppConfiguration;

        private void Awake() { DontDestroyOnLoad(gameObject); }

        private IEnumerator Start()
        {
            int exitCode = 2;
            try
            {
                exitCode = H1CountDiagnosticProbe.RunAndWrite(
                    expectedBaselineBuildId, expectedRuntimeAbiHash,
                    expectedFeatureEnabled, expectedCppConfiguration);
            }
            catch (Exception error)
            {
                UnityDebug.LogException(error);
            }
#if !UNITY_EDITOR
            Application.Quit(exitCode);
#endif
            yield break;
        }
    }

    internal static class H1CountDiagnosticProbe
    {
        private const int SchemaVersion = 2;
        private const long MaxFixtureBytes = 32L * 1024L * 1024L;
        private const string ResultKind = "H1CountDiagnosticResult";
        private const string ShadowParameterAssembly = "AssemblyShadow.H1Count.Target";
        private const string ShadowNestedAssembly = "AssemblyShadow.H1Nested.Target";
        private const string StableAotName = "mscorlib";
        private static H1CountEarlyStartup.Receipt s_earlyReceipt;

        internal static int RunAndWrite(string expectedBaselineBuildId, string expectedRuntimeAbiHash,
            bool expectedFeatureEnabled, string expectedCppConfiguration)
        {
            H1CountDiagnosticResult result = NewResult(expectedBaselineBuildId, expectedRuntimeAbiHash,
                expectedFeatureEnabled, expectedCppConfiguration);
            s_earlyReceipt = null;
            string outputPath = null;
            try
            {
                outputPath = RequiredArgument("-shadowH1Result");
                result.resultPath = outputPath;
                ValidateNewAbsolutePath(outputPath);
                result.family = RequiredArgument("-shadowH1Family");
                result.path = RequiredArgument("-shadowH1Path");
                result.caseId = RequiredArgument("-shadowH1Case");
                result.fixturePath = RequiredArgument("-shadowH1Fixture");
                result.fixtureSha256Expected = RequiredArgument("-shadowH1FixtureSha256");
                ValidateEnum(result.family, "parameters", "nested", "family");
                ValidateEnum(result.path, "ordinary", "shadow", "path");
                CaseSpec spec = FindCase(result.family, result.caseId);
                if (spec == null) throw new InvalidOperationException("Unknown H1 canonical case: " + result.caseId);
                result.expectedOutcome = spec.accepted ? "Accepted" : "ControlledRejected";
                result.expectedCount = spec.count;
                result.fixturePath = RequireAbsoluteFile(result.fixturePath);
                long fixtureSize;
                byte[] dllBytes = ReadBoundedFixture(result.fixturePath, out fixtureSize);
                result.fixtureSize = fixtureSize;
                result.inputHashBefore = Sha256(dllBytes);
                RequireSha256(result.fixtureSha256Expected, result.inputHashBefore);

                ValidateBuildInputs(result);
                if (result.path == "shadow")
                {
                    s_earlyReceipt = ConsumeEarlyReceipt(result);
                    result.witness = WitnessObservation(s_earlyReceipt.witness);
                    AddConsumedEarlySnapshot(result, s_earlyReceipt, "before");
                }
                else
                {
                    result.witness = WitnessObservation(H1CountEarlyStartup.LoadOrdinaryWitness());
                    CaptureNativeSnapshot(result, "before");
                }

                if (result.path == "ordinary") RunOrdinary(result, spec, dllBytes);
                else RunShadow(result, spec, dllBytes);

                long afterSize;
                byte[] afterBytes = ReadBoundedFixture(result.fixturePath, out afterSize);
                if (afterSize != result.fixtureSize)
                    throw new InvalidOperationException("Fixture size changed during the probe.");
                result.inputHashAfter = Sha256(afterBytes);
                if (result.inputHashBefore != result.inputHashAfter)
                    throw new InvalidOperationException("Fixture bytes changed during the probe.");
                CaptureNativeSnapshot(result, "after");
                CaptureNativeSnapshot(result, "final");
                VerifyFinalLedger(result);
                bool covered = spec.accepted ? result.operationSucceeded : result.observedControlledRejection;
                result.result = covered ? "Passed" : "NoCoverage";
                if (covered)
                    result.failureClass = "None";
                else
                {
                    result.failureClass = "NoCoverage";
                    if (string.IsNullOrEmpty(result.countGuardDiagnosticReason))
                        result.countGuardDiagnosticReason = "The expected operation did not produce independently attributable count-guard evidence.";
                }
            }
            catch (Exception error)
            {
                result.result = "Failed";
                result.failureClass = ClassifyFailure(error);
                result.errorFull = ExceptionText(error);
                result.disposition = "FailureBeforeCompletion";
                TryCaptureNativeSnapshot(result, "after");
                TryCaptureNativeSnapshot(result, "final");
                TryCaptureNativeSnapshot(result, "failure");
            }

            if (string.IsNullOrEmpty(outputPath))
            {
                UnityDebug.LogError("H1 count diagnostic did not receive an output path; no receipt can be written.");
                return 2;
            }
            try
            {
                WriteNewReceipt(outputPath, result);
                return result.result == "Passed" ? 0 : 2;
            }
            catch (Exception writeError)
            {
                UnityDebug.LogError("H1 count diagnostic receipt write failed: " + ExceptionText(writeError));
                return 2;
            }
        }

        private static H1CountDiagnosticResult NewResult(string baseline, string abi, bool feature, string cpp)
        {
            H1CountDiagnosticResult result = new H1CountDiagnosticResult();
            result.schemaVersion = SchemaVersion;
            result.kind = ResultKind;
            result.result = "Failed";
            result.failureClass = "Unstarted";
            result.expectedBaselineBuildId = baseline;
            result.expectedRuntimeAbiHash = abi;
            result.expectedFeatureEnabled = feature;
            result.expectedCppConfiguration = cpp;
            result.unityVersion = Application.unityVersion;
            result.platform = Application.platform.ToString();
            result.buildGuid = Application.buildGUID;
            result.processId = Process.GetCurrentProcess().Id;
            result.startUtc = DateTime.UtcNow.ToString("o");
            result.debugIsDebugBuild = UnityDebug.isDebugBuild;
            result.developmentBuild = UnityDebug.isDebugBuild;
#if ENABLE_IL2CPP && !UNITY_EDITOR
            result.il2cpp = true;
#else
            result.il2cpp = false;
#endif
            result.operationSteps = new List<H1CountOperationStep>();
            result.snapshots = new List<H1CountSnapshotRecord>();
            result.publication = new H1CountPublicationObservation();
            result.parameter = new H1CountParameterObservation();
            result.nested = new H1CountNestedObservation();
            result.witness = new H1CountWitnessObservation();
            result.operationSucceeded = false;
            result.externalFixtureByteAuditBindingRequired = true;
            result.earlyStartupConsumed = false;
            result.disposition = "Uncompleted";
            return result;
        }

        private static void RunOrdinary(H1CountDiagnosticResult result, CaseSpec spec, byte[] dllBytes)
        {
            result.disposition = "OrdinaryAssemblyLoadOnly";
            result.publication.pathContract = "ordinary Assembly.Load(byte[]) only; AssemblyShadowRuntime was not called.";
            CapturePublicationInventory(result, true);
            H1CountDiagnosticAssemblyLoad(result, "ordinary-load", true);
            Assembly assembly = null;
            try
            {
                assembly = Assembly.Load(dllBytes);
                AddStep(result, "ordinary-load", "Assembly.Load(byte[])", true, AssemblyShadowErrorCode.Success, "Assembly loaded.");
                result.publication.publicAssemblyLoaded = true;
                RecordAssemblyIdentity(result, assembly, spec, false);
                if (!spec.accepted)
                    throw new InvalidOperationException("Controlled-rejected ordinary fixture loaded as a public assembly.");
                InspectAcceptedAssembly(result, spec, assembly);
                CapturePublicationInventory(result, false);
                result.operationSucceeded = true;
            }
            catch (Exception error)
            {
                if (spec.accepted) throw;
                result.publication.publicAssemblyLoaded = assembly != null;
                CapturePublicationInventory(result, false);
                result.publication.publicAssemblyInventoryStable = AllPublicationInventoriesStable(result.publication);
                result.publication.publicIdentityObservationAvailable = true;
                result.publication.noPublicFixtureIdentity = assembly == null && result.publication.publicAssemblyInventoryStable;
                result.publication.publicAssemblyObservation = result.publication.noPublicFixtureIdentity
                    ? "Assembly.Load returned no assembly and the complete logical, physical, and published image inventories remained unchanged."
                    : "Ordinary rejection did not establish absence of a newly published assembly/image identity.";
                result.publication.rejectedExceptionFull = ExceptionText(error);
                AddExceptionStep(result, "ordinary-load", "Assembly.Load(byte[])", ExceptionText(error));
                if (assembly != null || !result.publication.publicAssemblyInventoryStable)
                    throw new InvalidOperationException("Ordinary rejected input changed the public assembly inventory.");
                result.observedControlledRejection = ObserveCountGuard(result, spec, ExceptionMessages(error), "ordinary-exception");
                result.disposition = "OrdinaryRejectedNoCommitNoAbort";
            }
        }

        private static void H1CountDiagnosticAssemblyLoad(H1CountDiagnosticResult result, string name, bool ordinary)
        {
            AddStep(result, name, ordinary ? "ordinary-path-selected" : "shadow-path-selected", true,
                AssemblyShadowErrorCode.Success, ordinary ? "No shadow API call permitted on ordinary path." : "Shadow transaction path selected.");
        }

        private static void RunShadow(H1CountDiagnosticResult result, CaseSpec spec, byte[] dllBytes)
        {
            string targetAssembly = spec.family == "parameters" ? ShadowParameterAssembly : ShadowNestedAssembly;
            if (s_earlyReceipt == null)
                throw new InvalidOperationException("Shadow path requires an authenticated early startup receipt.");
            ApplyEarlyReceipt(result, spec, targetAssembly, s_earlyReceipt);
            if (spec.accepted)
            {
                Assembly assembly = Assembly.Load(targetAssembly);
                result.publication.publicAssemblyLoaded = true;
                CapturePublicationInventory(result, false);
                RecordAssemblyIdentity(result, assembly, spec, true);
                AssemblyExecutionMode mode;
                AssemblyShadowErrorCode executionCode = AssemblyShadowRuntime.GetAssemblyExecutionMode(targetAssembly, out mode);
                result.publication.executionModeAvailable = executionCode == AssemblyShadowErrorCode.Success;
                result.publication.executionModeCode = executionCode.ToString();
                result.publication.executionMode = mode.ToString();
                if (executionCode != AssemblyShadowErrorCode.Success || mode != AssemblyExecutionMode.InterpreterShadow)
                    throw new InvalidOperationException("Committed target did not report InterpreterShadow execution mode: " + executionCode + "/" + mode);
                InspectAcceptedAssembly(result, spec, assembly);
                result.operationSucceeded = true;
            }
            else
            {
                result.controlledRejectionErrorFull = result.publication.failureDiagnosticsDetail;
                result.observedControlledRejection = ObserveCountGuard(result, spec,
                    result.controlledRejectionErrorFull, "shadow-diagnostics-detail");
                VerifyRejectedShadowState(result, targetAssembly);
            }
            return;
#if false
            result.publication.pathContract = "ConfigureCandidates -> BeginTransaction -> ReserveMetadataBudget(profile 2) -> StageAssembly -> ValidateTransaction -> CommitTransaction; logical-name Assembly.Load after commit.";
            CapturePublicationInventory(result, true);
            if (!result.expectedFeatureEnabled)
                throw new InvalidOperationException("The shadow path requires an Assembly Shadow ON Player.");
            AssemblyShadowErrorCode code = AssemblyShadowRuntime.ConfigureCandidates(result.expectedBaselineBuildId,
                new[] { ShadowParameterAssembly, ShadowNestedAssembly }, new[] { StableAotName });
            result.publication.configureCalled = true;
            result.publication.configureCode = code.ToString();
            AddStep(result, "configure", "ConfigureCandidates", code == AssemblyShadowErrorCode.Success, code,
                "Exact embedded two-candidate set plus mscorlib stable allowlist.");
            if (code != AssemblyShadowErrorCode.Success) throw new InvalidOperationException("ConfigureCandidates failed: " + code);
            RequireState(result, "after-configure", AssemblyShadowState.CandidatesRegistered);

            code = AssemblyShadowRuntime.BeginTransaction(result.caseId, result.expectedBaselineBuildId,
                new[] { targetAssembly }, 2);
            result.publication.beginCalled = true;
            result.publication.beginCode = code.ToString();
            AddStep(result, "begin", "BeginTransaction", code == AssemblyShadowErrorCode.Success, code, "Exact one-member closure.");
            if (code != AssemblyShadowErrorCode.Success) throw new InvalidOperationException("BeginTransaction failed: " + code);
            RequireState(result, "after-begin", AssemblyShadowState.Staging);

            code = AssemblyShadowRuntime.ReserveMetadataBudget(new[] { result.fixtureSize }, 2);
            result.publication.reserveCalled = true;
            result.publication.reserveCode = code.ToString();
            result.publication.reserveProfileVersion = 2;
            AddStep(result, "reserve", "ReserveMetadataBudget", code == AssemblyShadowErrorCode.Success, code,
                "One exact ordered fixture size reserved under profile 2.");
            if (code != AssemblyShadowErrorCode.Success)
            {
                RequireState(result, "after-reserve-failure", AssemblyShadowState.Staging);
                CaptureNativeSnapshot(result, "after-reserve-failure");
                result.admissionFailedNoCoverage = true;
                result.countGuardDiagnosticReason = "Profile 2 metadata admission failed before StageAssembly; the production count guard was not reached.";
                result.disposition = "AdmissionFailedBeforeStageNoCoverage";
                return;
            }
            RequireState(result, "after-reserve", AssemblyShadowState.Staging);
            CaptureNativeSnapshot(result, "after-reserve");
            VerifyShadowReservationLedger(result);

            code = AssemblyShadowRuntime.StageAssembly(dllBytes, null);
            result.publication.stageCalled = true;
            result.publication.stageCode = code.ToString();
            AddStep(result, "stage", "StageAssembly", code == AssemblyShadowErrorCode.Success, code, "Bounded fixture bytes staged once.");
            if (code != AssemblyShadowErrorCode.Success) throw new InvalidOperationException("StageAssembly failed before count validation: " + code);
            RequireState(result, "after-stage", AssemblyShadowState.Staged);
            CaptureNativeSnapshot(result, "after-stage");
            VerifyShadowStageLedger(result);
            if (!spec.accepted)
            {
                code = AssemblyShadowRuntime.ValidateTransaction();
                result.publication.validateCalled = true;
                result.publication.validateCode = code.ToString();
                AddStep(result, "validate", "ValidateTransaction", false, code,
                    "Count guards execute while staged runtime metadata is initialized.");
                if (code != AssemblyShadowErrorCode.ReferenceResolutionFailed)
                    throw new InvalidOperationException("Expected count rejection at ValidateTransaction with ReferenceResolutionFailed, observed " + code + ".");
                RequireState(result, "after-validate", AssemblyShadowState.Failed);
                CaptureNativeSnapshot(result, "after-validate");
                string diagnostic = CaptureShadowFailureDiagnostic(result, code);
                result.controlledRejectionErrorFull = diagnostic;
                result.observedControlledRejection = ObserveCountGuard(result, spec, diagnostic, "shadow-diagnostics-detail");
                result.disposition = "ValidationFailedNoCommitNoAbort";
                VerifyRejectedShadowState(result, targetAssembly);
                return;
            }

            code = AssemblyShadowRuntime.ValidateTransaction();
            result.publication.validateCalled = true;
            result.publication.validateCode = code.ToString();
            AddStep(result, "validate", "ValidateTransaction", code == AssemblyShadowErrorCode.Success, code, "Validated once.");
            if (code != AssemblyShadowErrorCode.Success) throw new InvalidOperationException("ValidateTransaction failed: " + code);
            RequireState(result, "after-validate", AssemblyShadowState.Validated);
            CaptureNativeSnapshot(result, "after-validate");

            code = AssemblyShadowRuntime.CommitTransaction();
            result.publication.commitCalled = true;
            result.publication.commitCode = code.ToString();
            AddStep(result, "commit", "CommitTransaction", code == AssemblyShadowErrorCode.Success, code, "Committed once.");
            if (code != AssemblyShadowErrorCode.Success) throw new InvalidOperationException("CommitTransaction failed: " + code);
            RequireState(result, "after-commit", AssemblyShadowState.Committed);
            CaptureNativeSnapshot(result, "after-commit");
            result.publication.committed = true;
            result.disposition = "CommittedAndPublished";
            result.publication.initializerObserved = false;
            result.publication.initializerObservation = "No initializer API is exposed by the runtime contract; no initializer result is fabricated.";

            Assembly assembly = Assembly.Load(targetAssembly);
            result.publication.publicAssemblyLoaded = true;
            CapturePublicationInventory(result, false);
            RecordAssemblyIdentity(result, assembly, spec, true);
            AssemblyExecutionMode mode;
            code = AssemblyShadowRuntime.GetAssemblyExecutionMode(targetAssembly, out mode);
            result.publication.executionModeAvailable = code == AssemblyShadowErrorCode.Success;
            result.publication.executionModeCode = code.ToString();
            result.publication.executionMode = mode.ToString();
            if (code != AssemblyShadowErrorCode.Success || mode != AssemblyExecutionMode.InterpreterShadow)
                throw new InvalidOperationException("Committed target did not report InterpreterShadow execution mode: " + code + "/" + mode);
            InspectAcceptedAssembly(result, spec, assembly);
            result.operationSucceeded = true;
#endif
        }

        private static H1CountEarlyStartup.Receipt ConsumeEarlyReceipt(H1CountDiagnosticResult result)
        {
            string json = H1CountEarlyStartup.LastReceiptJson;
            if (string.IsNullOrEmpty(json))
                throw new InvalidOperationException("Shadow path did not expose an early startup receipt.");
            H1CountEarlyStartup.Receipt receipt = H1CountEarlyStartup.LastReceipt;
            if (receipt == null || receipt.schemaVersion != H1CountEarlyStartupReceiptSchemaVersion || receipt.kind != "H1CountEarlyStartupResult" ||
                !receipt.diagnosticOnly || receipt.path != "shadow")
                throw new InvalidOperationException("Early startup receipt header is invalid.");
            string supplied = receipt.receiptSha256;
            if (!H1CountEarlyStartup.ReceiptCodec.VerifySerialized(json, supplied))
                throw new InvalidOperationException("Early startup receipt authentication failed.");
            if (receipt.resultPath != RequiredArgument("-shadowH1EarlyResult") || receipt.family != result.family ||
                receipt.caseId != result.caseId || receipt.expectedCount != result.expectedCount ||
                receipt.expectedOutcome != result.expectedOutcome || receipt.baselineBuildId != result.expectedBaselineBuildId ||
                receipt.runtimeAbiHash != result.expectedRuntimeAbiHash || receipt.fixturePath != result.fixturePath ||
                receipt.fixtureSha256Expected != result.fixtureSha256Expected || receipt.fixtureSize != result.fixtureSize ||
                receipt.inputHashBefore != result.inputHashBefore || receipt.inputHashAfter != result.inputHashBefore)
                throw new InvalidOperationException("Early startup receipt input/build binding differs.");
            bool accepted = result.expectedOutcome == "Accepted";
            string[] phases = accepted
                ? new[] { "before", "after-configure", "after-begin", "after-reserve", "after-stage", "after-validate", "after-commit", "after", "final" }
                : new[] { "before", "after-configure", "after-begin", "after-reserve", "after-stage", "after-validate", "after", "final" };
            if (receipt.snapshots == null || receipt.snapshots.Count != phases.Length)
                throw new InvalidOperationException("Early startup receipt snapshot count differs.");
            for (int i = 0; i < phases.Length; ++i)
                if (receipt.snapshots[i] == null || receipt.snapshots[i].phase != phases[i] ||
                    receipt.snapshots[i].nativeCode != "Success" || receipt.snapshots[i].diagnosticsCode != "Success" ||
                    string.IsNullOrEmpty(receipt.snapshots[i].nativeJson) || string.IsNullOrEmpty(receipt.snapshots[i].diagnosticsJson))
                    throw new InvalidOperationException("Early startup native snapshot sequence is invalid at index " + i + ".");
                else
                {
                    H1CountNativeDiagnosticSnapshot native = H1CountNativeDiagnostics.Parse(receipt.snapshots[i].nativeJson);
                    AssemblyShadowDiagnostics diagnostics = AssemblyShadowDiagnostics.Parse(receipt.snapshots[i].diagnosticsJson);
                    if (!native.featureEnabled || !diagnostics.enabled || diagnostics.schemaVersion != 1)
                        throw new InvalidOperationException("Early startup native feature/diagnostic observation is invalid at " + phases[i] + ".");
                }
            string[] operations = accepted ? new[] { "configure", "begin", "reserve", "stage", "validate", "commit" } :
                new[] { "configure", "begin", "reserve", "stage", "validate" };
            if (receipt.operations == null || receipt.operations.Count != operations.Length)
                throw new InvalidOperationException("Early startup operation count differs.");
            for (int i = 0; i < operations.Length; ++i)
                if (receipt.operations[i] == null || receipt.operations[i].phase != operations[i] ||
                    receipt.operations[i].code != (i == 4 && !accepted ? "ReferenceResolutionFailed" : "Success") ||
                    receipt.operations[i].intCode != (int)((i == 4 && !accepted) ? AssemblyShadowErrorCode.ReferenceResolutionFailed : AssemblyShadowErrorCode.Success))
                    throw new InvalidOperationException("Early startup operation sequence is invalid at index " + i + ".");
            if (receipt.baselineAlreadyUsed || (accepted && (receipt.result != "Committed" || receipt.callbackReturnCode != 0 || !receipt.committed)) ||
                (!accepted && (receipt.result != "ExpectedValidationRejection" || receipt.callbackReturnCode != 1 || receipt.committed)))
                throw new InvalidOperationException("Early startup receipt outcome is invalid.");
            result.earlyStartupConsumed = true;
            result.earlyStartupResult = receipt.result;
            result.earlyStartupReceiptSha256 = supplied;
            return receipt;
        }

        private static void AddConsumedEarlySnapshot(H1CountDiagnosticResult result,
            H1CountEarlyStartup.Receipt receipt, string phase)
        {
            H1CountEarlyStartup.SnapshotReceipt source = receipt.snapshots[0];
            H1CountNativeDiagnosticSnapshot snapshot = H1CountNativeDiagnostics.Parse(source.nativeJson);
            if (snapshot.featureEnabled != result.expectedFeatureEnabled)
                throw new InvalidOperationException("Early startup native feature state differs.");
            // The scene starts after Unity has continued bootstrapping. Preserve
            // the authenticated pre-transaction native catalog rather than
            // recapturing a later host state and calling it "before".
            result.publication.publicAssembliesBefore = InventoryKeys(snapshot.logicalAssemblies);
            result.publication.physicalAssembliesBefore = InventoryKeys(snapshot.physicalAssemblies);
            result.publication.publishedInterpreterImagesBefore = InventoryKeys(snapshot.publishedInterpreterImages);
            result.snapshots.Add(new H1CountSnapshotRecord { phase = phase, available = true, snapshot = snapshot });
            BindOrVerifyWitness(result, snapshot, phase);
        }

        private static void AddConsumedEarlyPhase(H1CountDiagnosticResult result,
            H1CountEarlyStartup.Receipt receipt, string phase)
        {
            for (int i = 0; i < receipt.snapshots.Count; ++i)
                if (receipt.snapshots[i].phase == phase)
                {
                    H1CountNativeDiagnosticSnapshot snapshot = H1CountNativeDiagnostics.Parse(receipt.snapshots[i].nativeJson);
                    if (snapshot.featureEnabled != result.expectedFeatureEnabled)
                        throw new InvalidOperationException("Early startup native feature state differs at " + phase + ".");
                    result.snapshots.Add(new H1CountSnapshotRecord { phase = phase, available = true, snapshot = snapshot });
                    BindOrVerifyWitness(result, snapshot, phase);
                    return;
                }
            throw new InvalidOperationException("Early startup snapshot missing: " + phase);
        }

        private static void ApplyEarlyReceipt(H1CountDiagnosticResult result, CaseSpec spec, string targetAssembly,
            H1CountEarlyStartup.Receipt receipt)
        {
            bool accepted = spec.accepted;
            result.publication.pathContract = "H1CountEarlyStartup ConfigureCandidates -> BeginTransaction -> ReserveMetadataBudget(profile 2) -> StageAssembly -> ValidateTransaction -> CommitTransaction; scene performs post-commit reflection/publication only.";
            string[] phases = accepted ? new[] { "after-configure", "after-begin", "after-reserve", "after-stage", "after-validate", "after-commit" } :
                new[] { "after-configure", "after-begin", "after-reserve", "after-stage", "after-validate" };
            for (int i = 0; i < phases.Length; ++i) AddConsumedEarlyPhase(result, receipt, phases[i]);
            string[] operationNames = accepted ? new[] { "configure", "begin", "reserve", "stage", "validate", "commit" } :
                new[] { "configure", "begin", "reserve", "stage", "validate" };
            for (int i = 0; i < operationNames.Length; ++i)
            {
                H1CountEarlyStartup.OperationReceipt operation = receipt.operations[i];
                AssemblyShadowErrorCode code = (AssemblyShadowErrorCode)operation.intCode;
                AddStep(result, operationNames[i], operationNames[i] == "configure" ? "ConfigureCandidates" :
                    operationNames[i] == "begin" ? "BeginTransaction" : operationNames[i] == "reserve" ? "ReserveMetadataBudget" :
                    operationNames[i] == "stage" ? "StageAssembly" : operationNames[i] == "validate" ? "ValidateTransaction" : "CommitTransaction",
                    code == AssemblyShadowErrorCode.Success, code, "Authenticated early-startup operation.");
            }
            result.publication.configureCalled = true; result.publication.configureCode = "Success";
            result.publication.beginCalled = true; result.publication.beginCode = "Success";
            result.publication.reserveCalled = true; result.publication.reserveCode = "Success"; result.publication.reserveProfileVersion = 2;
            result.publication.stageCalled = true; result.publication.stageCode = "Success";
            result.publication.validateCalled = true; result.publication.validateCode = accepted ? "Success" : "ReferenceResolutionFailed";
            result.publication.abortCalled = false;
            result.states.Add(new H1CountStateObservation { phase = "after-configure", available = true, code = "Success", state = AssemblyShadowState.CandidatesRegistered.ToString() });
            result.states.Add(new H1CountStateObservation { phase = "after-begin", available = true, code = "Success", state = AssemblyShadowState.Staging.ToString() });
            result.states.Add(new H1CountStateObservation { phase = "after-reserve", available = true, code = "Success", state = AssemblyShadowState.Staging.ToString() });
            result.states.Add(new H1CountStateObservation { phase = "after-stage", available = true, code = "Success", state = AssemblyShadowState.Staged.ToString() });
            result.states.Add(new H1CountStateObservation { phase = "after-validate", available = true, code = "Success", state = (accepted ? AssemblyShadowState.Validated : AssemblyShadowState.Failed).ToString() });
            if (accepted)
            {
                result.publication.commitCalled = true; result.publication.commitCode = "Success"; result.publication.committed = true;
                result.states.Add(new H1CountStateObservation { phase = "after-commit", available = true, code = "Success", state = AssemblyShadowState.Committed.ToString() });
                result.disposition = "CommittedAndPublished";
            }
            else
            {
                H1CountEarlyStartup.SnapshotReceipt failure = receipt.snapshots[receipt.snapshots.Count - 3];
                AssemblyShadowDiagnostics diagnostics = AssemblyShadowDiagnostics.Parse(failure.diagnosticsJson);
                if (diagnostics.state != AssemblyShadowState.Failed.ToString() || diagnostics.lastError != (int)AssemblyShadowErrorCode.ReferenceResolutionFailed || string.IsNullOrEmpty(diagnostics.detail))
                    throw new InvalidOperationException("Early startup rejection diagnostics are not retained.");
                result.publication.failureDiagnosticsAvailable = true; result.publication.failureDiagnosticsCode = "Success";
                result.publication.failureDiagnosticsJson = failure.diagnosticsJson; result.publication.failureDiagnosticsState = diagnostics.state;
                result.publication.failureDiagnosticsLastError = diagnostics.lastError; result.publication.failureDiagnosticsDetail = diagnostics.detail;
                result.disposition = "ValidationFailedNoCommitNoAbort";
            }
        }

        private static void VerifyRejectedShadowState(H1CountDiagnosticResult result, string targetAssembly)
        {
            if (result.publication.commitCalled)
                throw new InvalidOperationException("CommitTransaction was called after a count rejection.");
            if (result.publication.abortCalled)
                throw new InvalidOperationException("AbortTransaction was called after a retained validation failure.");
            AssemblyExecutionMode mode;
            AssemblyShadowErrorCode code = AssemblyShadowRuntime.GetAssemblyExecutionMode(targetAssembly, out mode);
            result.publication.executionModeAvailable = code == AssemblyShadowErrorCode.Success;
            result.publication.executionModeCode = code.ToString();
            result.publication.executionMode = mode.ToString();
            result.publication.publicAssemblyLoaded = false;
            CapturePublicationInventory(result, false);
            result.publication.publicAssemblyInventoryStable = AllPublicationInventoriesStable(result.publication);
            result.publication.publicIdentityObservationAvailable = true;
            result.publication.noPublicFixtureIdentity = result.publication.publicAssemblyInventoryStable;
            result.publication.publicAssemblyObservation = result.publication.publicAssemblyInventoryStable
                ? "Rejected before publication; logical, physical, and published image inventories were unchanged and no fixture MVID was fabricated."
                : "A logical, physical, or published image inventory changed; fixture identity absence is not established.";
            if (code != AssemblyShadowErrorCode.Success || mode != AssemblyExecutionMode.AotBaseline)
                throw new InvalidOperationException("Rejected target execution mode was not truthfully available as AotBaseline: " + code + "/" + mode);
            if (!result.publication.publicAssemblyInventoryStable)
                throw new InvalidOperationException("Rejected shadow validation changed a logical, physical, or published image inventory.");
        }

        private static void InspectAcceptedAssembly(H1CountDiagnosticResult result, CaseSpec spec, Assembly assembly)
        {
            if (spec.family == "parameters") InspectParameters(result, spec, assembly);
            else InspectNested(result, spec, assembly);
        }

        private static void InspectParameters(H1CountDiagnosticResult result, CaseSpec spec, Assembly assembly)
        {
            string typeName = result.path == "shadow" ? "AssemblyShadow.H1Count.Target" :
                "AssemblyShadow.H1Count.Ordinary_" + Sanitize(spec.id);
            Type type = assembly.GetType(typeName, true);
            BindingFlags flags = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.Instance;
            MethodInfo method = type.GetMethod("Probe", flags);
            if (method == null) throw new InvalidOperationException("Probe method was not found on " + typeName);
            ParameterInfo[] parameters = method.GetParameters();
            result.parameter.available = true;
            result.parameter.targetType = type.FullName;
            result.parameter.targetMethod = method.ToString();
            result.parameter.count = parameters.Length;
            result.observedCount = parameters.Length;
            result.observedCountAvailable = true;
            result.parameter.returnType = method.ReturnType.FullName;
            result.parameter.instance = !method.IsStatic;
            result.parameter.parameterTypes = new string[parameters.Length];
            for (int i = 0; i < parameters.Length; ++i) result.parameter.parameterTypes[i] = parameters[i].ParameterType.FullName;
            result.parameter.paramRows = ReadParamRows(method);
            H1CountParamRow[] repeatedRows = ReadParamRows(method);
            result.parameter.paramRowsRepeatPassed = SameParamRows(result.parameter.paramRows, repeatedRows);
            result.parameter.repeatPassed = SameParameterShape(parameters, method.GetParameters(), result.parameter.parameterTypes) &&
                result.parameter.paramRowsRepeatPassed;
            if (parameters.Length != spec.count) throw new InvalidOperationException("Parameter count mismatch: expected " + spec.count + ", observed " + parameters.Length);
            if (result.parameter.instance != spec.instance) throw new InvalidOperationException("Instance/static mismatch.");
            if (result.parameter.returnType != "System.Int32") throw new InvalidOperationException("Return type mismatch: " + result.parameter.returnType);
            if (spec.mixedKinds != null) RequireTypes(result.parameter.parameterTypes, spec.mixedKinds);
            else for (int i = 0; i < result.parameter.parameterTypes.Length; ++i) if (result.parameter.parameterTypes[i] != "System.Int32") throw new InvalidOperationException("Parameter type mismatch at " + i);
            ValidateParamRows(result.parameter, spec);
            if (!result.parameter.repeatPassed) throw new InvalidOperationException("Repeated parameter type or Param-row reflection differed.");
            if (spec.count <= 1)
            {
                try
                {
                    object receiver = spec.instance ? Activator.CreateInstance(type) : null;
                    object[] args = spec.count == 0 ? new object[0] : new object[] { 0 };
                    result.parameter.invocationAttempted = true;
                    object invocationResult = method.Invoke(receiver, args);
                    result.parameter.invocationResult = invocationResult == null ? null : invocationResult.ToString();
                    result.parameter.invocationSucceeded = true;
                }
                catch (Exception error) { throw new InvalidOperationException("Small valid Probe invocation failed: " + ExceptionText(error)); }
            }
        }

        private static void InspectNested(H1CountDiagnosticResult result, CaseSpec spec, Assembly assembly)
        {
            result.nested.available = true;
            result.nested.targetType = "AssemblyShadow.H1Nested.Target";
            result.nested.groups = new H1CountNestedGroup[spec.declaringNames.Length];
            int total = 0;
            for (int group = 0; group < spec.declaringNames.Length; ++group)
            {
                string declaringName = "AssemblyShadow.H1Nested." + spec.declaringNames[group];
                Type parent = assembly.GetType(declaringName, true);
                Type[] children = parent.GetNestedTypes(BindingFlags.Public | BindingFlags.NonPublic);
                H1CountNestedGroup observed = new H1CountNestedGroup();
                observed.declaringType = declaringName;
                observed.count = children.Length;
                observed.children = new string[children.Length];
                for (int i = 0; i < children.Length; ++i)
                {
                    observed.children[i] = children[i].FullName;
                    if (children[i].DeclaringType != parent) throw new InvalidOperationException("Nested declaring type mismatch.");
                }
                observed.first = children.Length == 0 ? null : observed.children[0];
                observed.last = children.Length == 0 ? null : observed.children[children.Length - 1];
                observed.childrenSha256 = children.Length == 0 ? null : Sha256(Join(observed.children, "\n"));
                Type[] repeated = parent.GetNestedTypes(BindingFlags.Public | BindingFlags.NonPublic);
                observed.repeatPassed = SameTypeSequence(children, repeated);
                result.nested.groups[group] = observed;
                total += children.Length;
                string[] expected = ExpectedNestedNames(spec.declaringNames[group], spec.groupCounts[group]);
                RequireSequence(observed.children, expected, "nested group " + declaringName);
                if (!observed.repeatPassed) throw new InvalidOperationException("Repeated nested enumeration differed.");
            }
            result.nested.totalCount = total;
            result.observedCount = total;
            result.observedCountAvailable = true;
            result.nested.repeatPassed = true;
            if (total != spec.count) throw new InvalidOperationException("Nested count mismatch: expected " + spec.count + ", observed " + total);
        }

        private static H1CountParamRow[] ReadParamRows(MethodInfo method)
        {
            List<H1CountParamRow> rows = new List<H1CountParamRow>();
            string returnName = method.ReturnParameter == null ? null : method.ReturnParameter.Name;
            if (!string.IsNullOrEmpty(returnName)) rows.Add(new H1CountParamRow { sequence = 0, name = returnName, isReturn = true });
            ParameterInfo[] parameters = method.GetParameters();
            for (int i = 0; i < parameters.Length; ++i)
                if (!string.IsNullOrEmpty(parameters[i].Name)) rows.Add(new H1CountParamRow { sequence = i + 1, name = parameters[i].Name, isReturn = false });
            return rows.ToArray();
        }

        private static void ValidateParamRows(H1CountParameterObservation observation, CaseSpec spec)
        {
            H1CountParamRow[] rows = observation.paramRows;
            if (spec.variant == "return255")
            {
                observation.returnParameterRowByteOracleRequired = true;
                if (rows.Length == 0)
                {
                    observation.returnParameterRowPublicReflectionAvailable = false;
                    observation.returnParameterRowObservation = "Public reflection did not expose Param sequence 0; the externally bound fixture byte audit remains the row-0 oracle.";
                    return;
                }
                if (rows.Length != 1 || rows[0].sequence != 0 || rows[0].name != "result" || !rows[0].isReturn)
                    throw new InvalidOperationException("Public reflection returned an unexpected return Param row.");
                observation.returnParameterRowPublicReflectionAvailable = true;
                observation.returnParameterRowObservation = "Public reflection exposed Param sequence 0 with name result; the fixture byte audit remains independently required.";
            }
            else if (spec.variant == "partial-names")
            {
                int expectedRowCount = 0;
                for (int sequence = 1; sequence <= spec.count; sequence += 17) ++expectedRowCount;
                if (rows.Length != expectedRowCount)
                    throw new InvalidOperationException("Partial Param-row count mismatch: expected " + expectedRowCount + ", observed " + rows.Length + ".");
                int row = 0;
                for (int sequence = 1; sequence <= spec.count; sequence += 17, ++row)
                {
                    if (rows[row].sequence != sequence || rows[row].name != "p" + sequence.ToString("D4") || rows[row].isReturn)
                        throw new InvalidOperationException("Partial Param row mismatch at expected sequence " + sequence + ".");
                }
            }
            else if (rows.Length != 0) throw new InvalidOperationException("Unexpected named Param rows.");
        }

        private static bool SameParamRows(H1CountParamRow[] left, H1CountParamRow[] right)
        {
            if (left == null || right == null || left.Length != right.Length) return false;
            for (int i = 0; i < left.Length; ++i)
                if (left[i].sequence != right[i].sequence || left[i].name != right[i].name || left[i].isReturn != right[i].isReturn)
                    return false;
            return true;
        }

        private static bool SameParameterShape(ParameterInfo[] left, ParameterInfo[] right, string[] expected)
        {
            if (left.Length != right.Length || left.Length != expected.Length) return false;
            for (int i = 0; i < left.Length; ++i) if (left[i].ParameterType.FullName != right[i].ParameterType.FullName || expected[i] != left[i].ParameterType.FullName) return false;
            return true;
        }

        private static bool SameTypeSequence(Type[] left, Type[] right)
        {
            if (left.Length != right.Length) return false;
            for (int i = 0; i < left.Length; ++i) if (left[i] != right[i]) return false;
            return true;
        }


        private static void CapturePublicationInventory(H1CountDiagnosticResult result, bool before)
        {
            H1CountNativeDiagnosticSnapshot snapshot = H1CountNativeDiagnostics.Read();
            string[] logical = InventoryKeys(snapshot.logicalAssemblies);
            string[] physical = InventoryKeys(snapshot.physicalAssemblies);
            string[] published = InventoryKeys(snapshot.publishedInterpreterImages);
            if (before)
            {
                result.publication.publicAssembliesBefore = logical;
                result.publication.physicalAssembliesBefore = physical;
                result.publication.publishedInterpreterImagesBefore = published;
            }
            else
            {
                result.publication.publicAssembliesAfter = logical;
                result.publication.physicalAssembliesAfter = physical;
                result.publication.publishedInterpreterImagesAfter = published;
            }
        }

        private static string[] InventoryKeys(H1CountNativeAssemblyIdentity[] identities)
        {
            if (identities == null) throw new InvalidOperationException("Native assembly inventory was unavailable.");
            List<string> keys = new List<string>(identities.Length);
            for (int i = 0; i < identities.Length; ++i)
            {
                H1CountNativeAssemblyIdentity identity = identities[i];
                if (identity == null || string.IsNullOrEmpty(identity.identityKey))
                    throw new InvalidOperationException("Native assembly inventory contained an incomplete identity.");
                // identityKey begins with name|MVID|fullName for the verifier,
                // and already carries the native assembly/image identities and
                // interpreter image ID needed to distinguish physical entries.
                keys.Add(identity.identityKey);
            }
            keys.Sort(StringComparer.Ordinal);
            return keys.ToArray();
        }

        private static bool SameStrings(string[] left, string[] right)
        {
            if (left == null || right == null || left.Length != right.Length) return false;
            for (int i = 0; i < left.Length; ++i) if (left[i] != right[i]) return false;
            return true;
        }

        private static bool AllPublicationInventoriesStable(H1CountPublicationObservation publication)
        {
            return SameStrings(publication.publicAssembliesBefore, publication.publicAssembliesAfter) &&
                SameStrings(publication.physicalAssembliesBefore, publication.physicalAssembliesAfter) &&
                SameStrings(publication.publishedInterpreterImagesBefore, publication.publishedInterpreterImagesAfter);
        }

        private static void RecordAssemblyIdentity(H1CountDiagnosticResult result, Assembly assembly, CaseSpec spec, bool shadow)
        {
            result.publication.publicAssemblyName = assembly.GetName().Name;
            result.publication.publicAssemblyFullName = assembly.FullName;
            H1CountNativeAssemblyIdentity observed = FindNativeLogicalIdentity(result.publication.publicAssemblyName);
            if (!observed.mvidAvailable || string.IsNullOrEmpty(observed.mvid))
                throw new InvalidOperationException("Published interpreter identity did not expose its native Module MVID.");
            if (observed.imageKind != "Interpreter" || observed.imageId == 0 ||
                string.IsNullOrEmpty(observed.nativeAssemblyId) || string.IsNullOrEmpty(observed.nativeImageId))
                throw new InvalidOperationException("Published interpreter identity is missing its native assembly/image identity.");
            H1CountNativeDiagnosticSnapshot before = FindSnapshot(result, "before");
            if (before == null || observed.imageId != before.nextImageId)
                throw new InvalidOperationException("Published interpreter image ID did not follow the preloaded witness ledger.");
            result.publication.publicAssemblyMvid = observed.mvidAvailable ? observed.mvid : null;
            result.publication.publicAssemblyMvidAvailable = observed.mvidAvailable;
            result.publication.nativeAssemblyId = observed.nativeAssemblyId;
            result.publication.nativeImageId = observed.nativeImageId;
            result.publication.imageKind = observed.imageKind;
            result.publication.imageId = observed.imageId;
            result.publication.nativeAssemblyFullName = observed.fullName;
            if (observed.fullName != result.publication.publicAssemblyFullName)
                throw new InvalidOperationException("Native/public assembly full-name observations differ.");
            result.publication.publicAssemblyMatchesExpected = result.publication.publicAssemblyName == (shadow ?
                (spec.family == "parameters" ? ShadowParameterAssembly : ShadowNestedAssembly) :
                (spec.family == "parameters" ? "AssemblyShadow.H1Count.Ordinary." : "AssemblyShadow.H1Nested.Ordinary.") + spec.id);
            if (!result.publication.publicAssemblyMatchesExpected) throw new InvalidOperationException("Public assembly identity mismatch.");
        }

        private static H1CountNativeAssemblyIdentity FindNativeLogicalIdentity(string name)
        {
            H1CountNativeDiagnosticSnapshot snapshot = H1CountNativeDiagnostics.Read();
            for (int i = 0; i < snapshot.logicalAssemblies.Length; ++i)
            {
                H1CountNativeAssemblyIdentity identity = snapshot.logicalAssemblies[i];
                if (identity != null && identity.name == name)
                    return identity;
            }
            throw new InvalidOperationException("Native logical assembly identity was not published: " + name);
        }

        private static H1CountStateObservation CaptureState(H1CountDiagnosticResult result, string phase)
        {
            AssemblyShadowState state;
            AssemblyShadowErrorCode code = AssemblyShadowRuntime.GetState(out state);
            H1CountStateObservation observation = new H1CountStateObservation {
                phase = phase, available = code == AssemblyShadowErrorCode.Success,
                code = code.ToString(), state = state.ToString()
            };
            result.states.Add(observation);
            return observation;
        }

        private static void RequireState(H1CountDiagnosticResult result, string phase, AssemblyShadowState expected)
        {
            H1CountStateObservation observation = CaptureState(result, phase);
            if (!observation.available || observation.state != expected.ToString())
                throw new InvalidOperationException("Assembly Shadow state mismatch at " + phase + ": expected " + expected +
                    ", observed " + observation.code + "/" + observation.state + ".");
        }

        private static H1CountNativeDiagnosticSnapshot CaptureNativeSnapshot(H1CountDiagnosticResult result, string phase)
        {
            H1CountNativeDiagnosticSnapshot snapshot = H1CountNativeDiagnostics.Read();
            result.snapshots.Add(new H1CountSnapshotRecord
            {
                phase = phase,
                available = true,
                snapshot = snapshot,
                errorFull = null
            });
            if (snapshot.featureEnabled != result.expectedFeatureEnabled)
                throw new InvalidOperationException("Native featureEnabled disagrees with expectedFeatureEnabled.");
            BindOrVerifyWitness(result, snapshot, phase);
            return snapshot;
        }

        private static void TryCaptureNativeSnapshot(H1CountDiagnosticResult result, string phase)
        {
            try { CaptureNativeSnapshot(result, phase); }
            catch (Exception error) { result.snapshots.Add(new H1CountSnapshotRecord { phase = phase, available = false, errorFull = ExceptionText(error) }); }
        }

        private static H1CountWitnessObservation WitnessObservation(H1CountEarlyStartup.WitnessReceipt witness)
        {
            if (witness == null) throw new InvalidOperationException("The ordinary witness receipt is missing.");
            string path = Path.GetFullPath(witness.path ?? "");
            if (path != witness.path || !path.EndsWith(H1CountEarlyStartup.OrdinaryWitnessRelativePath, StringComparison.Ordinal) ||
                witness.sha256 != H1CountEarlyStartup.OrdinaryWitnessSha256 ||
                witness.assemblyName != H1CountEarlyStartup.OrdinaryWitnessAssembly ||
                witness.assemblyFullName != "AssemblyShadowBaseline.HotUpdate, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null" ||
                witness.observationKind != "NativeAssemblyIdentity")
                throw new InvalidOperationException("The ordinary witness receipt identity observation is invalid.");
            H1CountWitnessObservation result = new H1CountWitnessObservation {
                available = true, path = witness.path, sha256 = witness.sha256,
                assemblyName = witness.assemblyName, assemblyFullName = witness.assemblyFullName,
                observationKind = witness.observationKind,
                logicalIdentityKeys = WitnessReceiptKeys(witness.logicalIdentityKeys, "logical"),
                physicalIdentityKeys = WitnessReceiptKeys(witness.physicalIdentityKeys, "physical"),
                publishedIdentityKeys = WitnessReceiptKeys(witness.publishedIdentityKeys, "published")
            };
            H1CountEarlyStartup.RequireWitnessBytes(witness.path);
            return result;
        }

        private static void BindOrVerifyWitness(H1CountDiagnosticResult result,
            H1CountNativeDiagnosticSnapshot snapshot, string phase)
        {
            if (result.witness == null || !result.witness.available)
                throw new InvalidOperationException("Ordinary witness was not established before native snapshot " + phase + ".");
            string[][] values = {
                WitnessKeys(snapshot.logicalAssemblies, result.witness, "logical", phase),
                WitnessKeys(snapshot.physicalAssemblies, result.witness, "physical", phase),
                WitnessKeys(snapshot.publishedInterpreterImages, result.witness, "published", phase)
            };
            bool unbound = result.witness.logicalIdentityKeys.Length == 0 &&
                result.witness.physicalIdentityKeys.Length == 0 && result.witness.publishedIdentityKeys.Length == 0;
            if (unbound)
            {
                result.witness.logicalIdentityKeys = values[0];
                result.witness.physicalIdentityKeys = values[1];
                result.witness.publishedIdentityKeys = values[2];
                return;
            }
            if (!SameStrings(result.witness.logicalIdentityKeys, values[0]) ||
                     !SameStrings(result.witness.physicalIdentityKeys, values[1]) ||
                     !SameStrings(result.witness.publishedIdentityKeys, values[2]))
                throw new InvalidOperationException("Ordinary witness native identity changed at " + phase + ".");
        }

        private const int H1CountEarlyStartupReceiptSchemaVersion = 2;

        private static string[] WitnessReceiptKeys(string[] values, string inventory)
        {
            if (values == null || values.Length == 0) return new string[0];
            return RequireWitnessKeys(values, inventory);
        }

        private static string[] RequireWitnessKeys(string[] values, string inventory)
        {
            if (values == null || values.Length != 1 || string.IsNullOrEmpty(values[0]))
                throw new InvalidOperationException("Early witness " + inventory + " identity binding is incomplete.");
            return (string[])values.Clone();
        }

        private static string[] WitnessKeys(H1CountNativeAssemblyIdentity[] values,
            H1CountWitnessObservation witness, string inventory, string phase)
        {
            if (values == null) throw new InvalidOperationException("Native " + inventory + " inventory is unavailable at " + phase + ".");
            bool logicalInventory = inventory == "logical";
            List<string> matches = new List<string>();
            for (int i = 0; i < values.Length; ++i)
            {
                H1CountNativeAssemblyIdentity value = values[i];
                if (value != null && value.name == witness.assemblyName && value.fullName == witness.assemblyFullName &&
                    value.imageKind == (logicalInventory ? "Aot" : "Interpreter"))
                {
                    bool complete = logicalInventory
                        ? !value.published && !value.mvidAvailable && string.IsNullOrEmpty(value.mvid) && value.imageId == 0
                        : value.published && value.mvidAvailable && !string.IsNullOrEmpty(value.mvid) && value.imageId == 1;
                    if (!complete ||
                        string.IsNullOrEmpty(value.nativeAssemblyId) || value.nativeAssemblyId == "0" || value.nativeAssemblyId == "0x0" ||
                        string.IsNullOrEmpty(value.nativeImageId) || value.nativeImageId == "0" || value.nativeImageId == "0x0" ||
                        string.IsNullOrEmpty(value.identityKey))
                        throw new InvalidOperationException("Native " + inventory + " witness identity is incomplete at " + phase + ".");
                    matches.Add(value.identityKey);
                }
            }
            if (matches.Count != 1) throw new InvalidOperationException("Native " + inventory + " witness identity is missing or ambiguous at " + phase + ".");
            return matches.ToArray();
        }

        private static void VerifyFinalLedger(H1CountDiagnosticResult result)
        {
            H1CountNativeDiagnosticSnapshot before = FindSnapshot(result, "before");
            H1CountNativeDiagnosticSnapshot final = FindSnapshot(result, "final");
            if (before == null || final == null)
                throw new InvalidOperationException("Required before/final H1 ledger snapshots are unavailable.");
            if (result.admissionFailedNoCoverage)
            {
                RequireLedgerCounters(final, before.ordinaryAllocatedCount, before.shadowAllocatedCount,
                    before.reservedImageCount, before.reservationCount, before.nextImageId,
                    "Profile 2 admission failure changed the process-lifetime image ledger.");
                if (final.reservedPages != before.reservedPages || final.nextPageSlot != before.nextPageSlot)
                    throw new InvalidOperationException("Profile 2 admission failure changed retained page credits.");
                result.ledgerVerified = true;
                result.ledgerObservation = "Profile 2 admission failed before reservation; no image identity or path counter was consumed.";
                return;
            }
            bool ordinary = result.path == "ordinary";
            ulong expectedOrdinary = before.ordinaryAllocatedCount + (ordinary ? 1UL : 0UL);
            ulong expectedShadow = before.shadowAllocatedCount + (ordinary ? 0UL : 1UL);
            ulong expectedReserved = before.reservedImageCount + (ordinary ? 0UL : 1UL);
            RequireLedgerCounters(final, expectedOrdinary, expectedShadow, expectedReserved,
                before.reservationCount + 1UL, before.nextImageId + 1UL,
                "Final H1 ledger did not retain exactly one path-owned image identity without refund.");
            if (ordinary)
            {
                if (final.reservedPages <= before.reservedPages || final.nextPageSlot <= before.nextPageSlot)
                    throw new InvalidOperationException("Ordinary load did not retain the allocated image's page credits.");
            }
            else
            {
                H1CountNativeDiagnosticSnapshot reserved = FindSnapshot(result, "after-reserve");
                if (reserved == null || final.reservedPages < reserved.reservedPages ||
                    final.nextPageSlot < reserved.nextPageSlot ||
                    final.reservedPages - reserved.reservedPages != final.nextPageSlot - reserved.nextPageSlot)
                    throw new InvalidOperationException("Shadow final ledger did not retain one monotonically extended profile 2 reservation.");
            }
            result.ledgerVerified = true;
            result.ledgerObservation = ordinary
                ? "Exactly one ordinary image identity remained charged; shadow and reserved-image counters were unchanged."
                : "Exactly one profile 2 reservation remained charged and could grow monotonically as validation populated sparse metadata pages; Stage used it for one shadow image and the ordinary counter was unchanged.";
        }

        private static void VerifyShadowReservationLedger(H1CountDiagnosticResult result)
        {
            H1CountNativeDiagnosticSnapshot before = FindSnapshot(result, "before");
            H1CountNativeDiagnosticSnapshot reserved = FindSnapshot(result, "after-reserve");
            if (before == null || reserved == null)
                throw new InvalidOperationException("Shadow reservation ledger snapshots are unavailable.");
            RequireLedgerCounters(reserved, before.ordinaryAllocatedCount, before.shadowAllocatedCount,
                before.reservedImageCount + 1UL, before.reservationCount + 1UL, before.nextImageId + 1UL,
                "Profile 2 reservation did not charge exactly one retained identity before StageAssembly.");
            if (reserved.reservedPages <= before.reservedPages || reserved.nextPageSlot <= before.nextPageSlot ||
                reserved.reservedPages - before.reservedPages != reserved.nextPageSlot - before.nextPageSlot)
                throw new InvalidOperationException("Profile 2 reservation did not charge a consistent positive page-credit range.");
        }

        private static void VerifyShadowStageLedger(H1CountDiagnosticResult result)
        {
            H1CountNativeDiagnosticSnapshot before = FindSnapshot(result, "before");
            H1CountNativeDiagnosticSnapshot staged = FindSnapshot(result, "after-stage");
            if (before == null || staged == null)
                throw new InvalidOperationException("Shadow stage ledger snapshots are unavailable.");
            RequireLedgerCounters(staged, before.ordinaryAllocatedCount, before.shadowAllocatedCount + 1UL,
                before.reservedImageCount + 1UL, before.reservationCount + 1UL, before.nextImageId + 1UL,
                "StageAssembly did not consume the retained profile 2 reservation exactly once.");
            H1CountNativeDiagnosticSnapshot reserved = FindSnapshot(result, "after-reserve");
            if (reserved == null || staged.reservedPages != reserved.reservedPages || staged.nextPageSlot != reserved.nextPageSlot)
                throw new InvalidOperationException("StageAssembly changed the retained profile 2 reservation credits.");
        }

        private static void RequireLedgerCounters(H1CountNativeDiagnosticSnapshot snapshot, ulong ordinary,
            ulong shadow, ulong reserved, ulong reservations, ulong nextImageId, string message)
        {
            if (snapshot.ordinaryAllocatedCount != ordinary || snapshot.shadowAllocatedCount != shadow ||
                snapshot.reservedImageCount != reserved || snapshot.reservationCount != reservations ||
                snapshot.nextImageId != nextImageId)
                throw new InvalidOperationException(message);
        }

        private static H1CountNativeDiagnosticSnapshot FindSnapshot(H1CountDiagnosticResult result, string phase)
        {
            for (int i = result.snapshots.Count - 1; i >= 0; --i)
                if (result.snapshots[i].phase == phase && result.snapshots[i].available)
                    return result.snapshots[i].snapshot;
            return null;
        }

        private static void AddStep(H1CountDiagnosticResult result, string name, string operation, bool success, AssemblyShadowErrorCode code, string detail)
        {
            result.operationSteps.Add(new H1CountOperationStep { name = name, operation = operation, success = success, code = code.ToString(), detail = detail, errorFull = success ? null : detail });
        }

        private static void AddExceptionStep(H1CountDiagnosticResult result, string name, string operation, string detail)
        {
            result.operationSteps.Add(new H1CountOperationStep {
                name = name, operation = operation, success = false, code = "Exception",
                detail = "The managed loader threw; no AssemblyShadowErrorCode applies to the ordinary path.", errorFull = detail
            });
        }

        private static void ValidateBuildInputs(H1CountDiagnosticResult result)
        {
            if (string.IsNullOrEmpty(result.expectedBaselineBuildId) || string.IsNullOrEmpty(result.expectedRuntimeAbiHash))
                throw new InvalidOperationException("Expected baseline build ID and runtime ABI hash are required.");
            RequireSha256(result.expectedRuntimeAbiHash, result.expectedRuntimeAbiHash);
            if (result.expectedCppConfiguration != "Debug" && result.expectedCppConfiguration != "Release")
                throw new InvalidOperationException("Serialized build-declared C++ configuration must be Debug or Release.");
            result.buildDeclaredCppConfiguration = result.expectedCppConfiguration;
            result.actualCppConfiguration = null;
            result.actualCppConfigurationAvailable = false;
            result.externalBuildReceiptBindingRequired = true;
            result.cppConfigurationObservation = "The Player cannot independently observe its IL2CPP C++ configuration. The launcher/verifier must bind this serialized declaration to the immutable diagnostic build receipt.";
        }

        private static string RequiredArgument(string name)
        {
            string[] args = Environment.GetCommandLineArgs();
            for (int i = 0; i + 1 < args.Length; ++i) if (args[i] == name) return args[i + 1];
            throw new InvalidOperationException("Missing required argument " + name);
        }

        private static void ValidateNewAbsolutePath(string path)
        {
            if (string.IsNullOrEmpty(path) || !Path.IsPathRooted(path)) throw new InvalidOperationException("Result path must be absolute.");
            if (File.Exists(path)) throw new IOException("Result path already exists; receipts are new-only: " + path);
            string parent = Path.GetDirectoryName(path);
            if (string.IsNullOrEmpty(parent) || !Directory.Exists(parent)) throw new DirectoryNotFoundException(parent);
        }

        private static string RequireAbsoluteFile(string path)
        {
            if (string.IsNullOrEmpty(path) || !Path.IsPathRooted(path) || !File.Exists(path)) throw new FileNotFoundException("Fixture path must be an existing absolute file.", path);
            return Path.GetFullPath(path);
        }

        private static byte[] ReadBoundedFixture(string path, out long length)
        {
            using (FileStream stream = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.Read))
            {
                length = stream.Length;
                if (length <= 0 || length > MaxFixtureBytes)
                    throw new InvalidOperationException("Fixture size is outside the bounded 32 MiB input limit: " + length);
                byte[] bytes = new byte[checked((int)length)];
                int offset = 0;
                while (offset < bytes.Length)
                {
                    int read = stream.Read(bytes, offset, bytes.Length - offset);
                    if (read <= 0) throw new EndOfStreamException("Fixture ended before its captured bounded length.");
                    offset += read;
                }
                if (stream.Length != length)
                    throw new IOException("Fixture length changed during the bounded read.");
                return bytes;
            }
        }

        private static void ValidateEnum(string value, string first, string second, string name)
        {
            if (value != first && value != second) throw new InvalidOperationException("Invalid " + name + ": " + value);
        }

        private static void RequireSha256(string expected, string actual)
        {
            if (expected == null || expected.Length != 64 || actual == null || actual.Length != 64 || expected.ToLowerInvariant() != actual.ToLowerInvariant())
                throw new InvalidOperationException("SHA-256 mismatch or malformed hash. expected=" + expected + " actual=" + actual);
            for (int i = 0; i < expected.Length; ++i)
            {
                char c = expected[i];
                if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f') || (c >= 'A' && c <= 'F')))
                    throw new InvalidOperationException("SHA-256 contains a non-hex character at index " + i + ".");
            }
        }

        private static string CaptureShadowFailureDiagnostic(H1CountDiagnosticResult result, AssemblyShadowErrorCode expectedError)
        {
            string json;
            AssemblyShadowErrorCode code = AssemblyShadowRuntime.GetDiagnosticsJson(out json);
            result.publication.failureDiagnosticsAvailable = code == AssemblyShadowErrorCode.Success && !string.IsNullOrEmpty(json);
            result.publication.failureDiagnosticsCode = code.ToString();
            result.publication.failureDiagnosticsJson = json;
            if (!result.publication.failureDiagnosticsAvailable)
                throw new InvalidOperationException("Assembly Shadow failure diagnostics were unavailable: " + code + ".");
            AssemblyShadowDiagnostics diagnostics = AssemblyShadowDiagnostics.Parse(json);
            result.publication.failureDiagnosticsState = diagnostics.state;
            result.publication.failureDiagnosticsLastError = diagnostics.lastError;
            result.publication.failureDiagnosticsDetail = diagnostics.detail;
            if (diagnostics.schemaVersion != 1 || diagnostics.state != AssemblyShadowState.Failed.ToString() ||
                diagnostics.lastError != (int)expectedError || string.IsNullOrEmpty(diagnostics.detail))
                throw new InvalidOperationException("Assembly Shadow failure diagnostics did not bind the Failed state to " + expectedError + ".");
            return diagnostics.detail;
        }

        private static bool ObserveCountGuard(H1CountDiagnosticResult result, CaseSpec spec, string diagnostic, string source)
        {
            result.countGuardDiagnostic = diagnostic;
            result.countGuardDiagnosticSource = source;
            result.countGuardExpectedDecodedCount = spec.count;
            if (spec.family == "parameters")
            {
                int decodedCount;
                bool exactFamily = TryReadParameterGuardCount(diagnostic, out decodedCount) && decodedCount == spec.count;
                result.countGuardExpectedNativeMessage = "method token:<token> parameter count:<actual> is too large, or method:<type>.<method> parameter count:<actual> is too large";
                result.countGuardDiagnosticAvailable = exactFamily;
                result.countGuardDecodedCountAvailable = exactFamily;
                result.countGuardCountSource = exactFamily ? "native-parameter-guard-diagnostic" : null;
                if (exactFamily)
                {
                    result.countGuardDecodedCount = decodedCount;
                    result.countGuardDiagnosticReason = "Exact parameter-family native guard text included the decoded count.";
                    return true;
                }
                result.countGuardDiagnosticReason = "No exact parameter-family native guard diagnostic containing the decoded count was available.";
                return false;
            }

            const string nestedGuard = "interpreter nested type count exceeds native limit";
            result.countGuardExpectedNativeMessage = nestedGuard + " (current native text has no decoded count)";
            bool exactNestedGuard = diagnostic != null && diagnostic.IndexOf(nestedGuard, StringComparison.Ordinal) >= 0;
            result.countGuardDiagnosticAvailable = exactNestedGuard;
            result.countGuardDecodedCountAvailable = false;
            result.countGuardCountSource = exactNestedGuard ? "independently-bound-fixture-byte-oracle" : null;
            result.countGuardDiagnosticReason = exactNestedGuard
                ? "The exact nested-family guard fired; its native text omits the count, so the expected count is attributed only through the independently authenticated fixture byte audit."
                : "No exact nested-family native guard diagnostic was available.";
            return exactNestedGuard;
        }

        private static bool TryReadParameterGuardCount(string diagnostic, out int count)
        {
            count = -1;
            if (string.IsNullOrEmpty(diagnostic)) return false;
            const string marker = "parameter count:";
            int search = 0;
            bool found = false;
            while (search < diagnostic.Length)
            {
                int markerStart = diagnostic.IndexOf(marker, search, StringComparison.Ordinal);
                if (markerStart < 0) break;
                search = markerStart + marker.Length;
                int lineStart = markerStart == 0 ? 0 : diagnostic.LastIndexOf('\n', markerStart - 1) + 1;
                bool exactPrefix = HasExactParameterGuardPrefix(diagnostic, lineStart, markerStart);
                int end = search;
                ulong parsed = 0;
                while (end < diagnostic.Length && diagnostic[end] >= '0' && diagnostic[end] <= '9')
                {
                    parsed = parsed * 10UL + (uint)(diagnostic[end] - '0');
                    if (parsed > int.MaxValue) break;
                    ++end;
                }
                const string suffix = " is too large";
                int suffixEnd = end + suffix.Length;
                bool exactSuffix = end > search && parsed <= int.MaxValue && suffixEnd <= diagnostic.Length &&
                    string.CompareOrdinal(diagnostic, end, suffix, 0, suffix.Length) == 0 &&
                    (suffixEnd == diagnostic.Length || diagnostic[suffixEnd] == '\r' || diagnostic[suffixEnd] == '\n');
                if (!exactPrefix || !exactSuffix) continue;
                if (found && count != (int)parsed) return false;
                count = (int)parsed;
                found = true;
            }
            return found;
        }

        private static bool HasExactParameterGuardPrefix(string diagnostic, int lineStart, int markerStart)
        {
            if (markerStart <= lineStart || diagnostic[markerStart - 1] != ' ') return false;
            const string tokenPrefix = "method token:";
            int tokenStart = diagnostic.IndexOf(tokenPrefix, lineStart, markerStart - lineStart, StringComparison.Ordinal);
            if (tokenStart >= 0)
            {
                int digitStart = tokenStart + tokenPrefix.Length;
                int digitEnd = markerStart - 1;
                if (digitStart >= digitEnd) return false;
                for (int i = digitStart; i < digitEnd; ++i)
                    if (diagnostic[i] < '0' || diagnostic[i] > '9') return false;
                return true;
            }

            const string namedPrefix = "method:";
            int namedStart = diagnostic.IndexOf(namedPrefix, lineStart, markerStart - lineStart, StringComparison.Ordinal);
            if (namedStart < 0) return false;
            int nameStart = namedStart + namedPrefix.Length;
            int nameEnd = markerStart - 1;
            if (nameStart >= nameEnd) return false;
            int separator = diagnostic.IndexOf('.', nameStart, nameEnd - nameStart);
            return separator > nameStart && separator + 1 < nameEnd;
        }

        private static string ExceptionMessages(Exception error)
        {
            StringBuilder builder = new StringBuilder();
            Exception current = error;
            for (int depth = 0; current != null && depth < 16; ++depth, current = current.InnerException)
            {
                if (depth != 0) builder.Append("\n");
                builder.Append(current.GetType().FullName).Append(": ").Append(current.Message);
            }
            return builder.ToString();
        }

        private static string ClassifyFailure(Exception error)
        {
            return "ProbeFailure";
        }

        private static string ExceptionText(Exception error)
        {
            return error == null ? "<null>" : error.GetType().FullName + ": " + error.Message + "\n" + error.StackTrace;
        }

        private static void WriteNewReceipt(string path, H1CountDiagnosticResult result)
        {
            result.endUtc = DateTime.UtcNow.ToString("o");
            using (FileStream stream = new FileStream(path, FileMode.CreateNew, FileAccess.Write, FileShare.None))
            using (StreamWriter writer = new StreamWriter(stream, new UTF8Encoding(false)))
                writer.Write(JsonUtility.ToJson(result, true));
        }

        private static CaseSpec FindCase(string family, string id)
        {
            CaseSpec[] cases = family == "parameters" ? ParameterCases() : NestedCases();
            for (int i = 0; i < cases.Length; ++i) if (cases[i].id == id) return cases[i];
            return null;
        }

        private static CaseSpec[] ParameterCases()
        {
            return new[]
            {
                Param("H1R-P01-a", 0, true, false, null), Param("H1R-P01-b", 1, true, false, null),
                Param("H1R-P01-c", 254, true, false, null), Param("H1R-P01-d", 255, true, false, null),
                Param("H1R-P02-a", 256, false, false, null), Param("H1R-P02-b", 65535, false, false, null),
                Param("H1R-P03-a", 65536, false, false, null), Param("H1R-P03-b", 65537, false, false, null),
                ParamVariant("H1R-P04-return255", "return255", 255, true, false, null),
                ParamVariant("H1R-P04-partial-names", "partial-names", 255, true, false, null),
                ParamVariant("H1R-P04-instance", "instance", 255, true, true, null),
                ParamVariant("H1R-P04-mixed-kinds", "mixed-kinds", 255, true, false,
                    new[] { "System.Int32", "System.String", "System.Object", "System.Int32&", "System.String[]" })
            };
        }

        private static CaseSpec[] NestedCases()
        {
            return new[]
            {
                Nested("H1R-N01-a", 0, true, new[] { "Target" }, new[] { 0 }), Nested("H1R-N01-b", 1, true, new[] { "Target" }, new[] { 1 }),
                Nested("H1R-N01-c", 65534, true, new[] { "Target" }, new[] { 65534 }), Nested("H1R-N01-d", 65535, true, new[] { "Target" }, new[] { 65535 }),
                Nested("H1R-N02-a", 65536, false, new[] { "Target" }, new[] { 65536 }), Nested("H1R-N02-b", 65537, false, new[] { "Target" }, new[] { 65537 }),
                Nested("H1R-N03-interleaved", 4, true, new[] { "Target", "SiblingB" }, new[] { 2, 2 }),
                Nested("H1R-N04-adjacent-valid", 65536, true, new[] { "Target", "SiblingB" }, new[] { 1, 65535 }),
                Nested("H1R-N04-adjacent-overflow", 65537, false, new[] { "Target", "SiblingB" }, new[] { 1, 65536 }),
                Nested("H1R-N05-final-repeat", 65535, true, new[] { "Target" }, new[] { 65535 })
            };
        }

        private static CaseSpec Param(string id, int count, bool accepted, bool instance, string[] mixed) { return ParamVariant(id, "base", count, accepted, instance, mixed); }
        private static CaseSpec ParamVariant(string id, string variant, int count, bool accepted, bool instance, string[] mixed)
        {
            return new CaseSpec { id = id, family = "parameters", count = count, accepted = accepted, instance = instance, variant = variant, mixedKinds = mixed };
        }
        private static CaseSpec Nested(string id, int count, bool accepted, string[] names, int[] counts)
        {
            return new CaseSpec { id = id, family = "nested", count = count, accepted = accepted, declaringNames = names, groupCounts = counts };
        }

        private static string[] ExpectedNestedNames(string declaring, int count)
        {
            string[] names = new string[count];
            for (int i = 0; i < count; ++i) names[i] = "AssemblyShadow.H1Nested." + declaring + "+" + declaring + "Child" + i.ToString("D5");
            return names;
        }

        private static void RequireTypes(string[] actual, string[] pattern)
        {
            for (int i = 0; i < actual.Length; ++i) if (actual[i] != pattern[i % pattern.Length]) throw new InvalidOperationException("Mixed parameter type mismatch at " + i);
        }
        private static void RequireSequence(string[] actual, string[] expected, string label)
        {
            if (actual.Length != expected.Length) throw new InvalidOperationException(label + " count mismatch.");
            for (int i = 0; i < actual.Length; ++i) if (actual[i] != expected[i]) throw new InvalidOperationException(label + " order/name mismatch at " + i);
        }
        private static string Sanitize(string value) { return value.Replace('-', '_'); }
        private static string Join(string[] values, string separator)
        {
            StringBuilder builder = new StringBuilder();
            for (int i = 0; i < values.Length; ++i) { if (i != 0) builder.Append(separator); builder.Append(values[i]); }
            return builder.ToString();
        }
        private static string Sha256(byte[] bytes)
        {
            using (SHA256 sha = SHA256.Create()) return Hex(sha.ComputeHash(bytes));
        }
        private static string Sha256(string value) { return Sha256(Encoding.UTF8.GetBytes(value)); }
        private static string Hex(byte[] bytes)
        {
            StringBuilder builder = new StringBuilder(bytes.Length * 2);
            for (int i = 0; i < bytes.Length; ++i) builder.Append(bytes[i].ToString("x2"));
            return builder.ToString();
        }
    }

    internal sealed class CaseSpec
    {
        internal string id, family, variant;
        internal int count;
        internal bool accepted, instance;
        internal string[] mixedKinds, declaringNames;
        internal int[] groupCounts;
    }

    [Serializable]
    public sealed class H1CountDiagnosticResult
    {
        public int schemaVersion; public string kind; public string result; public string failureClass; public string errorFull;
        public string family; public string path; public string caseId; public string expectedOutcome; public int expectedCount; public int observedCount = -1; public bool observedCountAvailable; public string disposition;
        public string resultPath; public string fixturePath; public string fixtureSha256Expected; public long fixtureSize;
        public string inputHashBefore; public string inputHashAfter; public string expectedBaselineBuildId; public string expectedRuntimeAbiHash;
        public bool expectedFeatureEnabled; public string expectedCppConfiguration; public string buildDeclaredCppConfiguration; public string actualCppConfiguration;
        public bool actualCppConfigurationAvailable; public bool externalBuildReceiptBindingRequired; public string cppConfigurationObservation; public string controlledRejectionErrorFull;
        public bool externalFixtureByteAuditBindingRequired;
        public string unityVersion; public string platform; public string buildGuid; public int processId; public string startUtc; public string endUtc;
        public bool debugIsDebugBuild; public bool developmentBuild; public bool il2cpp; public bool operationSucceeded; public bool observedControlledRejection;
        public bool earlyStartupConsumed; public string earlyStartupResult; public string earlyStartupReceiptSha256;
        public H1CountWitnessObservation witness;
        public bool ledgerVerified; public string ledgerObservation; public bool admissionFailedNoCoverage;
        public bool countGuardDiagnosticAvailable; public string countGuardDiagnostic; public string countGuardDiagnosticSource; public string countGuardExpectedNativeMessage;
        public int countGuardExpectedDecodedCount = -1; public bool countGuardDecodedCountAvailable; public int countGuardDecodedCount = -1; public string countGuardDiagnosticReason;
        public string countGuardCountSource;
        public List<H1CountOperationStep> operationSteps; public List<H1CountSnapshotRecord> snapshots; public List<H1CountStateObservation> states = new List<H1CountStateObservation>();
        public H1CountPublicationObservation publication; public H1CountParameterObservation parameter; public H1CountNestedObservation nested;
    }
    [Serializable] public sealed class H1CountOperationStep { public string name; public string operation; public bool success; public string code; public string detail; public string errorFull; }
    [Serializable] public sealed class H1CountSnapshotRecord { public string phase; public bool available; public string errorFull; public H1CountNativeDiagnosticSnapshot snapshot; }
    [Serializable] public sealed class H1CountStateObservation { public string phase; public bool available; public string code; public string state; }
    [Serializable] public sealed class H1CountPublicationObservation
    {
        public string pathContract; public bool configureCalled; public string configureCode; public bool beginCalled; public string beginCode;
        public bool reserveCalled; public string reserveCode; public int reserveProfileVersion;
        public bool stageCalled; public string stageCode; public bool validateCalled; public string validateCode; public bool commitCalled; public string commitCode;
        public bool abortCalled; public bool committed; public bool initializerObserved; public string initializerObservation;
        public bool publicAssemblyLoaded; public string publicAssemblyName; public string publicAssemblyFullName; public string publicAssemblyMvid;
        public bool publicAssemblyMatchesExpected; public bool noPublicFixtureIdentity; public bool publicIdentityObservationAvailable; public bool publicAssemblyInventoryStable;
        public string nativeAssemblyId; public string nativeImageId; public string nativeAssemblyFullName;
        public bool publicAssemblyMvidAvailable; public string imageKind; public uint imageId;
        public string[] publicAssembliesBefore; public string[] publicAssembliesAfter;
        public string[] physicalAssembliesBefore; public string[] physicalAssembliesAfter;
        public string[] publishedInterpreterImagesBefore; public string[] publishedInterpreterImagesAfter;
        public string publicAssemblyObservation; public string rejectedExceptionFull;
        public bool executionModeAvailable; public string executionModeCode; public string executionMode;
        public bool failureDiagnosticsAvailable; public string failureDiagnosticsCode; public string failureDiagnosticsJson;
        public string failureDiagnosticsState; public int failureDiagnosticsLastError; public string failureDiagnosticsDetail;
    }
    [Serializable] public sealed class H1CountParameterObservation
    {
        public bool available; public string targetType; public string targetMethod; public int count = -1; public string returnType; public bool instance;
        public string[] parameterTypes; public H1CountParamRow[] paramRows; public bool repeatPassed; public bool paramRowsRepeatPassed;
        public bool returnParameterRowByteOracleRequired; public bool returnParameterRowPublicReflectionAvailable; public string returnParameterRowObservation;
        public bool invocationAttempted; public bool invocationSucceeded; public string invocationResult;
    }
    [Serializable] public sealed class H1CountParamRow { public int sequence; public string name; public bool isReturn; }
    [Serializable] public sealed class H1CountNestedObservation { public bool available; public string targetType; public int totalCount = -1; public H1CountNestedGroup[] groups; public bool repeatPassed; }
    [Serializable] public sealed class H1CountNestedGroup
    {
        public string declaringType; public int count = -1; public string first; public string last; public string childrenSha256; public string[] children; public bool repeatPassed;
    }
    [Serializable] public sealed class H1CountWitnessObservation
    {
        public bool available; public string path; public string sha256; public string assemblyName, assemblyFullName;
        public string observationKind;
        public string[] logicalIdentityKeys, physicalIdentityKeys, publishedIdentityKeys;
    }
}
