using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using HybridCLR.Editor;
using HybridCLR.Editor.AssemblyShadow;
using UnityEditor.Build;
using UnityEngine;

namespace AssemblyShadowDemo.Editor
{
    /// <summary>Captures an immutable copy of the exact pinned native installation used by an H1 diagnostic build.</summary>
    public static class H1BuildInputProvenance
    {
        private const int VerificationTimeoutMilliseconds = 120000;
        private static readonly string[] GeneratedFiles = {
            "hybridclr/generated/AssemblyManifest.cpp",
            "hybridclr/generated/MethodBridge.cpp",
            "hybridclr/generated/UnityVersion.h",
            "hybridclr/generated/libil2cpp-version.txt",
        };

        public static Capture CaptureAfterGenerate(string projectRoot, string sourcePinFile, bool featureEnabled)
        {
            return CaptureAfterGenerate(projectRoot, sourcePinFile, featureEnabled, null);
        }

        public static Capture CaptureAfterGenerate(string projectRoot, string sourcePinFile, bool featureEnabled,
            string snapshotParent)
        {
            projectRoot = Path.GetFullPath(projectRoot);
            string liveInstalledRoot = Path.GetFullPath(Path.Combine(SettingsUtil.LocalIl2CppDir, "libil2cpp"));
            string liveExternalRoot = Path.GetFullPath(Path.Combine(SettingsUtil.LocalIl2CppDir, "external"));
            string livePinsPath = MakeProjectPath(projectRoot, sourcePinFile);
            Require(livePinsPath == Path.GetFullPath(Path.Combine(projectRoot, "ProjectSettings/AssemblyShadowSourcePins.json")),
                "Native verifier requires the canonical ProjectSettings/AssemblyShadowSourcePins.json source pin.");
            string liveVerifier = Path.Combine(projectRoot, "Tools/AssemblyShadow/verify-installed-runtime.py");
            string liveSupportVerifier = Path.Combine(Path.GetDirectoryName(liveVerifier), "shadow_tools.py");
            RequireRegularFile(livePinsPath, "Pinned source file");
            RequireRegularFile(liveVerifier, "Native verification tool");
            RequireRegularFile(liveSupportVerifier, "Native verification support tool");
            string python = FindPython3();
            string liveSourcePinSha256 = ShadowHash.File(livePinsPath);
            string liveVerificationToolSha256 = ShadowHash.File(liveVerifier);
            string liveVerificationSupportToolSha256 = ShadowHash.File(liveSupportVerifier);
            string pythonExecutableSha256 = ShadowHash.File(python);
            string liveInstallReceiptPath = Path.Combine(liveInstalledRoot, "assembly-shadow-install.json");
            Inventory liveInstalledInventory = CaptureInventory(liveInstalledRoot);
            Inventory liveExternalInventory = CaptureExternalInventory(liveExternalRoot);
            string liveInstallReceiptSha256 = ShadowHash.File(liveInstallReceiptPath);

            string expectedShadow = featureEnabled ? "on" : "off";
            string[] argv = { python, liveVerifier, "--project", projectRoot, "--skip-demo-source", "--expect-shadow", expectedShadow, "--json" };
            ProcessResult result = Run(argv, projectRoot);
            Require(result.exitCode == 0 && !result.timedOut,
                "Pinned native installation verification failed with exit code " + result.exitCode +
                "; timedOut=" + result.timedOut + "; killAttempted=" + result.killAttempted +
                "; killError=" + result.killError + "; stdout=" + result.stdout + "; stderr=" + result.stderr);
            Require(ShadowHash.File(livePinsPath) == liveSourcePinSha256,
                "Pinned source file changed during native installation verification.");
            Require(ShadowHash.File(liveVerifier) == liveVerificationToolSha256,
                "Native verification tool changed while it was running.");
            Require(ShadowHash.File(liveSupportVerifier) == liveVerificationSupportToolSha256,
                "Native verification support tool changed during native installation verification.");
            Require(ShadowHash.File(python) == pythonExecutableSha256,
                "Python executable changed during native installation verification.");
            Require(ShadowHash.File(liveInstallReceiptPath) == liveInstallReceiptSha256,
                "Installed native receipt changed during native installation verification.");
            Inventory liveInstalledAfterVerification = CaptureInventory(liveInstalledRoot);
            Inventory liveExternalAfterVerification = CaptureExternalInventory(liveExternalRoot);
            Require(liveInstalledAfterVerification.hash == liveInstalledInventory.hash &&
                    SameFiles(liveInstalledAfterVerification.files, liveInstalledInventory.files),
                "Installed libil2cpp changed during native installation verification.");
            Require(liveExternalAfterVerification.hash == liveExternalInventory.hash &&
                    SameFiles(liveExternalAfterVerification.files, liveExternalInventory.files),
                "External native files changed during native installation verification.");

            string snapshotRoot = CreateSnapshotRoot(projectRoot, snapshotParent);
            string snapshotSourcePinFile = Path.Combine(snapshotRoot, "source-pins.json");
            string snapshotVerificationToolPath = Path.Combine(snapshotRoot, "tools", "verify-installed-runtime.py");
            string snapshotVerificationSupportToolPath = Path.Combine(snapshotRoot, "tools", "shadow_tools.py");
            string snapshotInstalledRoot = Path.Combine(snapshotRoot, "installedlibil2cpp");
            string snapshotExternalRoot = Path.Combine(snapshotRoot, "external");
            CopyFileExact(livePinsPath, snapshotSourcePinFile, liveSourcePinSha256, "pinned source file");
            CopyFileExact(liveVerifier, snapshotVerificationToolPath, liveVerificationToolSha256, "native verification tool");
            CopyFileExact(liveSupportVerifier, snapshotVerificationSupportToolPath,
                liveVerificationSupportToolSha256, "native verification support tool");
            CopyInventory(liveInstalledRoot, snapshotInstalledRoot, liveInstalledInventory.files, "installed libil2cpp");
            CopyInventory(liveExternalRoot, snapshotExternalRoot, liveExternalInventory.files, "external native");

            Inventory snapshotInstalledInventory = CaptureInventory(snapshotInstalledRoot);
            Inventory snapshotExternalInventory = CaptureExternalInventory(snapshotExternalRoot);
            Require(snapshotInstalledInventory.hash == liveInstalledInventory.hash &&
                    SameFiles(snapshotInstalledInventory.files, liveInstalledInventory.files),
                "Copied installed libil2cpp snapshot differs from the verified live inventory.");
            Require(snapshotExternalInventory.hash == liveExternalInventory.hash &&
                    SameFiles(snapshotExternalInventory.files, liveExternalInventory.files),
                "Copied external native snapshot differs from the verified live inventory.");
            Inventory snapshotInventory = CaptureSnapshotInventory(snapshotRoot);

            Require(ShadowHash.File(livePinsPath) == liveSourcePinSha256,
                "Pinned source file changed while its immutable snapshot was created.");
            Require(ShadowHash.File(liveVerifier) == liveVerificationToolSha256,
                "Native verification tool changed while its immutable snapshot was created.");
            Require(ShadowHash.File(liveSupportVerifier) == liveVerificationSupportToolSha256,
                "Native verification support tool changed while its immutable snapshot was created.");
            Require(ShadowHash.File(python) == pythonExecutableSha256,
                "Python executable changed while native provenance was captured.");
            Require(ShadowHash.File(liveInstallReceiptPath) == liveInstallReceiptSha256,
                "Installed native receipt changed while its immutable snapshot was created.");
            Inventory liveInstalledAfterCopy = CaptureInventory(liveInstalledRoot);
            Inventory liveExternalAfterCopy = CaptureExternalInventory(liveExternalRoot);
            Require(liveInstalledAfterCopy.hash == liveInstalledInventory.hash &&
                    SameFiles(liveInstalledAfterCopy.files, liveInstalledInventory.files),
                "Installed libil2cpp changed while its immutable snapshot was created.");
            Require(liveExternalAfterCopy.hash == liveExternalInventory.hash &&
                    SameFiles(liveExternalAfterCopy.files, liveExternalInventory.files),
                "External native files changed while their immutable snapshot was created.");

            return new Capture {
                schemaVersion = 2,
                projectRoot = projectRoot,
                snapshotRoot = snapshotRoot,
                snapshotFiles = snapshotInventory.files,
                snapshotInventorySha256 = snapshotInventory.hash,
                installedRoot = snapshotInstalledRoot,
                sourcePinFile = snapshotSourcePinFile,
                sourcePinSha256 = liveSourcePinSha256,
                installReceiptPath = Path.Combine(snapshotInstalledRoot, "assembly-shadow-install.json"),
                installReceiptSha256 = liveInstallReceiptSha256,
                verificationToolPath = snapshotVerificationToolPath,
                verificationToolSha256 = liveVerificationToolSha256,
                verificationSupportToolPath = snapshotVerificationSupportToolPath,
                verificationSupportToolSha256 = liveVerificationSupportToolSha256,
                pythonExecutable = python,
                pythonExecutableSha256 = pythonExecutableSha256,
                verificationArgv = argv,
                verificationExitCode = result.exitCode,
                verificationStdout = result.stdout,
                verificationStderr = result.stderr,
                installedFiles = snapshotInstalledInventory.files,
                installedInventorySha256 = snapshotInstalledInventory.hash,
                externalRoot = snapshotExternalRoot,
                externalFiles = snapshotExternalInventory.files,
                externalInventorySha256 = snapshotExternalInventory.hash,
                liveInstalledRoot = liveInstalledRoot,
                liveExternalRoot = liveExternalRoot,
                liveSourcePinFile = livePinsPath,
                liveSourcePinSha256 = liveSourcePinSha256,
                liveInstallReceiptPath = liveInstallReceiptPath,
                liveInstallReceiptSha256 = liveInstallReceiptSha256,
                liveVerificationToolPath = liveVerifier,
                liveVerificationToolSha256 = liveVerificationToolSha256,
                liveVerificationSupportToolPath = liveSupportVerifier,
                liveVerificationSupportToolSha256 = liveVerificationSupportToolSha256,
                liveInstalledInventorySha256 = liveInstalledInventory.hash,
                liveExternalInventorySha256 = liveExternalInventory.hash,
            };
        }

