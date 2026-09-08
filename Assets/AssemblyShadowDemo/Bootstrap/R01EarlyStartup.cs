using System;
using System.Collections.Generic;
using System.IO;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using System.Diagnostics;
using HybridCLR;
using UnityEngine.Scripting;

namespace AssemblyShadowDemo
{
    /// <summary>
    /// The managed half of the R01 earliest-startup experiment. This type is
    /// deliberately pure BCL: native code invokes Run after Runtime::Init and
    /// before the Unity global catalog is admitted. It does not own Unity
    /// services, JSON parsing, or the native callback registration point.
    /// </summary>
    [Preserve]
    public static class R01EarlyStartup
    {
        public const int CapsuleVersion = 1;
        public const int MaxCapsuleBytes = 16 * 1024 * 1024;
        public const int MaxStringBytes = 16384;
        public const int MaxArrayCount = 65536;
        public const string CapsuleMagic = "R01EARLY";
        public const string FixedOrdinarySha256 = "9108a2396fd1a292a1446a96b6e61ac19108fd930d8d2b70edb4c3af72780e27";

        private const string CapsuleArgument = "-shadowEarlyCapsule";
        private const string CapsuleShaArgument = "-shadowEarlyCapsuleSha256";
        private const string ResultArgument = "-shadowEarlyResult";
        private const string OrdinaryAssemblyName = "AssemblyShadowBaseline.HotUpdate";
        private const string OrdinaryGuardPrefix = "__AssemblyShadowReflectionBinding_";
        private const string InternalAssemblyName = "AssemblyA.Implementation.Internal";
        private const string InternalEntryType = "AssemblyA.Implementation.Internal.InternalEntry";
        private const string ObjectWitnessType = "AssemblyA.Implementation.Internal.M06ExecutionWitness+M06InternalNode";
        private const string CctorWitnessType = "AssemblyA.Implementation.Internal.M06ExecutionWitness";
        private const int RuntimeAbiVersion = 1;

        private static string s_lastReceiptJson;

        /// <summary>The exact receipt retained in managed memory for post-startup handoff.</summary>
        public static string LastReceiptJson { get { return s_lastReceiptJson; } }

