AssemblyShadowError AssemblyShadow::GetExecutionDiagnosticsJson(std::string& json)
{
    json.clear();
    std::array<Il2CppClass*, kMaximumExecutionClasses> classes{};
    size_t count = 0;
    if (assembly_shadow_r02::ObservationCounters::Level >= 2)
    {
        ExecutionObservationLock lock;
        for (Il2CppClass* klass : s_executionClasses)
            if (klass) classes[count++] = klass;
    }
    // No observation lock remains held while reading physical metadata. The
    // inventory creates neither classes nor generic instances, including AOT.
    AssemblyVector assemblies;
    if (count) Assembly::CaptureShadowEnumeration(assemblies);
    AssemblyShadowTypeKey::MetadataTypeImages images;
    for (const Il2CppAssembly* assembly : assemblies)
        for (uint32_t index = 0; index < assembly->image->typeCount; ++index)
            images.emplace(MetadataCache::GetAssemblyTypeHandle(assembly->image, index), assembly->image);

    const ActiveSnapshot* active = s_active.load(std::memory_order_acquire);
    const AssemblyShadowState state = s_state.load(std::memory_order_acquire);
    // Subset increments release-publish their preceding total increments. Read
    // them with acquire before totals: no impossible subset > total snapshot.
    const uint64_t shadowChecks = s_shadowMethodChecks.load(std::memory_order_acquire);
    const uint64_t rejectedChecks = s_rejectedBaselineMethods.load(std::memory_order_acquire);
    const uint64_t methodChecks = s_methodChecks.load(std::memory_order_relaxed);
    const uint64_t shadowTransforms = s_shadowInterpreterTransformations.load(std::memory_order_acquire);
    const uint64_t transforms = s_interpreterTransformations.load(std::memory_order_relaxed);
    std::ostringstream output;
    output << std::boolalpha << "{\"schemaVersion\":1,\"enabled\":true,\"stateCode\":" << static_cast<int>(state)
        << ",\"state\":" << AssemblyShadowDiagnostics::Quote(AssemblyShadowDiagnostics::StateName(state))
        << ",\"generation\":" << (active ? active->generation : 0)
        << ",\"methodChecks\":" << methodChecks << ",\"shadowMethodChecks\":" << shadowChecks
        << ",\"rejectedBaselineMethods\":" << rejectedChecks
        << ",\"baselineClassCctorStarted\":" << s_baselineClassCctorStarted.load(std::memory_order_relaxed)
        << ",\"shadowClassCctorStarted\":" << s_shadowClassCctorStarted.load(std::memory_order_relaxed)
        << ",\"interpreterTransformations\":" << transforms
        << ",\"shadowInterpreterTransformations\":" << shadowTransforms
        << ",\"droppedClassObservations\":" << s_droppedClassObservations.load(std::memory_order_relaxed)
        << ",\"classes\":[";
    for (size_t index = 0; index < count; ++index)
    {
        Il2CppClass* klass = classes[index];
        const Il2CppAssembly* owner = klass->image->assembly;
        const bool baseline = active && active->byAssembly.count(owner);
        const bool shadow = active && active->shadowToBaseline.count(owner);
        std::string typeKey;
        try { typeKey = AssemblyShadowTypeKey::FormatMetadataOnly(&klass->byval_arg, images); }
        catch (const ShadowTypeResolutionFailure& failure) { return failure.error; }
        void* storage;
        {
            il2cpp::os::FastAutoLock metadataLock(&g_MetadataLock);
            storage = klass->static_fields; // Only already-existing storage.
        }
        const bool started = os::Atomic::LoadRelaxed(reinterpret_cast<const int32_t*>(&klass->cctor_started)) != 0;
        const bool finished = os::Atomic::LoadRelaxed(reinterpret_cast<const int32_t*>(&klass->cctor_finished_or_no_cctor)) != 0;
        const bool exception = os::Atomic::LoadRelaxed(reinterpret_cast<const int32_t*>(&klass->initializationExceptionGCHandle)) != 0;
        std::string pointer;
#if IL2CPP_DEBUG
        const bool details = true;
        if (storage)
        {
            std::ostringstream address;
            address << "0x" << std::hex << reinterpret_cast<uintptr_t>(storage);
            pointer = address.str();
        }
#else
        const bool details = false;
#endif
        if (index) output << ',';
        output << "{\"logicalAssembly\":" << AssemblyShadowDiagnostics::Quote(owner->aname.name)
            << ",\"typeKey\":" << AssemblyShadowDiagnostics::Quote(typeKey)
            << ",\"executionModeCode\":" << (baseline || shadow ? 1 : 0)
            << ",\"executionMode\":" << AssemblyShadowDiagnostics::Quote(baseline || shadow ? "InterpreterShadow" : "AotBaseline")
            << ",\"physicalImageKind\":" << AssemblyShadowDiagnostics::Quote(Interpreter(owner) ? "Interpreter" : "Aot")
            << ",\"isActive\":" << !baseline
            << ",\"cctorStarted\":" << started << ",\"cctorFinished\":" << finished
            << ",\"hasInitializationException\":" << exception
            << ",\"staticStoragePointer\":" << AssemblyShadowDiagnostics::Quote(pointer)
            << ",\"pointerDetailsAvailable\":" << details << ",\"staticStorageAvailable\":" << (storage != nullptr) << '}';
    }
    output << "]";
    assembly_shadow_r02::AppendDiagnostics(output);
    output << "}";
    json = output.str();
    return AssemblyShadowError::Success;
}