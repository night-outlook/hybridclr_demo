// AOT source compile-and-reflection check only. No Player or native PInvoke.
using System;
using System.Linq;
using System.Reflection;
using AssemblyShadow.R03.IR;
using UnityEngine;

internal static class Program
{
    private static int Main()
    {
        var owner = typeof(R03CapturedGenericAotOwner);
        var player = typeof(R03CapturedGenericPlayer);
        if (owner.Assembly != player.Assembly ||
            owner.Assembly.GetReferencedAssemblies().Any(x => x.Name == "Methods"))
            return 2;
        var method = owner.GetMethod("Touch", BindingFlags.Static | BindingFlags.Public);
        if (method == null || !method.IsGenericMethodDefinition ||
            method.GetGenericArguments().Length != 1 ||
            owner.GetProperty("Calls").GetValue(null) is not int)
            return 3;
        var runtimeInit = player.GetMethod("Run", BindingFlags.NonPublic | BindingFlags.Static);
        if (runtimeInit == null || runtimeInit.GetCustomAttributes(
            typeof(RuntimeInitializeOnLoadMethodAttribute), false).Length != 1)
            return 4;
        if (R03CapturedGenericAotOwner.Calls != 0 ||
            R03CapturedGenericAotOwner.WarmShared() != 42 ||
            R03CapturedGenericAotOwner.Calls != 1)
            return 5;
        Console.WriteLine("HOST ONLY: actual captured AOT Player source compiled; no native/Unity execution.");
        return 0;
    }
}