        public static void RequireUnchanged(Capture expected)
        {
            Require(expected != null, "Native provenance capture is missing.");
            Require(expected.schemaVersion == 2, "Native provenance capture has an unsupported schema version.");
            Require(IsWithinRoot(expected.snapshotRoot, expected.sourcePinFile) &&
                    IsWithinRoot(expected.snapshotRoot, expected.verificationToolPath) &&
                    IsWithinRoot(expected.snapshotRoot, expected.verificationSupportToolPath) &&
                    IsWithinRoot(expected.snapshotRoot, expected.installReceiptPath) &&
                    IsWithinRoot(expected.snapshotRoot, expected.installedRoot) &&
                    IsWithinRoot(expected.snapshotRoot, expected.externalRoot),
                "Native provenance snapshot paths are not contained by the immutable snapshot root.");
            Require(ShadowHash.File(expected.sourcePinFile) == expected.sourcePinSha256, "Snapshotted source pin file changed during H1 Player build.");
            Require(ShadowHash.File(expected.verificationToolPath) == expected.verificationToolSha256, "Snapshotted native verification tool changed during H1 Player build.");
            Require(ShadowHash.File(expected.verificationSupportToolPath) == expected.verificationSupportToolSha256, "Snapshotted native verification support tool changed during H1 Player build.");
            Require(ShadowHash.File(expected.installReceiptPath) == expected.installReceiptSha256, "Snapshotted native receipt changed during H1 Player build.");
            Inventory snapshotInstalled = CaptureInventory(expected.installedRoot);
            Require(snapshotInstalled.hash == expected.installedInventorySha256 && SameFiles(snapshotInstalled.files, expected.installedFiles),
                "Snapshotted installed libil2cpp files or hashes changed during H1 Player build.");
            Inventory snapshotExternal = CaptureExternalInventory(expected.externalRoot);
            Require(snapshotExternal.hash == expected.externalInventorySha256 && SameFiles(snapshotExternal.files, expected.externalFiles),
                "Snapshotted external native files or hashes changed during H1 Player build.");
            Inventory snapshot = CaptureSnapshotInventory(expected.snapshotRoot);
            Require(snapshot.hash == expected.snapshotInventorySha256 && SameFiles(snapshot.files, expected.snapshotFiles),
                "Native provenance snapshot files or hashes changed during H1 Player build.");

            Require(ShadowHash.File(expected.liveSourcePinFile) == expected.liveSourcePinSha256, "Live source pin file changed during H1 Player build.");
            Require(ShadowHash.File(expected.liveVerificationToolPath) == expected.liveVerificationToolSha256, "Live native verification tool changed during H1 Player build.");
            Require(ShadowHash.File(expected.liveVerificationSupportToolPath) == expected.liveVerificationSupportToolSha256, "Live native verification support tool changed during H1 Player build.");
            Require(ShadowHash.File(expected.pythonExecutable) == expected.pythonExecutableSha256, "Python executable changed during H1 Player build.");
            Require(ShadowHash.File(expected.liveInstallReceiptPath) == expected.liveInstallReceiptSha256, "Live installed native receipt changed during H1 Player build.");
            Inventory liveInstalled = CaptureInventory(expected.liveInstalledRoot);
            Require(liveInstalled.hash == expected.liveInstalledInventorySha256 && SameFiles(liveInstalled.files, expected.installedFiles),
                "Live installed libil2cpp files or hashes changed during H1 Player build.");
            Inventory liveExternal = CaptureExternalInventory(expected.liveExternalRoot);
            Require(liveExternal.hash == expected.liveExternalInventorySha256 && SameFiles(liveExternal.files, expected.externalFiles),
                "Live external native files or hashes changed during H1 Player build.");
        }