        [Preserve]
        public static int Run()
        {
            Receipt receipt = new Receipt();
            Stopwatch total = Stopwatch.StartNew();
            Arguments arguments = null;
            R01EarlyObserver observer = null;
            R01EarlyInitializerCapture initializerCapture = null;
            TextWriter previousConsole = null;
            bool observerStarted = false;
            Action startObserver = null;
            try
            {
                arguments = Arguments.Read(Environment.GetCommandLineArgs());
                receipt.capsulePath = arguments.capsulePath;
                receipt.capsuleSha256 = arguments.capsuleSha256;
                receipt.resultPath = arguments.resultPath;
                Require(!File.Exists(arguments.resultPath) && !Directory.Exists(arguments.resultPath), "R01 early result already exists.");
                receipt.processId = ProcessId();
                receipt.managedThreadId = Environment.CurrentManagedThreadId;
                receipt.stopwatchFrequency = Stopwatch.Frequency;

                byte[] capsuleBytes = ReadCapsuleBytes(arguments.capsulePath);
                string actualCapsuleSha = Sha256(capsuleBytes);
                Require(actualCapsuleSha == arguments.capsuleSha256, "R01 capsule SHA-256 differs from the launcher digest.");
                Capsule capsule = CapsuleCodec.Parse(capsuleBytes);
                receipt.mode = capsule.mode;
                receipt.baselineBuildId = capsule.baselineBuildId;
                receipt.runtimeAbiHash = capsule.runtimeAbiHash;
                receipt.patchId = capsule.patchId;
                ValidateCapsule(capsule);

                receipt.byteInputs = new List<ByteInputReceipt>();
                var seenPaths = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
                List<OwnedInput> closure = ReadClosureInputs(capsule, receipt, seenPaths);
                OwnedInput ordinary = null;
                if (capsule.mode == "OrdinaryFirst" || capsule.mode == "OrdinaryAfterReserve")
                    ordinary = ReadOrdinaryInput(capsule, receipt, seenPaths);
                VerifyPrerequisites(capsule, receipt, seenPaths);
                if (capsule.mode == "Oversize")
                {
                    OwnedInput last = closure[closure.Count - 1];
                    Require(last.bytes.Length < 64 * 1024 * 1024, "Oversize source already exceeds its fixture bound.");
                    byte[] padded = new byte[64 * 1024 * 1024];
                    Buffer.BlockCopy(last.bytes, 0, padded, 0, last.bytes.Length);
                    last.bytes = padded;
                    receipt.byteInputs.Add(new ByteInputReceipt { name = last.name, path = last.path,
                        length = padded.LongLength, sha256 = Sha256(padded), kind = "oversize-dll" });
                }
                long[] sizes = BudgetSizes(closure);

                if (capsule.mode == "Control" || capsule.mode == "MetadataFailure" || capsule.mode == "InitializerFailure")
                {
                    previousConsole = Console.Out;
                    initializerCapture = new R01EarlyInitializerCapture(previousConsole);
                    Console.SetOut(initializerCapture);
                    observer = new R01EarlyObserver();
                    startObserver = delegate { observer.StartAndWaitBefore(); observerStarted = true; };
                }

                Snapshot(receipt, "before-startup-ops", sizes);
                if (capsule.mode == "Baseline")
                {
                    receipt.result = "Passed";
                    receipt.callbackReturnCode = 0;
                }
                else if (capsule.mode == "Control")
                {
                    RunTransaction(receipt, capsule, closure, sizes, null, false, false, startObserver);
                    receipt.result = "Passed";
                    receipt.callbackReturnCode = 0;
                }
                else if (capsule.mode == "OrdinaryFirst")
                {
                    OrdinaryGuard(receipt, ordinary, "ordinary-before-configure");
                    Snapshot(receipt, "after-ordinary-before-configure", sizes);
                    RunTransaction(receipt, capsule, closure, sizes, null, false, false);
                    receipt.result = "Passed";
                    receipt.callbackReturnCode = 0;
                }
                else if (capsule.mode == "OrdinaryAfterReserve")
                {
                    RunTransaction(receipt, capsule, closure, sizes, ordinary, true, false);
                    receipt.result = "Passed";
                    receipt.callbackReturnCode = 0;
                }
                else if (capsule.mode == "Oversize")
                {
                    RunOversize(receipt, capsule, sizes);
                    receipt.result = "PassedExpectedRejection";
                    receipt.callbackReturnCode = 1;
                }
                else if (capsule.mode == "Mismatch")
                {
                    RunMismatch(receipt, capsule, closure, sizes);
                    receipt.result = "PassedExpectedRejection";
                    receipt.callbackReturnCode = 1;
                }
                else if (capsule.mode == "Type" || capsule.mode == "Object" || capsule.mode == "Cctor")
                {
                    Witness(receipt, capsule.mode);
                    Snapshot(receipt, "after-preconfigure-witness", sizes);
                    RunTransaction(receipt, capsule, closure, sizes, null, false, true);
                    receipt.result = "PassedExpectedRejection";
                    receipt.callbackReturnCode = 1;
                }
                else if (capsule.mode == "NativeScript")
                {
                    Witness(receipt, capsule.mode);
                    Snapshot(receipt, "after-preconfigure-witness", sizes);
                    RunTransaction(receipt, capsule, closure, sizes, null, false, true);
                    receipt.result = "PassedExpectedRejection";
                    receipt.callbackReturnCode = 1;
                }
                else if (capsule.mode == "MetadataFailure")
                {
                    RunFailureTransaction(receipt, capsule, closure, sizes, false, startObserver);
                    receipt.result = "PassedExpectedFailure";
                    receipt.callbackReturnCode = 1;
                }
                else if (capsule.mode == "InitializerFailure")
                {
                    RunFailureTransaction(receipt, capsule, closure, sizes, true, startObserver);
                    receipt.result = "PassedExpectedFailure";
                    receipt.callbackReturnCode = 1;
                }
                else
                {
                    throw new InvalidDataException("Unsupported R01 early mode: " + capsule.mode);
                }
            }
            catch (Exception error)
            {
                receipt.result = "Failed";
                receipt.callbackReturnCode = 1;
                receipt.error = error.ToString();
                if (receipt.processId == 0) receipt.processId = ProcessId();
                if (receipt.managedThreadId == 0) receipt.managedThreadId = Environment.CurrentManagedThreadId;
                if (receipt.stopwatchFrequency == 0) receipt.stopwatchFrequency = Stopwatch.Frequency;
                if (arguments != null)
                {
                    if (string.IsNullOrEmpty(receipt.capsulePath)) receipt.capsulePath = arguments.capsulePath;
                    if (string.IsNullOrEmpty(receipt.capsuleSha256)) receipt.capsuleSha256 = arguments.capsuleSha256;
                    if (string.IsNullOrEmpty(receipt.resultPath)) receipt.resultPath = arguments.resultPath;
                }
            }
            finally
            {
                if (observer != null)
                {
                    try { if (observerStarted) observer.MarkAfterAndWait(); }
                    catch (Exception error) { ObservationFailure(receipt, error); }
                    finally
                    {
                        try
                        {
                            observer.Stop();
                            receipt.observerJoined = observer.Joined;
                            receipt.observerSamples = observer.Samples;
                            receipt.observerErrors = observer.Errors;
                            receipt.observerDroppedBefore = observer.droppedBefore;
                            receipt.observerDroppedAfter = observer.droppedAfter;
                            Require(receipt.observerJoined && receipt.observerErrors.Length == 0, "Early observer failed or did not join.");
                        }
                        catch (Exception error) { ObservationFailure(receipt, error); }
                    }
                }
                try
                {
                    if (previousConsole != null) Console.SetOut(previousConsole);
                    if (initializerCapture != null) receipt.initializerEvents = initializerCapture.Events;
                }
                catch (Exception error) { ObservationFailure(receipt, error); }
            }
            receipt.elapsedTicks = total.ElapsedTicks;
            string json = ReceiptCodec.Serialize(receipt);
            s_lastReceiptJson = json;
            if (arguments != null && !string.IsNullOrEmpty(arguments.resultPath))
            {
                try { WriteNew(arguments.resultPath, json); }
                catch (Exception writeError)
                {
                    receipt.result = "Failed";
                    receipt.callbackReturnCode = 2;
                    receipt.error = string.IsNullOrEmpty(receipt.error) ? writeError.ToString() : receipt.error + "\nReceipt write: " + writeError;
                    json = ReceiptCodec.Serialize(receipt);
                    s_lastReceiptJson = json;
                }
            }
            return receipt.callbackReturnCode;
        }

        private static long[] BudgetSizes(List<OwnedInput> closure)
        {
            var sizes = new long[closure.Count];
            for (int i = 0; i < closure.Count; ++i) sizes[i] = closure[i].bytes.LongLength;
            return sizes;
        }

        private static void ObservationFailure(Receipt receipt, Exception error)
        {
            receipt.result = "Failed";
            receipt.callbackReturnCode = 1;
            receipt.error = string.IsNullOrEmpty(receipt.error) ? error.ToString() : receipt.error + "\nObserver: " + error;
        }

        private static void RunOversize(Receipt receipt, Capsule capsule, long[] sizes)
        {
            AssemblyShadowMetadataCapacity before = LastCapacity(receipt);
            Require(!before.fits && before.firstFailingIndex == sizes.Length - 1 &&
                before.acceptedImages == (uint)(sizes.Length - 1), "Oversize dry-run did not fail at the last member.");
            Operation(receipt, "configure", AssemblyShadowErrorCode.Success, delegate {
                return AssemblyShadowRuntime.ConfigureCandidates(capsule.baselineBuildId, capsule.candidateNames, capsule.stableAotNames);
            });
            Snapshot(receipt, "after-configure", sizes);
            Operation(receipt, "begin", AssemblyShadowErrorCode.Success, delegate {
                return AssemblyShadowRuntime.BeginTransaction(capsule.patchId, capsule.baselineBuildId, capsule.closureLoadOrder, RuntimeAbiVersion);
            });
            Snapshot(receipt, "after-begin", sizes);
            Operation(receipt, "reserve", AssemblyShadowErrorCode.MetadataCapacityExceeded, delegate {
                return AssemblyShadowRuntime.ReserveMetadataBudget(sizes, 1);
            });
            Snapshot(receipt, "after-failed-reserve", sizes);
            AssemblyShadowMetadataCapacity after = LastCapacity(receipt);
            Require(SameCursors(before.cursors, after.cursors) && SameCursors(before.finalCursors, after.finalCursors) &&
                before.acceptedImages == after.acceptedImages && !after.fits &&
                before.ordinaryAllocatedCount == after.ordinaryAllocatedCount && before.shadowAllocatedCount == after.shadowAllocatedCount &&
                before.reservedImageCount == after.reservedImageCount, "Failed reservation changed the shared allocation state.");
            Operation(receipt, "abort", AssemblyShadowErrorCode.Success, delegate { return AssemblyShadowRuntime.AbortTransaction(); });
            Snapshot(receipt, "after-abort", sizes);
        }

