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
    /// <summary>Captures the exact pinned native installation used by an H1 diagnostic build.</summary>
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
            projectRoot = Path.GetFullPath(projectRoot);
            string installedRoot = Path.GetFullPath(Path.Combine(SettingsUtil.LocalIl2CppDir, "libil2cpp"));
            string externalRoot = Path.GetFullPath(Path.Combine(SettingsUtil.LocalIl2CppDir, "external"));
            string pinsPath = MakeProjectPath(projectRoot, sourcePinFile);
            string verifier = Path.Combine(projectRoot, "Tools/AssemblyShadow/verify-installed-runtime.py");
            string supportVerifier = Path.Combine(Path.GetDirectoryName(verifier), "shadow_tools.py");
            Require(File.Exists(verifier) && !IsSymlink(verifier), "Native verification tool is missing or symlinked: " + verifier);
            Require(File.Exists(supportVerifier) && !IsSymlink(supportVerifier), "Native verification support tool is missing or symlinked: " + supportVerifier);
            string python = FindPython3();
            string expectedShadow = featureEnabled ? "on" : "off";
            string[] argv = { python, verifier, "--project", projectRoot, "--skip-demo-source", "--expect-shadow", expectedShadow, "--json" };
            ProcessResult result = Run(argv, projectRoot);
            Require(result.exitCode == 0 && !result.timedOut,
                "Pinned native installation verification failed with exit code " + result.exitCode +
                "; timedOut=" + result.timedOut + "; killAttempted=" + result.killAttempted +
                "; killError=" + result.killError + "; stdout=" + result.stdout + "; stderr=" + result.stderr);
            Inventory inventory = CaptureInventory(installedRoot);
            Inventory externalInventory = CaptureExternalInventory(externalRoot);
            return new Capture {
                projectRoot = projectRoot,
                installedRoot = installedRoot,
                sourcePinFile = pinsPath,
                sourcePinSha256 = ShadowHash.File(pinsPath),
                installReceiptPath = Path.Combine(installedRoot, "assembly-shadow-install.json"),
                installReceiptSha256 = ShadowHash.File(Path.Combine(installedRoot, "assembly-shadow-install.json")),
                verificationToolPath = verifier,
                verificationToolSha256 = ShadowHash.File(verifier),
                verificationSupportToolPath = supportVerifier,
                verificationSupportToolSha256 = ShadowHash.File(supportVerifier),
                pythonExecutable = python,
                verificationArgv = argv,
                verificationExitCode = result.exitCode,
                verificationStdout = result.stdout,
                verificationStderr = result.stderr,
                installedFiles = inventory.files,
                installedInventorySha256 = inventory.hash,
                externalRoot = externalRoot,
                externalFiles = externalInventory.files,
                externalInventorySha256 = externalInventory.hash,
            };
        }

        public static void RequireUnchanged(Capture expected)
        {
            Require(expected != null, "Native provenance capture is missing.");
            Require(ShadowHash.File(expected.sourcePinFile) == expected.sourcePinSha256, "Pinned source file changed during H1 Player build.");
            Require(ShadowHash.File(expected.verificationToolPath) == expected.verificationToolSha256, "Native verification tool changed during H1 Player build.");
            Require(ShadowHash.File(expected.verificationSupportToolPath) == expected.verificationSupportToolSha256, "Native verification support tool changed during H1 Player build.");
            Require(ShadowHash.File(expected.installReceiptPath) == expected.installReceiptSha256, "Installed native receipt changed during H1 Player build.");
            Inventory actual = CaptureInventory(expected.installedRoot);
            Require(actual.hash == expected.installedInventorySha256 && SameFiles(actual.files, expected.installedFiles),
                "Installed libil2cpp files or hashes changed during H1 Player build.");
            Inventory external = CaptureExternalInventory(expected.externalRoot);
            Require(external.hash == expected.externalInventorySha256 && SameFiles(external.files, expected.externalFiles),
                "Installed external native files or hashes changed during H1 Player build.");
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
            foreach (string generated in GeneratedFiles)
            {
                Require(!expected.ContainsKey(generated), "Generated native path overlaps the pinned source inventory: " + generated);
                expected.Add(generated, new FileEntry { path = generated, source = "generated", sha256 = "" });
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

        private static bool IsSymlink(string path)
        {
            try { return (File.GetAttributes(path) & FileAttributes.ReparsePoint) != 0; }
            catch (FileNotFoundException) { return false; }
        }

        private static string Quote(string value)
        { return "\"" + value.Replace("\\", "\\\\").Replace("\"", "\\\"") + "\""; }

        private static void Require(bool condition, string message)
        { if (!condition) throw new BuildFailedException(message); }

        [Serializable] private sealed class InstallReceipt { public SourceFileHash[] sourceFileHashes; }
        [Serializable] private sealed class SourceFileHash { public string path, source, sha256; }
        [Serializable] private sealed class ProcessResult { public int exitCode; public bool timedOut, killAttempted; public string stdout, stderr, killError; }
        private sealed class Inventory { public FileEntry[] files; public string hash; }
        [Serializable] public sealed class FileEntry { public string path, source, sha256; }
        [Serializable] public sealed class Capture
        {
            public string projectRoot, installedRoot, externalRoot, sourcePinFile, sourcePinSha256, installReceiptPath, installReceiptSha256;
            public string verificationToolPath, verificationToolSha256, verificationSupportToolPath, verificationSupportToolSha256, pythonExecutable;
            public string[] verificationArgv;
            public int verificationExitCode;
            public string verificationStdout, verificationStderr, installedInventorySha256, externalInventorySha256;
            public FileEntry[] installedFiles, externalFiles;
        }
    }
}