        private static string CreateSnapshotRoot(string projectRoot, string snapshotParent)
        {
            string parent = string.IsNullOrWhiteSpace(snapshotParent)
                ? Path.Combine(projectRoot, "_temp", "AssemblyShadow")
                : MakeProjectPath(projectRoot, snapshotParent);
            Directory.CreateDirectory(parent);
            Require(!IsSymlink(parent), "Native provenance snapshot parent is symlinked: " + parent);
            for (int attempt = 0; attempt != 10; ++attempt)
            {
                string root = Path.Combine(parent, "H1NativeProvenance-" + Guid.NewGuid().ToString("N"));
                if (File.Exists(root) || Directory.Exists(root)) continue;
                Directory.CreateDirectory(root);
                Require(!IsSymlink(root), "Native provenance snapshot root is symlinked: " + root);
                return root;
            }
            throw new BuildFailedException("Could not allocate a new native provenance snapshot directory under: " + parent);
        }

        private static void CopyInventory(string sourceRoot, string destinationRoot, FileEntry[] files, string label)
        {
            Require(files != null && files.Length != 0, "Cannot snapshot an empty " + label + " inventory.");
            Require(!File.Exists(destinationRoot) && !Directory.Exists(destinationRoot),
                "Native provenance destination must be new: " + destinationRoot);
            Directory.CreateDirectory(destinationRoot);
            foreach (FileEntry file in files.OrderBy(item => item.path, StringComparer.Ordinal))
            {
                Require(file != null && IsSafeRelative(file.path) && file.sha256 != null && file.sha256.Length == 64,
                    "Cannot snapshot an invalid " + label + " inventory entry.");
                string relativePath = file.path.Replace('/', Path.DirectorySeparatorChar);
                CopyFileExact(Path.Combine(sourceRoot, relativePath), Path.Combine(destinationRoot, relativePath),
                    file.sha256, label + " file " + file.path);
            }
        }