        private static void RunMismatch(Receipt receipt, Capsule capsule, List<OwnedInput> closure, long[] sizes)
        {
            Operation(receipt, "configure", AssemblyShadowErrorCode.Success, delegate {
                return AssemblyShadowRuntime.ConfigureCandidates(capsule.baselineBuildId, capsule.candidateNames, capsule.stableAotNames);
            });
            Snapshot(receipt, "after-configure", sizes);
            Operation(receipt, "begin", AssemblyShadowErrorCode.Success, delegate {
                return AssemblyShadowRuntime.BeginTransaction(capsule.patchId, capsule.baselineBuildId, capsule.closureLoadOrder, RuntimeAbiVersion);
            });
            Snapshot(receipt, "after-begin", sizes);
            Operation(receipt, "reserve", AssemblyShadowErrorCode.Success, delegate {
                return AssemblyShadowRuntime.ReserveMetadataBudget(sizes, 1);
            });
            Snapshot(receipt, "after-reserve", sizes);

            AssemblyShadowMetadataCapacity before = LastCapacity(receipt);
            OwnedInput first = closure[0];
            byte[] mismatched = new byte[checked(first.bytes.Length + 1)];
            Buffer.BlockCopy(first.bytes, 0, mismatched, 0, first.bytes.Length);
            receipt.byteInputs.Add(new ByteInputReceipt {
                name = first.name, path = first.path, length = mismatched.LongLength,
                sha256 = Sha256(mismatched), kind = "mismatch-dll"
            });
            Operation(receipt, "stage:" + first.name, AssemblyShadowErrorCode.MetadataBudgetMismatch, delegate {
                return AssemblyShadowRuntime.StageAssembly(mismatched, first.pdbBytes);
            });
            Snapshot(receipt, "after-mismatch", sizes);
            AssemblyShadowMetadataCapacity after = LastCapacity(receipt);
            Require(SameCursors(before.cursors, after.cursors) && before.ordinaryAllocatedCount == after.ordinaryAllocatedCount &&
                before.shadowAllocatedCount == after.shadowAllocatedCount && before.reservedImageCount == after.reservedImageCount,
                "Rejected Stage consumed or released an owner/index reservation.");
            Operation(receipt, "abort", AssemblyShadowErrorCode.Success, delegate { return AssemblyShadowRuntime.AbortTransaction(); });
            Snapshot(receipt, "after-abort", sizes);
        }

        private static AssemblyShadowMetadataCapacity LastCapacity(Receipt receipt)
        {
            SnapshotReceipt snapshot = receipt.snapshots[receipt.snapshots.Count - 1];
            Require(snapshot.capacityCode == "Success", "Native capacity query failed.");
            // This DTO uses the strict BCL reader, not Unity serialization.
            return AssemblyShadowMetadataCapacity.Parse(snapshot.capacityJson);
        }

        private static bool SameCursors(uint[] left, uint[] right)
        {
            if (left == null || right == null || left.Length != right.Length) return false;
            for (int i = 0; i < left.Length; ++i) if (left[i] != right[i]) return false;
            return true;
        }

        private static void RunTransaction(Receipt receipt, Capsule capsule, List<OwnedInput> closure, long[] sizes,
            OwnedInput ordinary, bool ordinaryAfterReserve, bool expectedBaselineUse, Action afterBegin = null)
        {
            Operation(receipt, "configure", AssemblyShadowErrorCode.Success, delegate {
                return AssemblyShadowRuntime.ConfigureCandidates(capsule.baselineBuildId, capsule.candidateNames, capsule.stableAotNames);
            });
            Snapshot(receipt, "after-configure", sizes);
            Operation(receipt, "begin", AssemblyShadowErrorCode.Success, delegate {
                return AssemblyShadowRuntime.BeginTransaction(capsule.patchId, capsule.baselineBuildId, capsule.closureLoadOrder, RuntimeAbiVersion);
            });
            if (afterBegin != null) afterBegin();
            Snapshot(receipt, "after-begin", sizes);
            Operation(receipt, "reserve", AssemblyShadowErrorCode.Success, delegate {
                return AssemblyShadowRuntime.ReserveMetadataBudget(sizes, 1);
            });
            Snapshot(receipt, "after-reserve", sizes);
            if (ordinaryAfterReserve)
            {
                OrdinaryGuard(receipt, ordinary, "ordinary-after-reserve");
                Snapshot(receipt, "after-ordinary-after-reserve", sizes);
            }
            for (int i = 0; i < closure.Count; ++i)
            {
                int index = i;
                Operation(receipt, "stage:" + closure[index].name, AssemblyShadowErrorCode.Success, delegate {
                    return AssemblyShadowRuntime.StageAssembly(closure[index].bytes, closure[index].pdbBytes);
                });
            }
            Snapshot(receipt, "after-stage", sizes);
            Operation(receipt, "validate", expectedBaselineUse ? AssemblyShadowErrorCode.BaselineAlreadyUsed : AssemblyShadowErrorCode.Success, delegate {
                return AssemblyShadowRuntime.ValidateTransaction();
            });
            Snapshot(receipt, "after-validate", sizes);
            if (expectedBaselineUse)
            {
                Operation(receipt, "abort", AssemblyShadowErrorCode.Success, delegate { return AssemblyShadowRuntime.AbortTransaction(); });
                Snapshot(receipt, "after-abort", sizes);
            }
            else
            {
                Operation(receipt, "commit", AssemblyShadowErrorCode.Success, delegate { return AssemblyShadowRuntime.CommitTransaction(); });
                Snapshot(receipt, "after-commit", sizes);
            }
        }

