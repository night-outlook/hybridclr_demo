
using System;
using System.IO;
public static class R03CompilerProbe {
 public static void Run() {
  var args = Environment.GetCommandLineArgs();
  int i = Array.IndexOf(args, "-r03CompilerMarker");
  if (i < 0 || i + 1 >= args.Length) throw new InvalidOperationException("Marker required");
  using (var stream = new FileStream(args[i + 1], FileMode.CreateNew)) {
   var bytes = System.Text.Encoding.UTF8.GetBytes("R03CompilerProbe-v1");
   stream.Write(bytes, 0, bytes.Length);
  }
 }
}
