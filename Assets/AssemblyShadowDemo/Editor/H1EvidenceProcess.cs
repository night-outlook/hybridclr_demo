using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using UnityEditor.Build;

namespace AssemblyShadowDemo.Editor
{
    /// <summary>Runs only explicit local evidence commands, never a shell.</summary>
    public static class H1EvidenceProcess
    {
        public static string PythonExecutable()
        {
            string[] args = Environment.GetCommandLineArgs();
            string result = null;
            for (int i = 0; i < args.Length; ++i)
            {
                if (args[i] != "-shadowH1Python") continue;
                if (result != null || i + 1 >= args.Length || string.IsNullOrWhiteSpace(args[i + 1]))
                    throw new BuildFailedException("Missing/duplicate -shadowH1Python argument.");
                result = args[++i];
            }
            return result ?? "python3";
        }

        public static string Quote(string argument)
        {
            if (argument == null || argument.IndexOf('\0') >= 0 || argument.IndexOf('\n') >= 0 || argument.IndexOf('\r') >= 0)
                throw new ArgumentException("Invalid process argument.");
            // Mono/.NET ProcessStartInfo argument grammar, not shell escaping.
            return "\"" + argument.Replace("\\", "\\\\").Replace("\"", "\\\"") + "\"";
        }

        public static string RunPython(string projectRoot, string script, params string[] arguments)
        {
            string absoluteScript = Path.GetFullPath(Path.Combine(projectRoot, script));
            if (!File.Exists(absoluteScript)) throw new BuildFailedException("Missing evidence tool: " + absoluteScript);
            var info = new ProcessStartInfo
            {
                FileName = PythonExecutable(),
                Arguments = string.Join(" ", new[] { absoluteScript }.Concat(arguments).Select(Quote)),
                WorkingDirectory = projectRoot, UseShellExecute = false,
                RedirectStandardOutput = true, RedirectStandardError = true, CreateNoWindow = true,
            };
            using (var process = Process.Start(info))
            {
                if (process == null) throw new BuildFailedException("Evidence tool did not start.");
                Task<string> stdout = process.StandardOutput.ReadToEndAsync();
                Task<string> stderr = process.StandardError.ReadToEndAsync();
                if (!process.WaitForExit(300000))
                {
                    try { process.Kill(); } catch (InvalidOperationException) { }
                    throw new BuildFailedException("Evidence tool timed out; preserve this build attempt.");
                }
                if (!Task.WaitAll(new Task[] { stdout, stderr }, 10000))
                    throw new BuildFailedException("Evidence command streams did not complete.");
                if (process.ExitCode != 0)
                    throw new BuildFailedException("Evidence tool failed: " + absoluteScript + "\n" + stdout.Result + "\n" + stderr.Result);
                return stdout.Result;
            }
        }
    }
}