        private static void RunFailureTransaction(Receipt receipt, Capsule capsule, List<OwnedInput> closure, long[] sizes, bool initializerFailure, Action afterBegin)
        {
            Operation(receipt, "configure", AssemblyShadowErrorCode.Success, delegate {
                return AssemblyShadowRuntime.ConfigureCandidates(capsule.baselineBuildId, capsule.candidateNames, capsule.stableAotNames);
            });
            Snapshot(receipt, "after-configure", sizes);
            Operation(receipt, "begin", AssemblyShadowErrorCode.Success, delegate {
                return AssemblyShadowRuntime.BeginTransaction(capsule.patchId, capsule.baselineBuildId, capsule.closureLoadOrder, RuntimeAbiVersion);
            });
            if (afterBegin != null) afterBegin();
            Snapshot(receipt, "after-begin", sizes);
            Operation(receipt, "reserve", AssemblyShadowErrorCode.Success, delegate {
                return AssemblyShadowRuntime.ReserveMetadataBudget(sizes, 1);
            });
            Snapshot(receipt, "after-reserve", sizes);
            for (int i = 0; i < closure.Count; ++i)
            {
                int index = i;
                Operation(receipt, "stage:" + closure[index].name, AssemblyShadowErrorCode.Success, delegate {
                    return AssemblyShadowRuntime.StageAssembly(closure[index].bytes, closure[index].pdbBytes);
                });
            }
            Snapshot(receipt, "after-stage", sizes);
            Operation(receipt, "validate", initializerFailure ? AssemblyShadowErrorCode.Success : AssemblyShadowErrorCode.ReferenceResolutionFailed, delegate {
                return AssemblyShadowRuntime.ValidateTransaction();
            });
            Snapshot(receipt, "after-validate", sizes);
            if (initializerFailure)
            {
                Operation(receipt, "commit", AssemblyShadowErrorCode.ModuleInitializerFailed, delegate { return AssemblyShadowRuntime.CommitTransaction(); });
                Snapshot(receipt, "after-commit", sizes);
                Operation(receipt, "abort", AssemblyShadowErrorCode.AlreadyCommitted, delegate { return AssemblyShadowRuntime.AbortTransaction(); });
                Operation(receipt, "begin-after-commit", AssemblyShadowErrorCode.AlreadyCommitted, delegate {
                    return AssemblyShadowRuntime.BeginTransaction("R01-restart-forbidden", capsule.baselineBuildId, capsule.closureLoadOrder, RuntimeAbiVersion);
                });
                Snapshot(receipt, "after-rejected-operations", sizes);
            }
            else
            {
                Operation(receipt, "abort", AssemblyShadowErrorCode.InvalidState, delegate { return AssemblyShadowRuntime.AbortTransaction(); });
                Operation(receipt, "begin-after-failure", AssemblyShadowErrorCode.InvalidState, delegate {
                    return AssemblyShadowRuntime.BeginTransaction("R01-restart-forbidden", capsule.baselineBuildId, capsule.closureLoadOrder, RuntimeAbiVersion);
                });
                Snapshot(receipt, "after-rejected-operations", sizes);
            }
        }

        private static void Operation(Receipt receipt, string phase, AssemblyShadowErrorCode expected, Func<AssemblyShadowErrorCode> operation)
        {
            long started = Stopwatch.GetTimestamp();
            AssemblyShadowErrorCode actual;
            try { actual = operation(); }
            catch (Exception error)
            {
                receipt.operations.Add(new OperationReceipt { phase = phase, code = "Exception", intCode = -1, startedTicks = started, elapsedTicks = Stopwatch.GetTimestamp() - started });
                throw new InvalidOperationException("R01 native operation threw at " + phase + ".", error);
            }
            long elapsed = Stopwatch.GetTimestamp() - started;
            receipt.operations.Add(new OperationReceipt { phase = phase, code = actual.ToString(), intCode = (int)actual, startedTicks = started, elapsedTicks = elapsed });
            Require(actual == expected, phase + ": expected " + expected + ", got " + actual + ".");
        }

        private static void Snapshot(Receipt receipt, string phase, long[] sizes)
        {
            var snapshot = new SnapshotReceipt { phase = phase, orderedSizes = sizes == null ? new long[0] : (long[])sizes.Clone() };
            string json;
            snapshot.diagnosticsCode = AssemblyShadowRuntime.GetDiagnosticsJson(out json).ToString();
            snapshot.diagnosticsJson = json;
            snapshot.recoveryCode = AssemblyShadowRuntime.GetRecoveryInfoJson(out json).ToString();
            snapshot.recoveryJson = json;
            snapshot.capacityCode = AssemblyShadowRuntime.GetMetadataCapacityJson(snapshot.orderedSizes, out json).ToString();
            snapshot.capacityJson = json;
            receipt.snapshots.Add(snapshot);
        }

        private static void OrdinaryGuard(Receipt receipt, OwnedInput ordinary, string phase)
        {
            long started = Stopwatch.GetTimestamp();
            MethodInfo guard = FindOrdinaryGuard();
            Assembly loaded;
            try { loaded = (Assembly)guard.Invoke(null, new object[] { ordinary.bytes }); }
            catch (TargetInvocationException error) { throw error.InnerException ?? error; }
            long elapsed = Stopwatch.GetTimestamp() - started;
            receipt.operations.Add(new OperationReceipt { phase = phase, code = AssemblyShadowErrorCode.Success.ToString(), intCode = (int)AssemblyShadowErrorCode.Success, startedTicks = started, elapsedTicks = elapsed });
            Require(loaded != null && loaded.GetName().Name == OrdinaryAssemblyName, "The fixed M00 ordinary guard returned an unexpected assembly.");
        }

        private static MethodInfo FindOrdinaryGuard()
        {
            MethodInfo[] methods = typeof(AssemblyShadowBaseline.BaselineBootstrap).GetMethods(BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.DeclaredOnly);
            MethodInfo found = null;
            foreach (MethodInfo method in methods)
            {
                if (!method.Name.StartsWith(OrdinaryGuardPrefix, StringComparison.Ordinal)) continue;
                Require(found == null, "The fixed M00 ordinary guard is ambiguous.");
                Require(method.ReturnType == typeof(Assembly) && method.GetParameters().Length == 1 && method.GetParameters()[0].ParameterType == typeof(byte[]),
                    "The fixed M00 ordinary guard signature changed.");
                found = method;
            }
            Require(found != null, "The fixed M00 ordinary guard is missing.");
            return found;
        }