        private static void CopyFileExact(string source, string destination, string expectedSha256, string label)
        {
            RequireRegularFile(source, label);
            Require(ShadowHash.File(source) == expectedSha256, label + " changed before it could be snapshotted: " + source);
            Require(!File.Exists(destination) && !Directory.Exists(destination),
                "Native provenance snapshot path must be new: " + destination);
            string parent = Path.GetDirectoryName(destination);
            Require(!string.IsNullOrEmpty(parent), "Native provenance snapshot file has no parent: " + destination);
            Directory.CreateDirectory(parent);
            File.Copy(source, destination, false);
            RequireRegularFile(destination, "Snapshotted " + label);
            Require(ShadowHash.File(destination) == expectedSha256,
                "Snapshotted " + label + " differs from its verified live bytes: " + destination);
        }

        private static Inventory CaptureSnapshotInventory(string snapshotRoot)
        {
            Require(Directory.Exists(snapshotRoot) && !IsSymlink(snapshotRoot),
                "Native provenance snapshot root is missing or symlinked: " + snapshotRoot);
            var files = new List<FileEntry>();
            var pendingDirectories = new Stack<string>();
            pendingDirectories.Push(snapshotRoot);
            while (pendingDirectories.Count != 0)
            {
                string directory = pendingDirectories.Pop();
                foreach (string file in Directory.GetFiles(directory, "*", SearchOption.TopDirectoryOnly))
                {
                    Require(!IsSymlink(file), "Symlinked native provenance snapshot file: " + file);
                    files.Add(new FileEntry {
                        path = Relative(snapshotRoot, file), source = "snapshot", sha256 = ShadowHash.File(file),
                    });
                }
                foreach (string child in Directory.GetDirectories(directory, "*", SearchOption.TopDirectoryOnly))
                {
                    Require(!IsSymlink(child), "Symlinked native provenance snapshot directory: " + child);
                    pendingDirectories.Push(child);
                }
            }
            Require(files.Count != 0, "Native provenance snapshot inventory is empty: " + snapshotRoot);
            files = files.OrderBy(item => item.path, StringComparer.Ordinal).ToList();
            return new Inventory { files = files.ToArray(), hash = InventoryHash(files) };
        }

