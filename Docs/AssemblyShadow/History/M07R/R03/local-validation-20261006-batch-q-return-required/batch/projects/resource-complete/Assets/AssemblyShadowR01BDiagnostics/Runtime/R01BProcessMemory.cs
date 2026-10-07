using System;
using System.Runtime.InteropServices;

namespace AssemblyShadowDemo
{
internal static class R01BProcessMemory
{
    public const string Measurement = "DarwinMachTaskBasicInfoResidentAndLifetimePeakBytes";

    private const string LibSystem = "/usr/lib/libSystem.B.dylib";
    private const int MachTaskBasicInfoFlavor = 20;
    private const uint MachTaskBasicInfoCount = 12;

    [StructLayout(LayoutKind.Sequential, Pack = 4)]
    internal struct MachTaskBasicInfo
    {
        public ulong VirtualSize, ResidentSize, ResidentSizeMax;
        public int UserSeconds, UserMicroseconds, SystemSeconds, SystemMicroseconds;
        public int Policy, SuspendCount;
    }

    [DllImport(LibSystem, EntryPoint = "mach_task_self", ExactSpelling = true, CallingConvention = CallingConvention.Cdecl)]
    internal static extern uint MachTaskSelf();

    [DllImport(LibSystem, EntryPoint = "task_info", ExactSpelling = true, CallingConvention = CallingConvention.Cdecl)]
    internal static extern int TaskInfo(uint task, int flavor, out MachTaskBasicInfo info, ref uint count);

    // mach_task_self() acquires a send-right reference; retain one for this process.
    private static readonly uint TaskPort = MachTaskSelf();

    public struct Sample
    {
        public long ResidentBytes;
        public long PeakResidentBytes;
    }

    public static Sample Capture()
    {
        if (IntPtr.Size != 8 || Marshal.SizeOf(typeof(MachTaskBasicInfo)) != 48)
            throw new PlatformNotSupportedException("Expected the 64-bit macOS MACH_TASK_BASIC_INFO ABI.");
        uint task = TaskPort;
        if (task == 0)
            throw new InvalidOperationException("mach_task_self returned MACH_PORT_NULL.");
        uint count = MachTaskBasicInfoCount;
        MachTaskBasicInfo info;
        int result = TaskInfo(task, MachTaskBasicInfoFlavor, out info, ref count);
        if (result != 0 || count != MachTaskBasicInfoCount)
            throw new InvalidOperationException("task_info(MACH_TASK_BASIC_INFO) failed: kern_return_t=" + result + ", count=" + count + ".");
        if (info.ResidentSize == 0 || info.ResidentSizeMax < info.ResidentSize ||
            info.ResidentSize > long.MaxValue || info.ResidentSizeMax > long.MaxValue)
            throw new InvalidOperationException("task_info returned invalid resident-memory counters.");
        return new Sample { ResidentBytes = (long)info.ResidentSize, PeakResidentBytes = (long)info.ResidentSizeMax };
    }
}
}