        private static void Witness(Receipt receipt, string mode)
        {
            long started = Stopwatch.GetTimestamp();
            if (mode == "NativeScript")
            {
                InvokeNativeScriptWitness();
            }
            else
            {
                Assembly assembly = Assembly.Load(InternalAssemblyName);
                if (mode == "Type")
                {
                    Type type = assembly.GetType(InternalEntryType, true);
                    Require(type.Assembly.GetName().Name == InternalAssemblyName, "Type witness resolved from the wrong assembly.");
                }
                else if (mode == "Object")
                {
                    Type type = assembly.GetType(ObjectWitnessType, true);
                    object value = Activator.CreateInstance(type);
                    Require(value != null && value.GetType().Assembly.GetName().Name == InternalAssemblyName, "Object witness resolved from the wrong assembly.");
                }
                else
                {
                    Type type = assembly.GetType(CctorWitnessType, true);
                    MethodInfo evidence = type.GetMethod("GetModuleEvidence", BindingFlags.Public | BindingFlags.Static);
                    Require(evidence != null, "Cctor witness method is missing.");
                    string[] values = (string[])evidence.Invoke(null, null);
                    bool observed = false;
                    foreach (string value in values ?? new string[0]) observed |= value == "cctor=1";
                    Require(observed, "Cctor witness did not report exactly one initialization.");
                }
            }
            receipt.operations.Add(new OperationReceipt { phase = "preconfigure-" + mode.ToLowerInvariant(), code = AssemblyShadowErrorCode.Success.ToString(), intCode = 0,
                startedTicks = started, elapsedTicks = Stopwatch.GetTimestamp() - started });
        }

        private static void InvokeNativeScriptWitness()
        {
            IntPtr klass = R01NativeScriptWitness.ResolveCandidate();
            Require(klass != IntPtr.Zero, "R01 native-script witness returned a null class.");
        }

        private static List<OwnedInput> ReadClosureInputs(Capsule capsule, Receipt receipt, HashSet<string> seenPaths)
        {
            var result = new List<OwnedInput>(capsule.inputs.Length);
            for (int i = 0; i < capsule.inputs.Length; ++i)
            {
                InputRecord record = capsule.inputs[i];
                Require(record.name.Equals(capsule.closureLoadOrder[i], StringComparison.OrdinalIgnoreCase), "Input order differs from closure order.");
                OwnedInput input = ReadOwned(record.name, record.dllPath, record.dllLength, record.dllSha256, "dll", receipt, seenPaths);
                if (string.IsNullOrEmpty(record.pdbPath))
                {
                    Require(record.pdbLength == 0 && record.pdbSha256.Length == 0, "Zero PDB requires empty path, hash, and length.");
                }
                else
                {
                    input.pdbBytes = ReadOwned(record.name, record.pdbPath, record.pdbLength, record.pdbSha256, "pdb", receipt, seenPaths).bytes;
                }
                result.Add(input);
            }
            return result;
        }

        private static OwnedInput ReadOrdinaryInput(Capsule capsule, Receipt receipt, HashSet<string> seenPaths)
        {
            return ReadOwned(OrdinaryAssemblyName, capsule.ordinaryPath, FileLength(capsule.ordinaryPath), capsule.ordinarySha256, "ordinary", receipt, seenPaths);
        }

        private static OwnedInput ReadOwned(string name, string path, long declaredLength, string expectedSha, string kind, Receipt receipt, HashSet<string> seenPaths)
        {
            string full = ValidatePath(path);
            Require(seenPaths.Add(full), "R01 capsule repeats a file path: " + full);
            Require(declaredLength >= 0 && declaredLength <= int.MaxValue, "Owned input length is not representable as a managed byte array.");
            receipt.inputReadCount++;
            byte[] bytes = new byte[checked((int)declaredLength)];
            string actualSha;
            using (var sha = SHA256.Create())
            using (var stream = new FileStream(full, FileMode.Open, FileAccess.Read, FileShare.Read, 65536, FileOptions.SequentialScan))
            {
                Require(stream.Length == declaredLength, "Input length changed: " + full);
                int offset = 0;
                while (offset < bytes.Length)
                {
                    int read = stream.Read(bytes, offset, bytes.Length - offset);
                    Require(read > 0, "Input ended before its declared length: " + full);
                    sha.TransformBlock(bytes, offset, read, null, 0);
                    offset += read;
                }
                Require(stream.ReadByte() == -1, "Input grew while being read: " + full);
                sha.TransformFinalBlock(new byte[0], 0, 0);
                actualSha = Hex(sha.Hash);
            }
            Require(actualSha == expectedSha, "Input SHA-256 differs: " + full);
            receipt.byteInputs.Add(new ByteInputReceipt { name = name, path = full, length = bytes.LongLength, sha256 = actualSha, kind = kind });
            return new OwnedInput { name = name, path = full, bytes = bytes };
        }

        private static void VerifyPrerequisites(Capsule capsule, Receipt receipt, HashSet<string> seenPaths)
        {
            foreach (PrerequisiteRecord prerequisite in capsule.prerequisites)
            {
                string full = ValidatePath(prerequisite.path);
                Require(seenPaths.Add(full), "R01 capsule repeats a file path: " + full);
                receipt.inputReadCount++;
                string actualSha;
                long actualLength = 0;
                using (var sha = SHA256.Create())
                using (var stream = new FileStream(full, FileMode.Open, FileAccess.Read, FileShare.Read, 65536, FileOptions.SequentialScan))
                {
                    Require(stream.Length == prerequisite.length, "Prerequisite length changed: " + full);
                    byte[] buffer = new byte[65536];
                    int read;
                    while ((read = stream.Read(buffer, 0, buffer.Length)) != 0)
                    {
                        sha.TransformBlock(buffer, 0, read, null, 0);
                        actualLength += read;
                    }
                    sha.TransformFinalBlock(new byte[0], 0, 0);
                    actualSha = Hex(sha.Hash);
                }
                Require(actualLength == prerequisite.length && actualSha == prerequisite.sha256, "Prerequisite bytes changed: " + full);
                receipt.byteInputs.Add(new ByteInputReceipt { name = "", path = full, length = actualLength, sha256 = actualSha, kind = "prerequisite" });
            }
        }