        private static Inventory CaptureInventory(string installedRoot)
        {
            Require(Directory.Exists(installedRoot) && !IsSymlink(installedRoot), "Installed libil2cpp root is missing or symlinked: " + installedRoot);
            for (DirectoryInfo parent = new DirectoryInfo(installedRoot); parent != null; parent = parent.Parent)
                Require(!IsSymlink(parent.FullName), "Symlinked installed native path component: " + parent.FullName);
            string receiptPath = Path.Combine(installedRoot, "assembly-shadow-install.json");
            Require(File.Exists(receiptPath) && !IsSymlink(receiptPath), "Installed native receipt is missing or symlinked: " + receiptPath);
            InstallReceipt receipt = JsonUtility.FromJson<InstallReceipt>(File.ReadAllText(receiptPath));
            Require(receipt != null && receipt.sourceFileHashes != null, "Installed native receipt has no source inventory.");
            var expected = new Dictionary<string, FileEntry>(StringComparer.Ordinal);
            foreach (SourceFileHash source in receipt.sourceFileHashes)
            {
                Require(source != null && !string.IsNullOrWhiteSpace(source.source) && source.sha256 != null && source.sha256.Length == 64 &&
                    IsSafeRelative(source.path) && !expected.ContainsKey(source.path),
                    "Installed native receipt contains an invalid or duplicate source path.");
                expected.Add(source.path, new FileEntry { path = source.path, source = source.source, sha256 = source.sha256 });
            }
            Require(receipt.generatedFileExclusions != null && receipt.generatedFileExclusions.Length == GeneratedFiles.Length &&
                new HashSet<string>(receipt.generatedFileExclusions, StringComparer.Ordinal).SetEquals(GeneratedFiles),
                "Installed native generated exclusions differ from the fixed four-file contract.");
            foreach (string generated in GeneratedFiles)
            {
                // The receipt retains the pinned template hash; generated build bytes are captured independently.
                expected[generated] = new FileEntry { path = generated, source = "generated", sha256 = "" };
            }
            expected.Add("assembly-shadow-install.json", new FileEntry { path = "assembly-shadow-install.json", source = "install-receipt", sha256 = "" });
            var actualPathList = new List<string>();
            var pendingDirectories = new Stack<string>();
            pendingDirectories.Push(installedRoot);
            while (pendingDirectories.Count != 0)
            {
                string directory = pendingDirectories.Pop();
                foreach (string file in Directory.GetFiles(directory, "*", SearchOption.TopDirectoryOnly))
                {
                    Require(!IsSymlink(file), "Symlinked installed native file: " + file);
                    actualPathList.Add(Relative(installedRoot, file));
                }
                foreach (string child in Directory.GetDirectories(directory, "*", SearchOption.TopDirectoryOnly))
                {
                    Require(!IsSymlink(child), "Symlinked installed native directory: " + child);
                    pendingDirectories.Push(child);
                }
            }
            string[] actualPaths = actualPathList.OrderBy(path => path, StringComparer.Ordinal).ToArray();
            Require(actualPaths.SequenceEqual(expected.Keys.OrderBy(path => path, StringComparer.Ordinal), StringComparer.Ordinal),
                "Installed libil2cpp inventory contains missing or unexpected paths.");
            var files = new List<FileEntry>();
            foreach (string path in actualPaths)
            {
                FileEntry entry = expected[path];
                entry.sha256 = ShadowHash.File(Path.Combine(installedRoot, path));
                if (path != "assembly-shadow-install.json" && !path.StartsWith("hybridclr/generated/", StringComparison.Ordinal))
                {
                    SourceFileHash claimed = receipt.sourceFileHashes.Single(item => item.path == path);
                    Require(entry.sha256 == claimed.sha256, "Installed native source hash differs from its installation receipt: " + path);
                }
                files.Add(entry);
            }
            foreach (string generated in GeneratedFiles)
                Require(files.Any(item => item.path == generated && item.sha256.Length != 0), "Generated native file is missing: " + generated);
            return new Inventory { files = files.ToArray(), hash = InventoryHash(files) };
        }