        private static void ValidateCapsule(Capsule capsule)
        {
            string[] modes = { "Control", "OrdinaryFirst", "OrdinaryAfterReserve", "Oversize", "Mismatch", "Type", "Object", "Cctor", "NativeScript", "MetadataFailure", "InitializerFailure", "Baseline" };
            Require(Array.IndexOf(modes, capsule.mode) >= 0, "Unsupported R01 early mode.");
            Require(!string.IsNullOrEmpty(capsule.baselineBuildId) && !string.IsNullOrEmpty(capsule.runtimeAbiHash) && !string.IsNullOrEmpty(capsule.patchId), "R01 capsule identity is incomplete.");
            Require(IsLowerSha(capsule.runtimeAbiHash), "R01 runtime ABI hash is malformed.");
            Require(capsule.candidateNames.Length > 0 && capsule.candidateNames.Length <= MaxArrayCount, "R01 candidate list is empty or oversized.");
            Require(capsule.closureLoadOrder.Length > 0 && capsule.closureLoadOrder.Length <= MaxArrayCount, "R01 closure list is empty or oversized.");
            Require(capsule.inputs.Length == capsule.closureLoadOrder.Length, "R01 input count differs from closure count.");
            UniqueNames(capsule.candidateNames, "candidate");
            UniqueNames(capsule.stableAotNames, "stable AOT");
            UniqueNames(capsule.closureLoadOrder, "closure");
            UniqueNames(Array.ConvertAll(capsule.inputs, delegate(InputRecord row) { return row.name; }), "input");
            var candidates = new HashSet<string>(capsule.candidateNames, StringComparer.OrdinalIgnoreCase);
            foreach (string stable in capsule.stableAotNames) Require(!candidates.Contains(stable), "Candidate/stable AOT overlap.");
            foreach (string name in capsule.closureLoadOrder) Require(candidates.Contains(name), "Closure member is not a candidate: " + name);
            bool ordinaryMode = capsule.mode == "OrdinaryFirst" || capsule.mode == "OrdinaryAfterReserve";
            if (ordinaryMode)
                Require(Path.IsPathRooted(capsule.ordinaryPath) && capsule.ordinarySha256 == FixedOrdinarySha256, "R01 ordinary input is not the pinned M00 image.");
            else
                Require(capsule.ordinaryPath.Length == 0 && capsule.ordinarySha256.Length == 0, "Unexpected ordinary payload.");
            Require(capsule.prerequisites.Length > 0 && capsule.prerequisites.Length <= MaxArrayCount, "R01 prerequisite list is missing or oversized.");
            foreach (InputRecord input in capsule.inputs)
            {
                Require(IsLowerSha(input.dllSha256) && input.dllLength >= 0, "R01 DLL input is malformed.");
                bool noPdb = string.IsNullOrEmpty(input.pdbPath);
                Require(noPdb ? input.pdbLength == 0 && input.pdbSha256.Length == 0 : input.pdbLength > 0 && IsLowerSha(input.pdbSha256), "R01 PDB tuple is malformed.");
            }
            foreach (PrerequisiteRecord prerequisite in capsule.prerequisites)
                Require(prerequisite.length >= 0 && IsLowerSha(prerequisite.sha256), "R01 prerequisite tuple is malformed.");
        }

        private static void UniqueNames(string[] values, string kind)
        {
            var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            foreach (string value in values)
            {
                Require(!string.IsNullOrEmpty(value) && seen.Add(value), "Duplicate or empty " + kind + " name.");
            }
        }

        private static byte[] ReadCapsuleBytes(string path)
        {
            string full = ValidatePath(path);
            using (var stream = new FileStream(full, FileMode.Open, FileAccess.Read, FileShare.Read, 65536, FileOptions.SequentialScan))
            {
                Require(stream.Length <= MaxCapsuleBytes, "R01 capsule exceeds the 16 MiB limit.");
                byte[] bytes = new byte[checked((int)stream.Length)];
                int offset = 0;
                while (offset < bytes.Length)
                {
                    int read = stream.Read(bytes, offset, bytes.Length - offset);
                    Require(read > 0, "R01 capsule ended early.");
                    offset += read;
                }
                Require(stream.ReadByte() == -1, "R01 capsule grew while being read.");
                return bytes;
            }
        }

        private static string ValidatePath(string path)
        {
            Require(!string.IsNullOrEmpty(path) && Path.IsPathRooted(path) && path.IndexOf('\0') < 0, "R01 path must be absolute and NUL-free.");
            return Path.GetFullPath(path);
        }

        private static long FileLength(string path)
        {
            string full = ValidatePath(path);
            Require(File.Exists(full), "R01 input file is missing: " + full);
            return new FileInfo(full).Length;
        }

        private static bool IsLowerSha(string value)
        {
            if (value == null || value.Length != 64) return false;
            for (int i = 0; i < value.Length; ++i)
                if ((value[i] < '0' || value[i] > '9') && (value[i] < 'a' || value[i] > 'f')) return false;
            return true;
        }

        private static string Sha256(byte[] bytes)
        {
            using (var sha = SHA256.Create()) return Hex(sha.ComputeHash(bytes));
        }

        private static string Hex(byte[] bytes)
        {
            var builder = new StringBuilder(bytes.Length * 2);
            foreach (byte value in bytes) builder.Append(value.ToString("x2"));
            return builder.ToString();
        }

        private static int ProcessId()
        {
            try { return Process.GetCurrentProcess().Id; }
            catch { return 0; }
        }

        private static void WriteNew(string path, string json)
        {
            string parent = Path.GetDirectoryName(path);
            if (!string.IsNullOrEmpty(parent) && !Directory.Exists(parent)) Directory.CreateDirectory(parent);
            using (var stream = new FileStream(path, FileMode.CreateNew, FileAccess.Write, FileShare.None))
            using (var writer = new StreamWriter(stream, new UTF8Encoding(false))) writer.Write(json);
        }

        private static void Require(bool condition, string message)
        {
            if (!condition) throw new InvalidDataException(message);
        }

        public sealed class Capsule
        {
            public string mode, baselineBuildId, runtimeAbiHash, patchId;
            public string[] candidateNames, stableAotNames, closureLoadOrder;
            public InputRecord[] inputs;
            public string ordinaryPath, ordinarySha256;
            public PrerequisiteRecord[] prerequisites;
        }

        public sealed class InputRecord
        {
            public string name, dllPath, dllSha256, pdbPath, pdbSha256;
            public long dllLength, pdbLength;
        }

        public sealed class PrerequisiteRecord
        {
            public string path, sha256;
            public long length;
        }

        private sealed class OwnedInput
        {
            public string name, path;
            public byte[] bytes, pdbBytes;
        }

        public static class CapsuleCodec
        {
            public static Capsule Parse(byte[] bytes)
            {
                Require(bytes != null && bytes.Length <= MaxCapsuleBytes, "R01 capsule is null or oversized.");
                var reader = new CapsuleReader(bytes);
                Require(reader.ReadAscii(8) == CapsuleMagic, "R01 capsule magic is invalid.");
                Require(reader.ReadInt32() == CapsuleVersion, "R01 capsule version is unsupported.");
                var capsule = new Capsule {
                    mode = reader.ReadString(), baselineBuildId = reader.ReadString(), runtimeAbiHash = reader.ReadString(), patchId = reader.ReadString(),
                    candidateNames = reader.ReadStrings(), stableAotNames = reader.ReadStrings()
                };
                int inputCount = reader.ReadCount();
                capsule.inputs = new InputRecord[inputCount];
                for (int i = 0; i < inputCount; ++i)
                    capsule.inputs[i] = new InputRecord { name = reader.ReadString(), dllPath = reader.ReadString(), dllLength = reader.ReadInt64(), dllSha256 = reader.ReadString(), pdbPath = reader.ReadString(), pdbLength = reader.ReadInt64(), pdbSha256 = reader.ReadString() };
                capsule.closureLoadOrder = Array.ConvertAll(capsule.inputs, delegate(InputRecord input) { return input.name; });
                capsule.ordinaryPath = reader.ReadString();
                capsule.ordinarySha256 = reader.ReadString();
                int prerequisiteCount = reader.ReadCount();
                capsule.prerequisites = new PrerequisiteRecord[prerequisiteCount];
                for (int i = 0; i < prerequisiteCount; ++i)
                    capsule.prerequisites[i] = new PrerequisiteRecord { path = reader.ReadString(), length = reader.ReadInt64(), sha256 = reader.ReadString() };
                reader.End();
                ValidateCapsule(capsule);
                return capsule;
            }
        }

        private sealed class CapsuleReader
        {
            private readonly byte[] bytes;
            private int offset;
            internal CapsuleReader(byte[] bytes) { this.bytes = bytes; }
            internal string ReadAscii(int count)
            {
                byte[] value = ReadBytes(count);
                for (int i = 0; i < value.Length; ++i) Require(value[i] < 128, "R01 capsule magic is not ASCII.");
                return Encoding.ASCII.GetString(value);
            }
            internal int ReadInt32() { return unchecked((int)(uint)(ReadByte() | (ReadByte() << 8) | (ReadByte() << 16) | (ReadByte() << 24))); }
            internal long ReadInt64()
            {
                ulong value = 0;
                for (int i = 0; i < 8; ++i) value |= ((ulong)ReadByte()) << (8 * i);
                return unchecked((long)value);
            }
            internal string ReadString()
            {
                int length = ReadInt32();
                Require(length >= 0 && length <= MaxStringBytes && length <= bytes.Length - offset, "R01 capsule string length is invalid.");
                string value;
                try { value = new UTF8Encoding(false, true).GetString(ReadBytes(length)); }
                catch (DecoderFallbackException error) { throw new InvalidDataException("R01 capsule string is not UTF-8.", error); }
                Require(value.IndexOf('\0') < 0, "R01 capsule string contains NUL.");
                return value;
            }
            internal string[] ReadStrings()
            {
                int count = ReadCount();
                var values = new string[count];
                for (int i = 0; i < count; ++i) values[i] = ReadString();
                return values;
            }
            internal int ReadCount()
            {
                int count = ReadInt32();
                Require(count >= 0 && count <= MaxArrayCount, "R01 capsule array count is invalid.");
                return count;
            }
            internal void End() { Require(offset == bytes.Length, "R01 capsule has trailing bytes."); }
            private byte[] ReadBytes(int count)
            {
                Require(count >= 0 && count <= bytes.Length - offset, "R01 capsule is truncated.");
                var value = new byte[count];
                Buffer.BlockCopy(bytes, offset, value, 0, count);
                offset += count;
                return value;
            }
            private byte ReadByte()
            {
                Require(offset < bytes.Length, "R01 capsule is truncated.");
                return bytes[offset++];
            }
        }

        public sealed class Receipt
        {
            public int schemaVersion = 1, processId, managedThreadId, callbackReturnCode;
            public long stopwatchFrequency, elapsedTicks;
            public string kind = "R01EarlyStartupReceipt", mode = "", capsulePath = "", capsuleSha256 = "", resultPath = "", baselineBuildId = "", runtimeAbiHash = "", patchId = "", result = "Failed", error = "";
            public int inputReadCount;
            public bool observerJoined;
            public int observerDroppedBefore, observerDroppedAfter;
            public string[] observerErrors = new string[0];
            public R01EarlyObserver.Sample[] observerSamples = new R01EarlyObserver.Sample[0];
            public R01EarlyInitializerCapture.Event[] initializerEvents = new R01EarlyInitializerCapture.Event[0];
            public List<OperationReceipt> operations = new List<OperationReceipt>();
            public List<SnapshotReceipt> snapshots = new List<SnapshotReceipt>();
            public List<ByteInputReceipt> byteInputs = new List<ByteInputReceipt>();
        }

        public sealed class OperationReceipt
        {
            public string phase = "", code = "";
            public int intCode;
            public long startedTicks, elapsedTicks;
        }

        public sealed class SnapshotReceipt
        {
            public string phase = "", diagnosticsCode = "", diagnosticsJson = "", recoveryCode = "", recoveryJson = "", capacityCode = "", capacityJson = "";
            public long[] orderedSizes = new long[0];
        }

        public sealed class ByteInputReceipt
        {
            public string name = "", path = "", sha256 = "", kind = "";
            public long length;
        }