        private static Inventory CaptureExternalInventory(string externalRoot)
        {
            Require(Directory.Exists(externalRoot) && !IsSymlink(externalRoot), "Installed external native root is missing or symlinked: " + externalRoot);
            for (DirectoryInfo parent = new DirectoryInfo(externalRoot); parent != null; parent = parent.Parent)
                Require(!IsSymlink(parent.FullName), "Symlinked external native path component: " + parent.FullName);
            var files = new List<FileEntry>();
            var pendingDirectories = new Stack<string>();
            pendingDirectories.Push(externalRoot);
            while (pendingDirectories.Count != 0)
            {
                string directory = pendingDirectories.Pop();
                foreach (string file in Directory.GetFiles(directory, "*", SearchOption.TopDirectoryOnly))
                {
                    Require(!IsSymlink(file), "Symlinked external native file: " + file);
                    files.Add(new FileEntry {
                        path = Relative(externalRoot, file), source = "external", sha256 = ShadowHash.File(file),
                    });
                }
                foreach (string child in Directory.GetDirectories(directory, "*", SearchOption.TopDirectoryOnly))
                {
                    Require(!IsSymlink(child), "Symlinked external native directory: " + child);
                    pendingDirectories.Push(child);
                }
            }
            Require(files.Count != 0, "Installed external native inventory is empty: " + externalRoot);
            files = files.OrderBy(item => item.path, StringComparer.Ordinal).ToList();
            return new Inventory { files = files.ToArray(), hash = InventoryHash(files) };
        }

        private static bool SameFiles(FileEntry[] left, FileEntry[] right)
        {
            if (left == null || right == null || left.Length != right.Length) return false;
            return left.OrderBy(item => item.path, StringComparer.Ordinal).Zip(right.OrderBy(item => item.path, StringComparer.Ordinal),
                (a, b) => a.path == b.path && a.source == b.source && a.sha256 == b.sha256).All(value => value);
        }

        private static string InventoryHash(IEnumerable<FileEntry> files)
        {
            return ShadowHash.Text(string.Join("\n", files.OrderBy(item => item.path, StringComparer.Ordinal)
                .Select(item => item.path + "\0" + item.source + "\0" + item.sha256).ToArray()));
        }

        private static ProcessResult Run(string[] argv, string workingDirectory)
        {
            var info = new ProcessStartInfo {
                FileName = argv[0],
                Arguments = string.Join(" ", argv.Skip(1).Select(Quote)),
                WorkingDirectory = workingDirectory,
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true,
            };
            using (var process = new Process { StartInfo = info })
            {
                try { Require(process.Start(), "Could not start native verification tool."); }
                catch (Exception error) { throw new BuildFailedException("Could not start native verification tool: " + error.Message); }
                Task<string> stdoutTask = process.StandardOutput.ReadToEndAsync();
                Task<string> stderrTask = process.StandardError.ReadToEndAsync();
                bool exited = process.WaitForExit(VerificationTimeoutMilliseconds);
                bool timedOut = !exited;
                bool killed = false;
                string killError = "";
                if (!exited)
                {
                    try { process.Kill(); killed = true; }
                    catch (Exception error) { killError = error.Message; }
                    try { exited = process.WaitForExit(5000); }
                    catch (Exception error) { killError = error.Message; }
                }
                bool drained = false;
                try { drained = Task.WaitAll(new Task[] { stdoutTask, stderrTask }, 5000); }
                catch (AggregateException) { }
                string stdout = drained && stdoutTask.Status == TaskStatus.RanToCompletion ? stdoutTask.Result : "<stdout drain timed out>";
                string stderr = drained && stderrTask.Status == TaskStatus.RanToCompletion ? stderrTask.Result : "<stderr drain timed out>";
                int exitCode = exited ? process.ExitCode : -1;
                return new ProcessResult {
                    exitCode = exitCode, stdout = stdout, stderr = stderr,
                    timedOut = timedOut, killAttempted = timedOut || killed, killError = killError,
                };
            }
        }

        private static string FindPython3()
        {
            var candidates = new List<string>();
            string configured = Environment.GetEnvironmentVariable("PYTHON3");
            if (!string.IsNullOrWhiteSpace(configured)) candidates.Add(configured);
            candidates.Add("/usr/bin/python3");
            candidates.Add("/opt/homebrew/bin/python3");
            candidates.Add("/usr/local/bin/python3");
            string path = Environment.GetEnvironmentVariable("PATH") ?? "";
            candidates.AddRange(path.Split(Path.PathSeparator).Where(item => !string.IsNullOrWhiteSpace(item)).Select(item => Path.Combine(item, "python3")));
            string result = candidates.Select(Path.GetFullPath).FirstOrDefault(item => File.Exists(item) && !IsSymlink(item));
            Require(!string.IsNullOrWhiteSpace(result), "A discovered or configured python3 executable is required for native provenance verification.");
            return result;
        }

        private static string MakeProjectPath(string projectRoot, string path)
        { return Path.IsPathRooted(path) ? Path.GetFullPath(path) : Path.GetFullPath(Path.Combine(projectRoot, path)); }

        private static string Relative(string root, string path)
        { return path.Substring(root.TrimEnd(Path.DirectorySeparatorChar) .Length + 1).Replace(Path.DirectorySeparatorChar, '/'); }

        private static bool IsSafeRelative(string path)
        {
            return !string.IsNullOrWhiteSpace(path) && !Path.IsPathRooted(path) && path.IndexOf('\\') < 0 &&
                path.Split('/').All(item => item.Length > 0 && item != "." && item != "..");
        }

        private static bool IsWithinRoot(string root, string path)
        {
            if (string.IsNullOrWhiteSpace(root) || string.IsNullOrWhiteSpace(path)) return false;
            string canonicalRoot = Path.GetFullPath(root).TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
            string canonicalPath = Path.GetFullPath(path);
            return canonicalPath.StartsWith(canonicalRoot + Path.DirectorySeparatorChar, StringComparison.Ordinal);
        }

        private static void RequireRegularFile(string path, string label)
        {
            Require(File.Exists(path) && !IsSymlink(path), label + " is missing or symlinked: " + path);
        }

        private static bool IsSymlink(string path)
        {
            try { return (File.GetAttributes(path) & FileAttributes.ReparsePoint) != 0; }
            catch (FileNotFoundException) { return false; }
        }

        private static string Quote(string value)
        { return "\"" + value.Replace("\\", "\\\\").Replace("\"", "\\\"") + "\""; }

        private static void Require(bool condition, string message)
        { if (!condition) throw new BuildFailedException(message); }

        [Serializable] private sealed class InstallReceipt { public SourceFileHash[] sourceFileHashes; public string[] generatedFileExclusions; }
        [Serializable] private sealed class SourceFileHash { public string path, source, sha256; }
        [Serializable] private sealed class ProcessResult { public int exitCode; public bool timedOut, killAttempted; public string stdout, stderr, killError; }
        private sealed class Inventory { public FileEntry[] files; public string hash; }
        [Serializable] public sealed class FileEntry { public string path, source, sha256; }
        [Serializable] public sealed class Capture
        {
            public int schemaVersion;
            public string projectRoot, snapshotRoot, snapshotInventorySha256;
            public string installedRoot, externalRoot, sourcePinFile, sourcePinSha256, installReceiptPath, installReceiptSha256;
            public string verificationToolPath, verificationToolSha256, verificationSupportToolPath, verificationSupportToolSha256;
            public string pythonExecutable, pythonExecutableSha256;
            public string liveInstalledRoot, liveExternalRoot, liveSourcePinFile, liveSourcePinSha256;
            public string liveInstallReceiptPath, liveInstallReceiptSha256;
            public string liveVerificationToolPath, liveVerificationToolSha256;
            public string liveVerificationSupportToolPath, liveVerificationSupportToolSha256;
            public string[] verificationArgv;
            public int verificationExitCode;
            public string verificationStdout, verificationStderr, installedInventorySha256, externalInventorySha256;
            public string liveInstalledInventorySha256, liveExternalInventorySha256;
            public FileEntry[] snapshotFiles, installedFiles, externalFiles;
        }
    }
}