        public static class ReceiptCodec
        {
            public static string Serialize(Receipt receipt)
            {
                var json = new StringBuilder(4096);
                json.Append('{');
                Property(json, "schemaVersion", receipt.schemaVersion); Property(json, "kind", receipt.kind); Property(json, "mode", receipt.mode);
                Property(json, "processId", receipt.processId); Property(json, "managedThreadId", receipt.managedThreadId); Property(json, "stopwatchFrequency", receipt.stopwatchFrequency); Property(json, "elapsedTicks", receipt.elapsedTicks);
                Property(json, "capsulePath", receipt.capsulePath); Property(json, "capsuleSha256", receipt.capsuleSha256); Property(json, "resultPath", receipt.resultPath);
                Property(json, "baselineBuildId", receipt.baselineBuildId); Property(json, "runtimeAbiHash", receipt.runtimeAbiHash); Property(json, "patchId", receipt.patchId);
                Property(json, "result", receipt.result); Property(json, "error", receipt.error); Property(json, "callbackReturnCode", receipt.callbackReturnCode); Property(json, "inputReadCount", receipt.inputReadCount);
                Array(json, "operations", receipt.operations, WriteOperation); Array(json, "snapshots", receipt.snapshots, WriteSnapshot); Array(json, "byteInputs", receipt.byteInputs, WriteByteInput);
                Property(json, "observerJoined", receipt.observerJoined);
                Property(json, "observerDroppedBefore", receipt.observerDroppedBefore); Property(json, "observerDroppedAfter", receipt.observerDroppedAfter);
                Array(json, "observerErrors", receipt.observerErrors, delegate(StringBuilder b, string value) { String(b, value); });
                Array(json, "observerSamples", receipt.observerSamples, WriteSample);
                Array(json, "initializerEvents", receipt.initializerEvents, WriteInitializer);
                json.Append('}');
                return json.ToString();
            }

            private static void WriteOperation(StringBuilder json, OperationReceipt value)
            {
                json.Append('{'); Property(json, "phase", value.phase); Property(json, "code", value.code); Property(json, "intCode", value.intCode); Property(json, "startedTicks", value.startedTicks); Property(json, "elapsedTicks", value.elapsedTicks); json.Append('}');
            }
            private static void WriteSample(StringBuilder json, R01EarlyObserver.Sample value)
            {
                json.Append('{'); Property(json, "phase", value.phase); Property(json, "rawJson", value.rawJson);
                Property(json, "code", value.code); Property(json, "threadId", value.threadId); Property(json, "ticks", value.ticks); json.Append('}');
            }
            private static void WriteInitializer(StringBuilder json, R01EarlyInitializerCapture.Event value)
            {
                json.Append('{'); Property(json, "name", value.name); Name(json, "diagnostics"); WriteSample(json, value.diagnostics); json.Append('}');
            }
            private static void WriteSnapshot(StringBuilder json, SnapshotReceipt value)
            {
                json.Append('{'); Property(json, "phase", value.phase); Property(json, "diagnosticsCode", value.diagnosticsCode); Property(json, "diagnosticsJson", value.diagnosticsJson); Property(json, "recoveryCode", value.recoveryCode); Property(json, "recoveryJson", value.recoveryJson); Property(json, "capacityCode", value.capacityCode); Property(json, "capacityJson", value.capacityJson); Array(json, "orderedSizes", value.orderedSizes, delegate(StringBuilder b, long n) { b.Append(n.ToString(System.Globalization.CultureInfo.InvariantCulture)); }); json.Append('}');
            }
            private static void WriteByteInput(StringBuilder json, ByteInputReceipt value)
            {
                json.Append('{'); Property(json, "name", value.name); Property(json, "path", value.path); Property(json, "length", value.length); Property(json, "sha256", value.sha256); Property(json, "kind", value.kind); json.Append('}');
            }
            private static void Array<T>(StringBuilder json, string name, IList<T> values, Action<StringBuilder, T> writer)
            {
                Name(json, name); json.Append('[');
                for (int i = 0; i < values.Count; ++i) { if (i != 0) json.Append(','); writer(json, values[i]); }
                json.Append(']');
            }
            private static void Array(StringBuilder json, string name, long[] values, Action<StringBuilder, long> writer)
            {
                Name(json, name); json.Append('[');
                for (int i = 0; i < values.Length; ++i) { if (i != 0) json.Append(','); writer(json, values[i]); }
                json.Append(']');
            }
            private static void Property(StringBuilder json, string name, string value) { Name(json, name); String(json, value ?? ""); }
            private static void Property(StringBuilder json, string name, int value) { Name(json, name); json.Append(value.ToString(System.Globalization.CultureInfo.InvariantCulture)); }
            private static void Property(StringBuilder json, string name, bool value) { Name(json, name); json.Append(value ? "true" : "false"); }
            private static void Property(StringBuilder json, string name, long value) { Name(json, name); json.Append(value.ToString(System.Globalization.CultureInfo.InvariantCulture)); }
            private static void Name(StringBuilder json, string name) { if (json[json.Length - 1] != '{' && json[json.Length - 1] != '[') json.Append(','); String(json, name); json.Append(':'); }
            private static void String(StringBuilder json, string value)
            {
                json.Append('"');
                foreach (char c in value)
                {
                    switch (c)
                    {
                        case '"': json.Append("\\\""); break; case '\\': json.Append("\\\\"); break; case '\b': json.Append("\\b"); break; case '\f': json.Append("\\f"); break; case '\n': json.Append("\\n"); break; case '\r': json.Append("\\r"); break; case '\t': json.Append("\\t"); break;
                        default: if (c < 32) json.Append("\\u").Append(((int)c).ToString("x4")); else json.Append(c); break;
                    }
                }
                json.Append('"');
            }
        }

        private sealed class Arguments
        {
            public string capsulePath, capsuleSha256, resultPath;
            public static Arguments Read(string[] args)
            {
                var result = new Arguments();
                result.capsulePath = One(args, CapsuleArgument); result.capsuleSha256 = One(args, CapsuleShaArgument); result.resultPath = One(args, ResultArgument);
                result.capsulePath = ValidatePath(result.capsulePath); result.resultPath = ValidatePath(result.resultPath);
                Require(IsLowerSha(result.capsuleSha256), "R01 capsule SHA-256 argument is malformed.");
                return result;
            }
            private static string One(string[] args, string name)
            {
                string found = null;
                for (int i = 0; i < args.Length; ++i)
                    if (args[i] == name)
                    {
                        Require(found == null && i + 1 < args.Length && !string.IsNullOrEmpty(args[i + 1]), "R01 argument is missing or duplicated: " + name);
                        found = args[++i];
                    }
                Require(found != null, "R01 argument is missing: " + name);
                return found;
            }
        }
    }
}
