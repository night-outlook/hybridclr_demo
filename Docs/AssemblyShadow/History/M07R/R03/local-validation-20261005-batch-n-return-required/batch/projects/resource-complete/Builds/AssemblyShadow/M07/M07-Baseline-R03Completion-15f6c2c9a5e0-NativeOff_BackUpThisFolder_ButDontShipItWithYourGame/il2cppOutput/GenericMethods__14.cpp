#include "pch-cpp.hpp"

#ifndef _MSC_VER
# include <alloca.h>
#else
# include <malloc.h>
#endif




template <typename T1>
struct VirtualActionInvoker1
{
	typedef void (*Action)(void*, T1, const RuntimeMethod*);

	static inline void Invoke (Il2CppMethodSlot slot, RuntimeObject* obj, T1 p1)
	{
		const VirtualInvokeData& invokeData = il2cpp_codegen_get_virtual_invoke_data(slot, obj);
		((Action)invokeData.methodPtr)(obj, p1, invokeData.method);
	}
};
template <typename R>
struct VirtualFuncInvoker0
{
	typedef R (*Func)(void*, const RuntimeMethod*);

	static inline R Invoke (Il2CppMethodSlot slot, RuntimeObject* obj)
	{
		const VirtualInvokeData& invokeData = il2cpp_codegen_get_virtual_invoke_data(slot, obj);
		return ((Func)invokeData.methodPtr)(obj, invokeData.method);
	}
};
template <typename T1, typename T2>
struct InterfaceActionInvoker2Invoker;
template <typename T1, typename T2>
struct InterfaceActionInvoker2Invoker<T1, T2*>
{
	static inline void Invoke (Il2CppMethodSlot slot, RuntimeClass* declaringInterface, RuntimeObject* obj, T1 p1, T2* p2)
	{
		const VirtualInvokeData& invokeData = il2cpp_codegen_get_interface_invoke_data(slot, obj, declaringInterface);
		void* params[2] = { &p1, p2 };
		invokeData.method->invoker_method(il2cpp_codegen_get_method_pointer(invokeData.method), invokeData.method, obj, params, params[1]);
	}
};
template <typename R>
struct InterfaceFuncInvoker0
{
	typedef R (*Func)(void*, const RuntimeMethod*);

	static inline R Invoke (Il2CppMethodSlot slot, RuntimeClass* declaringInterface, RuntimeObject* obj)
	{
		const VirtualInvokeData& invokeData = il2cpp_codegen_get_interface_invoke_data(slot, obj, declaringInterface);
		return ((Func)invokeData.methodPtr)(obj, invokeData.method);
	}
};
template <typename R, typename T1>
struct InterfaceFuncInvoker1
{
	typedef R (*Func)(void*, T1, const RuntimeMethod*);

	static inline R Invoke (Il2CppMethodSlot slot, RuntimeClass* declaringInterface, RuntimeObject* obj, T1 p1)
	{
		const VirtualInvokeData& invokeData = il2cpp_codegen_get_interface_invoke_data(slot, obj, declaringInterface);
		return ((Func)invokeData.methodPtr)(obj, p1, invokeData.method);
	}
};
template <typename T1, typename T2>
struct InvokerActionInvoker2;
template <typename T1, typename T2>
struct InvokerActionInvoker2<T1*, T2*>
{
	static inline void Invoke (Il2CppMethodPointer methodPtr, const RuntimeMethod* method, void* obj, T1* p1, T2* p2)
	{
		void* params[2] = { p1, p2 };
		method->invoker_method(methodPtr, method, obj, params, params[1]);
	}
};
template <typename T1, typename T2, typename T3, typename T4, typename T5, typename T6>
struct InvokerActionInvoker6;
template <typename T1, typename T2, typename T3, typename T4, typename T5, typename T6>
struct InvokerActionInvoker6<T1*, T2, T3, T4, T5*, T6*>
{
	static inline void Invoke (Il2CppMethodPointer methodPtr, const RuntimeMethod* method, void* obj, T1* p1, T2 p2, T3 p3, T4 p4, T5* p5, T6* p6)
	{
		void* params[6] = { p1, &p2, &p3, &p4, p5, p6 };
		method->invoker_method(methodPtr, method, obj, params, params[5]);
	}
};
template <typename R, typename T1, typename T2>
struct InvokerFuncInvoker2;
template <typename R, typename T1, typename T2>
struct InvokerFuncInvoker2<R, T1*, T2*>
{
	static inline R Invoke (Il2CppMethodPointer methodPtr, const RuntimeMethod* method, void* obj, T1* p1, T2* p2)
	{
		R ret;
		void* params[2] = { p1, p2 };
		method->invoker_method(methodPtr, method, obj, params, &ret);
		return ret;
	}
};

struct Action_1_t10DCB0C07D0D3C565CEACADC80D1152B35A45F6C;
struct Action_1_tD69A6DC9FBE94131E52F5A73B2A9D4AB51EEC404;
struct Action_1_t923A20D1D4F6B55B2ED5AE21B90F1A0CE0450D99;
struct Action_1_t00621160046FE06A171CE95A003D9AE71EBB2B1D;
struct Action_2_tB3E4CF19F3493DE4FE84AFFB77005AE79F9A3758;
struct Action_2_t94C644233E37D574986F0297182FA2BD8972B44A;
struct Action_2_tD2AB9B0AB95F0653AC53DC5114E5EC2958A3E36A;
struct Action_2_t156C43F079E7E68155FCDCD12DC77DD11AEF7E3C;
struct Action_2_t528DD1A0598C8661FA22AB60F7CEFBF784D3DA6B;
struct Action_2_t6F9B4FA82143ACF378558F06FC77D9CE0D68087D;
struct Dictionary_2_tE738E3156DB830A7FCEA2AE6066FC5BEA6715F0D;
struct Dictionary_2_tE62F67DD5E0705D89AA8A2987FB3C4C21A3C9AAF;
struct Dictionary_2_t18C83CD24384334A550468AC80B4F64B179517FB;
struct DynamicArray_1_t401F46C0081DE185BCAB1D30DE8D6B6DC9AA6AFB;
struct DynamicArray_1_t7C64F5A74B7BA6F6B3589A766CADE3F59C6C7BCA;
struct DynamicArray_1_tD456FAFFECC4879D97EE0F550727BF9C6B0B3FE6;
struct DynamicArray_1_t85D77BAA52B2801695EAE751BA0F9DD3C26AA604;
struct Field_1_t32151A22D4B1B5C1DFFDDACD9F3C78D19596507A;
struct Field_1_t7F813BE8CAF3F3F635B34474DDD7B797C5B6CD2A;
struct Field_1_tEE1A923EA8160028BC34CE74DF77A8FB37FCA5D3;
struct Func_1_t2BE7F58348C9CC544A8973B3A9E55541DE43C457;
struct Func_1_tC288CCB64EFD1F5FD49C3F8DE91FE62905E44BCD;
struct Func_1_tBB8824FA8746333BFFF3AB3CE4A41B58450AF431;
struct Func_3_tD46831209E6E19204CD8F9EAFC74DBFCA3C36C5F;
struct Func_3_tECED1961B53AB164A131061296ABA1276B4FBBB9;
struct Func_3_t3E644C82345CE04737DA5CDE018481FE0A88F821;
struct IList_1_t6EE90D273EFCF5E7E4C37FAB712E70BB6F1B4BFF;
struct IList_1_t8AC59FFD0F90EC2DAD4C3FA39B2A5851F9D2987A;
struct ITypeConstructor_1_t81670FEA206550EF92A986F4A63FC5302AB1D638;
struct ITypeConstructor_1_t3B0FE01881012CC548F6EE132D9D04AA93EDE092;
struct ITypeConstructor_1_t2957C3F3F922000D05C6AE59163AF0088BB8D2E4;
struct ITypeConstructor_1_t73C3366FF37ECFD1CC6142A80D1A0E31E89DDB04;
struct ITypeConstructor_1_t0FE2B73907C0A0AEB0E84716E021DD7420B23A2B;
struct ITypeConstructor_1_t5E4FD8D127EC0F24B375DF611109A9783C9949D0;
struct ITypeConstructor_1_tCC196E183FB5A7CF798C682F9C3B70CDDA50CFFF;
struct ITypeConstructor_1_tADCE5163310B602EB1878CA0050295BFB0F6B542;
struct ITypeConstructor_1_t61D5D3D9EDD28391B0FE316A5641A34D7FF16FD0;
struct ITypeConstructor_1_t5B814DBA70C191660AF27E38032998417073D7A2;
struct ITypeConstructor_1_t63AA3F84ED218C4C0589371B74758F62E3EFCF85;
struct List_1_tCD7772AB40D4E7A61CCAFDDF9E33C190D4F9E6D4;
struct List_1_t179992B095C528117EEF4782A1F45568BD2D51EA;
struct ObjectPool_1_t7FA933D4164A730DB5D7E5E1D315B49D70184F03;
struct ObjectPool_1_t26A8D6F0AC3E7D5C10AB98A9AF68B2EBC2ABE7EF;
struct AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001;
struct BooleanU5BU5D_tD317D27C31DB892BE79FAE3AEBC0B3FFB73DE9B4;
struct ByteU5BU5D_tA6237BF417AE52AD70CFB4EF24A7A82613DF9031;
struct CharU5BU5D_t799905CF001DD5F13F7DBB310181FC4D8B7D0AAB;
struct ColorU5BU5D_t612261CF293F6FFC3D80AB52259FF0DC2B2CC389;
struct DelegateU5BU5D_tC5AB7E8F745616680F337909D3A8E6C722CDF771;
struct DoubleU5BU5D_tCC308475BD3B8229DB2582938669EF2F9ECC1FEE;
struct GUIContentU5BU5D_t98DA1EEA8D0A2C4AE42CE11C4840B627CADFC503;
struct IRenderGraphResourceU5BU5D_tC72A5980774D8ACE9E681BE8A3FAB493A70BC2F3;
struct Int16U5BU5D_t8175CE8DD9C9F9FB0CF4F58E45BC570575B43CFB;
struct Int32U5BU5D_t19C97395396A72ECAF310612F0760F165060314C;
struct Int64U5BU5D_tAEDFCBDB5414E2A140A6F34C0538BF97FCF67A1D;
struct IntPtrU5BU5D_tFD177F8C806A6921AD7150264CCC62FA00CAD832;
struct ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918;
struct PlaneU5BU5D_t4EEF66BAA8B0140EFFF34F6183CE7F80546592BE;
struct SByteU5BU5D_t88116DA68378C3333DB73E7D36C1A06AFAA91913;
struct SingleU5BU5D_t89DEFE97BCEDB5857010E79ECE0F52CF6E93B87C;
struct StackTraceU5BU5D_t32FBCB20930EAF5BAE3F450FF75228E5450DA0DF;
struct StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248;
struct TypeU5BU5D_t97234E1129B564EB38B8D85CAC2AD8B5B9522FFB;
struct Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD;
struct __Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC;
struct WidgetU5BU5D_t39DEA55B87EF43C59C5699E0340B34185BA1E4A2;
struct LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263;
struct Action_tD00B0A84D7945E50C2DFFC28EFEE6ED44ED2AD07;
struct AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0;
struct Binder_t91BFCE95A7057FADF4D8A1A342AFE52872246235;
struct ComputeShader_tA7BDD0F6EE879D149480F5890BA2E665C50CFBF8;
struct DelegateData_t9B286B493293CD2D23A5B2B5EF0E5B1324C2B77E;
struct Exception_t;
struct GlobalJavaObjectRef_t20D8E5AAFC2EB2518FCABBF40465855E797FF0D8;
struct IDictionary_t6D03155AF1FA9083817AA5B6AD7DEEACC26AB220;
struct IRenderGraphResource_tF24653A388C17849844C128C19C7A6599C7ADB7D;
struct IRenderGraphResourcePool_t8BF833F3C5D0BD8E45632CF923363EC782F4DDA8;
struct Light_t1E68479B7782AF2050FAA02A5DC612FD034F18F3;
struct Material_t18053F08F347D0DCA5E1140EC7EC4533DD8A14E3;
struct MemberFilter_tF644F1AE82F611B677CE1964D5A3277DDA21D553;
struct Mesh_t6D9C539763A09BC2B12AEAEF36F6DFFC98AE63D4;
struct MethodInfo_t;
struct ProbeBrickBlendingPool_tD0DBB9B875C8C88A6410A239987DA3F9F4BE18F8;
struct ProbeBrickIndex_tF1B02DB88E5F4CF79533962B018B5724D74E32D2;
struct ProbeBrickPool_tC43640788A2B356F3F99A068D2CED6702E721693;
struct ProbeCellIndices_t0A30314A2B1D5F97E16BD321C179801D1B42C6AF;
struct ProbeReferenceVolume_t05ED7EF2BB9B58F26CE1629F0AA773D14100695F;
struct ProbeVolumeDebug_t295620780739F33AEAD1D1BB44C5252CE70D3DD8;
struct ProbeVolumeSceneData_t29FD126D36ED1E093C2EBBFB3F248DD5E2A86D90;
struct SafeSerializationManager_tCBB85B95DFD1634237140CD892E82D06ECB3F5E6;
struct Shader_tADC867D36B7876EE22427FAA2CE485105F4EE692;
struct String_t;
struct StringBuilder_t;
struct Texture_t791CBB51219779964E0E8A2ED7C1AA5F92A4A700;
struct Texture3D_tDC30A0F19B6055086859D1ABC098D6E6762000E1;
struct Type_t;
struct Void_t4861ACF8F4594C3437BB48B6E56783494B843915;
struct EnumField_t15C8FC0EB96499DFDCEC2B9DBB27B2BBCD5E262C;
struct IContainer_tBD9F21C42D4253E306C4EF7CFC72480E0C7C89B5;
struct Panel_t3A0D2006E8AEA607A6DF5188138E463A26085295;
struct Expression_t24E9476A15D0D7F6495CF8292DA48C63C871E4B7;
struct U3CU3Ec__DisplayClass171_0_t70061616D0F785A73C9408015CCBEBC3C2B43646;
struct RenderGraphResourcesData_tB2FF97B16A3E1DE700283778679C5CC0C39F4CFE;
struct ResourceCallback_t45358BA8AC82EF742271B868C50331854DD58EEC;
struct ResourceCreateCallback_t77EA2BCF3A19444CA1CA3861A67861084B462B82;
struct ITypeConstructor_tAEA6BC4B87F0F3739E4457F21908EF55F666EB08;
struct TypeConstructorVisitor_tFC61250F68BF43FE889F5B1002CBFF90648E9C7F;

IL2CPP_EXTERN_C RuntimeClass* AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001_il2cpp_TypeInfo_var;
IL2CPP_EXTERN_C RuntimeClass* AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0_il2cpp_TypeInfo_var;
IL2CPP_EXTERN_C RuntimeClass* AndroidReflection_tD59014B286F902906DBB75DA3473897D35684908_il2cpp_TypeInfo_var;
IL2CPP_EXTERN_C RuntimeClass* Assert_tDC16963451AC4364803739B73A4477ADCB365863_il2cpp_TypeInfo_var;
IL2CPP_EXTERN_C RuntimeClass* Debug_t8394C7EEAECA3689C2C9B9DE9C7166D73596276F_il2cpp_TypeInfo_var;
IL2CPP_EXTERN_C RuntimeClass* Exception_t_il2cpp_TypeInfo_var;
IL2CPP_EXTERN_C RuntimeClass* ExpressionEvaluator_tF912A1FA6CB7EA697DFA7926E78D808A446B48F0_il2cpp_TypeInfo_var;
IL2CPP_EXTERN_C RuntimeClass* StringBuilder_t_il2cpp_TypeInfo_var;
IL2CPP_EXTERN_C RuntimeClass* StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248_il2cpp_TypeInfo_var;
IL2CPP_EXTERN_C RuntimeClass* TypeUtility_t62F146E51B66BB18FA0E1EFA84A564FF2B8AAD03_il2cpp_TypeInfo_var;
IL2CPP_EXTERN_C RuntimeClass* Type_t_il2cpp_TypeInfo_var;
IL2CPP_EXTERN_C String_t* _stringLiteral24CC8D396132365E532646F936DFC8579E2299B2;
IL2CPP_EXTERN_C String_t* _stringLiteral42646B33B50B6AA15E22733C8900716F0FE19E1D;
IL2CPP_EXTERN_C String_t* _stringLiteral51253131B895C2F8066BCC47E62D44F18F43446C;
IL2CPP_EXTERN_C String_t* _stringLiteral622F5FF68A93093A1D312703FF92713F8BF2C946;
IL2CPP_EXTERN_C const RuntimeMethod* DynamicArray_1_Resize_mEEEB907EAEFD4C22DB449FF052CF6AC967A27AD1_RuntimeMethod_var;
IL2CPP_EXTERN_C const RuntimeMethod* DynamicArray_1_get_Item_m5FC9383C3A815B0DF7AAD4C2A5CDFB1A25586ECE_RuntimeMethod_var;
IL2CPP_EXTERN_C const RuntimeMethod* DynamicArray_1_get_size_m56D2768863B15299FA4F2F14E271686207A8C2E4_RuntimeMethod_var;
IL2CPP_EXTERN_C const RuntimeType* AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0_0_0_0_var;
IL2CPP_EXTERN_C const RuntimeType* Boolean_t09A6377A54BE2F9E6985A8149F19234FD7DDFE22_0_0_0_var;
IL2CPP_EXTERN_C const RuntimeType* Byte_t94D9231AC217BE4D2E004C4CD32DF6D099EA41A3_0_0_0_var;
IL2CPP_EXTERN_C const RuntimeType* Char_t521A6F19B456D956AF452D926C32709DC03D6B17_0_0_0_var;
IL2CPP_EXTERN_C const RuntimeType* Double_tE150EF3D1D43DEE85D533810AB4C742307EEDE5F_0_0_0_var;
IL2CPP_EXTERN_C const RuntimeType* Int16_tB8EF286A9C33492FA6E6D6E67320BE93E794A175_0_0_0_var;
IL2CPP_EXTERN_C const RuntimeType* Int32_t680FF22E76F6EFAD4375103CBBFFA0421349384C_0_0_0_var;
IL2CPP_EXTERN_C const RuntimeType* Int64_t092CFB123BE63C28ACDAF65C68F21A526050DBA3_0_0_0_var;
IL2CPP_EXTERN_C const RuntimeType* SByte_tFEFFEF5D2FEBF5207950AE6FAC150FC53B668DB5_0_0_0_var;
IL2CPP_EXTERN_C const RuntimeType* Single_t4530F2FF86FCB0DC29F35385CA1BD21BE294761C_0_0_0_var;
IL2CPP_EXTERN_C const RuntimeType* String_t_0_0_0_var;
struct Delegate_t_marshaled_com;
struct Delegate_t_marshaled_pinvoke;
struct Exception_t_marshaled_com;
struct Exception_t_marshaled_pinvoke;

struct AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001;
struct BooleanU5BU5D_tD317D27C31DB892BE79FAE3AEBC0B3FFB73DE9B4;
struct ByteU5BU5D_tA6237BF417AE52AD70CFB4EF24A7A82613DF9031;
struct CharU5BU5D_t799905CF001DD5F13F7DBB310181FC4D8B7D0AAB;
struct DoubleU5BU5D_tCC308475BD3B8229DB2582938669EF2F9ECC1FEE;
struct Int16U5BU5D_t8175CE8DD9C9F9FB0CF4F58E45BC570575B43CFB;
struct Int32U5BU5D_t19C97395396A72ECAF310612F0760F165060314C;
struct Int64U5BU5D_tAEDFCBDB5414E2A140A6F34C0538BF97FCF67A1D;
struct ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918;
struct SByteU5BU5D_t88116DA68378C3333DB73E7D36C1A06AFAA91913;
struct SingleU5BU5D_t89DEFE97BCEDB5857010E79ECE0F52CF6E93B87C;
struct StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248;
struct Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD;
struct __Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC;
struct LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263;

IL2CPP_EXTERN_C_BEGIN
IL2CPP_EXTERN_C_END

#ifdef __clang__
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Winvalid-offsetof"
#pragma clang diagnostic ignored "-Wunused-variable"
#endif
struct DynamicArray_1_t401F46C0081DE185BCAB1D30DE8D6B6DC9AA6AFB  : public RuntimeObject
{
	IRenderGraphResourceU5BU5D_tC72A5980774D8ACE9E681BE8A3FAB493A70BC2F3* ___m_Array;
	int32_t ___U3CsizeU3Ek__BackingField;
	int32_t ___U3CversionU3Ek__BackingField;
};
struct DynamicArray_1_t7C64F5A74B7BA6F6B3589A766CADE3F59C6C7BCA  : public RuntimeObject
{
	ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* ___m_Array;
	int32_t ___U3CsizeU3Ek__BackingField;
	int32_t ___U3CversionU3Ek__BackingField;
};
struct AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0  : public RuntimeObject
{
	GlobalJavaObjectRef_t20D8E5AAFC2EB2518FCABBF40465855E797FF0D8* ___m_jobject;
	GlobalJavaObjectRef_t20D8E5AAFC2EB2518FCABBF40465855E797FF0D8* ___m_jclass;
};
struct IRenderGraphResource_tF24653A388C17849844C128C19C7A6599C7ADB7D  : public RuntimeObject
{
	bool ___imported;
	bool ___shared;
	bool ___sharedExplicitRelease;
	bool ___requestFallBack;
	uint32_t ___writeCount;
	int32_t ___cachedHash;
	int32_t ___transientPassIndex;
	int32_t ___sharedResourceLastFrameUsed;
	IRenderGraphResourcePool_t8BF833F3C5D0BD8E45632CF923363EC782F4DDA8* ___m_Pool;
};
struct IRenderGraphResourcePool_t8BF833F3C5D0BD8E45632CF923363EC782F4DDA8  : public RuntimeObject
{
};
struct MemberInfo_t  : public RuntimeObject
{
};
struct String_t  : public RuntimeObject
{
	int32_t ____stringLength;
	Il2CppChar ____firstChar;
};
struct StringBuilder_t  : public RuntimeObject
{
	CharU5BU5D_t799905CF001DD5F13F7DBB310181FC4D8B7D0AAB* ___m_ChunkChars;
	StringBuilder_t* ___m_ChunkPrevious;
	int32_t ___m_ChunkLength;
	int32_t ___m_ChunkOffset;
	int32_t ___m_MaxCapacity;
};
struct ValueType_t6D9B272BD21782F0A9A14F2E41F85A50E97A986F  : public RuntimeObject
{
};
struct ValueType_t6D9B272BD21782F0A9A14F2E41F85A50E97A986F_marshaled_pinvoke
{
};
struct ValueType_t6D9B272BD21782F0A9A14F2E41F85A50E97A986F_marshaled_com
{
};
struct _AndroidJNIHelper_tA796944DDB1B1459DF68C9FFA518F452C81364F3  : public RuntimeObject
{
};
struct Expression_t24E9476A15D0D7F6495CF8292DA48C63C871E4B7  : public RuntimeObject
{
	StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* ___rpnTokens;
	bool ___hasVariables;
};
struct ReceiptCodec_t62789EC80E1A6901E2F97D487C1197F93BBBD358  : public RuntimeObject
{
};
struct RenderGraphResourcesData_tB2FF97B16A3E1DE700283778679C5CC0C39F4CFE  : public RuntimeObject
{
	DynamicArray_1_t401F46C0081DE185BCAB1D30DE8D6B6DC9AA6AFB* ___resourceArray;
	int32_t ___sharedResourcesCount;
	IRenderGraphResourcePool_t8BF833F3C5D0BD8E45632CF923363EC782F4DDA8* ___pool;
	ResourceCreateCallback_t77EA2BCF3A19444CA1CA3861A67861084B462B82* ___createResourceCallback;
	ResourceCallback_t45358BA8AC82EF742271B868C50331854DD58EEC* ___releaseResourceCallback;
};
struct TypeConstructorVisitor_tFC61250F68BF43FE889F5B1002CBFF90648E9C7F  : public RuntimeObject
{
	RuntimeObject* ___TypeConstructor;
};
struct U3CU3Ec__DisplayClass2_0_1_t41073816D00B5468033D7AA727FBFFB73E7C9BA2 
{
	Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* ___data;
};
struct U3CU3Ec__DisplayClass2_0_1_t95D21073081C2AD9435E6E2ED2FD63B720ABF032 
{
	__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC* ___data;
};
struct U3CU3Ec__DisplayClass2_0_1_tC4E3D65CA470C2F2DB85D9B32B717BE3200D4597 
{
	LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* ___data;
};
struct Boolean_t09A6377A54BE2F9E6985A8149F19234FD7DDFE22 
{
	bool ___m_value;
};
struct Byte_t94D9231AC217BE4D2E004C4CD32DF6D099EA41A3 
{
	uint8_t ___m_value;
};
struct Char_t521A6F19B456D956AF452D926C32709DC03D6B17 
{
	Il2CppChar ___m_value;
};
struct Double_tE150EF3D1D43DEE85D533810AB4C742307EEDE5F 
{
	double ___m_value;
};
struct Enum_t2A1A94B24E3B776EEF4E5E485E290BB9D4D072E2  : public ValueType_t6D9B272BD21782F0A9A14F2E41F85A50E97A986F
{
};
struct Enum_t2A1A94B24E3B776EEF4E5E485E290BB9D4D072E2_marshaled_pinvoke
{
};
struct Enum_t2A1A94B24E3B776EEF4E5E485E290BB9D4D072E2_marshaled_com
{
};
struct Int16_tB8EF286A9C33492FA6E6D6E67320BE93E794A175 
{
	int16_t ___m_value;
};
struct Int32_t680FF22E76F6EFAD4375103CBBFFA0421349384C 
{
	int32_t ___m_value;
};
struct Int64_t092CFB123BE63C28ACDAF65C68F21A526050DBA3 
{
	int64_t ___m_value;
};
struct IntPtr_t 
{
	void* ___m_value;
};
struct LayerMask_t97CB6BDADEDC3D6423C7BCFEA7F86DA2EC6241DB 
{
	int32_t ___m_Mask;
};
struct ProbeDilationSettings_t28A862582E313EFC300E6437FDCB9D9DC9A9A167 
{
	bool ___enableDilation;
	float ___dilationDistance;
	float ___dilationValidityThreshold;
	int32_t ___dilationIterations;
	bool ___squaredDistWeighting;
};
struct ProbeDilationSettings_t28A862582E313EFC300E6437FDCB9D9DC9A9A167_marshaled_pinvoke
{
	int32_t ___enableDilation;
	float ___dilationDistance;
	float ___dilationValidityThreshold;
	int32_t ___dilationIterations;
	int32_t ___squaredDistWeighting;
};
struct ProbeDilationSettings_t28A862582E313EFC300E6437FDCB9D9DC9A9A167_marshaled_com
{
	int32_t ___enableDilation;
	float ___dilationDistance;
	float ___dilationValidityThreshold;
	int32_t ___dilationIterations;
	int32_t ___squaredDistWeighting;
};
struct Quaternion_tDA59F214EF07D7700B26E40E562F267AF7306974 
{
	float ___x;
	float ___y;
	float ___z;
	float ___w;
};
struct SByte_tFEFFEF5D2FEBF5207950AE6FAC150FC53B668DB5 
{
	int8_t ___m_value;
};
struct Single_t4530F2FF86FCB0DC29F35385CA1BD21BE294761C 
{
	float ___m_value;
};
struct UInt64_t8F12534CC8FC4B5860F2A2CD1EE79D322E7A41AF 
{
	uint64_t ___m_value;
};
struct Vector3_t24C512C7B96BBABAD472002D0BA2BDA40A5A80B2 
{
	float ___x;
	float ___y;
	float ___z;
};
struct Vector3Int_t65CB06F557251D18A37BD71F3655BA836A357376 
{
	int32_t ___m_X;
	int32_t ___m_Y;
	int32_t ___m_Z;
};
struct Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 
{
	float ___x;
	float ___y;
	float ___z;
	float ___w;
};
struct Void_t4861ACF8F4594C3437BB48B6E56783494B843915 
{
	union
	{
		struct
		{
		};
		uint8_t Void_t4861ACF8F4594C3437BB48B6E56783494B843915__padding[1];
	};
};
struct LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 
{
	uint16_t ___visibleLightIndex;
	uint16_t ___lightBufferIndex;
	Light_t1E68479B7782AF2050FAA02A5DC612FD034F18F3* ___light;
};
struct LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2_marshaled_pinvoke
{
	uint16_t ___visibleLightIndex;
	uint16_t ___lightBufferIndex;
	Light_t1E68479B7782AF2050FAA02A5DC612FD034F18F3* ___light;
};
struct LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2_marshaled_com
{
	uint16_t ___visibleLightIndex;
	uint16_t ___lightBufferIndex;
	Light_t1E68479B7782AF2050FAA02A5DC612FD034F18F3* ___light;
};
struct Sorting_t85E1835DC268F696F8A2F1E889C951F4C48DC994 
{
	union
	{
		struct
		{
		};
		uint8_t Sorting_t85E1835DC268F696F8A2F1E889C951F4C48DC994__padding[1];
	};
};
struct DataLocation_t34FC6B68E8194966FC3C075EF4227E1522CB53BB 
{
	Texture_t791CBB51219779964E0E8A2ED7C1AA5F92A4A700* ___TexL0_L1rx;
	Texture_t791CBB51219779964E0E8A2ED7C1AA5F92A4A700* ___TexL1_G_ry;
	Texture_t791CBB51219779964E0E8A2ED7C1AA5F92A4A700* ___TexL1_B_rz;
	Texture_t791CBB51219779964E0E8A2ED7C1AA5F92A4A700* ___TexL2_0;
	Texture_t791CBB51219779964E0E8A2ED7C1AA5F92A4A700* ___TexL2_1;
	Texture_t791CBB51219779964E0E8A2ED7C1AA5F92A4A700* ___TexL2_2;
	Texture_t791CBB51219779964E0E8A2ED7C1AA5F92A4A700* ___TexL2_3;
	Texture3D_tDC30A0F19B6055086859D1ABC098D6E6762000E1* ___TexValidity;
	int32_t ___width;
	int32_t ___height;
	int32_t ___depth;
};
struct DataLocation_t34FC6B68E8194966FC3C075EF4227E1522CB53BB_marshaled_pinvoke
{
	Texture_t791CBB51219779964E0E8A2ED7C1AA5F92A4A700* ___TexL0_L1rx;
	Texture_t791CBB51219779964E0E8A2ED7C1AA5F92A4A700* ___TexL1_G_ry;
	Texture_t791CBB51219779964E0E8A2ED7C1AA5F92A4A700* ___TexL1_B_rz;
	Texture_t791CBB51219779964E0E8A2ED7C1AA5F92A4A700* ___TexL2_0;
	Texture_t791CBB51219779964E0E8A2ED7C1AA5F92A4A700* ___TexL2_1;
	Texture_t791CBB51219779964E0E8A2ED7C1AA5F92A4A700* ___TexL2_2;
	Texture_t791CBB51219779964E0E8A2ED7C1AA5F92A4A700* ___TexL2_3;
	Texture3D_tDC30A0F19B6055086859D1ABC098D6E6762000E1* ___TexValidity;
	int32_t ___width;
	int32_t ___height;
	int32_t ___depth;
};
struct DataLocation_t34FC6B68E8194966FC3C075EF4227E1522CB53BB_marshaled_com
{
	Texture_t791CBB51219779964E0E8A2ED7C1AA5F92A4A700* ___TexL0_L1rx;
	Texture_t791CBB51219779964E0E8A2ED7C1AA5F92A4A700* ___TexL1_G_ry;
	Texture_t791CBB51219779964E0E8A2ED7C1AA5F92A4A700* ___TexL1_B_rz;
	Texture_t791CBB51219779964E0E8A2ED7C1AA5F92A4A700* ___TexL2_0;
	Texture_t791CBB51219779964E0E8A2ED7C1AA5F92A4A700* ___TexL2_1;
	Texture_t791CBB51219779964E0E8A2ED7C1AA5F92A4A700* ___TexL2_2;
	Texture_t791CBB51219779964E0E8A2ED7C1AA5F92A4A700* ___TexL2_3;
	Texture3D_tDC30A0F19B6055086859D1ABC098D6E6762000E1* ___TexValidity;
	int32_t ___width;
	int32_t ___height;
	int32_t ___depth;
};
struct Bounds_t367E830C64BBF235ED8C3B2F8CF6254FDCAD39C3 
{
	Vector3_t24C512C7B96BBABAD472002D0BA2BDA40A5A80B2 ___m_Center;
	Vector3_t24C512C7B96BBABAD472002D0BA2BDA40A5A80B2 ___m_Extents;
};
struct Delegate_t  : public RuntimeObject
{
	intptr_t ___method_ptr;
	intptr_t ___invoke_impl;
	RuntimeObject* ___m_target;
	intptr_t ___method;
	intptr_t ___delegate_trampoline;
	intptr_t ___extra_arg;
	intptr_t ___method_code;
	intptr_t ___interp_method;
	intptr_t ___interp_invoke_impl;
	MethodInfo_t* ___method_info;
	MethodInfo_t* ___original_method_info;
	DelegateData_t9B286B493293CD2D23A5B2B5EF0E5B1324C2B77E* ___data;
	bool ___method_is_virtual;
};
struct Delegate_t_marshaled_pinvoke
{
	intptr_t ___method_ptr;
	intptr_t ___invoke_impl;
	Il2CppIUnknown* ___m_target;
	intptr_t ___method;
	intptr_t ___delegate_trampoline;
	intptr_t ___extra_arg;
	intptr_t ___method_code;
	intptr_t ___interp_method;
	intptr_t ___interp_invoke_impl;
	MethodInfo_t* ___method_info;
	MethodInfo_t* ___original_method_info;
	DelegateData_t9B286B493293CD2D23A5B2B5EF0E5B1324C2B77E* ___data;
	int32_t ___method_is_virtual;
};
struct Delegate_t_marshaled_com
{
	intptr_t ___method_ptr;
	intptr_t ___invoke_impl;
	Il2CppIUnknown* ___m_target;
	intptr_t ___method;
	intptr_t ___delegate_trampoline;
	intptr_t ___extra_arg;
	intptr_t ___method_code;
	intptr_t ___interp_method;
	intptr_t ___interp_invoke_impl;
	MethodInfo_t* ___method_info;
	MethodInfo_t* ___original_method_info;
	DelegateData_t9B286B493293CD2D23A5B2B5EF0E5B1324C2B77E* ___data;
	int32_t ___method_is_virtual;
};
struct Exception_t  : public RuntimeObject
{
	String_t* ____className;
	String_t* ____message;
	RuntimeObject* ____data;
	Exception_t* ____innerException;
	String_t* ____helpURL;
	RuntimeObject* ____stackTrace;
	String_t* ____stackTraceString;
	String_t* ____remoteStackTraceString;
	int32_t ____remoteStackIndex;
	RuntimeObject* ____dynamicMethods;
	int32_t ____HResult;
	String_t* ____source;
	SafeSerializationManager_tCBB85B95DFD1634237140CD892E82D06ECB3F5E6* ____safeSerializationManager;
	StackTraceU5BU5D_t32FBCB20930EAF5BAE3F450FF75228E5450DA0DF* ___captured_traces;
	IntPtrU5BU5D_tFD177F8C806A6921AD7150264CCC62FA00CAD832* ___native_trace_ips;
	int32_t ___caught_in_unmanaged;
};
struct Exception_t_marshaled_pinvoke
{
	char* ____className;
	char* ____message;
	RuntimeObject* ____data;
	Exception_t_marshaled_pinvoke* ____innerException;
	char* ____helpURL;
	Il2CppIUnknown* ____stackTrace;
	char* ____stackTraceString;
	char* ____remoteStackTraceString;
	int32_t ____remoteStackIndex;
	Il2CppIUnknown* ____dynamicMethods;
	int32_t ____HResult;
	char* ____source;
	SafeSerializationManager_tCBB85B95DFD1634237140CD892E82D06ECB3F5E6* ____safeSerializationManager;
	StackTraceU5BU5D_t32FBCB20930EAF5BAE3F450FF75228E5450DA0DF* ___captured_traces;
	Il2CppSafeArray* ___native_trace_ips;
	int32_t ___caught_in_unmanaged;
};
struct Exception_t_marshaled_com
{
	Il2CppChar* ____className;
	Il2CppChar* ____message;
	RuntimeObject* ____data;
	Exception_t_marshaled_com* ____innerException;
	Il2CppChar* ____helpURL;
	Il2CppIUnknown* ____stackTrace;
	Il2CppChar* ____stackTraceString;
	Il2CppChar* ____remoteStackTraceString;
	int32_t ____remoteStackIndex;
	Il2CppIUnknown* ____dynamicMethods;
	int32_t ____HResult;
	Il2CppChar* ____source;
	SafeSerializationManager_tCBB85B95DFD1634237140CD892E82D06ECB3F5E6* ____safeSerializationManager;
	StackTraceU5BU5D_t32FBCB20930EAF5BAE3F450FF75228E5450DA0DF* ___captured_traces;
	Il2CppSafeArray* ___native_trace_ips;
	int32_t ___caught_in_unmanaged;
};
struct ProbeVolumeBlendingTextureMemoryBudget_t7EE399384930322B57F0CF83315FE1FA651CB002 
{
	int32_t ___value__;
};
struct ProbeVolumeSHBands_t1515D16254FE4344C5FC4C9506F4F9A7ABA4D194 
{
	int32_t ___value__;
};
struct ProbeVolumeTextureMemoryBudget_t9F9B7221A5D6E98DAED0233C050A91A2D745CB66 
{
	int32_t ___value__;
};
struct RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B 
{
	intptr_t ___value;
};
struct VirtualOffsetSettings_tC91F136546790A8318F26B183DCB14460F426A44 
{
	bool ___useVirtualOffset;
	float ___outOfGeoOffset;
	float ___searchMultiplier;
	float ___rayOriginBias;
	int32_t ___maxHitsPerRay;
	LayerMask_t97CB6BDADEDC3D6423C7BCFEA7F86DA2EC6241DB ___collisionMask;
};
struct VirtualOffsetSettings_tC91F136546790A8318F26B183DCB14460F426A44_marshaled_pinvoke
{
	int32_t ___useVirtualOffset;
	float ___outOfGeoOffset;
	float ___searchMultiplier;
	float ___rayOriginBias;
	int32_t ___maxHitsPerRay;
	LayerMask_t97CB6BDADEDC3D6423C7BCFEA7F86DA2EC6241DB ___collisionMask;
};
struct VirtualOffsetSettings_tC91F136546790A8318F26B183DCB14460F426A44_marshaled_com
{
	int32_t ___useVirtualOffset;
	float ___outOfGeoOffset;
	float ___searchMultiplier;
	float ___rayOriginBias;
	int32_t ___maxHitsPerRay;
	LayerMask_t97CB6BDADEDC3D6423C7BCFEA7F86DA2EC6241DB ___collisionMask;
};
struct Flags_tBBD3C554E9057BB9AC0476F92D0328575F2C4193 
{
	int32_t ___value__;
};
struct InitInfo_t704DDF4A7F366AB2C84F08404C424B877802B058 
{
	Vector3Int_t65CB06F557251D18A37BD71F3655BA836A357376 ___pendingMinCellPosition;
	Vector3Int_t65CB06F557251D18A37BD71F3655BA836A357376 ___pendingMaxCellPosition;
};
struct RefVolTransform_t23FA849BA67F6FB0FDC6BA49A08C41D654FC8CE9 
{
	Vector3_t24C512C7B96BBABAD472002D0BA2BDA40A5A80B2 ___posWS;
	Quaternion_tDA59F214EF07D7700B26E40E562F267AF7306974 ___rot;
	float ___scale;
};
struct SettingsVersion_t3663C03E36EF45364E201CE47DCA26BDFCF05A2E 
{
	int32_t ___value__;
};
struct MulticastDelegate_t  : public Delegate_t
{
	DelegateU5BU5D_tC5AB7E8F745616680F337909D3A8E6C722CDF771* ___delegates;
};
struct MulticastDelegate_t_marshaled_pinvoke : public Delegate_t_marshaled_pinvoke
{
	Delegate_t_marshaled_pinvoke** ___delegates;
};
struct MulticastDelegate_t_marshaled_com : public Delegate_t_marshaled_com
{
	Delegate_t_marshaled_com** ___delegates;
};
struct ProbeVolumeBakingProcessSettings_t1A0C71DD07CFB6660AFC0D3EBF81FA5064CFDAD7 
{
	int32_t ___m_Version;
	ProbeDilationSettings_t28A862582E313EFC300E6437FDCB9D9DC9A9A167 ___dilationSettings;
	VirtualOffsetSettings_tC91F136546790A8318F26B183DCB14460F426A44 ___virtualOffsetSettings;
};
struct ProbeVolumeBakingProcessSettings_t1A0C71DD07CFB6660AFC0D3EBF81FA5064CFDAD7_marshaled_pinvoke
{
	int32_t ___m_Version;
	ProbeDilationSettings_t28A862582E313EFC300E6437FDCB9D9DC9A9A167_marshaled_pinvoke ___dilationSettings;
	VirtualOffsetSettings_tC91F136546790A8318F26B183DCB14460F426A44_marshaled_pinvoke ___virtualOffsetSettings;
};
struct ProbeVolumeBakingProcessSettings_t1A0C71DD07CFB6660AFC0D3EBF81FA5064CFDAD7_marshaled_com
{
	int32_t ___m_Version;
	ProbeDilationSettings_t28A862582E313EFC300E6437FDCB9D9DC9A9A167_marshaled_com ___dilationSettings;
	VirtualOffsetSettings_tC91F136546790A8318F26B183DCB14460F426A44_marshaled_com ___virtualOffsetSettings;
};
struct ProbeVolumeSystemParameters_t0654F2626ACA367E00C375BEB6FEA5B86CB0A58B 
{
	int32_t ___memoryBudget;
	int32_t ___blendingMemoryBudget;
	Mesh_t6D9C539763A09BC2B12AEAEF36F6DFFC98AE63D4* ___probeDebugMesh;
	Shader_tADC867D36B7876EE22427FAA2CE485105F4EE692* ___probeDebugShader;
	Mesh_t6D9C539763A09BC2B12AEAEF36F6DFFC98AE63D4* ___offsetDebugMesh;
	Shader_tADC867D36B7876EE22427FAA2CE485105F4EE692* ___offsetDebugShader;
	ComputeShader_tA7BDD0F6EE879D149480F5890BA2E665C50CFBF8* ___scenarioBlendingShader;
	ProbeVolumeSceneData_t29FD126D36ED1E093C2EBBFB3F248DD5E2A86D90* ___sceneData;
	int32_t ___shBands;
	bool ___supportsRuntimeDebug;
	bool ___supportStreaming;
};
struct ProbeVolumeSystemParameters_t0654F2626ACA367E00C375BEB6FEA5B86CB0A58B_marshaled_pinvoke
{
	int32_t ___memoryBudget;
	int32_t ___blendingMemoryBudget;
	Mesh_t6D9C539763A09BC2B12AEAEF36F6DFFC98AE63D4* ___probeDebugMesh;
	Shader_tADC867D36B7876EE22427FAA2CE485105F4EE692* ___probeDebugShader;
	Mesh_t6D9C539763A09BC2B12AEAEF36F6DFFC98AE63D4* ___offsetDebugMesh;
	Shader_tADC867D36B7876EE22427FAA2CE485105F4EE692* ___offsetDebugShader;
	ComputeShader_tA7BDD0F6EE879D149480F5890BA2E665C50CFBF8* ___scenarioBlendingShader;
	ProbeVolumeSceneData_t29FD126D36ED1E093C2EBBFB3F248DD5E2A86D90* ___sceneData;
	int32_t ___shBands;
	int32_t ___supportsRuntimeDebug;
	int32_t ___supportStreaming;
};
struct ProbeVolumeSystemParameters_t0654F2626ACA367E00C375BEB6FEA5B86CB0A58B_marshaled_com
{
	int32_t ___memoryBudget;
	int32_t ___blendingMemoryBudget;
	Mesh_t6D9C539763A09BC2B12AEAEF36F6DFFC98AE63D4* ___probeDebugMesh;
	Shader_tADC867D36B7876EE22427FAA2CE485105F4EE692* ___probeDebugShader;
	Mesh_t6D9C539763A09BC2B12AEAEF36F6DFFC98AE63D4* ___offsetDebugMesh;
	Shader_tADC867D36B7876EE22427FAA2CE485105F4EE692* ___offsetDebugShader;
	ComputeShader_tA7BDD0F6EE879D149480F5890BA2E665C50CFBF8* ___scenarioBlendingShader;
	ProbeVolumeSceneData_t29FD126D36ED1E093C2EBBFB3F248DD5E2A86D90* ___sceneData;
	int32_t ___shBands;
	int32_t ___supportsRuntimeDebug;
	int32_t ___supportStreaming;
};
struct Type_t  : public MemberInfo_t
{
	RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B ____impl;
};
struct Widget_tE8D6AF1D7525CC84E8F2C3B73162016736A6A2FF  : public RuntimeObject
{
	Panel_t3A0D2006E8AEA607A6DF5188138E463A26085295* ___m_Panel;
	RuntimeObject* ___m_Parent;
	int32_t ___U3CflagsU3Ek__BackingField;
	String_t* ___U3CdisplayNameU3Ek__BackingField;
	String_t* ___U3CtooltipU3Ek__BackingField;
	String_t* ___U3CqueryPathU3Ek__BackingField;
	Func_1_t2BE7F58348C9CC544A8973B3A9E55541DE43C457* ___isHiddenCallback;
};
struct Action_2_t156C43F079E7E68155FCDCD12DC77DD11AEF7E3C  : public MulticastDelegate_t
{
};
struct Action_2_t528DD1A0598C8661FA22AB60F7CEFBF784D3DA6B  : public MulticastDelegate_t
{
};
struct Action_2_t6F9B4FA82143ACF378558F06FC77D9CE0D68087D  : public MulticastDelegate_t
{
};
struct Field_1_t32151A22D4B1B5C1DFFDDACD9F3C78D19596507A  : public Widget_tE8D6AF1D7525CC84E8F2C3B73162016736A6A2FF
{
	Func_1_t2BE7F58348C9CC544A8973B3A9E55541DE43C457* ___U3CgetterU3Ek__BackingField;
	Action_1_t10DCB0C07D0D3C565CEACADC80D1152B35A45F6C* ___U3CsetterU3Ek__BackingField;
	Action_2_tB3E4CF19F3493DE4FE84AFFB77005AE79F9A3758* ___onValueChanged;
};
struct Field_1_t7F813BE8CAF3F3F635B34474DDD7B797C5B6CD2A  : public Widget_tE8D6AF1D7525CC84E8F2C3B73162016736A6A2FF
{
	Func_1_tC288CCB64EFD1F5FD49C3F8DE91FE62905E44BCD* ___U3CgetterU3Ek__BackingField;
	Action_1_tD69A6DC9FBE94131E52F5A73B2A9D4AB51EEC404* ___U3CsetterU3Ek__BackingField;
	Action_2_t94C644233E37D574986F0297182FA2BD8972B44A* ___onValueChanged;
};
struct Field_1_tEE1A923EA8160028BC34CE74DF77A8FB37FCA5D3  : public Widget_tE8D6AF1D7525CC84E8F2C3B73162016736A6A2FF
{
	Func_1_tBB8824FA8746333BFFF3AB3CE4A41B58450AF431* ___U3CgetterU3Ek__BackingField;
	Action_1_t923A20D1D4F6B55B2ED5AE21B90F1A0CE0450D99* ___U3CsetterU3Ek__BackingField;
	Action_2_tD2AB9B0AB95F0653AC53DC5114E5EC2958A3E36A* ___onValueChanged;
};
struct Func_3_tD46831209E6E19204CD8F9EAFC74DBFCA3C36C5F  : public MulticastDelegate_t
{
};
struct Func_3_tECED1961B53AB164A131061296ABA1276B4FBBB9  : public MulticastDelegate_t
{
};
struct Func_3_t3E644C82345CE04737DA5CDE018481FE0A88F821  : public MulticastDelegate_t
{
};
struct ProbeReferenceVolume_t05ED7EF2BB9B58F26CE1629F0AA773D14100695F  : public RuntimeObject
{
	bool ___m_IsInitialized;
	bool ___m_SupportStreaming;
	RefVolTransform_t23FA849BA67F6FB0FDC6BA49A08C41D654FC8CE9 ___m_Transform;
	int32_t ___m_MaxSubdivision;
	ProbeBrickPool_tC43640788A2B356F3F99A068D2CED6702E721693* ___m_Pool;
	ProbeBrickIndex_tF1B02DB88E5F4CF79533962B018B5724D74E32D2* ___m_Index;
	ProbeCellIndices_t0A30314A2B1D5F97E16BD321C179801D1B42C6AF* ___m_CellIndices;
	ProbeBrickBlendingPool_tD0DBB9B875C8C88A6410A239987DA3F9F4BE18F8* ___m_BlendingPool;
	List_1_t179992B095C528117EEF4782A1F45568BD2D51EA* ___m_TmpSrcChunks;
	SingleU5BU5D_t89DEFE97BCEDB5857010E79ECE0F52CF6E93B87C* ___m_PositionOffsets;
	Bounds_t367E830C64BBF235ED8C3B2F8CF6254FDCAD39C3 ___m_CurrGlobalBounds;
	Dictionary_2_tE62F67DD5E0705D89AA8A2987FB3C4C21A3C9AAF* ___cells;
	ObjectPool_1_t26A8D6F0AC3E7D5C10AB98A9AF68B2EBC2ABE7EF* ___m_CellInfoPool;
	ObjectPool_1_t7FA933D4164A730DB5D7E5E1D315B49D70184F03* ___m_BlendingCellInfoPool;
	DataLocation_t34FC6B68E8194966FC3C075EF4227E1522CB53BB ___m_TemporaryDataLocation;
	int32_t ___m_TemporaryDataLocationMemCost;
	int32_t ___m_CurrentProbeVolumeChunkSizeInBricks;
	ProbeVolumeSceneData_t29FD126D36ED1E093C2EBBFB3F248DD5E2A86D90* ___sceneData;
	Vector3Int_t65CB06F557251D18A37BD71F3655BA836A357376 ___minLoadedCellPos;
	Vector3Int_t65CB06F557251D18A37BD71F3655BA836A357376 ___maxLoadedCellPos;
	Action_1_t00621160046FE06A171CE95A003D9AE71EBB2B1D* ___retrieveExtraDataAction;
	Action_tD00B0A84D7945E50C2DFFC28EFEE6ED44ED2AD07* ___checksDuringBakeAction;
	bool ___m_BricksLoaded;
	Dictionary_2_t18C83CD24384334A550468AC80B4F64B179517FB* ___m_PendingAssetsToBeLoaded;
	Dictionary_2_t18C83CD24384334A550468AC80B4F64B179517FB* ___m_PendingAssetsToBeUnloaded;
	Dictionary_2_t18C83CD24384334A550468AC80B4F64B179517FB* ___m_ActiveAssets;
	bool ___m_NeedLoadAsset;
	bool ___m_ProbeReferenceVolumeInit;
	bool ___m_EnabledBySRP;
	InitInfo_t704DDF4A7F366AB2C84F08404C424B877802B058 ___m_PendingInitInfo;
	bool ___m_NeedsIndexRebuild;
	bool ___m_HasChangedIndex;
	int32_t ___m_CBShaderID;
	int32_t ___m_NumberOfCellsLoadedPerFrame;
	int32_t ___m_NumberOfCellsBlendedPerFrame;
	float ___m_TurnoverRate;
	int32_t ___m_MemoryBudget;
	int32_t ___m_BlendingMemoryBudget;
	int32_t ___m_SHBands;
	float ___m_ProbeVolumesWeight;
	bool ___clearAssetsOnVolumeClear;
	List_1_tCD7772AB40D4E7A61CCAFDDF9E33C190D4F9E6D4* ___U3CperSceneDataListU3Ek__BackingField;
	ProbeVolumeDebug_t295620780739F33AEAD1D1BB44C5252CE70D3DD8* ___U3CprobeVolumeDebugU3Ek__BackingField;
	ColorU5BU5D_t612261CF293F6FFC3D80AB52259FF0DC2B2CC389* ___U3CsubdivisionDebugColorsU3Ek__BackingField;
	WidgetU5BU5D_t39DEA55B87EF43C59C5699E0340B34185BA1E4A2* ___m_DebugItems;
	Mesh_t6D9C539763A09BC2B12AEAEF36F6DFFC98AE63D4* ___m_DebugMesh;
	Material_t18053F08F347D0DCA5E1140EC7EC4533DD8A14E3* ___m_DebugMaterial;
	Mesh_t6D9C539763A09BC2B12AEAEF36F6DFFC98AE63D4* ___m_DebugOffsetMesh;
	Material_t18053F08F347D0DCA5E1140EC7EC4533DD8A14E3* ___m_DebugOffsetMaterial;
	PlaneU5BU5D_t4EEF66BAA8B0140EFFF34F6183CE7F80546592BE* ___m_DebugFrustumPlanes;
	GUIContentU5BU5D_t98DA1EEA8D0A2C4AE42CE11C4840B627CADFC503* ___m_DebugScenarioNames;
	Int32U5BU5D_t19C97395396A72ECAF310612F0760F165060314C* ___m_DebugScenarioValues;
	String_t* ___m_DebugActiveSceneGUID;
	String_t* ___m_DebugActiveScenario;
	EnumField_t15C8FC0EB96499DFDCEC2B9DBB27B2BBCD5E262C* ___m_DebugScenarioField;
	ProbeVolumeBakingProcessSettings_t1A0C71DD07CFB6660AFC0D3EBF81FA5064CFDAD7 ___bakingProcessSettings;
	Dictionary_2_tE738E3156DB830A7FCEA2AE6066FC5BEA6715F0D* ___realtimeSubdivisionInfo;
	bool ___m_MaxSubdivVisualizedIsMaxAvailable;
	DynamicArray_1_t85D77BAA52B2801695EAE751BA0F9DD3C26AA604* ___m_LoadedCells;
	DynamicArray_1_t85D77BAA52B2801695EAE751BA0F9DD3C26AA604* ___m_ToBeLoadedCells;
	DynamicArray_1_t85D77BAA52B2801695EAE751BA0F9DD3C26AA604* ___m_TempCellToLoadList;
	DynamicArray_1_t85D77BAA52B2801695EAE751BA0F9DD3C26AA604* ___m_TempCellToUnloadList;
	DynamicArray_1_tD456FAFFECC4879D97EE0F550727BF9C6B0B3FE6* ___m_LoadedBlendingCells;
	DynamicArray_1_tD456FAFFECC4879D97EE0F550727BF9C6B0B3FE6* ___m_ToBeLoadedBlendingCells;
	DynamicArray_1_tD456FAFFECC4879D97EE0F550727BF9C6B0B3FE6* ___m_TempBlendingCellToLoadList;
	DynamicArray_1_tD456FAFFECC4879D97EE0F550727BF9C6B0B3FE6* ___m_TempBlendingCellToUnloadList;
	Vector3_t24C512C7B96BBABAD472002D0BA2BDA40A5A80B2 ___m_FrozenCameraPosition;
	bool ___m_HasRemainingCellsToBlend;
};
struct U3CU3Ec__DisplayClass171_0_t70061616D0F785A73C9408015CCBEBC3C2B43646  : public RuntimeObject
{
	ProbeReferenceVolume_t05ED7EF2BB9B58F26CE1629F0AA773D14100695F* ___U3CU3E4__this;
	ProbeVolumeSystemParameters_t0654F2626ACA367E00C375BEB6FEA5B86CB0A58B ___parameters;
};
struct AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0_StaticFields
{
	bool ___enableDebugPrints;
};
struct String_t_StaticFields
{
	String_t* ___Empty;
};
struct Boolean_t09A6377A54BE2F9E6985A8149F19234FD7DDFE22_StaticFields
{
	String_t* ___TrueString;
	String_t* ___FalseString;
};
struct Char_t521A6F19B456D956AF452D926C32709DC03D6B17_StaticFields
{
	ByteU5BU5D_tA6237BF417AE52AD70CFB4EF24A7A82613DF9031* ___s_categoryForLatin1;
};
struct IntPtr_t_StaticFields
{
	intptr_t ___Zero;
};
struct Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3_StaticFields
{
	Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 ___zeroVector;
	Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 ___oneVector;
	Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 ___positiveInfinityVector;
	Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 ___negativeInfinityVector;
};
struct LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2_StaticFields
{
	Func_3_t3E644C82345CE04737DA5CDE018481FE0A88F821* ___s_CompareByCookieSize;
	Func_3_t3E644C82345CE04737DA5CDE018481FE0A88F821* ___s_CompareByBufferIndex;
};
struct Exception_t_StaticFields
{
	RuntimeObject* ___s_EDILock;
};
struct Type_t_StaticFields
{
	Binder_t91BFCE95A7057FADF4D8A1A342AFE52872246235* ___s_defaultBinder;
	Il2CppChar ___Delimiter;
	TypeU5BU5D_t97234E1129B564EB38B8D85CAC2AD8B5B9522FFB* ___EmptyTypes;
	RuntimeObject* ___Missing;
	MemberFilter_tF644F1AE82F611B677CE1964D5A3277DDA21D553* ___FilterAttribute;
	MemberFilter_tF644F1AE82F611B677CE1964D5A3277DDA21D553* ___FilterName;
	MemberFilter_tF644F1AE82F611B677CE1964D5A3277DDA21D553* ___FilterNameIgnoreCase;
};
struct ProbeReferenceVolume_t05ED7EF2BB9B58F26CE1629F0AA773D14100695F_StaticFields
{
	String_t* ___defaultLightingScenario;
	ProbeReferenceVolume_t05ED7EF2BB9B58F26CE1629F0AA773D14100695F* ____instance;
	String_t* ___k_DebugPanelName;
};
#ifdef __clang__
#pragma clang diagnostic pop
#endif
struct StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248  : public RuntimeArray
{
	ALIGN_FIELD (8) String_t* m_Items[1];

	inline String_t* GetAt(il2cpp_array_size_t index) const
	{
		IL2CPP_ARRAY_BOUNDS_CHECK(index, (uint32_t)(this)->max_length);
		return m_Items[index];
	}
	inline String_t** GetAddressAt(il2cpp_array_size_t index)
	{
		IL2CPP_ARRAY_BOUNDS_CHECK(index, (uint32_t)(this)->max_length);
		return m_Items + index;
	}
	inline void SetAt(il2cpp_array_size_t index, String_t* value)
	{
		IL2CPP_ARRAY_BOUNDS_CHECK(index, (uint32_t)(this)->max_length);
		m_Items[index] = value;
		Il2CppCodeGenWriteBarrier((void**)m_Items + index, (void*)value);
	}
	inline String_t* GetAtUnchecked(il2cpp_array_size_t index) const
	{
		return m_Items[index];
	}
	inline String_t** GetAddressAtUnchecked(il2cpp_array_size_t index)
	{
		return m_Items + index;
	}
	inline void SetAtUnchecked(il2cpp_array_size_t index, String_t* value)
	{
		m_Items[index] = value;
		Il2CppCodeGenWriteBarrier((void**)m_Items + index, (void*)value);
	}
};
struct AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001  : public RuntimeArray
{
	ALIGN_FIELD (8) AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0* m_Items[1];

	inline AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0* GetAt(il2cpp_array_size_t index) const
	{
		IL2CPP_ARRAY_BOUNDS_CHECK(index, (uint32_t)(this)->max_length);
		return m_Items[index];
	}
	inline AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0** GetAddressAt(il2cpp_array_size_t index)
	{
		IL2CPP_ARRAY_BOUNDS_CHECK(index, (uint32_t)(this)->max_length);
		return m_Items + index;
	}
	inline void SetAt(il2cpp_array_size_t index, AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0* value)
	{
		IL2CPP_ARRAY_BOUNDS_CHECK(index, (uint32_t)(this)->max_length);
		m_Items[index] = value;
		Il2CppCodeGenWriteBarrier((void**)m_Items + index, (void*)value);
	}
	inline AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0* GetAtUnchecked(il2cpp_array_size_t index) const
	{
		return m_Items[index];
	}
	inline AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0** GetAddressAtUnchecked(il2cpp_array_size_t index)
	{
		return m_Items + index;
	}
	inline void SetAtUnchecked(il2cpp_array_size_t index, AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0* value)
	{
		m_Items[index] = value;
		Il2CppCodeGenWriteBarrier((void**)m_Items + index, (void*)value);
	}
};
struct Int32U5BU5D_t19C97395396A72ECAF310612F0760F165060314C  : public RuntimeArray
{
	ALIGN_FIELD (8) int32_t m_Items[1];

	inline int32_t GetAt(il2cpp_array_size_t index) const
	{
		IL2CPP_ARRAY_BOUNDS_CHECK(index, (uint32_t)(this)->max_length);
		return m_Items[index];
	}
	inline int32_t* GetAddressAt(il2cpp_array_size_t index)
	{
		IL2CPP_ARRAY_BOUNDS_CHECK(index, (uint32_t)(this)->max_length);
		return m_Items + index;
	}
	inline void SetAt(il2cpp_array_size_t index, int32_t value)
	{
		IL2CPP_ARRAY_BOUNDS_CHECK(index, (uint32_t)(this)->max_length);
		m_Items[index] = value;
	}
	inline int32_t GetAtUnchecked(il2cpp_array_size_t index) const
	{
		return m_Items[index];
	}
	inline int32_t* GetAddressAtUnchecked(il2cpp_array_size_t index)
	{
		return m_Items + index;
	}
	inline void SetAtUnchecked(il2cpp_array_size_t index, int32_t value)
	{
		m_Items[index] = value;
	}
};
struct BooleanU5BU5D_tD317D27C31DB892BE79FAE3AEBC0B3FFB73DE9B4  : public RuntimeArray
{
	ALIGN_FIELD (8) bool m_Items[1];

	inline bool GetAt(il2cpp_array_size_t index) const
	{
		IL2CPP_ARRAY_BOUNDS_CHECK(index, (uint32_t)(this)->max_length);
		return m_Items[index];
	}
	inline bool* GetAddressAt(il2cpp_array_size_t index)
	{
		IL2CPP_ARRAY_BOUNDS_CHECK(index, (uint32_t)(this)->max_length);
		return m_Items + index;
	}
	inline void SetAt(il2cpp_array_size_t index, bool value)
	{
		IL2CPP_ARRAY_BOUNDS_CHECK(index, (uint32_t)(this)->max_length);
		m_Items[index] = value;
	}
	inline bool GetAtUnchecked(il2cpp_array_size_t index) const
	{
		return m_Items[index];
	}
	inline bool* GetAddressAtUnchecked(il2cpp_array_size_t index)
	{
		return m_Items + index;
	}
	inline void SetAtUnchecked(il2cpp_array_size_t index, bool value)
	{
		m_Items[index] = value;
	}
};
struct ByteU5BU5D_tA6237BF417AE52AD70CFB4EF24A7A82613DF9031  : public RuntimeArray
{
	ALIGN_FIELD (8) uint8_t m_Items[1];

	inline uint8_t GetAt(il2cpp_array_size_t index) const
	{
		IL2CPP_ARRAY_BOUNDS_CHECK(index, (uint32_t)(this)->max_length);
		return m_Items[index];
	}
	inline uint8_t* GetAddressAt(il2cpp_array_size_t index)
	{
		IL2CPP_ARRAY_BOUNDS_CHECK(index, (uint32_t)(this)->max_length);
		return m_Items + index;
	}
	inline void SetAt(il2cpp_array_size_t index, uint8_t value)
	{
		IL2CPP_ARRAY_BOUNDS_CHECK(index, (uint32_t)(this)->max_length);
		m_Items[index] = value;
	}
	inline uint8_t GetAtUnchecked(il2cpp_array_size_t index) const
	{
		return m_Items[index];
	}
	inline uint8_t* GetAddressAtUnchecked(il2cpp_array_size_t index)
	{
		return m_Items + index;
	}
	inline void SetAtUnchecked(il2cpp_array_size_t index, uint8_t value)
	{
		m_Items[index] = value;
	}
};
struct SByteU5BU5D_t88116DA68378C3333DB73E7D36C1A06AFAA91913  : public RuntimeArray
{
	ALIGN_FIELD (8) int8_t m_Items[1];

	inline int8_t GetAt(il2cpp_array_size_t index) const
	{
		IL2CPP_ARRAY_BOUNDS_CHECK(index, (uint32_t)(this)->max_length);
		return m_Items[index];
	}
	inline int8_t* GetAddressAt(il2cpp_array_size_t index)
	{
		IL2CPP_ARRAY_BOUNDS_CHECK(index, (uint32_t)(this)->max_length);
		return m_Items + index;
	}
	inline void SetAt(il2cpp_array_size_t index, int8_t value)
	{
		IL2CPP_ARRAY_BOUNDS_CHECK(index, (uint32_t)(this)->max_length);
		m_Items[index] = value;
	}
	inline int8_t GetAtUnchecked(il2cpp_array_size_t index) const
	{
		return m_Items[index];
	}
	inline int8_t* GetAddressAtUnchecked(il2cpp_array_size_t index)
	{
		return m_Items + index;
	}
	inline void SetAtUnchecked(il2cpp_array_size_t index, int8_t value)
	{
		m_Items[index] = value;
	}
};
struct Int16U5BU5D_t8175CE8DD9C9F9FB0CF4F58E45BC570575B43CFB  : public RuntimeArray
{
	ALIGN_FIELD (8) int16_t m_Items[1];

	inline int16_t GetAt(il2cpp_array_size_t index) const
	{
		IL2CPP_ARRAY_BOUNDS_CHECK(index, (uint32_t)(this)->max_length);
		return m_Items[index];
	}
	inline int16_t* GetAddressAt(il2cpp_array_size_t index)
	{
		IL2CPP_ARRAY_BOUNDS_CHECK(index, (uint32_t)(this)->max_length);
		return m_Items + index;
	}
	inline void SetAt(il2cpp_array_size_t index, int16_t value)
	{
		IL2CPP_ARRAY_BOUNDS_CHECK(index, (uint32_t)(this)->max_length);
		m_Items[index] = value;
	}
	inline int16_t GetAtUnchecked(il2cpp_array_size_t index) const
	{
		return m_Items[index];
	}
	inline int16_t* GetAddressAtUnchecked(il2cpp_array_size_t index)
	{
		return m_Items + index;
	}
	inline void SetAtUnchecked(il2cpp_array_size_t index, int16_t value)
	{
		m_Items[index] = value;
	}
};
struct Int64U5BU5D_tAEDFCBDB5414E2A140A6F34C0538BF97FCF67A1D  : public RuntimeArray
{
	ALIGN_FIELD (8) int64_t m_Items[1];

	inline int64_t GetAt(il2cpp_array_size_t index) const
	{
		IL2CPP_ARRAY_BOUNDS_CHECK(index, (uint32_t)(this)->max_length);
		return m_Items[index];
	}
	inline int64_t* GetAddressAt(il2cpp_array_size_t index)
	{
		IL2CPP_ARRAY_BOUNDS_CHECK(index, (uint32_t)(this)->max_length);
		return m_Items + index;
	}
	inline void SetAt(il2cpp_array_size_t index, int64_t value)
	{
		IL2CPP_ARRAY_BOUNDS_CHECK(index, (uint32_t)(this)->max_length);
		m_Items[index] = value;
	}
	inline int64_t GetAtUnchecked(il2cpp_array_size_t index) const
	{
		return m_Items[index];
	}
	inline int64_t* GetAddressAtUnchecked(il2cpp_array_size_t index)
	{
		return m_Items + index;
	}
	inline void SetAtUnchecked(il2cpp_array_size_t index, int64_t value)
	{
		m_Items[index] = value;
	}
};
struct SingleU5BU5D_t89DEFE97BCEDB5857010E79ECE0F52CF6E93B87C  : public RuntimeArray
{
	ALIGN_FIELD (8) float m_Items[1];

	inline float GetAt(il2cpp_array_size_t index) const
	{
		IL2CPP_ARRAY_BOUNDS_CHECK(index, (uint32_t)(this)->max_length);
		return m_Items[index];
	}
	inline float* GetAddressAt(il2cpp_array_size_t index)
	{
		IL2CPP_ARRAY_BOUNDS_CHECK(index, (uint32_t)(this)->max_length);
		return m_Items + index;
	}
	inline void SetAt(il2cpp_array_size_t index, float value)
	{
		IL2CPP_ARRAY_BOUNDS_CHECK(index, (uint32_t)(this)->max_length);
		m_Items[index] = value;
	}
	inline float GetAtUnchecked(il2cpp_array_size_t index) const
	{
		return m_Items[index];
	}
	inline float* GetAddressAtUnchecked(il2cpp_array_size_t index)
	{
		return m_Items + index;
	}
	inline void SetAtUnchecked(il2cpp_array_size_t index, float value)
	{
		m_Items[index] = value;
	}
};
struct DoubleU5BU5D_tCC308475BD3B8229DB2582938669EF2F9ECC1FEE  : public RuntimeArray
{
	ALIGN_FIELD (8) double m_Items[1];

	inline double GetAt(il2cpp_array_size_t index) const
	{
		IL2CPP_ARRAY_BOUNDS_CHECK(index, (uint32_t)(this)->max_length);
		return m_Items[index];
	}
	inline double* GetAddressAt(il2cpp_array_size_t index)
	{
		IL2CPP_ARRAY_BOUNDS_CHECK(index, (uint32_t)(this)->max_length);
		return m_Items + index;
	}
	inline void SetAt(il2cpp_array_size_t index, double value)
	{
		IL2CPP_ARRAY_BOUNDS_CHECK(index, (uint32_t)(this)->max_length);
		m_Items[index] = value;
	}
	inline double GetAtUnchecked(il2cpp_array_size_t index) const
	{
		return m_Items[index];
	}
	inline double* GetAddressAtUnchecked(il2cpp_array_size_t index)
	{
		return m_Items + index;
	}
	inline void SetAtUnchecked(il2cpp_array_size_t index, double value)
	{
		m_Items[index] = value;
	}
};
struct CharU5BU5D_t799905CF001DD5F13F7DBB310181FC4D8B7D0AAB  : public RuntimeArray
{
	ALIGN_FIELD (8) Il2CppChar m_Items[1];

	inline Il2CppChar GetAt(il2cpp_array_size_t index) const
	{
		IL2CPP_ARRAY_BOUNDS_CHECK(index, (uint32_t)(this)->max_length);
		return m_Items[index];
	}
	inline Il2CppChar* GetAddressAt(il2cpp_array_size_t index)
	{
		IL2CPP_ARRAY_BOUNDS_CHECK(index, (uint32_t)(this)->max_length);
		return m_Items + index;
	}
	inline void SetAt(il2cpp_array_size_t index, Il2CppChar value)
	{
		IL2CPP_ARRAY_BOUNDS_CHECK(index, (uint32_t)(this)->max_length);
		m_Items[index] = value;
	}
	inline Il2CppChar GetAtUnchecked(il2cpp_array_size_t index) const
	{
		return m_Items[index];
	}
	inline Il2CppChar* GetAddressAtUnchecked(il2cpp_array_size_t index)
	{
		return m_Items + index;
	}
	inline void SetAtUnchecked(il2cpp_array_size_t index, Il2CppChar value)
	{
		m_Items[index] = value;
	}
};
struct ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918  : public RuntimeArray
{
	ALIGN_FIELD (8) RuntimeObject* m_Items[1];

	inline RuntimeObject* GetAt(il2cpp_array_size_t index) const
	{
		IL2CPP_ARRAY_BOUNDS_CHECK(index, (uint32_t)(this)->max_length);
		return m_Items[index];
	}
	inline RuntimeObject** GetAddressAt(il2cpp_array_size_t index)
	{
		IL2CPP_ARRAY_BOUNDS_CHECK(index, (uint32_t)(this)->max_length);
		return m_Items + index;
	}
	inline void SetAt(il2cpp_array_size_t index, RuntimeObject* value)
	{
		IL2CPP_ARRAY_BOUNDS_CHECK(index, (uint32_t)(this)->max_length);
		m_Items[index] = value;
		Il2CppCodeGenWriteBarrier((void**)m_Items + index, (void*)value);
	}
	inline RuntimeObject* GetAtUnchecked(il2cpp_array_size_t index) const
	{
		return m_Items[index];
	}
	inline RuntimeObject** GetAddressAtUnchecked(il2cpp_array_size_t index)
	{
		return m_Items + index;
	}
	inline void SetAtUnchecked(il2cpp_array_size_t index, RuntimeObject* value)
	{
		m_Items[index] = value;
		Il2CppCodeGenWriteBarrier((void**)m_Items + index, (void*)value);
	}
};
struct Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD  : public RuntimeArray
{
	ALIGN_FIELD (8) Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 m_Items[1];

	inline Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 GetAt(il2cpp_array_size_t index) const
	{
		IL2CPP_ARRAY_BOUNDS_CHECK(index, (uint32_t)(this)->max_length);
		return m_Items[index];
	}
	inline Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3* GetAddressAt(il2cpp_array_size_t index)
	{
		IL2CPP_ARRAY_BOUNDS_CHECK(index, (uint32_t)(this)->max_length);
		return m_Items + index;
	}
	inline void SetAt(il2cpp_array_size_t index, Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 value)
	{
		IL2CPP_ARRAY_BOUNDS_CHECK(index, (uint32_t)(this)->max_length);
		m_Items[index] = value;
	}
	inline Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 GetAtUnchecked(il2cpp_array_size_t index) const
	{
		return m_Items[index];
	}
	inline Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3* GetAddressAtUnchecked(il2cpp_array_size_t index)
	{
		return m_Items + index;
	}
	inline void SetAtUnchecked(il2cpp_array_size_t index, Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 value)
	{
		m_Items[index] = value;
	}
};
struct __Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC  : public RuntimeArray
{
	ALIGN_FIELD (8) uint8_t m_Items[1];

	inline uint8_t* GetAddressAt(il2cpp_array_size_t index)
	{
		IL2CPP_ARRAY_BOUNDS_CHECK(index, (uint32_t)(this)->max_length);
		return m_Items + il2cpp_array_calc_byte_offset(this, index);
	}
	inline uint8_t* GetAddressAtUnchecked(il2cpp_array_size_t index)
	{
		return m_Items + il2cpp_array_calc_byte_offset(this, index);
	}
};
struct LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263  : public RuntimeArray
{
	ALIGN_FIELD (8) LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 m_Items[1];

	inline LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 GetAt(il2cpp_array_size_t index) const
	{
		IL2CPP_ARRAY_BOUNDS_CHECK(index, (uint32_t)(this)->max_length);
		return m_Items[index];
	}
	inline LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2* GetAddressAt(il2cpp_array_size_t index)
	{
		IL2CPP_ARRAY_BOUNDS_CHECK(index, (uint32_t)(this)->max_length);
		return m_Items + index;
	}
	inline void SetAt(il2cpp_array_size_t index, LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 value)
	{
		IL2CPP_ARRAY_BOUNDS_CHECK(index, (uint32_t)(this)->max_length);
		m_Items[index] = value;
		Il2CppCodeGenWriteBarrier((void**)&((m_Items + index)->___light), (void*)NULL);
	}
	inline LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 GetAtUnchecked(il2cpp_array_size_t index) const
	{
		return m_Items[index];
	}
	inline LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2* GetAddressAtUnchecked(il2cpp_array_size_t index)
	{
		return m_Items + index;
	}
	inline void SetAtUnchecked(il2cpp_array_size_t index, LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 value)
	{
		m_Items[index] = value;
		Il2CppCodeGenWriteBarrier((void**)&((m_Items + index)->___light), (void*)NULL);
	}
};


IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR String_t* _AndroidJNIHelper_GetSignature_TisBoolean_t09A6377A54BE2F9E6985A8149F19234FD7DDFE22_m1BB764DB4D3E393C60E69169020A7EC792D639D5_gshared (ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* ___0_args, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR String_t* _AndroidJNIHelper_GetSignature_TisChar_t521A6F19B456D956AF452D926C32709DC03D6B17_mD783834059E75BFC7A7FEB544B6ABA307E91B2C4_gshared (ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* ___0_args, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR String_t* _AndroidJNIHelper_GetSignature_TisDouble_tE150EF3D1D43DEE85D533810AB4C742307EEDE5F_m74C4D07DCE96BE5E61ED2AAED270DF7469C5F341_gshared (ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* ___0_args, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR String_t* _AndroidJNIHelper_GetSignature_TisInt16_tB8EF286A9C33492FA6E6D6E67320BE93E794A175_m1E079B67FDC93E1BBE5C29D9C2BC09338DA0A5AA_gshared (ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* ___0_args, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR String_t* _AndroidJNIHelper_GetSignature_TisInt32_t680FF22E76F6EFAD4375103CBBFFA0421349384C_mA85CEF9411BD97B51F86CC460B32C46C2B873B12_gshared (ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* ___0_args, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR String_t* _AndroidJNIHelper_GetSignature_TisInt64_t092CFB123BE63C28ACDAF65C68F21A526050DBA3_m847042ADF26044DDB60469E1C3477EBBB1B55E11_gshared (ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* ___0_args, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR String_t* _AndroidJNIHelper_GetSignature_TisRuntimeObject_m7CC50A493D0C6897ECB2692A7CEFB3A2CD3655A5_gshared (ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* ___0_args, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR String_t* _AndroidJNIHelper_GetSignature_TisSByte_tFEFFEF5D2FEBF5207950AE6FAC150FC53B668DB5_mEAD40CF5E1A04E27AE3991DAB10ABB9EC6F37FBB_gshared (ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* ___0_args, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR String_t* _AndroidJNIHelper_GetSignature_TisSingle_t4530F2FF86FCB0DC29F35385CA1BD21BE294761C_mDD367BE518367698F0093E97FCF201D89B5790CB_gshared (ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* ___0_args, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR bool ExpressionEvaluator_EvaluateTokens_TisDouble_tE150EF3D1D43DEE85D533810AB4C742307EEDE5F_m791767867653D0CCE2BEFF83F336A41B5B3A718E_gshared (StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* ___0_tokens, double* ___1_value, int32_t ___2_index, int32_t ___3_count, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR bool ExpressionEvaluator_EvaluateTokens_TisInt64_t092CFB123BE63C28ACDAF65C68F21A526050DBA3_m7418F7A8835B2770EF83F1D52F2723897CD76DEB_gshared (StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* ___0_tokens, int64_t* ___1_value, int32_t ___2_index, int32_t ___3_count, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR bool ExpressionEvaluator_EvaluateTokens_TisUInt64_t8F12534CC8FC4B5860F2A2CD1EE79D322E7A41AF_mCFCF758DECB276DBCB0A8B83BAE195EF3B974780_gshared (StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* ___0_tokens, uint64_t* ___1_value, int32_t ___2_index, int32_t ___3_count, const RuntimeMethod* method) ;
IL2CPP_MANAGED_FORCE_INLINE IL2CPP_METHOD_ATTR int32_t Func_3_Invoke_mE6CD106F59B0ADD2DF9C211DC4CF4088F5A1A4BB_gshared_inline (Func_3_tD46831209E6E19204CD8F9EAFC74DBFCA3C36C5F* __this, Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 ___0_arg1, Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 ___1_arg2, const RuntimeMethod* method) ;
IL2CPP_MANAGED_FORCE_INLINE IL2CPP_METHOD_ATTR int32_t Func_3_Invoke_m2AED59BE1B0645C0DB5DAE117842A1C0AD4BDEBB_gshared_inline (Func_3_t3E644C82345CE04737DA5CDE018481FE0A88F821* __this, LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 ___0_arg1, LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 ___1_arg2, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void Sorting_U3CMedian3PivotU3Eg__SwapU7C2_0_TisVector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3_m2B2B04012DE1B591C8E7AD4765ECB8EF3790F795_gshared (int32_t ___0_a, int32_t ___1_b, U3CU3Ec__DisplayClass2_0_1_t41073816D00B5468033D7AA727FBFFB73E7C9BA2* ___2_p, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void Sorting_U3CMedian3PivotU3Eg__SwapU7C2_0_TisLightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2_m06FED96568508A808BFC2F0CB6D49F45194E6051_gshared (int32_t ___0_a, int32_t ___1_b, U3CU3Ec__DisplayClass2_0_1_tC4E3D65CA470C2F2DB85D9B32B717BE3200D4597* ___2_p, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 Sorting_Median3Pivot_TisVector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3_m61A04EAD49649BB481C390575840F890DC1AD6D9_gshared (Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* ___0_data, int32_t ___1_start, int32_t ___2_pivot, int32_t ___3_end, Func_3_tD46831209E6E19204CD8F9EAFC74DBFCA3C36C5F* ___4_compare, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 Sorting_Median3Pivot_TisLightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2_m3AE419868146FAEE6A59E9FA4E33484BFA9930B1_gshared (LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* ___0_data, int32_t ___1_start, int32_t ___2_pivot, int32_t ___3_end, Func_3_t3E644C82345CE04737DA5CDE018481FE0A88F821* ___4_compare, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void Sorting_InsertionSort_TisVector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3_m6B06894C5FA146D1CCE7ECBC21F553F16F2E96F5_gshared (Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* ___0_data, int32_t ___1_start, int32_t ___2_end, Func_3_tD46831209E6E19204CD8F9EAFC74DBFCA3C36C5F* ___3_compare, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR int32_t Sorting_Partition_TisVector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3_m5B1882A69C494B64F1EA761E21D0018C1D6AB6E8_gshared (Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* ___0_data, int32_t ___1_start, int32_t ___2_end, Func_3_tD46831209E6E19204CD8F9EAFC74DBFCA3C36C5F* ___3_compare, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void Sorting_QuickSort_TisVector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3_mAA6CA24576E19917524BFD6BE7AC3ACF4A18B570_gshared (Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* ___0_data, int32_t ___1_start, int32_t ___2_end, Func_3_tD46831209E6E19204CD8F9EAFC74DBFCA3C36C5F* ___3_compare, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void Sorting_InsertionSort_TisLightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2_m50C92303E813A7BFD084FB309E5FB9937C8F2065_gshared (LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* ___0_data, int32_t ___1_start, int32_t ___2_end, Func_3_t3E644C82345CE04737DA5CDE018481FE0A88F821* ___3_compare, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR int32_t Sorting_Partition_TisLightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2_m0E79CA1E375645FFDF3E1506F789825A9A6D3D95_gshared (LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* ___0_data, int32_t ___1_start, int32_t ___2_end, Func_3_t3E644C82345CE04737DA5CDE018481FE0A88F821* ___3_compare, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void Sorting_QuickSort_TisLightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2_mADD51465439832E9BCC31668A2DE42CFCCA07F9C_gshared (LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* ___0_data, int32_t ___1_start, int32_t ___2_end, Func_3_t3E644C82345CE04737DA5CDE018481FE0A88F821* ___3_compare, const RuntimeMethod* method) ;
IL2CPP_MANAGED_FORCE_INLINE IL2CPP_METHOD_ATTR void Action_2_Invoke_m7BFCE0BBCF67689D263059B56A8D79161B698587_gshared_inline (Action_2_t156C43F079E7E68155FCDCD12DC77DD11AEF7E3C* __this, RuntimeObject* ___0_arg1, RuntimeObject* ___1_arg2, const RuntimeMethod* method) ;
IL2CPP_MANAGED_FORCE_INLINE IL2CPP_METHOD_ATTR int32_t DynamicArray_1_get_size_m1B00C20A8CC4D62269585D16A58425D3F258836F_gshared_inline (DynamicArray_1_t7C64F5A74B7BA6F6B3589A766CADE3F59C6C7BCA* __this, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void DynamicArray_1_Resize_m3E24EB8A4A036B423BA304E8C3C94EBD0222822E_gshared (DynamicArray_1_t7C64F5A74B7BA6F6B3589A766CADE3F59C6C7BCA* __this, int32_t ___0_newSize, bool ___1_keepContent, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR RuntimeObject** DynamicArray_1_get_Item_m7DDF1E462D1484149A4D812CAD717F816205FD44_gshared (DynamicArray_1_t7C64F5A74B7BA6F6B3589A766CADE3F59C6C7BCA* __this, int32_t ___0_index, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_NO_INLINE IL2CPP_METHOD_ATTR RuntimeObject* Activator_CreateInstance_TisRuntimeObject_m62506836177F0F862A8D619638BF37F48721F138_gshared (const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR RuntimeObject* TypeUtility_CreateTypeConstructor_TisBounds_t367E830C64BBF235ED8C3B2F8CF6254FDCAD39C3_m16C827D0F6107B7998F6C99B57F7CC2F181E2198_gshared (const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR RuntimeObject* TypeUtility_CreateTypeConstructor_TisBoundsInt_t4E757DE5EFF9FCB42000F173360DDC63B5585485_m8F344250A2F9E6EE6DDBA6BA833BB36D0F272B66_gshared (const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR RuntimeObject* TypeUtility_CreateTypeConstructor_TisColor_tD001788D726C3A7F1379BEED0260B9591F440C1F_mBBCB804F367E06EA4D482F1B69165DD2B5BF38FF_gshared (const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR RuntimeObject* TypeUtility_CreateTypeConstructor_TisRuntimeObject_m4E17F588B090C1DADAE2D986BDA407DECEAC020F_gshared (const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR RuntimeObject* TypeUtility_CreateTypeConstructor_TisRect_tA04E0F8A1830E767F40FB27ECD8D309303571F0D_m2C5F5CF80D13B041768C7845C5AAEEC02BB683BA_gshared (const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR RuntimeObject* TypeUtility_CreateTypeConstructor_TisRectInt_t1744D10E1063135DA9D574F95205B98DAC600CB8_mF6949D9EDD480E6666CD975C66487AAD6ABC7D11_gshared (const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR RuntimeObject* TypeUtility_CreateTypeConstructor_TisVector2_t1FD6F485C871E832B347AB2DC8CBA08B739D8DF7_mE0C65F4221E48BB07F75856972A0CCDAE284AB9F_gshared (const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR RuntimeObject* TypeUtility_CreateTypeConstructor_TisVector2Int_t69B2886EBAB732D9B880565E18E7568F3DE0CE6A_mC8EF710494C8986B279262C6C64947BE2C1DC55C_gshared (const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR RuntimeObject* TypeUtility_CreateTypeConstructor_TisVector3_t24C512C7B96BBABAD472002D0BA2BDA40A5A80B2_m1AB8BF0921C24186B3C43FC4341AAD2F6FE87C4D_gshared (const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR RuntimeObject* TypeUtility_CreateTypeConstructor_TisVector3Int_t65CB06F557251D18A37BD71F3655BA836A357376_mB00220519A80AA5ACE36B7DBA2E6A6CB796302AF_gshared (const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR RuntimeObject* TypeUtility_CreateTypeConstructor_TisVector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3_mED1DC338E5DB62F3E64F6272A9F12150DA5CC1B9_gshared (const RuntimeMethod* method) ;

IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR Type_t* Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57 (RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B ___0_handle, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR bool AndroidReflection_IsPrimitive_mA41A9ECECE3D73679C79DC8B0FDD32B59570DF25 (Type_t* ___0_t, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR bool Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC (Type_t* ___0_left, Type_t* ___1_right, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR Int32U5BU5D_t19C97395396A72ECAF310612F0760F165060314C* AndroidJNISafe_FromIntArray_mC4C4DC70FFA39CD6E3E02FDAC7192324E6D4614E (intptr_t ___0_array, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR BooleanU5BU5D_tD317D27C31DB892BE79FAE3AEBC0B3FFB73DE9B4* AndroidJNISafe_FromBooleanArray_m36ED740401185EC0A959CA0F96A324A69E668646 (intptr_t ___0_array, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void Debug_LogWarning_m33EF1B897E0C7C6FF538989610BFAFFEF4628CA9 (RuntimeObject* ___0_message, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR ByteU5BU5D_tA6237BF417AE52AD70CFB4EF24A7A82613DF9031* AndroidJNISafe_FromByteArray_mB06EF0FDBF6C738231E8F9D4998C38551131C4C5 (intptr_t ___0_array, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR SByteU5BU5D_t88116DA68378C3333DB73E7D36C1A06AFAA91913* AndroidJNISafe_FromSByteArray_m261D638D8B059AB777BEF0BEFDD0822717DFF2B1 (intptr_t ___0_array, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR Int16U5BU5D_t8175CE8DD9C9F9FB0CF4F58E45BC570575B43CFB* AndroidJNISafe_FromShortArray_m62C0CB2D0BAE96D4B8CE365630361150EBE884FC (intptr_t ___0_array, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR Int64U5BU5D_tAEDFCBDB5414E2A140A6F34C0538BF97FCF67A1D* AndroidJNISafe_FromLongArray_mC4D73C0DA27F212947AB85AA2030A35BECDF8288 (intptr_t ___0_array, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR SingleU5BU5D_t89DEFE97BCEDB5857010E79ECE0F52CF6E93B87C* AndroidJNISafe_FromFloatArray_mDE02985159EEFD2CB28611C797AC21DE8B6300B8 (intptr_t ___0_array, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR DoubleU5BU5D_tCC308475BD3B8229DB2582938669EF2F9ECC1FEE* AndroidJNISafe_FromDoubleArray_mDEA8F2C7854101272F3A2733F351B570AAD5D9D9 (intptr_t ___0_array, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR CharU5BU5D_t799905CF001DD5F13F7DBB310181FC4D8B7D0AAB* AndroidJNISafe_FromCharArray_m54EDC9D2BE92F9973F4E00EE953EE242B231EA96 (intptr_t ___0_array, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR int32_t AndroidJNISafe_GetArrayLength_m809419F04C9BB93FED5B4A89F0539231C9B90E6F (intptr_t ___0_array, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR intptr_t AndroidJNI_GetObjectArrayElement_mC4CAF9744617F69EFCD95B71D95492DA20A0FACE (intptr_t ___0_array, int32_t ___1_index, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR String_t* AndroidJNISafe_GetStringChars_mE246814CD8FF4EDDEE6EBF107367C4A8EAF03849 (intptr_t ___0_str, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void AndroidJNISafe_DeleteLocalRef_m20303564C88A1B90E3D8D7A7D893392E18967094 (intptr_t ___0_localref, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void AndroidJavaObject__ctor_m0CEE7D570807333CE2C193A82AB3AB8D4F873A6B (AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0* __this, intptr_t ___0_jobject, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR String_t* String_Concat_m8855A6DE10F84DA7F4EC113CADDB59873A25573B (String_t* ___0_str0, String_t* ___1_str1, String_t* ___2_str2, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void Exception__ctor_m9B2BD92CD68916245A75109105D9071C9D430E7F (Exception_t* __this, String_t* ___0_message, const RuntimeMethod* method) ;
inline String_t* _AndroidJNIHelper_GetSignature_TisBoolean_t09A6377A54BE2F9E6985A8149F19234FD7DDFE22_m1BB764DB4D3E393C60E69169020A7EC792D639D5 (ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* ___0_args, const RuntimeMethod* method)
{
	return ((  String_t* (*) (ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918*, const RuntimeMethod*))_AndroidJNIHelper_GetSignature_TisBoolean_t09A6377A54BE2F9E6985A8149F19234FD7DDFE22_m1BB764DB4D3E393C60E69169020A7EC792D639D5_gshared)(___0_args, method);
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR intptr_t AndroidJNIHelper_GetMethodID_mDB705DC228B1BB30E6595068797FB3F2A1817BB8 (intptr_t ___0_javaClass, String_t* ___1_methodName, String_t* ___2_signature, bool ___3_isStatic, const RuntimeMethod* method) ;
inline String_t* _AndroidJNIHelper_GetSignature_TisChar_t521A6F19B456D956AF452D926C32709DC03D6B17_mD783834059E75BFC7A7FEB544B6ABA307E91B2C4 (ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* ___0_args, const RuntimeMethod* method)
{
	return ((  String_t* (*) (ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918*, const RuntimeMethod*))_AndroidJNIHelper_GetSignature_TisChar_t521A6F19B456D956AF452D926C32709DC03D6B17_mD783834059E75BFC7A7FEB544B6ABA307E91B2C4_gshared)(___0_args, method);
}
inline String_t* _AndroidJNIHelper_GetSignature_TisDouble_tE150EF3D1D43DEE85D533810AB4C742307EEDE5F_m74C4D07DCE96BE5E61ED2AAED270DF7469C5F341 (ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* ___0_args, const RuntimeMethod* method)
{
	return ((  String_t* (*) (ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918*, const RuntimeMethod*))_AndroidJNIHelper_GetSignature_TisDouble_tE150EF3D1D43DEE85D533810AB4C742307EEDE5F_m74C4D07DCE96BE5E61ED2AAED270DF7469C5F341_gshared)(___0_args, method);
}
inline String_t* _AndroidJNIHelper_GetSignature_TisInt16_tB8EF286A9C33492FA6E6D6E67320BE93E794A175_m1E079B67FDC93E1BBE5C29D9C2BC09338DA0A5AA (ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* ___0_args, const RuntimeMethod* method)
{
	return ((  String_t* (*) (ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918*, const RuntimeMethod*))_AndroidJNIHelper_GetSignature_TisInt16_tB8EF286A9C33492FA6E6D6E67320BE93E794A175_m1E079B67FDC93E1BBE5C29D9C2BC09338DA0A5AA_gshared)(___0_args, method);
}
inline String_t* _AndroidJNIHelper_GetSignature_TisInt32_t680FF22E76F6EFAD4375103CBBFFA0421349384C_mA85CEF9411BD97B51F86CC460B32C46C2B873B12 (ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* ___0_args, const RuntimeMethod* method)
{
	return ((  String_t* (*) (ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918*, const RuntimeMethod*))_AndroidJNIHelper_GetSignature_TisInt32_t680FF22E76F6EFAD4375103CBBFFA0421349384C_mA85CEF9411BD97B51F86CC460B32C46C2B873B12_gshared)(___0_args, method);
}
inline String_t* _AndroidJNIHelper_GetSignature_TisInt64_t092CFB123BE63C28ACDAF65C68F21A526050DBA3_m847042ADF26044DDB60469E1C3477EBBB1B55E11 (ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* ___0_args, const RuntimeMethod* method)
{
	return ((  String_t* (*) (ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918*, const RuntimeMethod*))_AndroidJNIHelper_GetSignature_TisInt64_t092CFB123BE63C28ACDAF65C68F21A526050DBA3_m847042ADF26044DDB60469E1C3477EBBB1B55E11_gshared)(___0_args, method);
}
inline String_t* _AndroidJNIHelper_GetSignature_TisRuntimeObject_m7CC50A493D0C6897ECB2692A7CEFB3A2CD3655A5 (ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* ___0_args, const RuntimeMethod* method)
{
	return ((  String_t* (*) (ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918*, const RuntimeMethod*))_AndroidJNIHelper_GetSignature_TisRuntimeObject_m7CC50A493D0C6897ECB2692A7CEFB3A2CD3655A5_gshared)(___0_args, method);
}
inline String_t* _AndroidJNIHelper_GetSignature_TisSByte_tFEFFEF5D2FEBF5207950AE6FAC150FC53B668DB5_mEAD40CF5E1A04E27AE3991DAB10ABB9EC6F37FBB (ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* ___0_args, const RuntimeMethod* method)
{
	return ((  String_t* (*) (ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918*, const RuntimeMethod*))_AndroidJNIHelper_GetSignature_TisSByte_tFEFFEF5D2FEBF5207950AE6FAC150FC53B668DB5_mEAD40CF5E1A04E27AE3991DAB10ABB9EC6F37FBB_gshared)(___0_args, method);
}
inline String_t* _AndroidJNIHelper_GetSignature_TisSingle_t4530F2FF86FCB0DC29F35385CA1BD21BE294761C_mDD367BE518367698F0093E97FCF201D89B5790CB (ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* ___0_args, const RuntimeMethod* method)
{
	return ((  String_t* (*) (ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918*, const RuntimeMethod*))_AndroidJNIHelper_GetSignature_TisSingle_t4530F2FF86FCB0DC29F35385CA1BD21BE294761C_mDD367BE518367698F0093E97FCF201D89B5790CB_gshared)(___0_args, method);
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR String_t* _AndroidJNIHelper_GetSignature_m414A7A6B98FB5565075E4C51F22C482F2BCEEF5F (RuntimeObject* ___0_obj, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR String_t* String_Concat_m9E3155FB84015C823606188F53B47CB44C444991 (String_t* ___0_str0, String_t* ___1_str1, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void StringBuilder__ctor_m1D99713357DE05DAFA296633639DB55F8C30587D (StringBuilder_t* __this, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR StringBuilder_t* StringBuilder_Append_m71228B30F05724CD2CD96D9611DCD61BFB96A6E1 (StringBuilder_t* __this, Il2CppChar ___0_value, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR StringBuilder_t* StringBuilder_Append_m08904D74E0C78E5F36DCD9C9303BDD07886D9F7D (StringBuilder_t* __this, String_t* ___0_value, const RuntimeMethod* method) ;
inline bool ExpressionEvaluator_EvaluateTokens_TisDouble_tE150EF3D1D43DEE85D533810AB4C742307EEDE5F_m791767867653D0CCE2BEFF83F336A41B5B3A718E (StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* ___0_tokens, double* ___1_value, int32_t ___2_index, int32_t ___3_count, const RuntimeMethod* method)
{
	return ((  bool (*) (StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248*, double*, int32_t, int32_t, const RuntimeMethod*))ExpressionEvaluator_EvaluateTokens_TisDouble_tE150EF3D1D43DEE85D533810AB4C742307EEDE5F_m791767867653D0CCE2BEFF83F336A41B5B3A718E_gshared)(___0_tokens, ___1_value, ___2_index, ___3_count, method);
}
inline bool ExpressionEvaluator_EvaluateTokens_TisInt64_t092CFB123BE63C28ACDAF65C68F21A526050DBA3_m7418F7A8835B2770EF83F1D52F2723897CD76DEB (StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* ___0_tokens, int64_t* ___1_value, int32_t ___2_index, int32_t ___3_count, const RuntimeMethod* method)
{
	return ((  bool (*) (StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248*, int64_t*, int32_t, int32_t, const RuntimeMethod*))ExpressionEvaluator_EvaluateTokens_TisInt64_t092CFB123BE63C28ACDAF65C68F21A526050DBA3_m7418F7A8835B2770EF83F1D52F2723897CD76DEB_gshared)(___0_tokens, ___1_value, ___2_index, ___3_count, method);
}
inline bool ExpressionEvaluator_EvaluateTokens_TisUInt64_t8F12534CC8FC4B5860F2A2CD1EE79D322E7A41AF_mCFCF758DECB276DBCB0A8B83BAE195EF3B974780 (StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* ___0_tokens, uint64_t* ___1_value, int32_t ___2_index, int32_t ___3_count, const RuntimeMethod* method)
{
	return ((  bool (*) (StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248*, uint64_t*, int32_t, int32_t, const RuntimeMethod*))ExpressionEvaluator_EvaluateTokens_TisUInt64_t8F12534CC8FC4B5860F2A2CD1EE79D322E7A41AF_mCFCF758DECB276DBCB0A8B83BAE195EF3B974780_gshared)(___0_tokens, ___1_value, ___2_index, ___3_count, method);
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void Assert_IsTrue_mE42C53B7220324D1FBAFB7AE48A7D8DD7796A663 (bool ___0_condition, const RuntimeMethod* method) ;
inline int32_t Func_3_Invoke_mE6CD106F59B0ADD2DF9C211DC4CF4088F5A1A4BB_inline (Func_3_tD46831209E6E19204CD8F9EAFC74DBFCA3C36C5F* __this, Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 ___0_arg1, Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 ___1_arg2, const RuntimeMethod* method)
{
	return ((  int32_t (*) (Func_3_tD46831209E6E19204CD8F9EAFC74DBFCA3C36C5F*, Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3, Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3, const RuntimeMethod*))Func_3_Invoke_mE6CD106F59B0ADD2DF9C211DC4CF4088F5A1A4BB_gshared_inline)(__this, ___0_arg1, ___1_arg2, method);
}
inline int32_t Func_3_Invoke_m2AED59BE1B0645C0DB5DAE117842A1C0AD4BDEBB_inline (Func_3_t3E644C82345CE04737DA5CDE018481FE0A88F821* __this, LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 ___0_arg1, LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 ___1_arg2, const RuntimeMethod* method)
{
	return ((  int32_t (*) (Func_3_t3E644C82345CE04737DA5CDE018481FE0A88F821*, LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2, LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2, const RuntimeMethod*))Func_3_Invoke_m2AED59BE1B0645C0DB5DAE117842A1C0AD4BDEBB_gshared_inline)(__this, ___0_arg1, ___1_arg2, method);
}
inline void Sorting_U3CMedian3PivotU3Eg__SwapU7C2_0_TisVector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3_m2B2B04012DE1B591C8E7AD4765ECB8EF3790F795 (int32_t ___0_a, int32_t ___1_b, U3CU3Ec__DisplayClass2_0_1_t41073816D00B5468033D7AA727FBFFB73E7C9BA2* ___2_p, const RuntimeMethod* method)
{
	((  void (*) (int32_t, int32_t, U3CU3Ec__DisplayClass2_0_1_t41073816D00B5468033D7AA727FBFFB73E7C9BA2*, const RuntimeMethod*))Sorting_U3CMedian3PivotU3Eg__SwapU7C2_0_TisVector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3_m2B2B04012DE1B591C8E7AD4765ECB8EF3790F795_gshared)(___0_a, ___1_b, ___2_p, method);
}
inline void Sorting_U3CMedian3PivotU3Eg__SwapU7C2_0_TisLightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2_m06FED96568508A808BFC2F0CB6D49F45194E6051 (int32_t ___0_a, int32_t ___1_b, U3CU3Ec__DisplayClass2_0_1_tC4E3D65CA470C2F2DB85D9B32B717BE3200D4597* ___2_p, const RuntimeMethod* method)
{
	((  void (*) (int32_t, int32_t, U3CU3Ec__DisplayClass2_0_1_tC4E3D65CA470C2F2DB85D9B32B717BE3200D4597*, const RuntimeMethod*))Sorting_U3CMedian3PivotU3Eg__SwapU7C2_0_TisLightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2_m06FED96568508A808BFC2F0CB6D49F45194E6051_gshared)(___0_a, ___1_b, ___2_p, method);
}
inline Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 Sorting_Median3Pivot_TisVector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3_m61A04EAD49649BB481C390575840F890DC1AD6D9 (Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* ___0_data, int32_t ___1_start, int32_t ___2_pivot, int32_t ___3_end, Func_3_tD46831209E6E19204CD8F9EAFC74DBFCA3C36C5F* ___4_compare, const RuntimeMethod* method)
{
	return ((  Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 (*) (Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD*, int32_t, int32_t, int32_t, Func_3_tD46831209E6E19204CD8F9EAFC74DBFCA3C36C5F*, const RuntimeMethod*))Sorting_Median3Pivot_TisVector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3_m61A04EAD49649BB481C390575840F890DC1AD6D9_gshared)(___0_data, ___1_start, ___2_pivot, ___3_end, ___4_compare, method);
}
inline LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 Sorting_Median3Pivot_TisLightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2_m3AE419868146FAEE6A59E9FA4E33484BFA9930B1 (LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* ___0_data, int32_t ___1_start, int32_t ___2_pivot, int32_t ___3_end, Func_3_t3E644C82345CE04737DA5CDE018481FE0A88F821* ___4_compare, const RuntimeMethod* method)
{
	return ((  LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 (*) (LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263*, int32_t, int32_t, int32_t, Func_3_t3E644C82345CE04737DA5CDE018481FE0A88F821*, const RuntimeMethod*))Sorting_Median3Pivot_TisLightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2_m3AE419868146FAEE6A59E9FA4E33484BFA9930B1_gshared)(___0_data, ___1_start, ___2_pivot, ___3_end, ___4_compare, method);
}
inline void Sorting_InsertionSort_TisVector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3_m6B06894C5FA146D1CCE7ECBC21F553F16F2E96F5 (Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* ___0_data, int32_t ___1_start, int32_t ___2_end, Func_3_tD46831209E6E19204CD8F9EAFC74DBFCA3C36C5F* ___3_compare, const RuntimeMethod* method)
{
	((  void (*) (Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD*, int32_t, int32_t, Func_3_tD46831209E6E19204CD8F9EAFC74DBFCA3C36C5F*, const RuntimeMethod*))Sorting_InsertionSort_TisVector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3_m6B06894C5FA146D1CCE7ECBC21F553F16F2E96F5_gshared)(___0_data, ___1_start, ___2_end, ___3_compare, method);
}
inline int32_t Sorting_Partition_TisVector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3_m5B1882A69C494B64F1EA761E21D0018C1D6AB6E8 (Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* ___0_data, int32_t ___1_start, int32_t ___2_end, Func_3_tD46831209E6E19204CD8F9EAFC74DBFCA3C36C5F* ___3_compare, const RuntimeMethod* method)
{
	return ((  int32_t (*) (Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD*, int32_t, int32_t, Func_3_tD46831209E6E19204CD8F9EAFC74DBFCA3C36C5F*, const RuntimeMethod*))Sorting_Partition_TisVector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3_m5B1882A69C494B64F1EA761E21D0018C1D6AB6E8_gshared)(___0_data, ___1_start, ___2_end, ___3_compare, method);
}
inline void Sorting_QuickSort_TisVector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3_mAA6CA24576E19917524BFD6BE7AC3ACF4A18B570 (Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* ___0_data, int32_t ___1_start, int32_t ___2_end, Func_3_tD46831209E6E19204CD8F9EAFC74DBFCA3C36C5F* ___3_compare, const RuntimeMethod* method)
{
	((  void (*) (Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD*, int32_t, int32_t, Func_3_tD46831209E6E19204CD8F9EAFC74DBFCA3C36C5F*, const RuntimeMethod*))Sorting_QuickSort_TisVector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3_mAA6CA24576E19917524BFD6BE7AC3ACF4A18B570_gshared)(___0_data, ___1_start, ___2_end, ___3_compare, method);
}
inline void Sorting_InsertionSort_TisLightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2_m50C92303E813A7BFD084FB309E5FB9937C8F2065 (LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* ___0_data, int32_t ___1_start, int32_t ___2_end, Func_3_t3E644C82345CE04737DA5CDE018481FE0A88F821* ___3_compare, const RuntimeMethod* method)
{
	((  void (*) (LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263*, int32_t, int32_t, Func_3_t3E644C82345CE04737DA5CDE018481FE0A88F821*, const RuntimeMethod*))Sorting_InsertionSort_TisLightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2_m50C92303E813A7BFD084FB309E5FB9937C8F2065_gshared)(___0_data, ___1_start, ___2_end, ___3_compare, method);
}
inline int32_t Sorting_Partition_TisLightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2_m0E79CA1E375645FFDF3E1506F789825A9A6D3D95 (LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* ___0_data, int32_t ___1_start, int32_t ___2_end, Func_3_t3E644C82345CE04737DA5CDE018481FE0A88F821* ___3_compare, const RuntimeMethod* method)
{
	return ((  int32_t (*) (LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263*, int32_t, int32_t, Func_3_t3E644C82345CE04737DA5CDE018481FE0A88F821*, const RuntimeMethod*))Sorting_Partition_TisLightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2_m0E79CA1E375645FFDF3E1506F789825A9A6D3D95_gshared)(___0_data, ___1_start, ___2_end, ___3_compare, method);
}
inline void Sorting_QuickSort_TisLightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2_mADD51465439832E9BCC31668A2DE42CFCCA07F9C (LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* ___0_data, int32_t ___1_start, int32_t ___2_end, Func_3_t3E644C82345CE04737DA5CDE018481FE0A88F821* ___3_compare, const RuntimeMethod* method)
{
	((  void (*) (LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263*, int32_t, int32_t, Func_3_t3E644C82345CE04737DA5CDE018481FE0A88F821*, const RuntimeMethod*))Sorting_QuickSort_TisLightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2_mADD51465439832E9BCC31668A2DE42CFCCA07F9C_gshared)(___0_data, ___1_start, ___2_end, ___3_compare, method);
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void ProbeReferenceVolume_UnregisterDebug_m29C8C2812597CC2D2B3FBD5CBD374E618C480187 (ProbeReferenceVolume_t05ED7EF2BB9B58F26CE1629F0AA773D14100695F* __this, bool ___0_destroyPanel, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void ProbeReferenceVolume_RegisterDebug_m2F302154AB36B9D5C1739DE3E699CF8574918F53 (ProbeReferenceVolume_t05ED7EF2BB9B58F26CE1629F0AA773D14100695F* __this, ProbeVolumeSystemParameters_t0654F2626ACA367E00C375BEB6FEA5B86CB0A58B ___0_parameters, const RuntimeMethod* method) ;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void ReceiptCodec_Name_mD9F23DCF6C1E464B6158DA93836EE05CE7738B08 (StringBuilder_t* ___0_json, String_t* ___1_name, const RuntimeMethod* method) ;
inline void Action_2_Invoke_mF1F80FA522B9327702466C4197420B39418278BD_inline (Action_2_t528DD1A0598C8661FA22AB60F7CEFBF784D3DA6B* __this, StringBuilder_t* ___0_arg1, RuntimeObject* ___1_arg2, const RuntimeMethod* method)
{
	((  void (*) (Action_2_t528DD1A0598C8661FA22AB60F7CEFBF784D3DA6B*, StringBuilder_t*, RuntimeObject*, const RuntimeMethod*))Action_2_Invoke_m7BFCE0BBCF67689D263059B56A8D79161B698587_gshared_inline)(__this, ___0_arg1, ___1_arg2, method);
}
inline int32_t DynamicArray_1_get_size_m56D2768863B15299FA4F2F14E271686207A8C2E4_inline (DynamicArray_1_t401F46C0081DE185BCAB1D30DE8D6B6DC9AA6AFB* __this, const RuntimeMethod* method)
{
	return ((  int32_t (*) (DynamicArray_1_t401F46C0081DE185BCAB1D30DE8D6B6DC9AA6AFB*, const RuntimeMethod*))DynamicArray_1_get_size_m1B00C20A8CC4D62269585D16A58425D3F258836F_gshared_inline)(__this, method);
}
inline void DynamicArray_1_Resize_mEEEB907EAEFD4C22DB449FF052CF6AC967A27AD1 (DynamicArray_1_t401F46C0081DE185BCAB1D30DE8D6B6DC9AA6AFB* __this, int32_t ___0_newSize, bool ___1_keepContent, const RuntimeMethod* method)
{
	((  void (*) (DynamicArray_1_t401F46C0081DE185BCAB1D30DE8D6B6DC9AA6AFB*, int32_t, bool, const RuntimeMethod*))DynamicArray_1_Resize_m3E24EB8A4A036B423BA304E8C3C94EBD0222822E_gshared)(__this, ___0_newSize, ___1_keepContent, method);
}
inline IRenderGraphResource_tF24653A388C17849844C128C19C7A6599C7ADB7D** DynamicArray_1_get_Item_m5FC9383C3A815B0DF7AAD4C2A5CDFB1A25586ECE (DynamicArray_1_t401F46C0081DE185BCAB1D30DE8D6B6DC9AA6AFB* __this, int32_t ___0_index, const RuntimeMethod* method)
{
	return ((  IRenderGraphResource_tF24653A388C17849844C128C19C7A6599C7ADB7D** (*) (DynamicArray_1_t401F46C0081DE185BCAB1D30DE8D6B6DC9AA6AFB*, int32_t, const RuntimeMethod*))DynamicArray_1_get_Item_m7DDF1E462D1484149A4D812CAD717F816205FD44_gshared)(__this, ___0_index, method);
}
inline RuntimeObject* Activator_CreateInstance_TisRuntimeObject_m62506836177F0F862A8D619638BF37F48721F138 (const RuntimeMethod* method)
{
	return ((  RuntimeObject* (*) (const RuntimeMethod*))Activator_CreateInstance_TisRuntimeObject_m62506836177F0F862A8D619638BF37F48721F138_gshared)(method);
}
inline RuntimeObject* TypeUtility_CreateTypeConstructor_TisBounds_t367E830C64BBF235ED8C3B2F8CF6254FDCAD39C3_m16C827D0F6107B7998F6C99B57F7CC2F181E2198 (const RuntimeMethod* method)
{
	return ((  RuntimeObject* (*) (const RuntimeMethod*))TypeUtility_CreateTypeConstructor_TisBounds_t367E830C64BBF235ED8C3B2F8CF6254FDCAD39C3_m16C827D0F6107B7998F6C99B57F7CC2F181E2198_gshared)(method);
}
inline RuntimeObject* TypeUtility_CreateTypeConstructor_TisBoundsInt_t4E757DE5EFF9FCB42000F173360DDC63B5585485_m8F344250A2F9E6EE6DDBA6BA833BB36D0F272B66 (const RuntimeMethod* method)
{
	return ((  RuntimeObject* (*) (const RuntimeMethod*))TypeUtility_CreateTypeConstructor_TisBoundsInt_t4E757DE5EFF9FCB42000F173360DDC63B5585485_m8F344250A2F9E6EE6DDBA6BA833BB36D0F272B66_gshared)(method);
}
inline RuntimeObject* TypeUtility_CreateTypeConstructor_TisColor_tD001788D726C3A7F1379BEED0260B9591F440C1F_mBBCB804F367E06EA4D482F1B69165DD2B5BF38FF (const RuntimeMethod* method)
{
	return ((  RuntimeObject* (*) (const RuntimeMethod*))TypeUtility_CreateTypeConstructor_TisColor_tD001788D726C3A7F1379BEED0260B9591F440C1F_mBBCB804F367E06EA4D482F1B69165DD2B5BF38FF_gshared)(method);
}
inline RuntimeObject* TypeUtility_CreateTypeConstructor_TisRuntimeObject_m4E17F588B090C1DADAE2D986BDA407DECEAC020F (const RuntimeMethod* method)
{
	return ((  RuntimeObject* (*) (const RuntimeMethod*))TypeUtility_CreateTypeConstructor_TisRuntimeObject_m4E17F588B090C1DADAE2D986BDA407DECEAC020F_gshared)(method);
}
inline RuntimeObject* TypeUtility_CreateTypeConstructor_TisRect_tA04E0F8A1830E767F40FB27ECD8D309303571F0D_m2C5F5CF80D13B041768C7845C5AAEEC02BB683BA (const RuntimeMethod* method)
{
	return ((  RuntimeObject* (*) (const RuntimeMethod*))TypeUtility_CreateTypeConstructor_TisRect_tA04E0F8A1830E767F40FB27ECD8D309303571F0D_m2C5F5CF80D13B041768C7845C5AAEEC02BB683BA_gshared)(method);
}
inline RuntimeObject* TypeUtility_CreateTypeConstructor_TisRectInt_t1744D10E1063135DA9D574F95205B98DAC600CB8_mF6949D9EDD480E6666CD975C66487AAD6ABC7D11 (const RuntimeMethod* method)
{
	return ((  RuntimeObject* (*) (const RuntimeMethod*))TypeUtility_CreateTypeConstructor_TisRectInt_t1744D10E1063135DA9D574F95205B98DAC600CB8_mF6949D9EDD480E6666CD975C66487AAD6ABC7D11_gshared)(method);
}
inline RuntimeObject* TypeUtility_CreateTypeConstructor_TisVector2_t1FD6F485C871E832B347AB2DC8CBA08B739D8DF7_mE0C65F4221E48BB07F75856972A0CCDAE284AB9F (const RuntimeMethod* method)
{
	return ((  RuntimeObject* (*) (const RuntimeMethod*))TypeUtility_CreateTypeConstructor_TisVector2_t1FD6F485C871E832B347AB2DC8CBA08B739D8DF7_mE0C65F4221E48BB07F75856972A0CCDAE284AB9F_gshared)(method);
}
inline RuntimeObject* TypeUtility_CreateTypeConstructor_TisVector2Int_t69B2886EBAB732D9B880565E18E7568F3DE0CE6A_mC8EF710494C8986B279262C6C64947BE2C1DC55C (const RuntimeMethod* method)
{
	return ((  RuntimeObject* (*) (const RuntimeMethod*))TypeUtility_CreateTypeConstructor_TisVector2Int_t69B2886EBAB732D9B880565E18E7568F3DE0CE6A_mC8EF710494C8986B279262C6C64947BE2C1DC55C_gshared)(method);
}
inline RuntimeObject* TypeUtility_CreateTypeConstructor_TisVector3_t24C512C7B96BBABAD472002D0BA2BDA40A5A80B2_m1AB8BF0921C24186B3C43FC4341AAD2F6FE87C4D (const RuntimeMethod* method)
{
	return ((  RuntimeObject* (*) (const RuntimeMethod*))TypeUtility_CreateTypeConstructor_TisVector3_t24C512C7B96BBABAD472002D0BA2BDA40A5A80B2_m1AB8BF0921C24186B3C43FC4341AAD2F6FE87C4D_gshared)(method);
}
inline RuntimeObject* TypeUtility_CreateTypeConstructor_TisVector3Int_t65CB06F557251D18A37BD71F3655BA836A357376_mB00220519A80AA5ACE36B7DBA2E6A6CB796302AF (const RuntimeMethod* method)
{
	return ((  RuntimeObject* (*) (const RuntimeMethod*))TypeUtility_CreateTypeConstructor_TisVector3Int_t65CB06F557251D18A37BD71F3655BA836A357376_mB00220519A80AA5ACE36B7DBA2E6A6CB796302AF_gshared)(method);
}
inline RuntimeObject* TypeUtility_CreateTypeConstructor_TisVector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3_mED1DC338E5DB62F3E64F6272A9F12150DA5CC1B9 (const RuntimeMethod* method)
{
	return ((  RuntimeObject* (*) (const RuntimeMethod*))TypeUtility_CreateTypeConstructor_TisVector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3_mED1DC338E5DB62F3E64F6272A9F12150DA5CC1B9_gshared)(method);
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR double _AndroidJNIHelper_ConvertFromJNIArray_TisDouble_tE150EF3D1D43DEE85D533810AB4C742307EEDE5F_m1F7F249CC7CDA2D6E136C627D983569B3674EA73_gshared (intptr_t ___0_array, const RuntimeMethod* method) 
{
	if (!il2cpp_rgctx_is_initialized(method))
	{
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&AndroidReflection_tD59014B286F902906DBB75DA3473897D35684908_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Boolean_t09A6377A54BE2F9E6985A8149F19234FD7DDFE22_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Byte_t94D9231AC217BE4D2E004C4CD32DF6D099EA41A3_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Char_t521A6F19B456D956AF452D926C32709DC03D6B17_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Debug_t8394C7EEAECA3689C2C9B9DE9C7166D73596276F_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Double_tE150EF3D1D43DEE85D533810AB4C742307EEDE5F_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Int16_tB8EF286A9C33492FA6E6D6E67320BE93E794A175_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Int32_t680FF22E76F6EFAD4375103CBBFFA0421349384C_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Int64_t092CFB123BE63C28ACDAF65C68F21A526050DBA3_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&SByte_tFEFFEF5D2FEBF5207950AE6FAC150FC53B668DB5_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Single_t4530F2FF86FCB0DC29F35385CA1BD21BE294761C_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&String_t_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Type_t_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&_stringLiteral24CC8D396132365E532646F936DFC8579E2299B2);
		il2cpp_rgctx_method_init(method);
	}
	Type_t* V_0 = NULL;
	bool V_1 = false;
	bool V_2 = false;
	double V_3 = 0.0;
	bool V_4 = false;
	bool V_5 = false;
	bool V_6 = false;
	bool V_7 = false;
	bool V_8 = false;
	bool V_9 = false;
	bool V_10 = false;
	bool V_11 = false;
	bool V_12 = false;
	int32_t V_13 = 0;
	StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* V_14 = NULL;
	int32_t V_15 = 0;
	intptr_t V_16;
	memset((&V_16), 0, sizeof(V_16));
	bool V_17 = false;
	bool V_18 = false;
	int32_t V_19 = 0;
	AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001* V_20 = NULL;
	int32_t V_21 = 0;
	intptr_t V_22;
	memset((&V_22), 0, sizeof(V_22));
	bool V_23 = false;
	double V_24 = 0.0;
	Type_t* G_B32_0 = NULL;
	String_t* G_B32_1 = NULL;
	Type_t* G_B31_0 = NULL;
	String_t* G_B31_1 = NULL;
	String_t* G_B33_0 = NULL;
	String_t* G_B33_1 = NULL;
	{
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_0 = { reinterpret_cast<intptr_t> (il2cpp_rgctx_type(method->rgctx_data, 0)) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_1;
		L_1 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_0, NULL);
		NullCheck(L_1);
		Type_t* L_2;
		L_2 = VirtualFuncInvoker0< Type_t* >::Invoke(45, L_1);
		V_0 = L_2;
		Type_t* L_3 = V_0;
		il2cpp_codegen_runtime_class_init_inline(AndroidReflection_tD59014B286F902906DBB75DA3473897D35684908_il2cpp_TypeInfo_var);
		bool L_4;
		L_4 = AndroidReflection_IsPrimitive_mA41A9ECECE3D73679C79DC8B0FDD32B59570DF25(L_3, NULL);
		V_1 = L_4;
		bool L_5 = V_1;
		if (!L_5)
		{
			goto IL_018e;
		}
	}
	{
		Type_t* L_6 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_7 = { reinterpret_cast<intptr_t> (Int32_t680FF22E76F6EFAD4375103CBBFFA0421349384C_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_8;
		L_8 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_7, NULL);
		bool L_9;
		L_9 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_6, L_8, NULL);
		V_2 = L_9;
		bool L_10 = V_2;
		if (!L_10)
		{
			goto IL_0044;
		}
	}
	{
		intptr_t L_11 = ___0_array;
		Int32U5BU5D_t19C97395396A72ECAF310612F0760F165060314C* L_12;
		L_12 = AndroidJNISafe_FromIntArray_mC4C4DC70FFA39CD6E3E02FDAC7192324E6D4614E(L_11, NULL);
		V_3 = ((*(double*)((double*)(double*)UnBox((RuntimeObject*)L_12, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_0044:
	{
		Type_t* L_13 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_14 = { reinterpret_cast<intptr_t> (Boolean_t09A6377A54BE2F9E6985A8149F19234FD7DDFE22_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_15;
		L_15 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_14, NULL);
		bool L_16;
		L_16 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_13, L_15, NULL);
		V_4 = L_16;
		bool L_17 = V_4;
		if (!L_17)
		{
			goto IL_006b;
		}
	}
	{
		intptr_t L_18 = ___0_array;
		BooleanU5BU5D_tD317D27C31DB892BE79FAE3AEBC0B3FFB73DE9B4* L_19;
		L_19 = AndroidJNISafe_FromBooleanArray_m36ED740401185EC0A959CA0F96A324A69E668646(L_18, NULL);
		V_3 = ((*(double*)((double*)(double*)UnBox((RuntimeObject*)L_19, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_006b:
	{
		Type_t* L_20 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_21 = { reinterpret_cast<intptr_t> (Byte_t94D9231AC217BE4D2E004C4CD32DF6D099EA41A3_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_22;
		L_22 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_21, NULL);
		bool L_23;
		L_23 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_20, L_22, NULL);
		V_5 = L_23;
		bool L_24 = V_5;
		if (!L_24)
		{
			goto IL_009e;
		}
	}
	{
		il2cpp_codegen_runtime_class_init_inline(Debug_t8394C7EEAECA3689C2C9B9DE9C7166D73596276F_il2cpp_TypeInfo_var);
		Debug_LogWarning_m33EF1B897E0C7C6FF538989610BFAFFEF4628CA9((RuntimeObject*)_stringLiteral24CC8D396132365E532646F936DFC8579E2299B2, NULL);
		intptr_t L_25 = ___0_array;
		ByteU5BU5D_tA6237BF417AE52AD70CFB4EF24A7A82613DF9031* L_26;
		L_26 = AndroidJNISafe_FromByteArray_mB06EF0FDBF6C738231E8F9D4998C38551131C4C5(L_25, NULL);
		V_3 = ((*(double*)((double*)(double*)UnBox((RuntimeObject*)L_26, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_009e:
	{
		Type_t* L_27 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_28 = { reinterpret_cast<intptr_t> (SByte_tFEFFEF5D2FEBF5207950AE6FAC150FC53B668DB5_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_29;
		L_29 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_28, NULL);
		bool L_30;
		L_30 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_27, L_29, NULL);
		V_6 = L_30;
		bool L_31 = V_6;
		if (!L_31)
		{
			goto IL_00c5;
		}
	}
	{
		intptr_t L_32 = ___0_array;
		SByteU5BU5D_t88116DA68378C3333DB73E7D36C1A06AFAA91913* L_33;
		L_33 = AndroidJNISafe_FromSByteArray_m261D638D8B059AB777BEF0BEFDD0822717DFF2B1(L_32, NULL);
		V_3 = ((*(double*)((double*)(double*)UnBox((RuntimeObject*)L_33, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_00c5:
	{
		Type_t* L_34 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_35 = { reinterpret_cast<intptr_t> (Int16_tB8EF286A9C33492FA6E6D6E67320BE93E794A175_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_36;
		L_36 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_35, NULL);
		bool L_37;
		L_37 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_34, L_36, NULL);
		V_7 = L_37;
		bool L_38 = V_7;
		if (!L_38)
		{
			goto IL_00ec;
		}
	}
	{
		intptr_t L_39 = ___0_array;
		Int16U5BU5D_t8175CE8DD9C9F9FB0CF4F58E45BC570575B43CFB* L_40;
		L_40 = AndroidJNISafe_FromShortArray_m62C0CB2D0BAE96D4B8CE365630361150EBE884FC(L_39, NULL);
		V_3 = ((*(double*)((double*)(double*)UnBox((RuntimeObject*)L_40, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_00ec:
	{
		Type_t* L_41 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_42 = { reinterpret_cast<intptr_t> (Int64_t092CFB123BE63C28ACDAF65C68F21A526050DBA3_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_43;
		L_43 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_42, NULL);
		bool L_44;
		L_44 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_41, L_43, NULL);
		V_8 = L_44;
		bool L_45 = V_8;
		if (!L_45)
		{
			goto IL_0113;
		}
	}
	{
		intptr_t L_46 = ___0_array;
		Int64U5BU5D_tAEDFCBDB5414E2A140A6F34C0538BF97FCF67A1D* L_47;
		L_47 = AndroidJNISafe_FromLongArray_mC4D73C0DA27F212947AB85AA2030A35BECDF8288(L_46, NULL);
		V_3 = ((*(double*)((double*)(double*)UnBox((RuntimeObject*)L_47, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_0113:
	{
		Type_t* L_48 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_49 = { reinterpret_cast<intptr_t> (Single_t4530F2FF86FCB0DC29F35385CA1BD21BE294761C_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_50;
		L_50 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_49, NULL);
		bool L_51;
		L_51 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_48, L_50, NULL);
		V_9 = L_51;
		bool L_52 = V_9;
		if (!L_52)
		{
			goto IL_013a;
		}
	}
	{
		intptr_t L_53 = ___0_array;
		SingleU5BU5D_t89DEFE97BCEDB5857010E79ECE0F52CF6E93B87C* L_54;
		L_54 = AndroidJNISafe_FromFloatArray_mDE02985159EEFD2CB28611C797AC21DE8B6300B8(L_53, NULL);
		V_3 = ((*(double*)((double*)(double*)UnBox((RuntimeObject*)L_54, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_013a:
	{
		Type_t* L_55 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_56 = { reinterpret_cast<intptr_t> (Double_tE150EF3D1D43DEE85D533810AB4C742307EEDE5F_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_57;
		L_57 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_56, NULL);
		bool L_58;
		L_58 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_55, L_57, NULL);
		V_10 = L_58;
		bool L_59 = V_10;
		if (!L_59)
		{
			goto IL_0161;
		}
	}
	{
		intptr_t L_60 = ___0_array;
		DoubleU5BU5D_tCC308475BD3B8229DB2582938669EF2F9ECC1FEE* L_61;
		L_61 = AndroidJNISafe_FromDoubleArray_mDEA8F2C7854101272F3A2733F351B570AAD5D9D9(L_60, NULL);
		V_3 = ((*(double*)((double*)(double*)UnBox((RuntimeObject*)L_61, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_0161:
	{
		Type_t* L_62 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_63 = { reinterpret_cast<intptr_t> (Char_t521A6F19B456D956AF452D926C32709DC03D6B17_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_64;
		L_64 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_63, NULL);
		bool L_65;
		L_65 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_62, L_64, NULL);
		V_11 = L_65;
		bool L_66 = V_11;
		if (!L_66)
		{
			goto IL_0188;
		}
	}
	{
		intptr_t L_67 = ___0_array;
		CharU5BU5D_t799905CF001DD5F13F7DBB310181FC4D8B7D0AAB* L_68;
		L_68 = AndroidJNISafe_FromCharArray_m54EDC9D2BE92F9973F4E00EE953EE242B231EA96(L_67, NULL);
		V_3 = ((*(double*)((double*)(double*)UnBox((RuntimeObject*)L_68, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_0188:
	{
		goto IL_0286;
	}

IL_018e:
	{
		Type_t* L_69 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_70 = { reinterpret_cast<intptr_t> (String_t_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_71;
		L_71 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_70, NULL);
		bool L_72;
		L_72 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_69, L_71, NULL);
		V_12 = L_72;
		bool L_73 = V_12;
		if (!L_73)
		{
			goto IL_01fa;
		}
	}
	{
		intptr_t L_74 = ___0_array;
		int32_t L_75;
		L_75 = AndroidJNISafe_GetArrayLength_m809419F04C9BB93FED5B4A89F0539231C9B90E6F(L_74, NULL);
		V_13 = L_75;
		int32_t L_76 = V_13;
		StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* L_77 = (StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248*)(StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248*)SZArrayNew(StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248_il2cpp_TypeInfo_var, (uint32_t)L_76);
		V_14 = L_77;
		V_15 = 0;
		goto IL_01e1;
	}

IL_01bb:
	{
		intptr_t L_78 = ___0_array;
		int32_t L_79 = V_15;
		intptr_t L_80;
		L_80 = AndroidJNI_GetObjectArrayElement_mC4CAF9744617F69EFCD95B71D95492DA20A0FACE(L_78, L_79, NULL);
		V_16 = L_80;
		StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* L_81 = V_14;
		int32_t L_82 = V_15;
		intptr_t L_83 = V_16;
		String_t* L_84;
		L_84 = AndroidJNISafe_GetStringChars_mE246814CD8FF4EDDEE6EBF107367C4A8EAF03849(L_83, NULL);
		NullCheck(L_81);
		(L_81)->SetAt(static_cast<il2cpp_array_size_t>(L_82), (String_t*)L_84);
		intptr_t L_85 = V_16;
		AndroidJNISafe_DeleteLocalRef_m20303564C88A1B90E3D8D7A7D893392E18967094(L_85, NULL);
		int32_t L_86 = V_15;
		V_15 = ((int32_t)il2cpp_codegen_add(L_86, 1));
	}

IL_01e1:
	{
		int32_t L_87 = V_15;
		int32_t L_88 = V_13;
		V_17 = (bool)((((int32_t)L_87) < ((int32_t)L_88))? 1 : 0);
		bool L_89 = V_17;
		if (L_89)
		{
			goto IL_01bb;
		}
	}
	{
		StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* L_90 = V_14;
		V_3 = ((*(double*)((double*)(double*)UnBox((RuntimeObject*)L_90, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_01fa:
	{
		Type_t* L_91 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_92 = { reinterpret_cast<intptr_t> (AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_93;
		L_93 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_92, NULL);
		bool L_94;
		L_94 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_91, L_93, NULL);
		V_18 = L_94;
		bool L_95 = V_18;
		if (!L_95)
		{
			goto IL_0263;
		}
	}
	{
		intptr_t L_96 = ___0_array;
		int32_t L_97;
		L_97 = AndroidJNISafe_GetArrayLength_m809419F04C9BB93FED5B4A89F0539231C9B90E6F(L_96, NULL);
		V_19 = L_97;
		int32_t L_98 = V_19;
		AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001* L_99 = (AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001*)(AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001*)SZArrayNew(AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001_il2cpp_TypeInfo_var, (uint32_t)L_98);
		V_20 = L_99;
		V_21 = 0;
		goto IL_024d;
	}

IL_0227:
	{
		intptr_t L_100 = ___0_array;
		int32_t L_101 = V_21;
		intptr_t L_102;
		L_102 = AndroidJNI_GetObjectArrayElement_mC4CAF9744617F69EFCD95B71D95492DA20A0FACE(L_100, L_101, NULL);
		V_22 = L_102;
		AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001* L_103 = V_20;
		int32_t L_104 = V_21;
		intptr_t L_105 = V_22;
		AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0* L_106 = (AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0*)il2cpp_codegen_object_new(AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0_il2cpp_TypeInfo_var);
		AndroidJavaObject__ctor_m0CEE7D570807333CE2C193A82AB3AB8D4F873A6B(L_106, L_105, NULL);
		NullCheck(L_103);
		ArrayElementTypeCheck (L_103, L_106);
		(L_103)->SetAt(static_cast<il2cpp_array_size_t>(L_104), (AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0*)L_106);
		intptr_t L_107 = V_22;
		AndroidJNISafe_DeleteLocalRef_m20303564C88A1B90E3D8D7A7D893392E18967094(L_107, NULL);
		int32_t L_108 = V_21;
		V_21 = ((int32_t)il2cpp_codegen_add(L_108, 1));
	}

IL_024d:
	{
		int32_t L_109 = V_21;
		int32_t L_110 = V_19;
		V_23 = (bool)((((int32_t)L_109) < ((int32_t)L_110))? 1 : 0);
		bool L_111 = V_23;
		if (L_111)
		{
			goto IL_0227;
		}
	}
	{
		AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001* L_112 = V_20;
		V_3 = ((*(double*)((double*)(double*)UnBox((RuntimeObject*)L_112, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_0263:
	{
		Type_t* L_113 = V_0;
		Type_t* L_114 = L_113;
		if (L_114)
		{
			G_B32_0 = L_114;
			G_B32_1 = ((String_t*)il2cpp_codegen_initialize_runtime_metadata_inline((uintptr_t*)&_stringLiteral51253131B895C2F8066BCC47E62D44F18F43446C));
			goto IL_0271;
		}
		G_B31_0 = L_114;
		G_B31_1 = ((String_t*)il2cpp_codegen_initialize_runtime_metadata_inline((uintptr_t*)&_stringLiteral51253131B895C2F8066BCC47E62D44F18F43446C));
	}
	{
		G_B33_0 = ((String_t*)(NULL));
		G_B33_1 = G_B31_1;
		goto IL_0276;
	}

IL_0271:
	{
		NullCheck((RuntimeObject*)G_B32_0);
		String_t* L_115;
		L_115 = VirtualFuncInvoker0< String_t* >::Invoke(3, (RuntimeObject*)G_B32_0);
		G_B33_0 = L_115;
		G_B33_1 = G_B32_1;
	}

IL_0276:
	{
		String_t* L_116;
		L_116 = String_Concat_m8855A6DE10F84DA7F4EC113CADDB59873A25573B(G_B33_1, G_B33_0, ((String_t*)il2cpp_codegen_initialize_runtime_metadata_inline((uintptr_t*)&_stringLiteral42646B33B50B6AA15E22733C8900716F0FE19E1D)), NULL);
		Exception_t* L_117 = (Exception_t*)il2cpp_codegen_object_new(((RuntimeClass*)il2cpp_codegen_initialize_runtime_metadata_inline((uintptr_t*)&Exception_t_il2cpp_TypeInfo_var)));
		Exception__ctor_m9B2BD92CD68916245A75109105D9071C9D430E7F(L_117, L_116, NULL);
		IL2CPP_RAISE_MANAGED_EXCEPTION(L_117, method);
	}

IL_0286:
	{
		il2cpp_codegen_initobj((&V_24), sizeof(double));
		double L_118 = V_24;
		V_3 = L_118;
		goto IL_0293;
	}

IL_0293:
	{
		double L_119 = V_3;
		return L_119;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR int16_t _AndroidJNIHelper_ConvertFromJNIArray_TisInt16_tB8EF286A9C33492FA6E6D6E67320BE93E794A175_m901F767E3189385BB47B5B021C40507AAF67D477_gshared (intptr_t ___0_array, const RuntimeMethod* method) 
{
	if (!il2cpp_rgctx_is_initialized(method))
	{
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&AndroidReflection_tD59014B286F902906DBB75DA3473897D35684908_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Boolean_t09A6377A54BE2F9E6985A8149F19234FD7DDFE22_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Byte_t94D9231AC217BE4D2E004C4CD32DF6D099EA41A3_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Char_t521A6F19B456D956AF452D926C32709DC03D6B17_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Debug_t8394C7EEAECA3689C2C9B9DE9C7166D73596276F_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Double_tE150EF3D1D43DEE85D533810AB4C742307EEDE5F_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Int16_tB8EF286A9C33492FA6E6D6E67320BE93E794A175_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Int32_t680FF22E76F6EFAD4375103CBBFFA0421349384C_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Int64_t092CFB123BE63C28ACDAF65C68F21A526050DBA3_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&SByte_tFEFFEF5D2FEBF5207950AE6FAC150FC53B668DB5_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Single_t4530F2FF86FCB0DC29F35385CA1BD21BE294761C_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&String_t_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Type_t_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&_stringLiteral24CC8D396132365E532646F936DFC8579E2299B2);
		il2cpp_rgctx_method_init(method);
	}
	Type_t* V_0 = NULL;
	bool V_1 = false;
	bool V_2 = false;
	int16_t V_3 = 0;
	bool V_4 = false;
	bool V_5 = false;
	bool V_6 = false;
	bool V_7 = false;
	bool V_8 = false;
	bool V_9 = false;
	bool V_10 = false;
	bool V_11 = false;
	bool V_12 = false;
	int32_t V_13 = 0;
	StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* V_14 = NULL;
	int32_t V_15 = 0;
	intptr_t V_16;
	memset((&V_16), 0, sizeof(V_16));
	bool V_17 = false;
	bool V_18 = false;
	int32_t V_19 = 0;
	AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001* V_20 = NULL;
	int32_t V_21 = 0;
	intptr_t V_22;
	memset((&V_22), 0, sizeof(V_22));
	bool V_23 = false;
	int16_t V_24 = 0;
	Type_t* G_B32_0 = NULL;
	String_t* G_B32_1 = NULL;
	Type_t* G_B31_0 = NULL;
	String_t* G_B31_1 = NULL;
	String_t* G_B33_0 = NULL;
	String_t* G_B33_1 = NULL;
	{
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_0 = { reinterpret_cast<intptr_t> (il2cpp_rgctx_type(method->rgctx_data, 0)) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_1;
		L_1 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_0, NULL);
		NullCheck(L_1);
		Type_t* L_2;
		L_2 = VirtualFuncInvoker0< Type_t* >::Invoke(45, L_1);
		V_0 = L_2;
		Type_t* L_3 = V_0;
		il2cpp_codegen_runtime_class_init_inline(AndroidReflection_tD59014B286F902906DBB75DA3473897D35684908_il2cpp_TypeInfo_var);
		bool L_4;
		L_4 = AndroidReflection_IsPrimitive_mA41A9ECECE3D73679C79DC8B0FDD32B59570DF25(L_3, NULL);
		V_1 = L_4;
		bool L_5 = V_1;
		if (!L_5)
		{
			goto IL_018e;
		}
	}
	{
		Type_t* L_6 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_7 = { reinterpret_cast<intptr_t> (Int32_t680FF22E76F6EFAD4375103CBBFFA0421349384C_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_8;
		L_8 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_7, NULL);
		bool L_9;
		L_9 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_6, L_8, NULL);
		V_2 = L_9;
		bool L_10 = V_2;
		if (!L_10)
		{
			goto IL_0044;
		}
	}
	{
		intptr_t L_11 = ___0_array;
		Int32U5BU5D_t19C97395396A72ECAF310612F0760F165060314C* L_12;
		L_12 = AndroidJNISafe_FromIntArray_mC4C4DC70FFA39CD6E3E02FDAC7192324E6D4614E(L_11, NULL);
		V_3 = ((*(int16_t*)((int16_t*)(int16_t*)UnBox((RuntimeObject*)L_12, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_0044:
	{
		Type_t* L_13 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_14 = { reinterpret_cast<intptr_t> (Boolean_t09A6377A54BE2F9E6985A8149F19234FD7DDFE22_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_15;
		L_15 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_14, NULL);
		bool L_16;
		L_16 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_13, L_15, NULL);
		V_4 = L_16;
		bool L_17 = V_4;
		if (!L_17)
		{
			goto IL_006b;
		}
	}
	{
		intptr_t L_18 = ___0_array;
		BooleanU5BU5D_tD317D27C31DB892BE79FAE3AEBC0B3FFB73DE9B4* L_19;
		L_19 = AndroidJNISafe_FromBooleanArray_m36ED740401185EC0A959CA0F96A324A69E668646(L_18, NULL);
		V_3 = ((*(int16_t*)((int16_t*)(int16_t*)UnBox((RuntimeObject*)L_19, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_006b:
	{
		Type_t* L_20 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_21 = { reinterpret_cast<intptr_t> (Byte_t94D9231AC217BE4D2E004C4CD32DF6D099EA41A3_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_22;
		L_22 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_21, NULL);
		bool L_23;
		L_23 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_20, L_22, NULL);
		V_5 = L_23;
		bool L_24 = V_5;
		if (!L_24)
		{
			goto IL_009e;
		}
	}
	{
		il2cpp_codegen_runtime_class_init_inline(Debug_t8394C7EEAECA3689C2C9B9DE9C7166D73596276F_il2cpp_TypeInfo_var);
		Debug_LogWarning_m33EF1B897E0C7C6FF538989610BFAFFEF4628CA9((RuntimeObject*)_stringLiteral24CC8D396132365E532646F936DFC8579E2299B2, NULL);
		intptr_t L_25 = ___0_array;
		ByteU5BU5D_tA6237BF417AE52AD70CFB4EF24A7A82613DF9031* L_26;
		L_26 = AndroidJNISafe_FromByteArray_mB06EF0FDBF6C738231E8F9D4998C38551131C4C5(L_25, NULL);
		V_3 = ((*(int16_t*)((int16_t*)(int16_t*)UnBox((RuntimeObject*)L_26, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_009e:
	{
		Type_t* L_27 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_28 = { reinterpret_cast<intptr_t> (SByte_tFEFFEF5D2FEBF5207950AE6FAC150FC53B668DB5_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_29;
		L_29 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_28, NULL);
		bool L_30;
		L_30 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_27, L_29, NULL);
		V_6 = L_30;
		bool L_31 = V_6;
		if (!L_31)
		{
			goto IL_00c5;
		}
	}
	{
		intptr_t L_32 = ___0_array;
		SByteU5BU5D_t88116DA68378C3333DB73E7D36C1A06AFAA91913* L_33;
		L_33 = AndroidJNISafe_FromSByteArray_m261D638D8B059AB777BEF0BEFDD0822717DFF2B1(L_32, NULL);
		V_3 = ((*(int16_t*)((int16_t*)(int16_t*)UnBox((RuntimeObject*)L_33, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_00c5:
	{
		Type_t* L_34 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_35 = { reinterpret_cast<intptr_t> (Int16_tB8EF286A9C33492FA6E6D6E67320BE93E794A175_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_36;
		L_36 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_35, NULL);
		bool L_37;
		L_37 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_34, L_36, NULL);
		V_7 = L_37;
		bool L_38 = V_7;
		if (!L_38)
		{
			goto IL_00ec;
		}
	}
	{
		intptr_t L_39 = ___0_array;
		Int16U5BU5D_t8175CE8DD9C9F9FB0CF4F58E45BC570575B43CFB* L_40;
		L_40 = AndroidJNISafe_FromShortArray_m62C0CB2D0BAE96D4B8CE365630361150EBE884FC(L_39, NULL);
		V_3 = ((*(int16_t*)((int16_t*)(int16_t*)UnBox((RuntimeObject*)L_40, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_00ec:
	{
		Type_t* L_41 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_42 = { reinterpret_cast<intptr_t> (Int64_t092CFB123BE63C28ACDAF65C68F21A526050DBA3_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_43;
		L_43 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_42, NULL);
		bool L_44;
		L_44 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_41, L_43, NULL);
		V_8 = L_44;
		bool L_45 = V_8;
		if (!L_45)
		{
			goto IL_0113;
		}
	}
	{
		intptr_t L_46 = ___0_array;
		Int64U5BU5D_tAEDFCBDB5414E2A140A6F34C0538BF97FCF67A1D* L_47;
		L_47 = AndroidJNISafe_FromLongArray_mC4D73C0DA27F212947AB85AA2030A35BECDF8288(L_46, NULL);
		V_3 = ((*(int16_t*)((int16_t*)(int16_t*)UnBox((RuntimeObject*)L_47, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_0113:
	{
		Type_t* L_48 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_49 = { reinterpret_cast<intptr_t> (Single_t4530F2FF86FCB0DC29F35385CA1BD21BE294761C_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_50;
		L_50 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_49, NULL);
		bool L_51;
		L_51 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_48, L_50, NULL);
		V_9 = L_51;
		bool L_52 = V_9;
		if (!L_52)
		{
			goto IL_013a;
		}
	}
	{
		intptr_t L_53 = ___0_array;
		SingleU5BU5D_t89DEFE97BCEDB5857010E79ECE0F52CF6E93B87C* L_54;
		L_54 = AndroidJNISafe_FromFloatArray_mDE02985159EEFD2CB28611C797AC21DE8B6300B8(L_53, NULL);
		V_3 = ((*(int16_t*)((int16_t*)(int16_t*)UnBox((RuntimeObject*)L_54, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_013a:
	{
		Type_t* L_55 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_56 = { reinterpret_cast<intptr_t> (Double_tE150EF3D1D43DEE85D533810AB4C742307EEDE5F_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_57;
		L_57 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_56, NULL);
		bool L_58;
		L_58 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_55, L_57, NULL);
		V_10 = L_58;
		bool L_59 = V_10;
		if (!L_59)
		{
			goto IL_0161;
		}
	}
	{
		intptr_t L_60 = ___0_array;
		DoubleU5BU5D_tCC308475BD3B8229DB2582938669EF2F9ECC1FEE* L_61;
		L_61 = AndroidJNISafe_FromDoubleArray_mDEA8F2C7854101272F3A2733F351B570AAD5D9D9(L_60, NULL);
		V_3 = ((*(int16_t*)((int16_t*)(int16_t*)UnBox((RuntimeObject*)L_61, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_0161:
	{
		Type_t* L_62 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_63 = { reinterpret_cast<intptr_t> (Char_t521A6F19B456D956AF452D926C32709DC03D6B17_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_64;
		L_64 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_63, NULL);
		bool L_65;
		L_65 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_62, L_64, NULL);
		V_11 = L_65;
		bool L_66 = V_11;
		if (!L_66)
		{
			goto IL_0188;
		}
	}
	{
		intptr_t L_67 = ___0_array;
		CharU5BU5D_t799905CF001DD5F13F7DBB310181FC4D8B7D0AAB* L_68;
		L_68 = AndroidJNISafe_FromCharArray_m54EDC9D2BE92F9973F4E00EE953EE242B231EA96(L_67, NULL);
		V_3 = ((*(int16_t*)((int16_t*)(int16_t*)UnBox((RuntimeObject*)L_68, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_0188:
	{
		goto IL_0286;
	}

IL_018e:
	{
		Type_t* L_69 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_70 = { reinterpret_cast<intptr_t> (String_t_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_71;
		L_71 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_70, NULL);
		bool L_72;
		L_72 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_69, L_71, NULL);
		V_12 = L_72;
		bool L_73 = V_12;
		if (!L_73)
		{
			goto IL_01fa;
		}
	}
	{
		intptr_t L_74 = ___0_array;
		int32_t L_75;
		L_75 = AndroidJNISafe_GetArrayLength_m809419F04C9BB93FED5B4A89F0539231C9B90E6F(L_74, NULL);
		V_13 = L_75;
		int32_t L_76 = V_13;
		StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* L_77 = (StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248*)(StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248*)SZArrayNew(StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248_il2cpp_TypeInfo_var, (uint32_t)L_76);
		V_14 = L_77;
		V_15 = 0;
		goto IL_01e1;
	}

IL_01bb:
	{
		intptr_t L_78 = ___0_array;
		int32_t L_79 = V_15;
		intptr_t L_80;
		L_80 = AndroidJNI_GetObjectArrayElement_mC4CAF9744617F69EFCD95B71D95492DA20A0FACE(L_78, L_79, NULL);
		V_16 = L_80;
		StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* L_81 = V_14;
		int32_t L_82 = V_15;
		intptr_t L_83 = V_16;
		String_t* L_84;
		L_84 = AndroidJNISafe_GetStringChars_mE246814CD8FF4EDDEE6EBF107367C4A8EAF03849(L_83, NULL);
		NullCheck(L_81);
		(L_81)->SetAt(static_cast<il2cpp_array_size_t>(L_82), (String_t*)L_84);
		intptr_t L_85 = V_16;
		AndroidJNISafe_DeleteLocalRef_m20303564C88A1B90E3D8D7A7D893392E18967094(L_85, NULL);
		int32_t L_86 = V_15;
		V_15 = ((int32_t)il2cpp_codegen_add(L_86, 1));
	}

IL_01e1:
	{
		int32_t L_87 = V_15;
		int32_t L_88 = V_13;
		V_17 = (bool)((((int32_t)L_87) < ((int32_t)L_88))? 1 : 0);
		bool L_89 = V_17;
		if (L_89)
		{
			goto IL_01bb;
		}
	}
	{
		StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* L_90 = V_14;
		V_3 = ((*(int16_t*)((int16_t*)(int16_t*)UnBox((RuntimeObject*)L_90, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_01fa:
	{
		Type_t* L_91 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_92 = { reinterpret_cast<intptr_t> (AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_93;
		L_93 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_92, NULL);
		bool L_94;
		L_94 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_91, L_93, NULL);
		V_18 = L_94;
		bool L_95 = V_18;
		if (!L_95)
		{
			goto IL_0263;
		}
	}
	{
		intptr_t L_96 = ___0_array;
		int32_t L_97;
		L_97 = AndroidJNISafe_GetArrayLength_m809419F04C9BB93FED5B4A89F0539231C9B90E6F(L_96, NULL);
		V_19 = L_97;
		int32_t L_98 = V_19;
		AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001* L_99 = (AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001*)(AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001*)SZArrayNew(AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001_il2cpp_TypeInfo_var, (uint32_t)L_98);
		V_20 = L_99;
		V_21 = 0;
		goto IL_024d;
	}

IL_0227:
	{
		intptr_t L_100 = ___0_array;
		int32_t L_101 = V_21;
		intptr_t L_102;
		L_102 = AndroidJNI_GetObjectArrayElement_mC4CAF9744617F69EFCD95B71D95492DA20A0FACE(L_100, L_101, NULL);
		V_22 = L_102;
		AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001* L_103 = V_20;
		int32_t L_104 = V_21;
		intptr_t L_105 = V_22;
		AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0* L_106 = (AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0*)il2cpp_codegen_object_new(AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0_il2cpp_TypeInfo_var);
		AndroidJavaObject__ctor_m0CEE7D570807333CE2C193A82AB3AB8D4F873A6B(L_106, L_105, NULL);
		NullCheck(L_103);
		ArrayElementTypeCheck (L_103, L_106);
		(L_103)->SetAt(static_cast<il2cpp_array_size_t>(L_104), (AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0*)L_106);
		intptr_t L_107 = V_22;
		AndroidJNISafe_DeleteLocalRef_m20303564C88A1B90E3D8D7A7D893392E18967094(L_107, NULL);
		int32_t L_108 = V_21;
		V_21 = ((int32_t)il2cpp_codegen_add(L_108, 1));
	}

IL_024d:
	{
		int32_t L_109 = V_21;
		int32_t L_110 = V_19;
		V_23 = (bool)((((int32_t)L_109) < ((int32_t)L_110))? 1 : 0);
		bool L_111 = V_23;
		if (L_111)
		{
			goto IL_0227;
		}
	}
	{
		AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001* L_112 = V_20;
		V_3 = ((*(int16_t*)((int16_t*)(int16_t*)UnBox((RuntimeObject*)L_112, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_0263:
	{
		Type_t* L_113 = V_0;
		Type_t* L_114 = L_113;
		if (L_114)
		{
			G_B32_0 = L_114;
			G_B32_1 = ((String_t*)il2cpp_codegen_initialize_runtime_metadata_inline((uintptr_t*)&_stringLiteral51253131B895C2F8066BCC47E62D44F18F43446C));
			goto IL_0271;
		}
		G_B31_0 = L_114;
		G_B31_1 = ((String_t*)il2cpp_codegen_initialize_runtime_metadata_inline((uintptr_t*)&_stringLiteral51253131B895C2F8066BCC47E62D44F18F43446C));
	}
	{
		G_B33_0 = ((String_t*)(NULL));
		G_B33_1 = G_B31_1;
		goto IL_0276;
	}

IL_0271:
	{
		NullCheck((RuntimeObject*)G_B32_0);
		String_t* L_115;
		L_115 = VirtualFuncInvoker0< String_t* >::Invoke(3, (RuntimeObject*)G_B32_0);
		G_B33_0 = L_115;
		G_B33_1 = G_B32_1;
	}

IL_0276:
	{
		String_t* L_116;
		L_116 = String_Concat_m8855A6DE10F84DA7F4EC113CADDB59873A25573B(G_B33_1, G_B33_0, ((String_t*)il2cpp_codegen_initialize_runtime_metadata_inline((uintptr_t*)&_stringLiteral42646B33B50B6AA15E22733C8900716F0FE19E1D)), NULL);
		Exception_t* L_117 = (Exception_t*)il2cpp_codegen_object_new(((RuntimeClass*)il2cpp_codegen_initialize_runtime_metadata_inline((uintptr_t*)&Exception_t_il2cpp_TypeInfo_var)));
		Exception__ctor_m9B2BD92CD68916245A75109105D9071C9D430E7F(L_117, L_116, NULL);
		IL2CPP_RAISE_MANAGED_EXCEPTION(L_117, method);
	}

IL_0286:
	{
		il2cpp_codegen_initobj((&V_24), sizeof(int16_t));
		int16_t L_118 = V_24;
		V_3 = L_118;
		goto IL_0293;
	}

IL_0293:
	{
		int16_t L_119 = V_3;
		return L_119;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR int32_t _AndroidJNIHelper_ConvertFromJNIArray_TisInt32_t680FF22E76F6EFAD4375103CBBFFA0421349384C_m37A94A4CA9F6456009CABE27D4AA2ED7B8365168_gshared (intptr_t ___0_array, const RuntimeMethod* method) 
{
	if (!il2cpp_rgctx_is_initialized(method))
	{
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&AndroidReflection_tD59014B286F902906DBB75DA3473897D35684908_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Boolean_t09A6377A54BE2F9E6985A8149F19234FD7DDFE22_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Byte_t94D9231AC217BE4D2E004C4CD32DF6D099EA41A3_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Char_t521A6F19B456D956AF452D926C32709DC03D6B17_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Debug_t8394C7EEAECA3689C2C9B9DE9C7166D73596276F_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Double_tE150EF3D1D43DEE85D533810AB4C742307EEDE5F_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Int16_tB8EF286A9C33492FA6E6D6E67320BE93E794A175_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Int32_t680FF22E76F6EFAD4375103CBBFFA0421349384C_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Int64_t092CFB123BE63C28ACDAF65C68F21A526050DBA3_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&SByte_tFEFFEF5D2FEBF5207950AE6FAC150FC53B668DB5_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Single_t4530F2FF86FCB0DC29F35385CA1BD21BE294761C_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&String_t_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Type_t_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&_stringLiteral24CC8D396132365E532646F936DFC8579E2299B2);
		il2cpp_rgctx_method_init(method);
	}
	Type_t* V_0 = NULL;
	bool V_1 = false;
	bool V_2 = false;
	int32_t V_3 = 0;
	bool V_4 = false;
	bool V_5 = false;
	bool V_6 = false;
	bool V_7 = false;
	bool V_8 = false;
	bool V_9 = false;
	bool V_10 = false;
	bool V_11 = false;
	bool V_12 = false;
	int32_t V_13 = 0;
	StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* V_14 = NULL;
	int32_t V_15 = 0;
	intptr_t V_16;
	memset((&V_16), 0, sizeof(V_16));
	bool V_17 = false;
	bool V_18 = false;
	int32_t V_19 = 0;
	AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001* V_20 = NULL;
	int32_t V_21 = 0;
	intptr_t V_22;
	memset((&V_22), 0, sizeof(V_22));
	bool V_23 = false;
	int32_t V_24 = 0;
	Type_t* G_B32_0 = NULL;
	String_t* G_B32_1 = NULL;
	Type_t* G_B31_0 = NULL;
	String_t* G_B31_1 = NULL;
	String_t* G_B33_0 = NULL;
	String_t* G_B33_1 = NULL;
	{
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_0 = { reinterpret_cast<intptr_t> (il2cpp_rgctx_type(method->rgctx_data, 0)) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_1;
		L_1 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_0, NULL);
		NullCheck(L_1);
		Type_t* L_2;
		L_2 = VirtualFuncInvoker0< Type_t* >::Invoke(45, L_1);
		V_0 = L_2;
		Type_t* L_3 = V_0;
		il2cpp_codegen_runtime_class_init_inline(AndroidReflection_tD59014B286F902906DBB75DA3473897D35684908_il2cpp_TypeInfo_var);
		bool L_4;
		L_4 = AndroidReflection_IsPrimitive_mA41A9ECECE3D73679C79DC8B0FDD32B59570DF25(L_3, NULL);
		V_1 = L_4;
		bool L_5 = V_1;
		if (!L_5)
		{
			goto IL_018e;
		}
	}
	{
		Type_t* L_6 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_7 = { reinterpret_cast<intptr_t> (Int32_t680FF22E76F6EFAD4375103CBBFFA0421349384C_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_8;
		L_8 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_7, NULL);
		bool L_9;
		L_9 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_6, L_8, NULL);
		V_2 = L_9;
		bool L_10 = V_2;
		if (!L_10)
		{
			goto IL_0044;
		}
	}
	{
		intptr_t L_11 = ___0_array;
		Int32U5BU5D_t19C97395396A72ECAF310612F0760F165060314C* L_12;
		L_12 = AndroidJNISafe_FromIntArray_mC4C4DC70FFA39CD6E3E02FDAC7192324E6D4614E(L_11, NULL);
		V_3 = ((*(int32_t*)((int32_t*)(int32_t*)UnBox((RuntimeObject*)L_12, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_0044:
	{
		Type_t* L_13 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_14 = { reinterpret_cast<intptr_t> (Boolean_t09A6377A54BE2F9E6985A8149F19234FD7DDFE22_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_15;
		L_15 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_14, NULL);
		bool L_16;
		L_16 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_13, L_15, NULL);
		V_4 = L_16;
		bool L_17 = V_4;
		if (!L_17)
		{
			goto IL_006b;
		}
	}
	{
		intptr_t L_18 = ___0_array;
		BooleanU5BU5D_tD317D27C31DB892BE79FAE3AEBC0B3FFB73DE9B4* L_19;
		L_19 = AndroidJNISafe_FromBooleanArray_m36ED740401185EC0A959CA0F96A324A69E668646(L_18, NULL);
		V_3 = ((*(int32_t*)((int32_t*)(int32_t*)UnBox((RuntimeObject*)L_19, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_006b:
	{
		Type_t* L_20 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_21 = { reinterpret_cast<intptr_t> (Byte_t94D9231AC217BE4D2E004C4CD32DF6D099EA41A3_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_22;
		L_22 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_21, NULL);
		bool L_23;
		L_23 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_20, L_22, NULL);
		V_5 = L_23;
		bool L_24 = V_5;
		if (!L_24)
		{
			goto IL_009e;
		}
	}
	{
		il2cpp_codegen_runtime_class_init_inline(Debug_t8394C7EEAECA3689C2C9B9DE9C7166D73596276F_il2cpp_TypeInfo_var);
		Debug_LogWarning_m33EF1B897E0C7C6FF538989610BFAFFEF4628CA9((RuntimeObject*)_stringLiteral24CC8D396132365E532646F936DFC8579E2299B2, NULL);
		intptr_t L_25 = ___0_array;
		ByteU5BU5D_tA6237BF417AE52AD70CFB4EF24A7A82613DF9031* L_26;
		L_26 = AndroidJNISafe_FromByteArray_mB06EF0FDBF6C738231E8F9D4998C38551131C4C5(L_25, NULL);
		V_3 = ((*(int32_t*)((int32_t*)(int32_t*)UnBox((RuntimeObject*)L_26, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_009e:
	{
		Type_t* L_27 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_28 = { reinterpret_cast<intptr_t> (SByte_tFEFFEF5D2FEBF5207950AE6FAC150FC53B668DB5_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_29;
		L_29 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_28, NULL);
		bool L_30;
		L_30 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_27, L_29, NULL);
		V_6 = L_30;
		bool L_31 = V_6;
		if (!L_31)
		{
			goto IL_00c5;
		}
	}
	{
		intptr_t L_32 = ___0_array;
		SByteU5BU5D_t88116DA68378C3333DB73E7D36C1A06AFAA91913* L_33;
		L_33 = AndroidJNISafe_FromSByteArray_m261D638D8B059AB777BEF0BEFDD0822717DFF2B1(L_32, NULL);
		V_3 = ((*(int32_t*)((int32_t*)(int32_t*)UnBox((RuntimeObject*)L_33, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_00c5:
	{
		Type_t* L_34 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_35 = { reinterpret_cast<intptr_t> (Int16_tB8EF286A9C33492FA6E6D6E67320BE93E794A175_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_36;
		L_36 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_35, NULL);
		bool L_37;
		L_37 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_34, L_36, NULL);
		V_7 = L_37;
		bool L_38 = V_7;
		if (!L_38)
		{
			goto IL_00ec;
		}
	}
	{
		intptr_t L_39 = ___0_array;
		Int16U5BU5D_t8175CE8DD9C9F9FB0CF4F58E45BC570575B43CFB* L_40;
		L_40 = AndroidJNISafe_FromShortArray_m62C0CB2D0BAE96D4B8CE365630361150EBE884FC(L_39, NULL);
		V_3 = ((*(int32_t*)((int32_t*)(int32_t*)UnBox((RuntimeObject*)L_40, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_00ec:
	{
		Type_t* L_41 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_42 = { reinterpret_cast<intptr_t> (Int64_t092CFB123BE63C28ACDAF65C68F21A526050DBA3_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_43;
		L_43 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_42, NULL);
		bool L_44;
		L_44 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_41, L_43, NULL);
		V_8 = L_44;
		bool L_45 = V_8;
		if (!L_45)
		{
			goto IL_0113;
		}
	}
	{
		intptr_t L_46 = ___0_array;
		Int64U5BU5D_tAEDFCBDB5414E2A140A6F34C0538BF97FCF67A1D* L_47;
		L_47 = AndroidJNISafe_FromLongArray_mC4D73C0DA27F212947AB85AA2030A35BECDF8288(L_46, NULL);
		V_3 = ((*(int32_t*)((int32_t*)(int32_t*)UnBox((RuntimeObject*)L_47, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_0113:
	{
		Type_t* L_48 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_49 = { reinterpret_cast<intptr_t> (Single_t4530F2FF86FCB0DC29F35385CA1BD21BE294761C_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_50;
		L_50 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_49, NULL);
		bool L_51;
		L_51 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_48, L_50, NULL);
		V_9 = L_51;
		bool L_52 = V_9;
		if (!L_52)
		{
			goto IL_013a;
		}
	}
	{
		intptr_t L_53 = ___0_array;
		SingleU5BU5D_t89DEFE97BCEDB5857010E79ECE0F52CF6E93B87C* L_54;
		L_54 = AndroidJNISafe_FromFloatArray_mDE02985159EEFD2CB28611C797AC21DE8B6300B8(L_53, NULL);
		V_3 = ((*(int32_t*)((int32_t*)(int32_t*)UnBox((RuntimeObject*)L_54, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_013a:
	{
		Type_t* L_55 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_56 = { reinterpret_cast<intptr_t> (Double_tE150EF3D1D43DEE85D533810AB4C742307EEDE5F_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_57;
		L_57 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_56, NULL);
		bool L_58;
		L_58 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_55, L_57, NULL);
		V_10 = L_58;
		bool L_59 = V_10;
		if (!L_59)
		{
			goto IL_0161;
		}
	}
	{
		intptr_t L_60 = ___0_array;
		DoubleU5BU5D_tCC308475BD3B8229DB2582938669EF2F9ECC1FEE* L_61;
		L_61 = AndroidJNISafe_FromDoubleArray_mDEA8F2C7854101272F3A2733F351B570AAD5D9D9(L_60, NULL);
		V_3 = ((*(int32_t*)((int32_t*)(int32_t*)UnBox((RuntimeObject*)L_61, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_0161:
	{
		Type_t* L_62 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_63 = { reinterpret_cast<intptr_t> (Char_t521A6F19B456D956AF452D926C32709DC03D6B17_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_64;
		L_64 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_63, NULL);
		bool L_65;
		L_65 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_62, L_64, NULL);
		V_11 = L_65;
		bool L_66 = V_11;
		if (!L_66)
		{
			goto IL_0188;
		}
	}
	{
		intptr_t L_67 = ___0_array;
		CharU5BU5D_t799905CF001DD5F13F7DBB310181FC4D8B7D0AAB* L_68;
		L_68 = AndroidJNISafe_FromCharArray_m54EDC9D2BE92F9973F4E00EE953EE242B231EA96(L_67, NULL);
		V_3 = ((*(int32_t*)((int32_t*)(int32_t*)UnBox((RuntimeObject*)L_68, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_0188:
	{
		goto IL_0286;
	}

IL_018e:
	{
		Type_t* L_69 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_70 = { reinterpret_cast<intptr_t> (String_t_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_71;
		L_71 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_70, NULL);
		bool L_72;
		L_72 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_69, L_71, NULL);
		V_12 = L_72;
		bool L_73 = V_12;
		if (!L_73)
		{
			goto IL_01fa;
		}
	}
	{
		intptr_t L_74 = ___0_array;
		int32_t L_75;
		L_75 = AndroidJNISafe_GetArrayLength_m809419F04C9BB93FED5B4A89F0539231C9B90E6F(L_74, NULL);
		V_13 = L_75;
		int32_t L_76 = V_13;
		StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* L_77 = (StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248*)(StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248*)SZArrayNew(StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248_il2cpp_TypeInfo_var, (uint32_t)L_76);
		V_14 = L_77;
		V_15 = 0;
		goto IL_01e1;
	}

IL_01bb:
	{
		intptr_t L_78 = ___0_array;
		int32_t L_79 = V_15;
		intptr_t L_80;
		L_80 = AndroidJNI_GetObjectArrayElement_mC4CAF9744617F69EFCD95B71D95492DA20A0FACE(L_78, L_79, NULL);
		V_16 = L_80;
		StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* L_81 = V_14;
		int32_t L_82 = V_15;
		intptr_t L_83 = V_16;
		String_t* L_84;
		L_84 = AndroidJNISafe_GetStringChars_mE246814CD8FF4EDDEE6EBF107367C4A8EAF03849(L_83, NULL);
		NullCheck(L_81);
		(L_81)->SetAt(static_cast<il2cpp_array_size_t>(L_82), (String_t*)L_84);
		intptr_t L_85 = V_16;
		AndroidJNISafe_DeleteLocalRef_m20303564C88A1B90E3D8D7A7D893392E18967094(L_85, NULL);
		int32_t L_86 = V_15;
		V_15 = ((int32_t)il2cpp_codegen_add(L_86, 1));
	}

IL_01e1:
	{
		int32_t L_87 = V_15;
		int32_t L_88 = V_13;
		V_17 = (bool)((((int32_t)L_87) < ((int32_t)L_88))? 1 : 0);
		bool L_89 = V_17;
		if (L_89)
		{
			goto IL_01bb;
		}
	}
	{
		StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* L_90 = V_14;
		V_3 = ((*(int32_t*)((int32_t*)(int32_t*)UnBox((RuntimeObject*)L_90, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_01fa:
	{
		Type_t* L_91 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_92 = { reinterpret_cast<intptr_t> (AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_93;
		L_93 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_92, NULL);
		bool L_94;
		L_94 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_91, L_93, NULL);
		V_18 = L_94;
		bool L_95 = V_18;
		if (!L_95)
		{
			goto IL_0263;
		}
	}
	{
		intptr_t L_96 = ___0_array;
		int32_t L_97;
		L_97 = AndroidJNISafe_GetArrayLength_m809419F04C9BB93FED5B4A89F0539231C9B90E6F(L_96, NULL);
		V_19 = L_97;
		int32_t L_98 = V_19;
		AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001* L_99 = (AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001*)(AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001*)SZArrayNew(AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001_il2cpp_TypeInfo_var, (uint32_t)L_98);
		V_20 = L_99;
		V_21 = 0;
		goto IL_024d;
	}

IL_0227:
	{
		intptr_t L_100 = ___0_array;
		int32_t L_101 = V_21;
		intptr_t L_102;
		L_102 = AndroidJNI_GetObjectArrayElement_mC4CAF9744617F69EFCD95B71D95492DA20A0FACE(L_100, L_101, NULL);
		V_22 = L_102;
		AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001* L_103 = V_20;
		int32_t L_104 = V_21;
		intptr_t L_105 = V_22;
		AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0* L_106 = (AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0*)il2cpp_codegen_object_new(AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0_il2cpp_TypeInfo_var);
		AndroidJavaObject__ctor_m0CEE7D570807333CE2C193A82AB3AB8D4F873A6B(L_106, L_105, NULL);
		NullCheck(L_103);
		ArrayElementTypeCheck (L_103, L_106);
		(L_103)->SetAt(static_cast<il2cpp_array_size_t>(L_104), (AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0*)L_106);
		intptr_t L_107 = V_22;
		AndroidJNISafe_DeleteLocalRef_m20303564C88A1B90E3D8D7A7D893392E18967094(L_107, NULL);
		int32_t L_108 = V_21;
		V_21 = ((int32_t)il2cpp_codegen_add(L_108, 1));
	}

IL_024d:
	{
		int32_t L_109 = V_21;
		int32_t L_110 = V_19;
		V_23 = (bool)((((int32_t)L_109) < ((int32_t)L_110))? 1 : 0);
		bool L_111 = V_23;
		if (L_111)
		{
			goto IL_0227;
		}
	}
	{
		AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001* L_112 = V_20;
		V_3 = ((*(int32_t*)((int32_t*)(int32_t*)UnBox((RuntimeObject*)L_112, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_0263:
	{
		Type_t* L_113 = V_0;
		Type_t* L_114 = L_113;
		if (L_114)
		{
			G_B32_0 = L_114;
			G_B32_1 = ((String_t*)il2cpp_codegen_initialize_runtime_metadata_inline((uintptr_t*)&_stringLiteral51253131B895C2F8066BCC47E62D44F18F43446C));
			goto IL_0271;
		}
		G_B31_0 = L_114;
		G_B31_1 = ((String_t*)il2cpp_codegen_initialize_runtime_metadata_inline((uintptr_t*)&_stringLiteral51253131B895C2F8066BCC47E62D44F18F43446C));
	}
	{
		G_B33_0 = ((String_t*)(NULL));
		G_B33_1 = G_B31_1;
		goto IL_0276;
	}

IL_0271:
	{
		NullCheck((RuntimeObject*)G_B32_0);
		String_t* L_115;
		L_115 = VirtualFuncInvoker0< String_t* >::Invoke(3, (RuntimeObject*)G_B32_0);
		G_B33_0 = L_115;
		G_B33_1 = G_B32_1;
	}

IL_0276:
	{
		String_t* L_116;
		L_116 = String_Concat_m8855A6DE10F84DA7F4EC113CADDB59873A25573B(G_B33_1, G_B33_0, ((String_t*)il2cpp_codegen_initialize_runtime_metadata_inline((uintptr_t*)&_stringLiteral42646B33B50B6AA15E22733C8900716F0FE19E1D)), NULL);
		Exception_t* L_117 = (Exception_t*)il2cpp_codegen_object_new(((RuntimeClass*)il2cpp_codegen_initialize_runtime_metadata_inline((uintptr_t*)&Exception_t_il2cpp_TypeInfo_var)));
		Exception__ctor_m9B2BD92CD68916245A75109105D9071C9D430E7F(L_117, L_116, NULL);
		IL2CPP_RAISE_MANAGED_EXCEPTION(L_117, method);
	}

IL_0286:
	{
		il2cpp_codegen_initobj((&V_24), sizeof(int32_t));
		int32_t L_118 = V_24;
		V_3 = L_118;
		goto IL_0293;
	}

IL_0293:
	{
		int32_t L_119 = V_3;
		return L_119;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR int64_t _AndroidJNIHelper_ConvertFromJNIArray_TisInt64_t092CFB123BE63C28ACDAF65C68F21A526050DBA3_mBE697F1C4D60A7F2BB06784B5CB0C540B7FBF664_gshared (intptr_t ___0_array, const RuntimeMethod* method) 
{
	if (!il2cpp_rgctx_is_initialized(method))
	{
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&AndroidReflection_tD59014B286F902906DBB75DA3473897D35684908_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Boolean_t09A6377A54BE2F9E6985A8149F19234FD7DDFE22_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Byte_t94D9231AC217BE4D2E004C4CD32DF6D099EA41A3_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Char_t521A6F19B456D956AF452D926C32709DC03D6B17_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Debug_t8394C7EEAECA3689C2C9B9DE9C7166D73596276F_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Double_tE150EF3D1D43DEE85D533810AB4C742307EEDE5F_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Int16_tB8EF286A9C33492FA6E6D6E67320BE93E794A175_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Int32_t680FF22E76F6EFAD4375103CBBFFA0421349384C_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Int64_t092CFB123BE63C28ACDAF65C68F21A526050DBA3_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&SByte_tFEFFEF5D2FEBF5207950AE6FAC150FC53B668DB5_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Single_t4530F2FF86FCB0DC29F35385CA1BD21BE294761C_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&String_t_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Type_t_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&_stringLiteral24CC8D396132365E532646F936DFC8579E2299B2);
		il2cpp_rgctx_method_init(method);
	}
	Type_t* V_0 = NULL;
	bool V_1 = false;
	bool V_2 = false;
	int64_t V_3 = 0;
	bool V_4 = false;
	bool V_5 = false;
	bool V_6 = false;
	bool V_7 = false;
	bool V_8 = false;
	bool V_9 = false;
	bool V_10 = false;
	bool V_11 = false;
	bool V_12 = false;
	int32_t V_13 = 0;
	StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* V_14 = NULL;
	int32_t V_15 = 0;
	intptr_t V_16;
	memset((&V_16), 0, sizeof(V_16));
	bool V_17 = false;
	bool V_18 = false;
	int32_t V_19 = 0;
	AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001* V_20 = NULL;
	int32_t V_21 = 0;
	intptr_t V_22;
	memset((&V_22), 0, sizeof(V_22));
	bool V_23 = false;
	int64_t V_24 = 0;
	Type_t* G_B32_0 = NULL;
	String_t* G_B32_1 = NULL;
	Type_t* G_B31_0 = NULL;
	String_t* G_B31_1 = NULL;
	String_t* G_B33_0 = NULL;
	String_t* G_B33_1 = NULL;
	{
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_0 = { reinterpret_cast<intptr_t> (il2cpp_rgctx_type(method->rgctx_data, 0)) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_1;
		L_1 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_0, NULL);
		NullCheck(L_1);
		Type_t* L_2;
		L_2 = VirtualFuncInvoker0< Type_t* >::Invoke(45, L_1);
		V_0 = L_2;
		Type_t* L_3 = V_0;
		il2cpp_codegen_runtime_class_init_inline(AndroidReflection_tD59014B286F902906DBB75DA3473897D35684908_il2cpp_TypeInfo_var);
		bool L_4;
		L_4 = AndroidReflection_IsPrimitive_mA41A9ECECE3D73679C79DC8B0FDD32B59570DF25(L_3, NULL);
		V_1 = L_4;
		bool L_5 = V_1;
		if (!L_5)
		{
			goto IL_018e;
		}
	}
	{
		Type_t* L_6 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_7 = { reinterpret_cast<intptr_t> (Int32_t680FF22E76F6EFAD4375103CBBFFA0421349384C_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_8;
		L_8 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_7, NULL);
		bool L_9;
		L_9 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_6, L_8, NULL);
		V_2 = L_9;
		bool L_10 = V_2;
		if (!L_10)
		{
			goto IL_0044;
		}
	}
	{
		intptr_t L_11 = ___0_array;
		Int32U5BU5D_t19C97395396A72ECAF310612F0760F165060314C* L_12;
		L_12 = AndroidJNISafe_FromIntArray_mC4C4DC70FFA39CD6E3E02FDAC7192324E6D4614E(L_11, NULL);
		V_3 = ((*(int64_t*)((int64_t*)(int64_t*)UnBox((RuntimeObject*)L_12, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_0044:
	{
		Type_t* L_13 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_14 = { reinterpret_cast<intptr_t> (Boolean_t09A6377A54BE2F9E6985A8149F19234FD7DDFE22_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_15;
		L_15 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_14, NULL);
		bool L_16;
		L_16 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_13, L_15, NULL);
		V_4 = L_16;
		bool L_17 = V_4;
		if (!L_17)
		{
			goto IL_006b;
		}
	}
	{
		intptr_t L_18 = ___0_array;
		BooleanU5BU5D_tD317D27C31DB892BE79FAE3AEBC0B3FFB73DE9B4* L_19;
		L_19 = AndroidJNISafe_FromBooleanArray_m36ED740401185EC0A959CA0F96A324A69E668646(L_18, NULL);
		V_3 = ((*(int64_t*)((int64_t*)(int64_t*)UnBox((RuntimeObject*)L_19, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_006b:
	{
		Type_t* L_20 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_21 = { reinterpret_cast<intptr_t> (Byte_t94D9231AC217BE4D2E004C4CD32DF6D099EA41A3_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_22;
		L_22 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_21, NULL);
		bool L_23;
		L_23 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_20, L_22, NULL);
		V_5 = L_23;
		bool L_24 = V_5;
		if (!L_24)
		{
			goto IL_009e;
		}
	}
	{
		il2cpp_codegen_runtime_class_init_inline(Debug_t8394C7EEAECA3689C2C9B9DE9C7166D73596276F_il2cpp_TypeInfo_var);
		Debug_LogWarning_m33EF1B897E0C7C6FF538989610BFAFFEF4628CA9((RuntimeObject*)_stringLiteral24CC8D396132365E532646F936DFC8579E2299B2, NULL);
		intptr_t L_25 = ___0_array;
		ByteU5BU5D_tA6237BF417AE52AD70CFB4EF24A7A82613DF9031* L_26;
		L_26 = AndroidJNISafe_FromByteArray_mB06EF0FDBF6C738231E8F9D4998C38551131C4C5(L_25, NULL);
		V_3 = ((*(int64_t*)((int64_t*)(int64_t*)UnBox((RuntimeObject*)L_26, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_009e:
	{
		Type_t* L_27 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_28 = { reinterpret_cast<intptr_t> (SByte_tFEFFEF5D2FEBF5207950AE6FAC150FC53B668DB5_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_29;
		L_29 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_28, NULL);
		bool L_30;
		L_30 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_27, L_29, NULL);
		V_6 = L_30;
		bool L_31 = V_6;
		if (!L_31)
		{
			goto IL_00c5;
		}
	}
	{
		intptr_t L_32 = ___0_array;
		SByteU5BU5D_t88116DA68378C3333DB73E7D36C1A06AFAA91913* L_33;
		L_33 = AndroidJNISafe_FromSByteArray_m261D638D8B059AB777BEF0BEFDD0822717DFF2B1(L_32, NULL);
		V_3 = ((*(int64_t*)((int64_t*)(int64_t*)UnBox((RuntimeObject*)L_33, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_00c5:
	{
		Type_t* L_34 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_35 = { reinterpret_cast<intptr_t> (Int16_tB8EF286A9C33492FA6E6D6E67320BE93E794A175_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_36;
		L_36 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_35, NULL);
		bool L_37;
		L_37 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_34, L_36, NULL);
		V_7 = L_37;
		bool L_38 = V_7;
		if (!L_38)
		{
			goto IL_00ec;
		}
	}
	{
		intptr_t L_39 = ___0_array;
		Int16U5BU5D_t8175CE8DD9C9F9FB0CF4F58E45BC570575B43CFB* L_40;
		L_40 = AndroidJNISafe_FromShortArray_m62C0CB2D0BAE96D4B8CE365630361150EBE884FC(L_39, NULL);
		V_3 = ((*(int64_t*)((int64_t*)(int64_t*)UnBox((RuntimeObject*)L_40, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_00ec:
	{
		Type_t* L_41 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_42 = { reinterpret_cast<intptr_t> (Int64_t092CFB123BE63C28ACDAF65C68F21A526050DBA3_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_43;
		L_43 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_42, NULL);
		bool L_44;
		L_44 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_41, L_43, NULL);
		V_8 = L_44;
		bool L_45 = V_8;
		if (!L_45)
		{
			goto IL_0113;
		}
	}
	{
		intptr_t L_46 = ___0_array;
		Int64U5BU5D_tAEDFCBDB5414E2A140A6F34C0538BF97FCF67A1D* L_47;
		L_47 = AndroidJNISafe_FromLongArray_mC4D73C0DA27F212947AB85AA2030A35BECDF8288(L_46, NULL);
		V_3 = ((*(int64_t*)((int64_t*)(int64_t*)UnBox((RuntimeObject*)L_47, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_0113:
	{
		Type_t* L_48 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_49 = { reinterpret_cast<intptr_t> (Single_t4530F2FF86FCB0DC29F35385CA1BD21BE294761C_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_50;
		L_50 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_49, NULL);
		bool L_51;
		L_51 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_48, L_50, NULL);
		V_9 = L_51;
		bool L_52 = V_9;
		if (!L_52)
		{
			goto IL_013a;
		}
	}
	{
		intptr_t L_53 = ___0_array;
		SingleU5BU5D_t89DEFE97BCEDB5857010E79ECE0F52CF6E93B87C* L_54;
		L_54 = AndroidJNISafe_FromFloatArray_mDE02985159EEFD2CB28611C797AC21DE8B6300B8(L_53, NULL);
		V_3 = ((*(int64_t*)((int64_t*)(int64_t*)UnBox((RuntimeObject*)L_54, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_013a:
	{
		Type_t* L_55 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_56 = { reinterpret_cast<intptr_t> (Double_tE150EF3D1D43DEE85D533810AB4C742307EEDE5F_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_57;
		L_57 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_56, NULL);
		bool L_58;
		L_58 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_55, L_57, NULL);
		V_10 = L_58;
		bool L_59 = V_10;
		if (!L_59)
		{
			goto IL_0161;
		}
	}
	{
		intptr_t L_60 = ___0_array;
		DoubleU5BU5D_tCC308475BD3B8229DB2582938669EF2F9ECC1FEE* L_61;
		L_61 = AndroidJNISafe_FromDoubleArray_mDEA8F2C7854101272F3A2733F351B570AAD5D9D9(L_60, NULL);
		V_3 = ((*(int64_t*)((int64_t*)(int64_t*)UnBox((RuntimeObject*)L_61, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_0161:
	{
		Type_t* L_62 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_63 = { reinterpret_cast<intptr_t> (Char_t521A6F19B456D956AF452D926C32709DC03D6B17_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_64;
		L_64 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_63, NULL);
		bool L_65;
		L_65 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_62, L_64, NULL);
		V_11 = L_65;
		bool L_66 = V_11;
		if (!L_66)
		{
			goto IL_0188;
		}
	}
	{
		intptr_t L_67 = ___0_array;
		CharU5BU5D_t799905CF001DD5F13F7DBB310181FC4D8B7D0AAB* L_68;
		L_68 = AndroidJNISafe_FromCharArray_m54EDC9D2BE92F9973F4E00EE953EE242B231EA96(L_67, NULL);
		V_3 = ((*(int64_t*)((int64_t*)(int64_t*)UnBox((RuntimeObject*)L_68, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_0188:
	{
		goto IL_0286;
	}

IL_018e:
	{
		Type_t* L_69 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_70 = { reinterpret_cast<intptr_t> (String_t_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_71;
		L_71 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_70, NULL);
		bool L_72;
		L_72 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_69, L_71, NULL);
		V_12 = L_72;
		bool L_73 = V_12;
		if (!L_73)
		{
			goto IL_01fa;
		}
	}
	{
		intptr_t L_74 = ___0_array;
		int32_t L_75;
		L_75 = AndroidJNISafe_GetArrayLength_m809419F04C9BB93FED5B4A89F0539231C9B90E6F(L_74, NULL);
		V_13 = L_75;
		int32_t L_76 = V_13;
		StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* L_77 = (StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248*)(StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248*)SZArrayNew(StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248_il2cpp_TypeInfo_var, (uint32_t)L_76);
		V_14 = L_77;
		V_15 = 0;
		goto IL_01e1;
	}

IL_01bb:
	{
		intptr_t L_78 = ___0_array;
		int32_t L_79 = V_15;
		intptr_t L_80;
		L_80 = AndroidJNI_GetObjectArrayElement_mC4CAF9744617F69EFCD95B71D95492DA20A0FACE(L_78, L_79, NULL);
		V_16 = L_80;
		StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* L_81 = V_14;
		int32_t L_82 = V_15;
		intptr_t L_83 = V_16;
		String_t* L_84;
		L_84 = AndroidJNISafe_GetStringChars_mE246814CD8FF4EDDEE6EBF107367C4A8EAF03849(L_83, NULL);
		NullCheck(L_81);
		(L_81)->SetAt(static_cast<il2cpp_array_size_t>(L_82), (String_t*)L_84);
		intptr_t L_85 = V_16;
		AndroidJNISafe_DeleteLocalRef_m20303564C88A1B90E3D8D7A7D893392E18967094(L_85, NULL);
		int32_t L_86 = V_15;
		V_15 = ((int32_t)il2cpp_codegen_add(L_86, 1));
	}

IL_01e1:
	{
		int32_t L_87 = V_15;
		int32_t L_88 = V_13;
		V_17 = (bool)((((int32_t)L_87) < ((int32_t)L_88))? 1 : 0);
		bool L_89 = V_17;
		if (L_89)
		{
			goto IL_01bb;
		}
	}
	{
		StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* L_90 = V_14;
		V_3 = ((*(int64_t*)((int64_t*)(int64_t*)UnBox((RuntimeObject*)L_90, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_01fa:
	{
		Type_t* L_91 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_92 = { reinterpret_cast<intptr_t> (AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_93;
		L_93 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_92, NULL);
		bool L_94;
		L_94 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_91, L_93, NULL);
		V_18 = L_94;
		bool L_95 = V_18;
		if (!L_95)
		{
			goto IL_0263;
		}
	}
	{
		intptr_t L_96 = ___0_array;
		int32_t L_97;
		L_97 = AndroidJNISafe_GetArrayLength_m809419F04C9BB93FED5B4A89F0539231C9B90E6F(L_96, NULL);
		V_19 = L_97;
		int32_t L_98 = V_19;
		AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001* L_99 = (AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001*)(AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001*)SZArrayNew(AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001_il2cpp_TypeInfo_var, (uint32_t)L_98);
		V_20 = L_99;
		V_21 = 0;
		goto IL_024d;
	}

IL_0227:
	{
		intptr_t L_100 = ___0_array;
		int32_t L_101 = V_21;
		intptr_t L_102;
		L_102 = AndroidJNI_GetObjectArrayElement_mC4CAF9744617F69EFCD95B71D95492DA20A0FACE(L_100, L_101, NULL);
		V_22 = L_102;
		AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001* L_103 = V_20;
		int32_t L_104 = V_21;
		intptr_t L_105 = V_22;
		AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0* L_106 = (AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0*)il2cpp_codegen_object_new(AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0_il2cpp_TypeInfo_var);
		AndroidJavaObject__ctor_m0CEE7D570807333CE2C193A82AB3AB8D4F873A6B(L_106, L_105, NULL);
		NullCheck(L_103);
		ArrayElementTypeCheck (L_103, L_106);
		(L_103)->SetAt(static_cast<il2cpp_array_size_t>(L_104), (AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0*)L_106);
		intptr_t L_107 = V_22;
		AndroidJNISafe_DeleteLocalRef_m20303564C88A1B90E3D8D7A7D893392E18967094(L_107, NULL);
		int32_t L_108 = V_21;
		V_21 = ((int32_t)il2cpp_codegen_add(L_108, 1));
	}

IL_024d:
	{
		int32_t L_109 = V_21;
		int32_t L_110 = V_19;
		V_23 = (bool)((((int32_t)L_109) < ((int32_t)L_110))? 1 : 0);
		bool L_111 = V_23;
		if (L_111)
		{
			goto IL_0227;
		}
	}
	{
		AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001* L_112 = V_20;
		V_3 = ((*(int64_t*)((int64_t*)(int64_t*)UnBox((RuntimeObject*)L_112, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_0263:
	{
		Type_t* L_113 = V_0;
		Type_t* L_114 = L_113;
		if (L_114)
		{
			G_B32_0 = L_114;
			G_B32_1 = ((String_t*)il2cpp_codegen_initialize_runtime_metadata_inline((uintptr_t*)&_stringLiteral51253131B895C2F8066BCC47E62D44F18F43446C));
			goto IL_0271;
		}
		G_B31_0 = L_114;
		G_B31_1 = ((String_t*)il2cpp_codegen_initialize_runtime_metadata_inline((uintptr_t*)&_stringLiteral51253131B895C2F8066BCC47E62D44F18F43446C));
	}
	{
		G_B33_0 = ((String_t*)(NULL));
		G_B33_1 = G_B31_1;
		goto IL_0276;
	}

IL_0271:
	{
		NullCheck((RuntimeObject*)G_B32_0);
		String_t* L_115;
		L_115 = VirtualFuncInvoker0< String_t* >::Invoke(3, (RuntimeObject*)G_B32_0);
		G_B33_0 = L_115;
		G_B33_1 = G_B32_1;
	}

IL_0276:
	{
		String_t* L_116;
		L_116 = String_Concat_m8855A6DE10F84DA7F4EC113CADDB59873A25573B(G_B33_1, G_B33_0, ((String_t*)il2cpp_codegen_initialize_runtime_metadata_inline((uintptr_t*)&_stringLiteral42646B33B50B6AA15E22733C8900716F0FE19E1D)), NULL);
		Exception_t* L_117 = (Exception_t*)il2cpp_codegen_object_new(((RuntimeClass*)il2cpp_codegen_initialize_runtime_metadata_inline((uintptr_t*)&Exception_t_il2cpp_TypeInfo_var)));
		Exception__ctor_m9B2BD92CD68916245A75109105D9071C9D430E7F(L_117, L_116, NULL);
		IL2CPP_RAISE_MANAGED_EXCEPTION(L_117, method);
	}

IL_0286:
	{
		il2cpp_codegen_initobj((&V_24), sizeof(int64_t));
		int64_t L_118 = V_24;
		V_3 = L_118;
		goto IL_0293;
	}

IL_0293:
	{
		int64_t L_119 = V_3;
		return L_119;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR RuntimeObject* _AndroidJNIHelper_ConvertFromJNIArray_TisRuntimeObject_m14AEE119AA362E7E6CA1E751688932596432A71D_gshared (intptr_t ___0_array, const RuntimeMethod* method) 
{
	if (!il2cpp_rgctx_is_initialized(method))
	{
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&AndroidReflection_tD59014B286F902906DBB75DA3473897D35684908_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Boolean_t09A6377A54BE2F9E6985A8149F19234FD7DDFE22_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Byte_t94D9231AC217BE4D2E004C4CD32DF6D099EA41A3_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Char_t521A6F19B456D956AF452D926C32709DC03D6B17_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Debug_t8394C7EEAECA3689C2C9B9DE9C7166D73596276F_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Double_tE150EF3D1D43DEE85D533810AB4C742307EEDE5F_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Int16_tB8EF286A9C33492FA6E6D6E67320BE93E794A175_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Int32_t680FF22E76F6EFAD4375103CBBFFA0421349384C_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Int64_t092CFB123BE63C28ACDAF65C68F21A526050DBA3_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&SByte_tFEFFEF5D2FEBF5207950AE6FAC150FC53B668DB5_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Single_t4530F2FF86FCB0DC29F35385CA1BD21BE294761C_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&String_t_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Type_t_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&_stringLiteral24CC8D396132365E532646F936DFC8579E2299B2);
		il2cpp_rgctx_method_init(method);
	}
	Type_t* V_0 = NULL;
	bool V_1 = false;
	bool V_2 = false;
	RuntimeObject* V_3 = NULL;
	bool V_4 = false;
	bool V_5 = false;
	bool V_6 = false;
	bool V_7 = false;
	bool V_8 = false;
	bool V_9 = false;
	bool V_10 = false;
	bool V_11 = false;
	bool V_12 = false;
	int32_t V_13 = 0;
	StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* V_14 = NULL;
	int32_t V_15 = 0;
	intptr_t V_16;
	memset((&V_16), 0, sizeof(V_16));
	bool V_17 = false;
	bool V_18 = false;
	int32_t V_19 = 0;
	AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001* V_20 = NULL;
	int32_t V_21 = 0;
	intptr_t V_22;
	memset((&V_22), 0, sizeof(V_22));
	bool V_23 = false;
	RuntimeObject* V_24 = NULL;
	Type_t* G_B32_0 = NULL;
	String_t* G_B32_1 = NULL;
	Type_t* G_B31_0 = NULL;
	String_t* G_B31_1 = NULL;
	String_t* G_B33_0 = NULL;
	String_t* G_B33_1 = NULL;
	{
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_0 = { reinterpret_cast<intptr_t> (il2cpp_rgctx_type(method->rgctx_data, 0)) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_1;
		L_1 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_0, NULL);
		NullCheck(L_1);
		Type_t* L_2;
		L_2 = VirtualFuncInvoker0< Type_t* >::Invoke(45, L_1);
		V_0 = L_2;
		Type_t* L_3 = V_0;
		il2cpp_codegen_runtime_class_init_inline(AndroidReflection_tD59014B286F902906DBB75DA3473897D35684908_il2cpp_TypeInfo_var);
		bool L_4;
		L_4 = AndroidReflection_IsPrimitive_mA41A9ECECE3D73679C79DC8B0FDD32B59570DF25(L_3, NULL);
		V_1 = L_4;
		bool L_5 = V_1;
		if (!L_5)
		{
			goto IL_018e;
		}
	}
	{
		Type_t* L_6 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_7 = { reinterpret_cast<intptr_t> (Int32_t680FF22E76F6EFAD4375103CBBFFA0421349384C_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_8;
		L_8 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_7, NULL);
		bool L_9;
		L_9 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_6, L_8, NULL);
		V_2 = L_9;
		bool L_10 = V_2;
		if (!L_10)
		{
			goto IL_0044;
		}
	}
	{
		intptr_t L_11 = ___0_array;
		Int32U5BU5D_t19C97395396A72ECAF310612F0760F165060314C* L_12;
		L_12 = AndroidJNISafe_FromIntArray_mC4C4DC70FFA39CD6E3E02FDAC7192324E6D4614E(L_11, NULL);
		V_3 = ((RuntimeObject*)Castclass((RuntimeObject*)L_12, il2cpp_rgctx_data(method->rgctx_data, 1)));
		goto IL_0293;
	}

IL_0044:
	{
		Type_t* L_13 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_14 = { reinterpret_cast<intptr_t> (Boolean_t09A6377A54BE2F9E6985A8149F19234FD7DDFE22_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_15;
		L_15 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_14, NULL);
		bool L_16;
		L_16 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_13, L_15, NULL);
		V_4 = L_16;
		bool L_17 = V_4;
		if (!L_17)
		{
			goto IL_006b;
		}
	}
	{
		intptr_t L_18 = ___0_array;
		BooleanU5BU5D_tD317D27C31DB892BE79FAE3AEBC0B3FFB73DE9B4* L_19;
		L_19 = AndroidJNISafe_FromBooleanArray_m36ED740401185EC0A959CA0F96A324A69E668646(L_18, NULL);
		V_3 = ((RuntimeObject*)Castclass((RuntimeObject*)L_19, il2cpp_rgctx_data(method->rgctx_data, 1)));
		goto IL_0293;
	}

IL_006b:
	{
		Type_t* L_20 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_21 = { reinterpret_cast<intptr_t> (Byte_t94D9231AC217BE4D2E004C4CD32DF6D099EA41A3_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_22;
		L_22 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_21, NULL);
		bool L_23;
		L_23 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_20, L_22, NULL);
		V_5 = L_23;
		bool L_24 = V_5;
		if (!L_24)
		{
			goto IL_009e;
		}
	}
	{
		il2cpp_codegen_runtime_class_init_inline(Debug_t8394C7EEAECA3689C2C9B9DE9C7166D73596276F_il2cpp_TypeInfo_var);
		Debug_LogWarning_m33EF1B897E0C7C6FF538989610BFAFFEF4628CA9((RuntimeObject*)_stringLiteral24CC8D396132365E532646F936DFC8579E2299B2, NULL);
		intptr_t L_25 = ___0_array;
		ByteU5BU5D_tA6237BF417AE52AD70CFB4EF24A7A82613DF9031* L_26;
		L_26 = AndroidJNISafe_FromByteArray_mB06EF0FDBF6C738231E8F9D4998C38551131C4C5(L_25, NULL);
		V_3 = ((RuntimeObject*)Castclass((RuntimeObject*)L_26, il2cpp_rgctx_data(method->rgctx_data, 1)));
		goto IL_0293;
	}

IL_009e:
	{
		Type_t* L_27 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_28 = { reinterpret_cast<intptr_t> (SByte_tFEFFEF5D2FEBF5207950AE6FAC150FC53B668DB5_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_29;
		L_29 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_28, NULL);
		bool L_30;
		L_30 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_27, L_29, NULL);
		V_6 = L_30;
		bool L_31 = V_6;
		if (!L_31)
		{
			goto IL_00c5;
		}
	}
	{
		intptr_t L_32 = ___0_array;
		SByteU5BU5D_t88116DA68378C3333DB73E7D36C1A06AFAA91913* L_33;
		L_33 = AndroidJNISafe_FromSByteArray_m261D638D8B059AB777BEF0BEFDD0822717DFF2B1(L_32, NULL);
		V_3 = ((RuntimeObject*)Castclass((RuntimeObject*)L_33, il2cpp_rgctx_data(method->rgctx_data, 1)));
		goto IL_0293;
	}

IL_00c5:
	{
		Type_t* L_34 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_35 = { reinterpret_cast<intptr_t> (Int16_tB8EF286A9C33492FA6E6D6E67320BE93E794A175_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_36;
		L_36 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_35, NULL);
		bool L_37;
		L_37 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_34, L_36, NULL);
		V_7 = L_37;
		bool L_38 = V_7;
		if (!L_38)
		{
			goto IL_00ec;
		}
	}
	{
		intptr_t L_39 = ___0_array;
		Int16U5BU5D_t8175CE8DD9C9F9FB0CF4F58E45BC570575B43CFB* L_40;
		L_40 = AndroidJNISafe_FromShortArray_m62C0CB2D0BAE96D4B8CE365630361150EBE884FC(L_39, NULL);
		V_3 = ((RuntimeObject*)Castclass((RuntimeObject*)L_40, il2cpp_rgctx_data(method->rgctx_data, 1)));
		goto IL_0293;
	}

IL_00ec:
	{
		Type_t* L_41 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_42 = { reinterpret_cast<intptr_t> (Int64_t092CFB123BE63C28ACDAF65C68F21A526050DBA3_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_43;
		L_43 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_42, NULL);
		bool L_44;
		L_44 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_41, L_43, NULL);
		V_8 = L_44;
		bool L_45 = V_8;
		if (!L_45)
		{
			goto IL_0113;
		}
	}
	{
		intptr_t L_46 = ___0_array;
		Int64U5BU5D_tAEDFCBDB5414E2A140A6F34C0538BF97FCF67A1D* L_47;
		L_47 = AndroidJNISafe_FromLongArray_mC4D73C0DA27F212947AB85AA2030A35BECDF8288(L_46, NULL);
		V_3 = ((RuntimeObject*)Castclass((RuntimeObject*)L_47, il2cpp_rgctx_data(method->rgctx_data, 1)));
		goto IL_0293;
	}

IL_0113:
	{
		Type_t* L_48 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_49 = { reinterpret_cast<intptr_t> (Single_t4530F2FF86FCB0DC29F35385CA1BD21BE294761C_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_50;
		L_50 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_49, NULL);
		bool L_51;
		L_51 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_48, L_50, NULL);
		V_9 = L_51;
		bool L_52 = V_9;
		if (!L_52)
		{
			goto IL_013a;
		}
	}
	{
		intptr_t L_53 = ___0_array;
		SingleU5BU5D_t89DEFE97BCEDB5857010E79ECE0F52CF6E93B87C* L_54;
		L_54 = AndroidJNISafe_FromFloatArray_mDE02985159EEFD2CB28611C797AC21DE8B6300B8(L_53, NULL);
		V_3 = ((RuntimeObject*)Castclass((RuntimeObject*)L_54, il2cpp_rgctx_data(method->rgctx_data, 1)));
		goto IL_0293;
	}

IL_013a:
	{
		Type_t* L_55 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_56 = { reinterpret_cast<intptr_t> (Double_tE150EF3D1D43DEE85D533810AB4C742307EEDE5F_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_57;
		L_57 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_56, NULL);
		bool L_58;
		L_58 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_55, L_57, NULL);
		V_10 = L_58;
		bool L_59 = V_10;
		if (!L_59)
		{
			goto IL_0161;
		}
	}
	{
		intptr_t L_60 = ___0_array;
		DoubleU5BU5D_tCC308475BD3B8229DB2582938669EF2F9ECC1FEE* L_61;
		L_61 = AndroidJNISafe_FromDoubleArray_mDEA8F2C7854101272F3A2733F351B570AAD5D9D9(L_60, NULL);
		V_3 = ((RuntimeObject*)Castclass((RuntimeObject*)L_61, il2cpp_rgctx_data(method->rgctx_data, 1)));
		goto IL_0293;
	}

IL_0161:
	{
		Type_t* L_62 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_63 = { reinterpret_cast<intptr_t> (Char_t521A6F19B456D956AF452D926C32709DC03D6B17_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_64;
		L_64 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_63, NULL);
		bool L_65;
		L_65 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_62, L_64, NULL);
		V_11 = L_65;
		bool L_66 = V_11;
		if (!L_66)
		{
			goto IL_0188;
		}
	}
	{
		intptr_t L_67 = ___0_array;
		CharU5BU5D_t799905CF001DD5F13F7DBB310181FC4D8B7D0AAB* L_68;
		L_68 = AndroidJNISafe_FromCharArray_m54EDC9D2BE92F9973F4E00EE953EE242B231EA96(L_67, NULL);
		V_3 = ((RuntimeObject*)Castclass((RuntimeObject*)L_68, il2cpp_rgctx_data(method->rgctx_data, 1)));
		goto IL_0293;
	}

IL_0188:
	{
		goto IL_0286;
	}

IL_018e:
	{
		Type_t* L_69 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_70 = { reinterpret_cast<intptr_t> (String_t_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_71;
		L_71 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_70, NULL);
		bool L_72;
		L_72 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_69, L_71, NULL);
		V_12 = L_72;
		bool L_73 = V_12;
		if (!L_73)
		{
			goto IL_01fa;
		}
	}
	{
		intptr_t L_74 = ___0_array;
		int32_t L_75;
		L_75 = AndroidJNISafe_GetArrayLength_m809419F04C9BB93FED5B4A89F0539231C9B90E6F(L_74, NULL);
		V_13 = L_75;
		int32_t L_76 = V_13;
		StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* L_77 = (StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248*)(StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248*)SZArrayNew(StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248_il2cpp_TypeInfo_var, (uint32_t)L_76);
		V_14 = L_77;
		V_15 = 0;
		goto IL_01e1;
	}

IL_01bb:
	{
		intptr_t L_78 = ___0_array;
		int32_t L_79 = V_15;
		intptr_t L_80;
		L_80 = AndroidJNI_GetObjectArrayElement_mC4CAF9744617F69EFCD95B71D95492DA20A0FACE(L_78, L_79, NULL);
		V_16 = L_80;
		StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* L_81 = V_14;
		int32_t L_82 = V_15;
		intptr_t L_83 = V_16;
		String_t* L_84;
		L_84 = AndroidJNISafe_GetStringChars_mE246814CD8FF4EDDEE6EBF107367C4A8EAF03849(L_83, NULL);
		NullCheck(L_81);
		(L_81)->SetAt(static_cast<il2cpp_array_size_t>(L_82), (String_t*)L_84);
		intptr_t L_85 = V_16;
		AndroidJNISafe_DeleteLocalRef_m20303564C88A1B90E3D8D7A7D893392E18967094(L_85, NULL);
		int32_t L_86 = V_15;
		V_15 = ((int32_t)il2cpp_codegen_add(L_86, 1));
	}

IL_01e1:
	{
		int32_t L_87 = V_15;
		int32_t L_88 = V_13;
		V_17 = (bool)((((int32_t)L_87) < ((int32_t)L_88))? 1 : 0);
		bool L_89 = V_17;
		if (L_89)
		{
			goto IL_01bb;
		}
	}
	{
		StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* L_90 = V_14;
		V_3 = ((RuntimeObject*)Castclass((RuntimeObject*)L_90, il2cpp_rgctx_data(method->rgctx_data, 1)));
		goto IL_0293;
	}

IL_01fa:
	{
		Type_t* L_91 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_92 = { reinterpret_cast<intptr_t> (AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_93;
		L_93 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_92, NULL);
		bool L_94;
		L_94 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_91, L_93, NULL);
		V_18 = L_94;
		bool L_95 = V_18;
		if (!L_95)
		{
			goto IL_0263;
		}
	}
	{
		intptr_t L_96 = ___0_array;
		int32_t L_97;
		L_97 = AndroidJNISafe_GetArrayLength_m809419F04C9BB93FED5B4A89F0539231C9B90E6F(L_96, NULL);
		V_19 = L_97;
		int32_t L_98 = V_19;
		AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001* L_99 = (AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001*)(AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001*)SZArrayNew(AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001_il2cpp_TypeInfo_var, (uint32_t)L_98);
		V_20 = L_99;
		V_21 = 0;
		goto IL_024d;
	}

IL_0227:
	{
		intptr_t L_100 = ___0_array;
		int32_t L_101 = V_21;
		intptr_t L_102;
		L_102 = AndroidJNI_GetObjectArrayElement_mC4CAF9744617F69EFCD95B71D95492DA20A0FACE(L_100, L_101, NULL);
		V_22 = L_102;
		AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001* L_103 = V_20;
		int32_t L_104 = V_21;
		intptr_t L_105 = V_22;
		AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0* L_106 = (AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0*)il2cpp_codegen_object_new(AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0_il2cpp_TypeInfo_var);
		AndroidJavaObject__ctor_m0CEE7D570807333CE2C193A82AB3AB8D4F873A6B(L_106, L_105, NULL);
		NullCheck(L_103);
		ArrayElementTypeCheck (L_103, L_106);
		(L_103)->SetAt(static_cast<il2cpp_array_size_t>(L_104), (AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0*)L_106);
		intptr_t L_107 = V_22;
		AndroidJNISafe_DeleteLocalRef_m20303564C88A1B90E3D8D7A7D893392E18967094(L_107, NULL);
		int32_t L_108 = V_21;
		V_21 = ((int32_t)il2cpp_codegen_add(L_108, 1));
	}

IL_024d:
	{
		int32_t L_109 = V_21;
		int32_t L_110 = V_19;
		V_23 = (bool)((((int32_t)L_109) < ((int32_t)L_110))? 1 : 0);
		bool L_111 = V_23;
		if (L_111)
		{
			goto IL_0227;
		}
	}
	{
		AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001* L_112 = V_20;
		V_3 = ((RuntimeObject*)Castclass((RuntimeObject*)L_112, il2cpp_rgctx_data(method->rgctx_data, 1)));
		goto IL_0293;
	}

IL_0263:
	{
		Type_t* L_113 = V_0;
		Type_t* L_114 = L_113;
		if (L_114)
		{
			G_B32_0 = L_114;
			G_B32_1 = ((String_t*)il2cpp_codegen_initialize_runtime_metadata_inline((uintptr_t*)&_stringLiteral51253131B895C2F8066BCC47E62D44F18F43446C));
			goto IL_0271;
		}
		G_B31_0 = L_114;
		G_B31_1 = ((String_t*)il2cpp_codegen_initialize_runtime_metadata_inline((uintptr_t*)&_stringLiteral51253131B895C2F8066BCC47E62D44F18F43446C));
	}
	{
		G_B33_0 = ((String_t*)(NULL));
		G_B33_1 = G_B31_1;
		goto IL_0276;
	}

IL_0271:
	{
		NullCheck((RuntimeObject*)G_B32_0);
		String_t* L_115;
		L_115 = VirtualFuncInvoker0< String_t* >::Invoke(3, (RuntimeObject*)G_B32_0);
		G_B33_0 = L_115;
		G_B33_1 = G_B32_1;
	}

IL_0276:
	{
		String_t* L_116;
		L_116 = String_Concat_m8855A6DE10F84DA7F4EC113CADDB59873A25573B(G_B33_1, G_B33_0, ((String_t*)il2cpp_codegen_initialize_runtime_metadata_inline((uintptr_t*)&_stringLiteral42646B33B50B6AA15E22733C8900716F0FE19E1D)), NULL);
		Exception_t* L_117 = (Exception_t*)il2cpp_codegen_object_new(((RuntimeClass*)il2cpp_codegen_initialize_runtime_metadata_inline((uintptr_t*)&Exception_t_il2cpp_TypeInfo_var)));
		Exception__ctor_m9B2BD92CD68916245A75109105D9071C9D430E7F(L_117, L_116, NULL);
		IL2CPP_RAISE_MANAGED_EXCEPTION(L_117, method);
	}

IL_0286:
	{
		il2cpp_codegen_initobj((&V_24), sizeof(RuntimeObject*));
		RuntimeObject* L_118 = V_24;
		V_3 = L_118;
		goto IL_0293;
	}

IL_0293:
	{
		RuntimeObject* L_119 = V_3;
		return L_119;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR int8_t _AndroidJNIHelper_ConvertFromJNIArray_TisSByte_tFEFFEF5D2FEBF5207950AE6FAC150FC53B668DB5_m01777984AFB915C1167148BC6056336EB200B151_gshared (intptr_t ___0_array, const RuntimeMethod* method) 
{
	if (!il2cpp_rgctx_is_initialized(method))
	{
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&AndroidReflection_tD59014B286F902906DBB75DA3473897D35684908_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Boolean_t09A6377A54BE2F9E6985A8149F19234FD7DDFE22_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Byte_t94D9231AC217BE4D2E004C4CD32DF6D099EA41A3_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Char_t521A6F19B456D956AF452D926C32709DC03D6B17_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Debug_t8394C7EEAECA3689C2C9B9DE9C7166D73596276F_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Double_tE150EF3D1D43DEE85D533810AB4C742307EEDE5F_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Int16_tB8EF286A9C33492FA6E6D6E67320BE93E794A175_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Int32_t680FF22E76F6EFAD4375103CBBFFA0421349384C_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Int64_t092CFB123BE63C28ACDAF65C68F21A526050DBA3_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&SByte_tFEFFEF5D2FEBF5207950AE6FAC150FC53B668DB5_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Single_t4530F2FF86FCB0DC29F35385CA1BD21BE294761C_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&String_t_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Type_t_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&_stringLiteral24CC8D396132365E532646F936DFC8579E2299B2);
		il2cpp_rgctx_method_init(method);
	}
	Type_t* V_0 = NULL;
	bool V_1 = false;
	bool V_2 = false;
	int8_t V_3 = 0x0;
	bool V_4 = false;
	bool V_5 = false;
	bool V_6 = false;
	bool V_7 = false;
	bool V_8 = false;
	bool V_9 = false;
	bool V_10 = false;
	bool V_11 = false;
	bool V_12 = false;
	int32_t V_13 = 0;
	StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* V_14 = NULL;
	int32_t V_15 = 0;
	intptr_t V_16;
	memset((&V_16), 0, sizeof(V_16));
	bool V_17 = false;
	bool V_18 = false;
	int32_t V_19 = 0;
	AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001* V_20 = NULL;
	int32_t V_21 = 0;
	intptr_t V_22;
	memset((&V_22), 0, sizeof(V_22));
	bool V_23 = false;
	int8_t V_24 = 0x0;
	Type_t* G_B32_0 = NULL;
	String_t* G_B32_1 = NULL;
	Type_t* G_B31_0 = NULL;
	String_t* G_B31_1 = NULL;
	String_t* G_B33_0 = NULL;
	String_t* G_B33_1 = NULL;
	{
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_0 = { reinterpret_cast<intptr_t> (il2cpp_rgctx_type(method->rgctx_data, 0)) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_1;
		L_1 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_0, NULL);
		NullCheck(L_1);
		Type_t* L_2;
		L_2 = VirtualFuncInvoker0< Type_t* >::Invoke(45, L_1);
		V_0 = L_2;
		Type_t* L_3 = V_0;
		il2cpp_codegen_runtime_class_init_inline(AndroidReflection_tD59014B286F902906DBB75DA3473897D35684908_il2cpp_TypeInfo_var);
		bool L_4;
		L_4 = AndroidReflection_IsPrimitive_mA41A9ECECE3D73679C79DC8B0FDD32B59570DF25(L_3, NULL);
		V_1 = L_4;
		bool L_5 = V_1;
		if (!L_5)
		{
			goto IL_018e;
		}
	}
	{
		Type_t* L_6 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_7 = { reinterpret_cast<intptr_t> (Int32_t680FF22E76F6EFAD4375103CBBFFA0421349384C_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_8;
		L_8 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_7, NULL);
		bool L_9;
		L_9 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_6, L_8, NULL);
		V_2 = L_9;
		bool L_10 = V_2;
		if (!L_10)
		{
			goto IL_0044;
		}
	}
	{
		intptr_t L_11 = ___0_array;
		Int32U5BU5D_t19C97395396A72ECAF310612F0760F165060314C* L_12;
		L_12 = AndroidJNISafe_FromIntArray_mC4C4DC70FFA39CD6E3E02FDAC7192324E6D4614E(L_11, NULL);
		V_3 = ((*(int8_t*)((int8_t*)(int8_t*)UnBox((RuntimeObject*)L_12, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_0044:
	{
		Type_t* L_13 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_14 = { reinterpret_cast<intptr_t> (Boolean_t09A6377A54BE2F9E6985A8149F19234FD7DDFE22_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_15;
		L_15 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_14, NULL);
		bool L_16;
		L_16 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_13, L_15, NULL);
		V_4 = L_16;
		bool L_17 = V_4;
		if (!L_17)
		{
			goto IL_006b;
		}
	}
	{
		intptr_t L_18 = ___0_array;
		BooleanU5BU5D_tD317D27C31DB892BE79FAE3AEBC0B3FFB73DE9B4* L_19;
		L_19 = AndroidJNISafe_FromBooleanArray_m36ED740401185EC0A959CA0F96A324A69E668646(L_18, NULL);
		V_3 = ((*(int8_t*)((int8_t*)(int8_t*)UnBox((RuntimeObject*)L_19, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_006b:
	{
		Type_t* L_20 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_21 = { reinterpret_cast<intptr_t> (Byte_t94D9231AC217BE4D2E004C4CD32DF6D099EA41A3_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_22;
		L_22 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_21, NULL);
		bool L_23;
		L_23 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_20, L_22, NULL);
		V_5 = L_23;
		bool L_24 = V_5;
		if (!L_24)
		{
			goto IL_009e;
		}
	}
	{
		il2cpp_codegen_runtime_class_init_inline(Debug_t8394C7EEAECA3689C2C9B9DE9C7166D73596276F_il2cpp_TypeInfo_var);
		Debug_LogWarning_m33EF1B897E0C7C6FF538989610BFAFFEF4628CA9((RuntimeObject*)_stringLiteral24CC8D396132365E532646F936DFC8579E2299B2, NULL);
		intptr_t L_25 = ___0_array;
		ByteU5BU5D_tA6237BF417AE52AD70CFB4EF24A7A82613DF9031* L_26;
		L_26 = AndroidJNISafe_FromByteArray_mB06EF0FDBF6C738231E8F9D4998C38551131C4C5(L_25, NULL);
		V_3 = ((*(int8_t*)((int8_t*)(int8_t*)UnBox((RuntimeObject*)L_26, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_009e:
	{
		Type_t* L_27 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_28 = { reinterpret_cast<intptr_t> (SByte_tFEFFEF5D2FEBF5207950AE6FAC150FC53B668DB5_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_29;
		L_29 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_28, NULL);
		bool L_30;
		L_30 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_27, L_29, NULL);
		V_6 = L_30;
		bool L_31 = V_6;
		if (!L_31)
		{
			goto IL_00c5;
		}
	}
	{
		intptr_t L_32 = ___0_array;
		SByteU5BU5D_t88116DA68378C3333DB73E7D36C1A06AFAA91913* L_33;
		L_33 = AndroidJNISafe_FromSByteArray_m261D638D8B059AB777BEF0BEFDD0822717DFF2B1(L_32, NULL);
		V_3 = ((*(int8_t*)((int8_t*)(int8_t*)UnBox((RuntimeObject*)L_33, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_00c5:
	{
		Type_t* L_34 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_35 = { reinterpret_cast<intptr_t> (Int16_tB8EF286A9C33492FA6E6D6E67320BE93E794A175_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_36;
		L_36 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_35, NULL);
		bool L_37;
		L_37 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_34, L_36, NULL);
		V_7 = L_37;
		bool L_38 = V_7;
		if (!L_38)
		{
			goto IL_00ec;
		}
	}
	{
		intptr_t L_39 = ___0_array;
		Int16U5BU5D_t8175CE8DD9C9F9FB0CF4F58E45BC570575B43CFB* L_40;
		L_40 = AndroidJNISafe_FromShortArray_m62C0CB2D0BAE96D4B8CE365630361150EBE884FC(L_39, NULL);
		V_3 = ((*(int8_t*)((int8_t*)(int8_t*)UnBox((RuntimeObject*)L_40, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_00ec:
	{
		Type_t* L_41 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_42 = { reinterpret_cast<intptr_t> (Int64_t092CFB123BE63C28ACDAF65C68F21A526050DBA3_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_43;
		L_43 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_42, NULL);
		bool L_44;
		L_44 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_41, L_43, NULL);
		V_8 = L_44;
		bool L_45 = V_8;
		if (!L_45)
		{
			goto IL_0113;
		}
	}
	{
		intptr_t L_46 = ___0_array;
		Int64U5BU5D_tAEDFCBDB5414E2A140A6F34C0538BF97FCF67A1D* L_47;
		L_47 = AndroidJNISafe_FromLongArray_mC4D73C0DA27F212947AB85AA2030A35BECDF8288(L_46, NULL);
		V_3 = ((*(int8_t*)((int8_t*)(int8_t*)UnBox((RuntimeObject*)L_47, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_0113:
	{
		Type_t* L_48 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_49 = { reinterpret_cast<intptr_t> (Single_t4530F2FF86FCB0DC29F35385CA1BD21BE294761C_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_50;
		L_50 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_49, NULL);
		bool L_51;
		L_51 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_48, L_50, NULL);
		V_9 = L_51;
		bool L_52 = V_9;
		if (!L_52)
		{
			goto IL_013a;
		}
	}
	{
		intptr_t L_53 = ___0_array;
		SingleU5BU5D_t89DEFE97BCEDB5857010E79ECE0F52CF6E93B87C* L_54;
		L_54 = AndroidJNISafe_FromFloatArray_mDE02985159EEFD2CB28611C797AC21DE8B6300B8(L_53, NULL);
		V_3 = ((*(int8_t*)((int8_t*)(int8_t*)UnBox((RuntimeObject*)L_54, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_013a:
	{
		Type_t* L_55 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_56 = { reinterpret_cast<intptr_t> (Double_tE150EF3D1D43DEE85D533810AB4C742307EEDE5F_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_57;
		L_57 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_56, NULL);
		bool L_58;
		L_58 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_55, L_57, NULL);
		V_10 = L_58;
		bool L_59 = V_10;
		if (!L_59)
		{
			goto IL_0161;
		}
	}
	{
		intptr_t L_60 = ___0_array;
		DoubleU5BU5D_tCC308475BD3B8229DB2582938669EF2F9ECC1FEE* L_61;
		L_61 = AndroidJNISafe_FromDoubleArray_mDEA8F2C7854101272F3A2733F351B570AAD5D9D9(L_60, NULL);
		V_3 = ((*(int8_t*)((int8_t*)(int8_t*)UnBox((RuntimeObject*)L_61, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_0161:
	{
		Type_t* L_62 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_63 = { reinterpret_cast<intptr_t> (Char_t521A6F19B456D956AF452D926C32709DC03D6B17_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_64;
		L_64 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_63, NULL);
		bool L_65;
		L_65 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_62, L_64, NULL);
		V_11 = L_65;
		bool L_66 = V_11;
		if (!L_66)
		{
			goto IL_0188;
		}
	}
	{
		intptr_t L_67 = ___0_array;
		CharU5BU5D_t799905CF001DD5F13F7DBB310181FC4D8B7D0AAB* L_68;
		L_68 = AndroidJNISafe_FromCharArray_m54EDC9D2BE92F9973F4E00EE953EE242B231EA96(L_67, NULL);
		V_3 = ((*(int8_t*)((int8_t*)(int8_t*)UnBox((RuntimeObject*)L_68, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_0188:
	{
		goto IL_0286;
	}

IL_018e:
	{
		Type_t* L_69 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_70 = { reinterpret_cast<intptr_t> (String_t_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_71;
		L_71 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_70, NULL);
		bool L_72;
		L_72 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_69, L_71, NULL);
		V_12 = L_72;
		bool L_73 = V_12;
		if (!L_73)
		{
			goto IL_01fa;
		}
	}
	{
		intptr_t L_74 = ___0_array;
		int32_t L_75;
		L_75 = AndroidJNISafe_GetArrayLength_m809419F04C9BB93FED5B4A89F0539231C9B90E6F(L_74, NULL);
		V_13 = L_75;
		int32_t L_76 = V_13;
		StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* L_77 = (StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248*)(StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248*)SZArrayNew(StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248_il2cpp_TypeInfo_var, (uint32_t)L_76);
		V_14 = L_77;
		V_15 = 0;
		goto IL_01e1;
	}

IL_01bb:
	{
		intptr_t L_78 = ___0_array;
		int32_t L_79 = V_15;
		intptr_t L_80;
		L_80 = AndroidJNI_GetObjectArrayElement_mC4CAF9744617F69EFCD95B71D95492DA20A0FACE(L_78, L_79, NULL);
		V_16 = L_80;
		StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* L_81 = V_14;
		int32_t L_82 = V_15;
		intptr_t L_83 = V_16;
		String_t* L_84;
		L_84 = AndroidJNISafe_GetStringChars_mE246814CD8FF4EDDEE6EBF107367C4A8EAF03849(L_83, NULL);
		NullCheck(L_81);
		(L_81)->SetAt(static_cast<il2cpp_array_size_t>(L_82), (String_t*)L_84);
		intptr_t L_85 = V_16;
		AndroidJNISafe_DeleteLocalRef_m20303564C88A1B90E3D8D7A7D893392E18967094(L_85, NULL);
		int32_t L_86 = V_15;
		V_15 = ((int32_t)il2cpp_codegen_add(L_86, 1));
	}

IL_01e1:
	{
		int32_t L_87 = V_15;
		int32_t L_88 = V_13;
		V_17 = (bool)((((int32_t)L_87) < ((int32_t)L_88))? 1 : 0);
		bool L_89 = V_17;
		if (L_89)
		{
			goto IL_01bb;
		}
	}
	{
		StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* L_90 = V_14;
		V_3 = ((*(int8_t*)((int8_t*)(int8_t*)UnBox((RuntimeObject*)L_90, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_01fa:
	{
		Type_t* L_91 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_92 = { reinterpret_cast<intptr_t> (AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_93;
		L_93 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_92, NULL);
		bool L_94;
		L_94 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_91, L_93, NULL);
		V_18 = L_94;
		bool L_95 = V_18;
		if (!L_95)
		{
			goto IL_0263;
		}
	}
	{
		intptr_t L_96 = ___0_array;
		int32_t L_97;
		L_97 = AndroidJNISafe_GetArrayLength_m809419F04C9BB93FED5B4A89F0539231C9B90E6F(L_96, NULL);
		V_19 = L_97;
		int32_t L_98 = V_19;
		AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001* L_99 = (AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001*)(AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001*)SZArrayNew(AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001_il2cpp_TypeInfo_var, (uint32_t)L_98);
		V_20 = L_99;
		V_21 = 0;
		goto IL_024d;
	}

IL_0227:
	{
		intptr_t L_100 = ___0_array;
		int32_t L_101 = V_21;
		intptr_t L_102;
		L_102 = AndroidJNI_GetObjectArrayElement_mC4CAF9744617F69EFCD95B71D95492DA20A0FACE(L_100, L_101, NULL);
		V_22 = L_102;
		AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001* L_103 = V_20;
		int32_t L_104 = V_21;
		intptr_t L_105 = V_22;
		AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0* L_106 = (AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0*)il2cpp_codegen_object_new(AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0_il2cpp_TypeInfo_var);
		AndroidJavaObject__ctor_m0CEE7D570807333CE2C193A82AB3AB8D4F873A6B(L_106, L_105, NULL);
		NullCheck(L_103);
		ArrayElementTypeCheck (L_103, L_106);
		(L_103)->SetAt(static_cast<il2cpp_array_size_t>(L_104), (AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0*)L_106);
		intptr_t L_107 = V_22;
		AndroidJNISafe_DeleteLocalRef_m20303564C88A1B90E3D8D7A7D893392E18967094(L_107, NULL);
		int32_t L_108 = V_21;
		V_21 = ((int32_t)il2cpp_codegen_add(L_108, 1));
	}

IL_024d:
	{
		int32_t L_109 = V_21;
		int32_t L_110 = V_19;
		V_23 = (bool)((((int32_t)L_109) < ((int32_t)L_110))? 1 : 0);
		bool L_111 = V_23;
		if (L_111)
		{
			goto IL_0227;
		}
	}
	{
		AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001* L_112 = V_20;
		V_3 = ((*(int8_t*)((int8_t*)(int8_t*)UnBox((RuntimeObject*)L_112, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_0263:
	{
		Type_t* L_113 = V_0;
		Type_t* L_114 = L_113;
		if (L_114)
		{
			G_B32_0 = L_114;
			G_B32_1 = ((String_t*)il2cpp_codegen_initialize_runtime_metadata_inline((uintptr_t*)&_stringLiteral51253131B895C2F8066BCC47E62D44F18F43446C));
			goto IL_0271;
		}
		G_B31_0 = L_114;
		G_B31_1 = ((String_t*)il2cpp_codegen_initialize_runtime_metadata_inline((uintptr_t*)&_stringLiteral51253131B895C2F8066BCC47E62D44F18F43446C));
	}
	{
		G_B33_0 = ((String_t*)(NULL));
		G_B33_1 = G_B31_1;
		goto IL_0276;
	}

IL_0271:
	{
		NullCheck((RuntimeObject*)G_B32_0);
		String_t* L_115;
		L_115 = VirtualFuncInvoker0< String_t* >::Invoke(3, (RuntimeObject*)G_B32_0);
		G_B33_0 = L_115;
		G_B33_1 = G_B32_1;
	}

IL_0276:
	{
		String_t* L_116;
		L_116 = String_Concat_m8855A6DE10F84DA7F4EC113CADDB59873A25573B(G_B33_1, G_B33_0, ((String_t*)il2cpp_codegen_initialize_runtime_metadata_inline((uintptr_t*)&_stringLiteral42646B33B50B6AA15E22733C8900716F0FE19E1D)), NULL);
		Exception_t* L_117 = (Exception_t*)il2cpp_codegen_object_new(((RuntimeClass*)il2cpp_codegen_initialize_runtime_metadata_inline((uintptr_t*)&Exception_t_il2cpp_TypeInfo_var)));
		Exception__ctor_m9B2BD92CD68916245A75109105D9071C9D430E7F(L_117, L_116, NULL);
		IL2CPP_RAISE_MANAGED_EXCEPTION(L_117, method);
	}

IL_0286:
	{
		il2cpp_codegen_initobj((&V_24), sizeof(int8_t));
		int8_t L_118 = V_24;
		V_3 = L_118;
		goto IL_0293;
	}

IL_0293:
	{
		int8_t L_119 = V_3;
		return L_119;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR float _AndroidJNIHelper_ConvertFromJNIArray_TisSingle_t4530F2FF86FCB0DC29F35385CA1BD21BE294761C_m6634501B2BC58937A4D852F6F2D8D55A9DFB6F64_gshared (intptr_t ___0_array, const RuntimeMethod* method) 
{
	if (!il2cpp_rgctx_is_initialized(method))
	{
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&AndroidReflection_tD59014B286F902906DBB75DA3473897D35684908_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Boolean_t09A6377A54BE2F9E6985A8149F19234FD7DDFE22_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Byte_t94D9231AC217BE4D2E004C4CD32DF6D099EA41A3_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Char_t521A6F19B456D956AF452D926C32709DC03D6B17_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Debug_t8394C7EEAECA3689C2C9B9DE9C7166D73596276F_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Double_tE150EF3D1D43DEE85D533810AB4C742307EEDE5F_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Int16_tB8EF286A9C33492FA6E6D6E67320BE93E794A175_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Int32_t680FF22E76F6EFAD4375103CBBFFA0421349384C_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Int64_t092CFB123BE63C28ACDAF65C68F21A526050DBA3_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&SByte_tFEFFEF5D2FEBF5207950AE6FAC150FC53B668DB5_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Single_t4530F2FF86FCB0DC29F35385CA1BD21BE294761C_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&String_t_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Type_t_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&_stringLiteral24CC8D396132365E532646F936DFC8579E2299B2);
		il2cpp_rgctx_method_init(method);
	}
	Type_t* V_0 = NULL;
	bool V_1 = false;
	bool V_2 = false;
	float V_3 = 0.0f;
	bool V_4 = false;
	bool V_5 = false;
	bool V_6 = false;
	bool V_7 = false;
	bool V_8 = false;
	bool V_9 = false;
	bool V_10 = false;
	bool V_11 = false;
	bool V_12 = false;
	int32_t V_13 = 0;
	StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* V_14 = NULL;
	int32_t V_15 = 0;
	intptr_t V_16;
	memset((&V_16), 0, sizeof(V_16));
	bool V_17 = false;
	bool V_18 = false;
	int32_t V_19 = 0;
	AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001* V_20 = NULL;
	int32_t V_21 = 0;
	intptr_t V_22;
	memset((&V_22), 0, sizeof(V_22));
	bool V_23 = false;
	float V_24 = 0.0f;
	Type_t* G_B32_0 = NULL;
	String_t* G_B32_1 = NULL;
	Type_t* G_B31_0 = NULL;
	String_t* G_B31_1 = NULL;
	String_t* G_B33_0 = NULL;
	String_t* G_B33_1 = NULL;
	{
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_0 = { reinterpret_cast<intptr_t> (il2cpp_rgctx_type(method->rgctx_data, 0)) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_1;
		L_1 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_0, NULL);
		NullCheck(L_1);
		Type_t* L_2;
		L_2 = VirtualFuncInvoker0< Type_t* >::Invoke(45, L_1);
		V_0 = L_2;
		Type_t* L_3 = V_0;
		il2cpp_codegen_runtime_class_init_inline(AndroidReflection_tD59014B286F902906DBB75DA3473897D35684908_il2cpp_TypeInfo_var);
		bool L_4;
		L_4 = AndroidReflection_IsPrimitive_mA41A9ECECE3D73679C79DC8B0FDD32B59570DF25(L_3, NULL);
		V_1 = L_4;
		bool L_5 = V_1;
		if (!L_5)
		{
			goto IL_018e;
		}
	}
	{
		Type_t* L_6 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_7 = { reinterpret_cast<intptr_t> (Int32_t680FF22E76F6EFAD4375103CBBFFA0421349384C_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_8;
		L_8 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_7, NULL);
		bool L_9;
		L_9 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_6, L_8, NULL);
		V_2 = L_9;
		bool L_10 = V_2;
		if (!L_10)
		{
			goto IL_0044;
		}
	}
	{
		intptr_t L_11 = ___0_array;
		Int32U5BU5D_t19C97395396A72ECAF310612F0760F165060314C* L_12;
		L_12 = AndroidJNISafe_FromIntArray_mC4C4DC70FFA39CD6E3E02FDAC7192324E6D4614E(L_11, NULL);
		V_3 = ((*(float*)((float*)(float*)UnBox((RuntimeObject*)L_12, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_0044:
	{
		Type_t* L_13 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_14 = { reinterpret_cast<intptr_t> (Boolean_t09A6377A54BE2F9E6985A8149F19234FD7DDFE22_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_15;
		L_15 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_14, NULL);
		bool L_16;
		L_16 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_13, L_15, NULL);
		V_4 = L_16;
		bool L_17 = V_4;
		if (!L_17)
		{
			goto IL_006b;
		}
	}
	{
		intptr_t L_18 = ___0_array;
		BooleanU5BU5D_tD317D27C31DB892BE79FAE3AEBC0B3FFB73DE9B4* L_19;
		L_19 = AndroidJNISafe_FromBooleanArray_m36ED740401185EC0A959CA0F96A324A69E668646(L_18, NULL);
		V_3 = ((*(float*)((float*)(float*)UnBox((RuntimeObject*)L_19, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_006b:
	{
		Type_t* L_20 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_21 = { reinterpret_cast<intptr_t> (Byte_t94D9231AC217BE4D2E004C4CD32DF6D099EA41A3_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_22;
		L_22 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_21, NULL);
		bool L_23;
		L_23 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_20, L_22, NULL);
		V_5 = L_23;
		bool L_24 = V_5;
		if (!L_24)
		{
			goto IL_009e;
		}
	}
	{
		il2cpp_codegen_runtime_class_init_inline(Debug_t8394C7EEAECA3689C2C9B9DE9C7166D73596276F_il2cpp_TypeInfo_var);
		Debug_LogWarning_m33EF1B897E0C7C6FF538989610BFAFFEF4628CA9((RuntimeObject*)_stringLiteral24CC8D396132365E532646F936DFC8579E2299B2, NULL);
		intptr_t L_25 = ___0_array;
		ByteU5BU5D_tA6237BF417AE52AD70CFB4EF24A7A82613DF9031* L_26;
		L_26 = AndroidJNISafe_FromByteArray_mB06EF0FDBF6C738231E8F9D4998C38551131C4C5(L_25, NULL);
		V_3 = ((*(float*)((float*)(float*)UnBox((RuntimeObject*)L_26, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_009e:
	{
		Type_t* L_27 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_28 = { reinterpret_cast<intptr_t> (SByte_tFEFFEF5D2FEBF5207950AE6FAC150FC53B668DB5_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_29;
		L_29 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_28, NULL);
		bool L_30;
		L_30 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_27, L_29, NULL);
		V_6 = L_30;
		bool L_31 = V_6;
		if (!L_31)
		{
			goto IL_00c5;
		}
	}
	{
		intptr_t L_32 = ___0_array;
		SByteU5BU5D_t88116DA68378C3333DB73E7D36C1A06AFAA91913* L_33;
		L_33 = AndroidJNISafe_FromSByteArray_m261D638D8B059AB777BEF0BEFDD0822717DFF2B1(L_32, NULL);
		V_3 = ((*(float*)((float*)(float*)UnBox((RuntimeObject*)L_33, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_00c5:
	{
		Type_t* L_34 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_35 = { reinterpret_cast<intptr_t> (Int16_tB8EF286A9C33492FA6E6D6E67320BE93E794A175_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_36;
		L_36 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_35, NULL);
		bool L_37;
		L_37 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_34, L_36, NULL);
		V_7 = L_37;
		bool L_38 = V_7;
		if (!L_38)
		{
			goto IL_00ec;
		}
	}
	{
		intptr_t L_39 = ___0_array;
		Int16U5BU5D_t8175CE8DD9C9F9FB0CF4F58E45BC570575B43CFB* L_40;
		L_40 = AndroidJNISafe_FromShortArray_m62C0CB2D0BAE96D4B8CE365630361150EBE884FC(L_39, NULL);
		V_3 = ((*(float*)((float*)(float*)UnBox((RuntimeObject*)L_40, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_00ec:
	{
		Type_t* L_41 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_42 = { reinterpret_cast<intptr_t> (Int64_t092CFB123BE63C28ACDAF65C68F21A526050DBA3_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_43;
		L_43 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_42, NULL);
		bool L_44;
		L_44 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_41, L_43, NULL);
		V_8 = L_44;
		bool L_45 = V_8;
		if (!L_45)
		{
			goto IL_0113;
		}
	}
	{
		intptr_t L_46 = ___0_array;
		Int64U5BU5D_tAEDFCBDB5414E2A140A6F34C0538BF97FCF67A1D* L_47;
		L_47 = AndroidJNISafe_FromLongArray_mC4D73C0DA27F212947AB85AA2030A35BECDF8288(L_46, NULL);
		V_3 = ((*(float*)((float*)(float*)UnBox((RuntimeObject*)L_47, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_0113:
	{
		Type_t* L_48 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_49 = { reinterpret_cast<intptr_t> (Single_t4530F2FF86FCB0DC29F35385CA1BD21BE294761C_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_50;
		L_50 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_49, NULL);
		bool L_51;
		L_51 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_48, L_50, NULL);
		V_9 = L_51;
		bool L_52 = V_9;
		if (!L_52)
		{
			goto IL_013a;
		}
	}
	{
		intptr_t L_53 = ___0_array;
		SingleU5BU5D_t89DEFE97BCEDB5857010E79ECE0F52CF6E93B87C* L_54;
		L_54 = AndroidJNISafe_FromFloatArray_mDE02985159EEFD2CB28611C797AC21DE8B6300B8(L_53, NULL);
		V_3 = ((*(float*)((float*)(float*)UnBox((RuntimeObject*)L_54, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_013a:
	{
		Type_t* L_55 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_56 = { reinterpret_cast<intptr_t> (Double_tE150EF3D1D43DEE85D533810AB4C742307EEDE5F_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_57;
		L_57 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_56, NULL);
		bool L_58;
		L_58 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_55, L_57, NULL);
		V_10 = L_58;
		bool L_59 = V_10;
		if (!L_59)
		{
			goto IL_0161;
		}
	}
	{
		intptr_t L_60 = ___0_array;
		DoubleU5BU5D_tCC308475BD3B8229DB2582938669EF2F9ECC1FEE* L_61;
		L_61 = AndroidJNISafe_FromDoubleArray_mDEA8F2C7854101272F3A2733F351B570AAD5D9D9(L_60, NULL);
		V_3 = ((*(float*)((float*)(float*)UnBox((RuntimeObject*)L_61, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_0161:
	{
		Type_t* L_62 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_63 = { reinterpret_cast<intptr_t> (Char_t521A6F19B456D956AF452D926C32709DC03D6B17_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_64;
		L_64 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_63, NULL);
		bool L_65;
		L_65 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_62, L_64, NULL);
		V_11 = L_65;
		bool L_66 = V_11;
		if (!L_66)
		{
			goto IL_0188;
		}
	}
	{
		intptr_t L_67 = ___0_array;
		CharU5BU5D_t799905CF001DD5F13F7DBB310181FC4D8B7D0AAB* L_68;
		L_68 = AndroidJNISafe_FromCharArray_m54EDC9D2BE92F9973F4E00EE953EE242B231EA96(L_67, NULL);
		V_3 = ((*(float*)((float*)(float*)UnBox((RuntimeObject*)L_68, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_0188:
	{
		goto IL_0286;
	}

IL_018e:
	{
		Type_t* L_69 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_70 = { reinterpret_cast<intptr_t> (String_t_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_71;
		L_71 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_70, NULL);
		bool L_72;
		L_72 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_69, L_71, NULL);
		V_12 = L_72;
		bool L_73 = V_12;
		if (!L_73)
		{
			goto IL_01fa;
		}
	}
	{
		intptr_t L_74 = ___0_array;
		int32_t L_75;
		L_75 = AndroidJNISafe_GetArrayLength_m809419F04C9BB93FED5B4A89F0539231C9B90E6F(L_74, NULL);
		V_13 = L_75;
		int32_t L_76 = V_13;
		StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* L_77 = (StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248*)(StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248*)SZArrayNew(StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248_il2cpp_TypeInfo_var, (uint32_t)L_76);
		V_14 = L_77;
		V_15 = 0;
		goto IL_01e1;
	}

IL_01bb:
	{
		intptr_t L_78 = ___0_array;
		int32_t L_79 = V_15;
		intptr_t L_80;
		L_80 = AndroidJNI_GetObjectArrayElement_mC4CAF9744617F69EFCD95B71D95492DA20A0FACE(L_78, L_79, NULL);
		V_16 = L_80;
		StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* L_81 = V_14;
		int32_t L_82 = V_15;
		intptr_t L_83 = V_16;
		String_t* L_84;
		L_84 = AndroidJNISafe_GetStringChars_mE246814CD8FF4EDDEE6EBF107367C4A8EAF03849(L_83, NULL);
		NullCheck(L_81);
		(L_81)->SetAt(static_cast<il2cpp_array_size_t>(L_82), (String_t*)L_84);
		intptr_t L_85 = V_16;
		AndroidJNISafe_DeleteLocalRef_m20303564C88A1B90E3D8D7A7D893392E18967094(L_85, NULL);
		int32_t L_86 = V_15;
		V_15 = ((int32_t)il2cpp_codegen_add(L_86, 1));
	}

IL_01e1:
	{
		int32_t L_87 = V_15;
		int32_t L_88 = V_13;
		V_17 = (bool)((((int32_t)L_87) < ((int32_t)L_88))? 1 : 0);
		bool L_89 = V_17;
		if (L_89)
		{
			goto IL_01bb;
		}
	}
	{
		StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* L_90 = V_14;
		V_3 = ((*(float*)((float*)(float*)UnBox((RuntimeObject*)L_90, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_01fa:
	{
		Type_t* L_91 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_92 = { reinterpret_cast<intptr_t> (AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_93;
		L_93 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_92, NULL);
		bool L_94;
		L_94 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_91, L_93, NULL);
		V_18 = L_94;
		bool L_95 = V_18;
		if (!L_95)
		{
			goto IL_0263;
		}
	}
	{
		intptr_t L_96 = ___0_array;
		int32_t L_97;
		L_97 = AndroidJNISafe_GetArrayLength_m809419F04C9BB93FED5B4A89F0539231C9B90E6F(L_96, NULL);
		V_19 = L_97;
		int32_t L_98 = V_19;
		AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001* L_99 = (AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001*)(AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001*)SZArrayNew(AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001_il2cpp_TypeInfo_var, (uint32_t)L_98);
		V_20 = L_99;
		V_21 = 0;
		goto IL_024d;
	}

IL_0227:
	{
		intptr_t L_100 = ___0_array;
		int32_t L_101 = V_21;
		intptr_t L_102;
		L_102 = AndroidJNI_GetObjectArrayElement_mC4CAF9744617F69EFCD95B71D95492DA20A0FACE(L_100, L_101, NULL);
		V_22 = L_102;
		AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001* L_103 = V_20;
		int32_t L_104 = V_21;
		intptr_t L_105 = V_22;
		AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0* L_106 = (AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0*)il2cpp_codegen_object_new(AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0_il2cpp_TypeInfo_var);
		AndroidJavaObject__ctor_m0CEE7D570807333CE2C193A82AB3AB8D4F873A6B(L_106, L_105, NULL);
		NullCheck(L_103);
		ArrayElementTypeCheck (L_103, L_106);
		(L_103)->SetAt(static_cast<il2cpp_array_size_t>(L_104), (AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0*)L_106);
		intptr_t L_107 = V_22;
		AndroidJNISafe_DeleteLocalRef_m20303564C88A1B90E3D8D7A7D893392E18967094(L_107, NULL);
		int32_t L_108 = V_21;
		V_21 = ((int32_t)il2cpp_codegen_add(L_108, 1));
	}

IL_024d:
	{
		int32_t L_109 = V_21;
		int32_t L_110 = V_19;
		V_23 = (bool)((((int32_t)L_109) < ((int32_t)L_110))? 1 : 0);
		bool L_111 = V_23;
		if (L_111)
		{
			goto IL_0227;
		}
	}
	{
		AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001* L_112 = V_20;
		V_3 = ((*(float*)((float*)(float*)UnBox((RuntimeObject*)L_112, il2cpp_rgctx_data(method->rgctx_data, 1)))));
		goto IL_0293;
	}

IL_0263:
	{
		Type_t* L_113 = V_0;
		Type_t* L_114 = L_113;
		if (L_114)
		{
			G_B32_0 = L_114;
			G_B32_1 = ((String_t*)il2cpp_codegen_initialize_runtime_metadata_inline((uintptr_t*)&_stringLiteral51253131B895C2F8066BCC47E62D44F18F43446C));
			goto IL_0271;
		}
		G_B31_0 = L_114;
		G_B31_1 = ((String_t*)il2cpp_codegen_initialize_runtime_metadata_inline((uintptr_t*)&_stringLiteral51253131B895C2F8066BCC47E62D44F18F43446C));
	}
	{
		G_B33_0 = ((String_t*)(NULL));
		G_B33_1 = G_B31_1;
		goto IL_0276;
	}

IL_0271:
	{
		NullCheck((RuntimeObject*)G_B32_0);
		String_t* L_115;
		L_115 = VirtualFuncInvoker0< String_t* >::Invoke(3, (RuntimeObject*)G_B32_0);
		G_B33_0 = L_115;
		G_B33_1 = G_B32_1;
	}

IL_0276:
	{
		String_t* L_116;
		L_116 = String_Concat_m8855A6DE10F84DA7F4EC113CADDB59873A25573B(G_B33_1, G_B33_0, ((String_t*)il2cpp_codegen_initialize_runtime_metadata_inline((uintptr_t*)&_stringLiteral42646B33B50B6AA15E22733C8900716F0FE19E1D)), NULL);
		Exception_t* L_117 = (Exception_t*)il2cpp_codegen_object_new(((RuntimeClass*)il2cpp_codegen_initialize_runtime_metadata_inline((uintptr_t*)&Exception_t_il2cpp_TypeInfo_var)));
		Exception__ctor_m9B2BD92CD68916245A75109105D9071C9D430E7F(L_117, L_116, NULL);
		IL2CPP_RAISE_MANAGED_EXCEPTION(L_117, method);
	}

IL_0286:
	{
		il2cpp_codegen_initobj((&V_24), sizeof(float));
		float L_118 = V_24;
		V_3 = L_118;
		goto IL_0293;
	}

IL_0293:
	{
		float L_119 = V_3;
		return L_119;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void _AndroidJNIHelper_ConvertFromJNIArray_TisIl2CppFullySharedGenericAny_mD6B660A63955117687D6131FC1DB255161D1A2BA_gshared (intptr_t ___0_array, Il2CppFullySharedGenericAny* il2cppRetVal, const RuntimeMethod* method) 
{
	if (!il2cpp_rgctx_is_initialized(method))
	{
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&AndroidReflection_tD59014B286F902906DBB75DA3473897D35684908_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Boolean_t09A6377A54BE2F9E6985A8149F19234FD7DDFE22_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Byte_t94D9231AC217BE4D2E004C4CD32DF6D099EA41A3_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Char_t521A6F19B456D956AF452D926C32709DC03D6B17_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Debug_t8394C7EEAECA3689C2C9B9DE9C7166D73596276F_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Double_tE150EF3D1D43DEE85D533810AB4C742307EEDE5F_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Int16_tB8EF286A9C33492FA6E6D6E67320BE93E794A175_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Int32_t680FF22E76F6EFAD4375103CBBFFA0421349384C_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Int64_t092CFB123BE63C28ACDAF65C68F21A526050DBA3_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&SByte_tFEFFEF5D2FEBF5207950AE6FAC150FC53B668DB5_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Single_t4530F2FF86FCB0DC29F35385CA1BD21BE294761C_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&String_t_0_0_0_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Type_t_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&_stringLiteral24CC8D396132365E532646F936DFC8579E2299B2);
		il2cpp_rgctx_method_init(method);
	}
	const uint32_t SizeOf_ArrayType_t15B09198CBBCA055D6DA2DC75D66B572B87D0FBF = il2cpp_codegen_sizeof(il2cpp_rgctx_data_no_init(method->rgctx_data, 1));
	const Il2CppFullySharedGenericAny L_13 = alloca(SizeOf_ArrayType_t15B09198CBBCA055D6DA2DC75D66B572B87D0FBF);
	const Il2CppFullySharedGenericAny L_22 = L_13;
	const Il2CppFullySharedGenericAny L_31 = L_13;
	const Il2CppFullySharedGenericAny L_40 = L_13;
	const Il2CppFullySharedGenericAny L_49 = L_13;
	const Il2CppFullySharedGenericAny L_58 = L_13;
	const Il2CppFullySharedGenericAny L_67 = L_13;
	const Il2CppFullySharedGenericAny L_76 = L_13;
	const Il2CppFullySharedGenericAny L_85 = L_13;
	const Il2CppFullySharedGenericAny L_109 = L_13;
	const Il2CppFullySharedGenericAny L_133 = L_13;
	const Il2CppFullySharedGenericAny L_140 = L_13;
	const Il2CppFullySharedGenericAny L_141 = L_13;
	Type_t* V_0 = NULL;
	bool V_1 = false;
	bool V_2 = false;
	Il2CppFullySharedGenericAny V_3 = alloca(SizeOf_ArrayType_t15B09198CBBCA055D6DA2DC75D66B572B87D0FBF);
	memset(V_3, 0, SizeOf_ArrayType_t15B09198CBBCA055D6DA2DC75D66B572B87D0FBF);
	bool V_4 = false;
	bool V_5 = false;
	bool V_6 = false;
	bool V_7 = false;
	bool V_8 = false;
	bool V_9 = false;
	bool V_10 = false;
	bool V_11 = false;
	bool V_12 = false;
	int32_t V_13 = 0;
	StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* V_14 = NULL;
	int32_t V_15 = 0;
	intptr_t V_16;
	memset((&V_16), 0, sizeof(V_16));
	bool V_17 = false;
	bool V_18 = false;
	int32_t V_19 = 0;
	AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001* V_20 = NULL;
	int32_t V_21 = 0;
	intptr_t V_22;
	memset((&V_22), 0, sizeof(V_22));
	bool V_23 = false;
	Il2CppFullySharedGenericAny V_24 = alloca(SizeOf_ArrayType_t15B09198CBBCA055D6DA2DC75D66B572B87D0FBF);
	memset(V_24, 0, SizeOf_ArrayType_t15B09198CBBCA055D6DA2DC75D66B572B87D0FBF);
	Type_t* G_B32_0 = NULL;
	String_t* G_B32_1 = NULL;
	Type_t* G_B31_0 = NULL;
	String_t* G_B31_1 = NULL;
	String_t* G_B33_0 = NULL;
	String_t* G_B33_1 = NULL;
	{
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_0 = { reinterpret_cast<intptr_t> (il2cpp_rgctx_type(method->rgctx_data, 0)) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_1;
		L_1 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_0, NULL);
		NullCheck(L_1);
		Type_t* L_2;
		L_2 = VirtualFuncInvoker0< Type_t* >::Invoke(45, L_1);
		V_0 = L_2;
		Type_t* L_3 = V_0;
		il2cpp_codegen_runtime_class_init_inline(AndroidReflection_tD59014B286F902906DBB75DA3473897D35684908_il2cpp_TypeInfo_var);
		bool L_4;
		L_4 = AndroidReflection_IsPrimitive_mA41A9ECECE3D73679C79DC8B0FDD32B59570DF25(L_3, NULL);
		V_1 = L_4;
		bool L_5 = V_1;
		if (!L_5)
		{
			goto IL_018e;
		}
	}
	{
		Type_t* L_6 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_7 = { reinterpret_cast<intptr_t> (Int32_t680FF22E76F6EFAD4375103CBBFFA0421349384C_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_8;
		L_8 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_7, NULL);
		bool L_9;
		L_9 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_6, L_8, NULL);
		V_2 = L_9;
		bool L_10 = V_2;
		if (!L_10)
		{
			goto IL_0044;
		}
	}
	{
		intptr_t L_11 = ___0_array;
		Int32U5BU5D_t19C97395396A72ECAF310612F0760F165060314C* L_12;
		L_12 = AndroidJNISafe_FromIntArray_mC4C4DC70FFA39CD6E3E02FDAC7192324E6D4614E(L_11, NULL);
		void* L_14 = UnBox_Any((RuntimeObject*)L_12, il2cpp_rgctx_data(method->rgctx_data, 1), L_13);
		il2cpp_codegen_memcpy(V_3, (((Il2CppFullySharedGenericAny)((Il2CppFullySharedGenericAny)(Il2CppFullySharedGenericAny*)L_14))), SizeOf_ArrayType_t15B09198CBBCA055D6DA2DC75D66B572B87D0FBF);
		goto IL_0293;
	}

IL_0044:
	{
		Type_t* L_15 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_16 = { reinterpret_cast<intptr_t> (Boolean_t09A6377A54BE2F9E6985A8149F19234FD7DDFE22_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_17;
		L_17 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_16, NULL);
		bool L_18;
		L_18 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_15, L_17, NULL);
		V_4 = L_18;
		bool L_19 = V_4;
		if (!L_19)
		{
			goto IL_006b;
		}
	}
	{
		intptr_t L_20 = ___0_array;
		BooleanU5BU5D_tD317D27C31DB892BE79FAE3AEBC0B3FFB73DE9B4* L_21;
		L_21 = AndroidJNISafe_FromBooleanArray_m36ED740401185EC0A959CA0F96A324A69E668646(L_20, NULL);
		void* L_23 = UnBox_Any((RuntimeObject*)L_21, il2cpp_rgctx_data(method->rgctx_data, 1), L_22);
		il2cpp_codegen_memcpy(V_3, (((Il2CppFullySharedGenericAny)((Il2CppFullySharedGenericAny)(Il2CppFullySharedGenericAny*)L_23))), SizeOf_ArrayType_t15B09198CBBCA055D6DA2DC75D66B572B87D0FBF);
		goto IL_0293;
	}

IL_006b:
	{
		Type_t* L_24 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_25 = { reinterpret_cast<intptr_t> (Byte_t94D9231AC217BE4D2E004C4CD32DF6D099EA41A3_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_26;
		L_26 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_25, NULL);
		bool L_27;
		L_27 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_24, L_26, NULL);
		V_5 = L_27;
		bool L_28 = V_5;
		if (!L_28)
		{
			goto IL_009e;
		}
	}
	{
		il2cpp_codegen_runtime_class_init_inline(Debug_t8394C7EEAECA3689C2C9B9DE9C7166D73596276F_il2cpp_TypeInfo_var);
		Debug_LogWarning_m33EF1B897E0C7C6FF538989610BFAFFEF4628CA9((RuntimeObject*)_stringLiteral24CC8D396132365E532646F936DFC8579E2299B2, NULL);
		intptr_t L_29 = ___0_array;
		ByteU5BU5D_tA6237BF417AE52AD70CFB4EF24A7A82613DF9031* L_30;
		L_30 = AndroidJNISafe_FromByteArray_mB06EF0FDBF6C738231E8F9D4998C38551131C4C5(L_29, NULL);
		void* L_32 = UnBox_Any((RuntimeObject*)L_30, il2cpp_rgctx_data(method->rgctx_data, 1), L_31);
		il2cpp_codegen_memcpy(V_3, (((Il2CppFullySharedGenericAny)((Il2CppFullySharedGenericAny)(Il2CppFullySharedGenericAny*)L_32))), SizeOf_ArrayType_t15B09198CBBCA055D6DA2DC75D66B572B87D0FBF);
		goto IL_0293;
	}

IL_009e:
	{
		Type_t* L_33 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_34 = { reinterpret_cast<intptr_t> (SByte_tFEFFEF5D2FEBF5207950AE6FAC150FC53B668DB5_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_35;
		L_35 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_34, NULL);
		bool L_36;
		L_36 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_33, L_35, NULL);
		V_6 = L_36;
		bool L_37 = V_6;
		if (!L_37)
		{
			goto IL_00c5;
		}
	}
	{
		intptr_t L_38 = ___0_array;
		SByteU5BU5D_t88116DA68378C3333DB73E7D36C1A06AFAA91913* L_39;
		L_39 = AndroidJNISafe_FromSByteArray_m261D638D8B059AB777BEF0BEFDD0822717DFF2B1(L_38, NULL);
		void* L_41 = UnBox_Any((RuntimeObject*)L_39, il2cpp_rgctx_data(method->rgctx_data, 1), L_40);
		il2cpp_codegen_memcpy(V_3, (((Il2CppFullySharedGenericAny)((Il2CppFullySharedGenericAny)(Il2CppFullySharedGenericAny*)L_41))), SizeOf_ArrayType_t15B09198CBBCA055D6DA2DC75D66B572B87D0FBF);
		goto IL_0293;
	}

IL_00c5:
	{
		Type_t* L_42 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_43 = { reinterpret_cast<intptr_t> (Int16_tB8EF286A9C33492FA6E6D6E67320BE93E794A175_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_44;
		L_44 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_43, NULL);
		bool L_45;
		L_45 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_42, L_44, NULL);
		V_7 = L_45;
		bool L_46 = V_7;
		if (!L_46)
		{
			goto IL_00ec;
		}
	}
	{
		intptr_t L_47 = ___0_array;
		Int16U5BU5D_t8175CE8DD9C9F9FB0CF4F58E45BC570575B43CFB* L_48;
		L_48 = AndroidJNISafe_FromShortArray_m62C0CB2D0BAE96D4B8CE365630361150EBE884FC(L_47, NULL);
		void* L_50 = UnBox_Any((RuntimeObject*)L_48, il2cpp_rgctx_data(method->rgctx_data, 1), L_49);
		il2cpp_codegen_memcpy(V_3, (((Il2CppFullySharedGenericAny)((Il2CppFullySharedGenericAny)(Il2CppFullySharedGenericAny*)L_50))), SizeOf_ArrayType_t15B09198CBBCA055D6DA2DC75D66B572B87D0FBF);
		goto IL_0293;
	}

IL_00ec:
	{
		Type_t* L_51 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_52 = { reinterpret_cast<intptr_t> (Int64_t092CFB123BE63C28ACDAF65C68F21A526050DBA3_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_53;
		L_53 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_52, NULL);
		bool L_54;
		L_54 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_51, L_53, NULL);
		V_8 = L_54;
		bool L_55 = V_8;
		if (!L_55)
		{
			goto IL_0113;
		}
	}
	{
		intptr_t L_56 = ___0_array;
		Int64U5BU5D_tAEDFCBDB5414E2A140A6F34C0538BF97FCF67A1D* L_57;
		L_57 = AndroidJNISafe_FromLongArray_mC4D73C0DA27F212947AB85AA2030A35BECDF8288(L_56, NULL);
		void* L_59 = UnBox_Any((RuntimeObject*)L_57, il2cpp_rgctx_data(method->rgctx_data, 1), L_58);
		il2cpp_codegen_memcpy(V_3, (((Il2CppFullySharedGenericAny)((Il2CppFullySharedGenericAny)(Il2CppFullySharedGenericAny*)L_59))), SizeOf_ArrayType_t15B09198CBBCA055D6DA2DC75D66B572B87D0FBF);
		goto IL_0293;
	}

IL_0113:
	{
		Type_t* L_60 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_61 = { reinterpret_cast<intptr_t> (Single_t4530F2FF86FCB0DC29F35385CA1BD21BE294761C_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_62;
		L_62 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_61, NULL);
		bool L_63;
		L_63 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_60, L_62, NULL);
		V_9 = L_63;
		bool L_64 = V_9;
		if (!L_64)
		{
			goto IL_013a;
		}
	}
	{
		intptr_t L_65 = ___0_array;
		SingleU5BU5D_t89DEFE97BCEDB5857010E79ECE0F52CF6E93B87C* L_66;
		L_66 = AndroidJNISafe_FromFloatArray_mDE02985159EEFD2CB28611C797AC21DE8B6300B8(L_65, NULL);
		void* L_68 = UnBox_Any((RuntimeObject*)L_66, il2cpp_rgctx_data(method->rgctx_data, 1), L_67);
		il2cpp_codegen_memcpy(V_3, (((Il2CppFullySharedGenericAny)((Il2CppFullySharedGenericAny)(Il2CppFullySharedGenericAny*)L_68))), SizeOf_ArrayType_t15B09198CBBCA055D6DA2DC75D66B572B87D0FBF);
		goto IL_0293;
	}

IL_013a:
	{
		Type_t* L_69 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_70 = { reinterpret_cast<intptr_t> (Double_tE150EF3D1D43DEE85D533810AB4C742307EEDE5F_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_71;
		L_71 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_70, NULL);
		bool L_72;
		L_72 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_69, L_71, NULL);
		V_10 = L_72;
		bool L_73 = V_10;
		if (!L_73)
		{
			goto IL_0161;
		}
	}
	{
		intptr_t L_74 = ___0_array;
		DoubleU5BU5D_tCC308475BD3B8229DB2582938669EF2F9ECC1FEE* L_75;
		L_75 = AndroidJNISafe_FromDoubleArray_mDEA8F2C7854101272F3A2733F351B570AAD5D9D9(L_74, NULL);
		void* L_77 = UnBox_Any((RuntimeObject*)L_75, il2cpp_rgctx_data(method->rgctx_data, 1), L_76);
		il2cpp_codegen_memcpy(V_3, (((Il2CppFullySharedGenericAny)((Il2CppFullySharedGenericAny)(Il2CppFullySharedGenericAny*)L_77))), SizeOf_ArrayType_t15B09198CBBCA055D6DA2DC75D66B572B87D0FBF);
		goto IL_0293;
	}

IL_0161:
	{
		Type_t* L_78 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_79 = { reinterpret_cast<intptr_t> (Char_t521A6F19B456D956AF452D926C32709DC03D6B17_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_80;
		L_80 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_79, NULL);
		bool L_81;
		L_81 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_78, L_80, NULL);
		V_11 = L_81;
		bool L_82 = V_11;
		if (!L_82)
		{
			goto IL_0188;
		}
	}
	{
		intptr_t L_83 = ___0_array;
		CharU5BU5D_t799905CF001DD5F13F7DBB310181FC4D8B7D0AAB* L_84;
		L_84 = AndroidJNISafe_FromCharArray_m54EDC9D2BE92F9973F4E00EE953EE242B231EA96(L_83, NULL);
		void* L_86 = UnBox_Any((RuntimeObject*)L_84, il2cpp_rgctx_data(method->rgctx_data, 1), L_85);
		il2cpp_codegen_memcpy(V_3, (((Il2CppFullySharedGenericAny)((Il2CppFullySharedGenericAny)(Il2CppFullySharedGenericAny*)L_86))), SizeOf_ArrayType_t15B09198CBBCA055D6DA2DC75D66B572B87D0FBF);
		goto IL_0293;
	}

IL_0188:
	{
		goto IL_0286;
	}

IL_018e:
	{
		Type_t* L_87 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_88 = { reinterpret_cast<intptr_t> (String_t_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_89;
		L_89 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_88, NULL);
		bool L_90;
		L_90 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_87, L_89, NULL);
		V_12 = L_90;
		bool L_91 = V_12;
		if (!L_91)
		{
			goto IL_01fa;
		}
	}
	{
		intptr_t L_92 = ___0_array;
		int32_t L_93;
		L_93 = AndroidJNISafe_GetArrayLength_m809419F04C9BB93FED5B4A89F0539231C9B90E6F(L_92, NULL);
		V_13 = L_93;
		int32_t L_94 = V_13;
		StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* L_95 = (StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248*)(StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248*)SZArrayNew(StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248_il2cpp_TypeInfo_var, (uint32_t)L_94);
		V_14 = L_95;
		V_15 = 0;
		goto IL_01e1;
	}

IL_01bb:
	{
		intptr_t L_96 = ___0_array;
		int32_t L_97 = V_15;
		intptr_t L_98;
		L_98 = AndroidJNI_GetObjectArrayElement_mC4CAF9744617F69EFCD95B71D95492DA20A0FACE(L_96, L_97, NULL);
		V_16 = L_98;
		StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* L_99 = V_14;
		int32_t L_100 = V_15;
		intptr_t L_101 = V_16;
		String_t* L_102;
		L_102 = AndroidJNISafe_GetStringChars_mE246814CD8FF4EDDEE6EBF107367C4A8EAF03849(L_101, NULL);
		NullCheck(L_99);
		(L_99)->SetAt(static_cast<il2cpp_array_size_t>(L_100), (String_t*)L_102);
		intptr_t L_103 = V_16;
		AndroidJNISafe_DeleteLocalRef_m20303564C88A1B90E3D8D7A7D893392E18967094(L_103, NULL);
		int32_t L_104 = V_15;
		V_15 = ((int32_t)il2cpp_codegen_add(L_104, 1));
	}

IL_01e1:
	{
		int32_t L_105 = V_15;
		int32_t L_106 = V_13;
		V_17 = (bool)((((int32_t)L_105) < ((int32_t)L_106))? 1 : 0);
		bool L_107 = V_17;
		if (L_107)
		{
			goto IL_01bb;
		}
	}
	{
		StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* L_108 = V_14;
		void* L_110 = UnBox_Any((RuntimeObject*)L_108, il2cpp_rgctx_data(method->rgctx_data, 1), L_109);
		il2cpp_codegen_memcpy(V_3, (((Il2CppFullySharedGenericAny)((Il2CppFullySharedGenericAny)(Il2CppFullySharedGenericAny*)L_110))), SizeOf_ArrayType_t15B09198CBBCA055D6DA2DC75D66B572B87D0FBF);
		goto IL_0293;
	}

IL_01fa:
	{
		Type_t* L_111 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_112 = { reinterpret_cast<intptr_t> (AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0_0_0_0_var) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_113;
		L_113 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_112, NULL);
		bool L_114;
		L_114 = Type_op_Equality_m99930A0E44E420A685FABA60E60BA1CC5FA0EBDC(L_111, L_113, NULL);
		V_18 = L_114;
		bool L_115 = V_18;
		if (!L_115)
		{
			goto IL_0263;
		}
	}
	{
		intptr_t L_116 = ___0_array;
		int32_t L_117;
		L_117 = AndroidJNISafe_GetArrayLength_m809419F04C9BB93FED5B4A89F0539231C9B90E6F(L_116, NULL);
		V_19 = L_117;
		int32_t L_118 = V_19;
		AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001* L_119 = (AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001*)(AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001*)SZArrayNew(AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001_il2cpp_TypeInfo_var, (uint32_t)L_118);
		V_20 = L_119;
		V_21 = 0;
		goto IL_024d;
	}

IL_0227:
	{
		intptr_t L_120 = ___0_array;
		int32_t L_121 = V_21;
		intptr_t L_122;
		L_122 = AndroidJNI_GetObjectArrayElement_mC4CAF9744617F69EFCD95B71D95492DA20A0FACE(L_120, L_121, NULL);
		V_22 = L_122;
		AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001* L_123 = V_20;
		int32_t L_124 = V_21;
		intptr_t L_125 = V_22;
		AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0* L_126 = (AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0*)il2cpp_codegen_object_new(AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0_il2cpp_TypeInfo_var);
		AndroidJavaObject__ctor_m0CEE7D570807333CE2C193A82AB3AB8D4F873A6B(L_126, L_125, NULL);
		NullCheck(L_123);
		ArrayElementTypeCheck (L_123, L_126);
		(L_123)->SetAt(static_cast<il2cpp_array_size_t>(L_124), (AndroidJavaObject_t8FFB930F335C1178405B82AC2BF512BB1EEF9EB0*)L_126);
		intptr_t L_127 = V_22;
		AndroidJNISafe_DeleteLocalRef_m20303564C88A1B90E3D8D7A7D893392E18967094(L_127, NULL);
		int32_t L_128 = V_21;
		V_21 = ((int32_t)il2cpp_codegen_add(L_128, 1));
	}

IL_024d:
	{
		int32_t L_129 = V_21;
		int32_t L_130 = V_19;
		V_23 = (bool)((((int32_t)L_129) < ((int32_t)L_130))? 1 : 0);
		bool L_131 = V_23;
		if (L_131)
		{
			goto IL_0227;
		}
	}
	{
		AndroidJavaObjectU5BU5D_tBCEB142050F282B940177011644246618E002001* L_132 = V_20;
		void* L_134 = UnBox_Any((RuntimeObject*)L_132, il2cpp_rgctx_data(method->rgctx_data, 1), L_133);
		il2cpp_codegen_memcpy(V_3, (((Il2CppFullySharedGenericAny)((Il2CppFullySharedGenericAny)(Il2CppFullySharedGenericAny*)L_134))), SizeOf_ArrayType_t15B09198CBBCA055D6DA2DC75D66B572B87D0FBF);
		goto IL_0293;
	}

IL_0263:
	{
		Type_t* L_135 = V_0;
		Type_t* L_136 = L_135;
		if (L_136)
		{
			G_B32_0 = L_136;
			G_B32_1 = ((String_t*)il2cpp_codegen_initialize_runtime_metadata_inline((uintptr_t*)&_stringLiteral51253131B895C2F8066BCC47E62D44F18F43446C));
			goto IL_0271;
		}
		G_B31_0 = L_136;
		G_B31_1 = ((String_t*)il2cpp_codegen_initialize_runtime_metadata_inline((uintptr_t*)&_stringLiteral51253131B895C2F8066BCC47E62D44F18F43446C));
	}
	{
		G_B33_0 = ((String_t*)(NULL));
		G_B33_1 = G_B31_1;
		goto IL_0276;
	}

IL_0271:
	{
		NullCheck((RuntimeObject*)G_B32_0);
		String_t* L_137;
		L_137 = VirtualFuncInvoker0< String_t* >::Invoke(3, (RuntimeObject*)G_B32_0);
		G_B33_0 = L_137;
		G_B33_1 = G_B32_1;
	}

IL_0276:
	{
		String_t* L_138;
		L_138 = String_Concat_m8855A6DE10F84DA7F4EC113CADDB59873A25573B(G_B33_1, G_B33_0, ((String_t*)il2cpp_codegen_initialize_runtime_metadata_inline((uintptr_t*)&_stringLiteral42646B33B50B6AA15E22733C8900716F0FE19E1D)), NULL);
		Exception_t* L_139 = (Exception_t*)il2cpp_codegen_object_new(((RuntimeClass*)il2cpp_codegen_initialize_runtime_metadata_inline((uintptr_t*)&Exception_t_il2cpp_TypeInfo_var)));
		Exception__ctor_m9B2BD92CD68916245A75109105D9071C9D430E7F(L_139, L_138, NULL);
		IL2CPP_RAISE_MANAGED_EXCEPTION(L_139, method);
	}

IL_0286:
	{
		il2cpp_codegen_initobj((Il2CppFullySharedGenericAny*)V_24, SizeOf_ArrayType_t15B09198CBBCA055D6DA2DC75D66B572B87D0FBF);
		il2cpp_codegen_memcpy(L_140, V_24, SizeOf_ArrayType_t15B09198CBBCA055D6DA2DC75D66B572B87D0FBF);
		il2cpp_codegen_memcpy(V_3, L_140, SizeOf_ArrayType_t15B09198CBBCA055D6DA2DC75D66B572B87D0FBF);
		goto IL_0293;
	}

IL_0293:
	{
		il2cpp_codegen_memcpy(L_141, V_3, SizeOf_ArrayType_t15B09198CBBCA055D6DA2DC75D66B572B87D0FBF);
		il2cpp_codegen_memcpy(il2cppRetVal, L_141, SizeOf_ArrayType_t15B09198CBBCA055D6DA2DC75D66B572B87D0FBF);
		return;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR intptr_t _AndroidJNIHelper_GetMethodID_TisBoolean_t09A6377A54BE2F9E6985A8149F19234FD7DDFE22_m5C5661781E8C49E962C2556FC75101FD0E862AFD_gshared (intptr_t ___0_jclass, String_t* ___1_methodName, ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* ___2_args, bool ___3_isStatic, const RuntimeMethod* method) 
{
	il2cpp_rgctx_method_init(method);
	intptr_t V_0;
	memset((&V_0), 0, sizeof(V_0));
	{
		intptr_t L_0 = ___0_jclass;
		String_t* L_1 = ___1_methodName;
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_2 = ___2_args;
		String_t* L_3;
		L_3 = _AndroidJNIHelper_GetSignature_TisBoolean_t09A6377A54BE2F9E6985A8149F19234FD7DDFE22_m1BB764DB4D3E393C60E69169020A7EC792D639D5(L_2, il2cpp_rgctx_method(method->rgctx_data, 0));
		bool L_4 = ___3_isStatic;
		intptr_t L_5;
		L_5 = AndroidJNIHelper_GetMethodID_mDB705DC228B1BB30E6595068797FB3F2A1817BB8(L_0, L_1, L_3, L_4, NULL);
		V_0 = L_5;
		goto IL_0012;
	}

IL_0012:
	{
		intptr_t L_6 = V_0;
		return L_6;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR intptr_t _AndroidJNIHelper_GetMethodID_TisChar_t521A6F19B456D956AF452D926C32709DC03D6B17_m465627642B00BC71088A5883058BB86DDBADABE0_gshared (intptr_t ___0_jclass, String_t* ___1_methodName, ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* ___2_args, bool ___3_isStatic, const RuntimeMethod* method) 
{
	il2cpp_rgctx_method_init(method);
	intptr_t V_0;
	memset((&V_0), 0, sizeof(V_0));
	{
		intptr_t L_0 = ___0_jclass;
		String_t* L_1 = ___1_methodName;
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_2 = ___2_args;
		String_t* L_3;
		L_3 = _AndroidJNIHelper_GetSignature_TisChar_t521A6F19B456D956AF452D926C32709DC03D6B17_mD783834059E75BFC7A7FEB544B6ABA307E91B2C4(L_2, il2cpp_rgctx_method(method->rgctx_data, 0));
		bool L_4 = ___3_isStatic;
		intptr_t L_5;
		L_5 = AndroidJNIHelper_GetMethodID_mDB705DC228B1BB30E6595068797FB3F2A1817BB8(L_0, L_1, L_3, L_4, NULL);
		V_0 = L_5;
		goto IL_0012;
	}

IL_0012:
	{
		intptr_t L_6 = V_0;
		return L_6;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR intptr_t _AndroidJNIHelper_GetMethodID_TisDouble_tE150EF3D1D43DEE85D533810AB4C742307EEDE5F_mA32D3320555971B585058A28FC5F5EC84DC10A34_gshared (intptr_t ___0_jclass, String_t* ___1_methodName, ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* ___2_args, bool ___3_isStatic, const RuntimeMethod* method) 
{
	il2cpp_rgctx_method_init(method);
	intptr_t V_0;
	memset((&V_0), 0, sizeof(V_0));
	{
		intptr_t L_0 = ___0_jclass;
		String_t* L_1 = ___1_methodName;
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_2 = ___2_args;
		String_t* L_3;
		L_3 = _AndroidJNIHelper_GetSignature_TisDouble_tE150EF3D1D43DEE85D533810AB4C742307EEDE5F_m74C4D07DCE96BE5E61ED2AAED270DF7469C5F341(L_2, il2cpp_rgctx_method(method->rgctx_data, 0));
		bool L_4 = ___3_isStatic;
		intptr_t L_5;
		L_5 = AndroidJNIHelper_GetMethodID_mDB705DC228B1BB30E6595068797FB3F2A1817BB8(L_0, L_1, L_3, L_4, NULL);
		V_0 = L_5;
		goto IL_0012;
	}

IL_0012:
	{
		intptr_t L_6 = V_0;
		return L_6;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR intptr_t _AndroidJNIHelper_GetMethodID_TisInt16_tB8EF286A9C33492FA6E6D6E67320BE93E794A175_mF0D2DB5B885B01587820A9F88C6CAD67C8DC1512_gshared (intptr_t ___0_jclass, String_t* ___1_methodName, ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* ___2_args, bool ___3_isStatic, const RuntimeMethod* method) 
{
	il2cpp_rgctx_method_init(method);
	intptr_t V_0;
	memset((&V_0), 0, sizeof(V_0));
	{
		intptr_t L_0 = ___0_jclass;
		String_t* L_1 = ___1_methodName;
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_2 = ___2_args;
		String_t* L_3;
		L_3 = _AndroidJNIHelper_GetSignature_TisInt16_tB8EF286A9C33492FA6E6D6E67320BE93E794A175_m1E079B67FDC93E1BBE5C29D9C2BC09338DA0A5AA(L_2, il2cpp_rgctx_method(method->rgctx_data, 0));
		bool L_4 = ___3_isStatic;
		intptr_t L_5;
		L_5 = AndroidJNIHelper_GetMethodID_mDB705DC228B1BB30E6595068797FB3F2A1817BB8(L_0, L_1, L_3, L_4, NULL);
		V_0 = L_5;
		goto IL_0012;
	}

IL_0012:
	{
		intptr_t L_6 = V_0;
		return L_6;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR intptr_t _AndroidJNIHelper_GetMethodID_TisInt32_t680FF22E76F6EFAD4375103CBBFFA0421349384C_mB340108BAAC2DA25B45971B719093FDF9B13E745_gshared (intptr_t ___0_jclass, String_t* ___1_methodName, ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* ___2_args, bool ___3_isStatic, const RuntimeMethod* method) 
{
	il2cpp_rgctx_method_init(method);
	intptr_t V_0;
	memset((&V_0), 0, sizeof(V_0));
	{
		intptr_t L_0 = ___0_jclass;
		String_t* L_1 = ___1_methodName;
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_2 = ___2_args;
		String_t* L_3;
		L_3 = _AndroidJNIHelper_GetSignature_TisInt32_t680FF22E76F6EFAD4375103CBBFFA0421349384C_mA85CEF9411BD97B51F86CC460B32C46C2B873B12(L_2, il2cpp_rgctx_method(method->rgctx_data, 0));
		bool L_4 = ___3_isStatic;
		intptr_t L_5;
		L_5 = AndroidJNIHelper_GetMethodID_mDB705DC228B1BB30E6595068797FB3F2A1817BB8(L_0, L_1, L_3, L_4, NULL);
		V_0 = L_5;
		goto IL_0012;
	}

IL_0012:
	{
		intptr_t L_6 = V_0;
		return L_6;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR intptr_t _AndroidJNIHelper_GetMethodID_TisInt64_t092CFB123BE63C28ACDAF65C68F21A526050DBA3_mF114D8205E13517DE4F8DB9772E9C40C7C43BD85_gshared (intptr_t ___0_jclass, String_t* ___1_methodName, ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* ___2_args, bool ___3_isStatic, const RuntimeMethod* method) 
{
	il2cpp_rgctx_method_init(method);
	intptr_t V_0;
	memset((&V_0), 0, sizeof(V_0));
	{
		intptr_t L_0 = ___0_jclass;
		String_t* L_1 = ___1_methodName;
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_2 = ___2_args;
		String_t* L_3;
		L_3 = _AndroidJNIHelper_GetSignature_TisInt64_t092CFB123BE63C28ACDAF65C68F21A526050DBA3_m847042ADF26044DDB60469E1C3477EBBB1B55E11(L_2, il2cpp_rgctx_method(method->rgctx_data, 0));
		bool L_4 = ___3_isStatic;
		intptr_t L_5;
		L_5 = AndroidJNIHelper_GetMethodID_mDB705DC228B1BB30E6595068797FB3F2A1817BB8(L_0, L_1, L_3, L_4, NULL);
		V_0 = L_5;
		goto IL_0012;
	}

IL_0012:
	{
		intptr_t L_6 = V_0;
		return L_6;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR intptr_t _AndroidJNIHelper_GetMethodID_TisRuntimeObject_m7BB44CFD4D80045298CF68828C0FA8F3E1FFE51C_gshared (intptr_t ___0_jclass, String_t* ___1_methodName, ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* ___2_args, bool ___3_isStatic, const RuntimeMethod* method) 
{
	il2cpp_rgctx_method_init(method);
	intptr_t V_0;
	memset((&V_0), 0, sizeof(V_0));
	{
		intptr_t L_0 = ___0_jclass;
		String_t* L_1 = ___1_methodName;
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_2 = ___2_args;
		String_t* L_3;
		L_3 = _AndroidJNIHelper_GetSignature_TisRuntimeObject_m7CC50A493D0C6897ECB2692A7CEFB3A2CD3655A5(L_2, il2cpp_rgctx_method(method->rgctx_data, 0));
		bool L_4 = ___3_isStatic;
		intptr_t L_5;
		L_5 = AndroidJNIHelper_GetMethodID_mDB705DC228B1BB30E6595068797FB3F2A1817BB8(L_0, L_1, L_3, L_4, NULL);
		V_0 = L_5;
		goto IL_0012;
	}

IL_0012:
	{
		intptr_t L_6 = V_0;
		return L_6;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR intptr_t _AndroidJNIHelper_GetMethodID_TisSByte_tFEFFEF5D2FEBF5207950AE6FAC150FC53B668DB5_m362BBB1CC3B8834A056A8F709649BD182E24E9BD_gshared (intptr_t ___0_jclass, String_t* ___1_methodName, ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* ___2_args, bool ___3_isStatic, const RuntimeMethod* method) 
{
	il2cpp_rgctx_method_init(method);
	intptr_t V_0;
	memset((&V_0), 0, sizeof(V_0));
	{
		intptr_t L_0 = ___0_jclass;
		String_t* L_1 = ___1_methodName;
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_2 = ___2_args;
		String_t* L_3;
		L_3 = _AndroidJNIHelper_GetSignature_TisSByte_tFEFFEF5D2FEBF5207950AE6FAC150FC53B668DB5_mEAD40CF5E1A04E27AE3991DAB10ABB9EC6F37FBB(L_2, il2cpp_rgctx_method(method->rgctx_data, 0));
		bool L_4 = ___3_isStatic;
		intptr_t L_5;
		L_5 = AndroidJNIHelper_GetMethodID_mDB705DC228B1BB30E6595068797FB3F2A1817BB8(L_0, L_1, L_3, L_4, NULL);
		V_0 = L_5;
		goto IL_0012;
	}

IL_0012:
	{
		intptr_t L_6 = V_0;
		return L_6;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR intptr_t _AndroidJNIHelper_GetMethodID_TisSingle_t4530F2FF86FCB0DC29F35385CA1BD21BE294761C_m86B190CF71EDCB08177B90F98C76A9545AF09FCB_gshared (intptr_t ___0_jclass, String_t* ___1_methodName, ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* ___2_args, bool ___3_isStatic, const RuntimeMethod* method) 
{
	il2cpp_rgctx_method_init(method);
	intptr_t V_0;
	memset((&V_0), 0, sizeof(V_0));
	{
		intptr_t L_0 = ___0_jclass;
		String_t* L_1 = ___1_methodName;
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_2 = ___2_args;
		String_t* L_3;
		L_3 = _AndroidJNIHelper_GetSignature_TisSingle_t4530F2FF86FCB0DC29F35385CA1BD21BE294761C_mDD367BE518367698F0093E97FCF201D89B5790CB(L_2, il2cpp_rgctx_method(method->rgctx_data, 0));
		bool L_4 = ___3_isStatic;
		intptr_t L_5;
		L_5 = AndroidJNIHelper_GetMethodID_mDB705DC228B1BB30E6595068797FB3F2A1817BB8(L_0, L_1, L_3, L_4, NULL);
		V_0 = L_5;
		goto IL_0012;
	}

IL_0012:
	{
		intptr_t L_6 = V_0;
		return L_6;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR intptr_t _AndroidJNIHelper_GetMethodID_TisIl2CppFullySharedGenericAny_mBB787943D3DB158E741B5FF2B66EFB90237F837C_gshared (intptr_t ___0_jclass, String_t* ___1_methodName, ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* ___2_args, bool ___3_isStatic, const RuntimeMethod* method) 
{
	il2cpp_rgctx_method_init(method);
	intptr_t V_0;
	memset((&V_0), 0, sizeof(V_0));
	{
		intptr_t L_0 = ___0_jclass;
		String_t* L_1 = ___1_methodName;
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_2 = ___2_args;
		String_t* L_3;
		L_3 = ((  String_t* (*) (ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918*, const RuntimeMethod*))il2cpp_codegen_get_direct_method_pointer(il2cpp_rgctx_method(method->rgctx_data, 0)))(L_2, il2cpp_rgctx_method(method->rgctx_data, 0));
		bool L_4 = ___3_isStatic;
		intptr_t L_5;
		L_5 = AndroidJNIHelper_GetMethodID_mDB705DC228B1BB30E6595068797FB3F2A1817BB8(L_0, L_1, L_3, L_4, NULL);
		V_0 = L_5;
		goto IL_0012;
	}

IL_0012:
	{
		intptr_t L_6 = V_0;
		return L_6;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR String_t* _AndroidJNIHelper_GetSignature_TisBoolean_t09A6377A54BE2F9E6985A8149F19234FD7DDFE22_m1BB764DB4D3E393C60E69169020A7EC792D639D5_gshared (ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* ___0_args, const RuntimeMethod* method) 
{
	if (!il2cpp_rgctx_is_initialized(method))
	{
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&StringBuilder_t_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Type_t_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&_stringLiteral622F5FF68A93093A1D312703FF92713F8BF2C946);
		il2cpp_rgctx_method_init(method);
	}
	StringBuilder_t* V_0 = NULL;
	bool V_1 = false;
	String_t* V_2 = NULL;
	ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* V_3 = NULL;
	int32_t V_4 = 0;
	RuntimeObject* V_5 = NULL;
	int32_t G_B3_0 = 0;
	{
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_0 = ___0_args;
		if (!L_0)
		{
			goto IL_000b;
		}
	}
	{
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_1 = ___0_args;
		NullCheck(L_1);
		G_B3_0 = ((((int32_t)(((RuntimeArray*)L_1)->max_length)) == ((int32_t)0))? 1 : 0);
		goto IL_000c;
	}

IL_000b:
	{
		G_B3_0 = 1;
	}

IL_000c:
	{
		V_1 = (bool)G_B3_0;
		bool L_2 = V_1;
		if (!L_2)
		{
			goto IL_002c;
		}
	}
	{
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_3 = { reinterpret_cast<intptr_t> (il2cpp_rgctx_type(method->rgctx_data, 0)) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_4;
		L_4 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_3, NULL);
		String_t* L_5;
		L_5 = _AndroidJNIHelper_GetSignature_m414A7A6B98FB5565075E4C51F22C482F2BCEEF5F((RuntimeObject*)L_4, NULL);
		String_t* L_6;
		L_6 = String_Concat_m9E3155FB84015C823606188F53B47CB44C444991(_stringLiteral622F5FF68A93093A1D312703FF92713F8BF2C946, L_5, NULL);
		V_2 = L_6;
		goto IL_008e;
	}

IL_002c:
	{
		StringBuilder_t* L_7 = (StringBuilder_t*)il2cpp_codegen_object_new(StringBuilder_t_il2cpp_TypeInfo_var);
		StringBuilder__ctor_m1D99713357DE05DAFA296633639DB55F8C30587D(L_7, NULL);
		V_0 = L_7;
		StringBuilder_t* L_8 = V_0;
		NullCheck(L_8);
		StringBuilder_t* L_9;
		L_9 = StringBuilder_Append_m71228B30F05724CD2CD96D9611DCD61BFB96A6E1(L_8, (Il2CppChar)((int32_t)40), NULL);
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_10 = ___0_args;
		V_3 = L_10;
		V_4 = 0;
		goto IL_005f;
	}

IL_0043:
	{
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_11 = V_3;
		int32_t L_12 = V_4;
		NullCheck(L_11);
		int32_t L_13 = L_12;
		RuntimeObject* L_14 = (L_11)->GetAt(static_cast<il2cpp_array_size_t>(L_13));
		V_5 = L_14;
		StringBuilder_t* L_15 = V_0;
		RuntimeObject* L_16 = V_5;
		String_t* L_17;
		L_17 = _AndroidJNIHelper_GetSignature_m414A7A6B98FB5565075E4C51F22C482F2BCEEF5F(L_16, NULL);
		NullCheck(L_15);
		StringBuilder_t* L_18;
		L_18 = StringBuilder_Append_m08904D74E0C78E5F36DCD9C9303BDD07886D9F7D(L_15, L_17, NULL);
		int32_t L_19 = V_4;
		V_4 = ((int32_t)il2cpp_codegen_add(L_19, 1));
	}

IL_005f:
	{
		int32_t L_20 = V_4;
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_21 = V_3;
		NullCheck(L_21);
		if ((((int32_t)L_20) < ((int32_t)((int32_t)(((RuntimeArray*)L_21)->max_length)))))
		{
			goto IL_0043;
		}
	}
	{
		StringBuilder_t* L_22 = V_0;
		NullCheck(L_22);
		StringBuilder_t* L_23;
		L_23 = StringBuilder_Append_m71228B30F05724CD2CD96D9611DCD61BFB96A6E1(L_22, (Il2CppChar)((int32_t)41), NULL);
		StringBuilder_t* L_24 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_25 = { reinterpret_cast<intptr_t> (il2cpp_rgctx_type(method->rgctx_data, 0)) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_26;
		L_26 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_25, NULL);
		String_t* L_27;
		L_27 = _AndroidJNIHelper_GetSignature_m414A7A6B98FB5565075E4C51F22C482F2BCEEF5F((RuntimeObject*)L_26, NULL);
		NullCheck(L_24);
		StringBuilder_t* L_28;
		L_28 = StringBuilder_Append_m08904D74E0C78E5F36DCD9C9303BDD07886D9F7D(L_24, L_27, NULL);
		StringBuilder_t* L_29 = V_0;
		NullCheck((RuntimeObject*)L_29);
		String_t* L_30;
		L_30 = VirtualFuncInvoker0< String_t* >::Invoke(3, (RuntimeObject*)L_29);
		V_2 = L_30;
		goto IL_008e;
	}

IL_008e:
	{
		String_t* L_31 = V_2;
		return L_31;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR String_t* _AndroidJNIHelper_GetSignature_TisChar_t521A6F19B456D956AF452D926C32709DC03D6B17_mD783834059E75BFC7A7FEB544B6ABA307E91B2C4_gshared (ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* ___0_args, const RuntimeMethod* method) 
{
	if (!il2cpp_rgctx_is_initialized(method))
	{
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&StringBuilder_t_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Type_t_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&_stringLiteral622F5FF68A93093A1D312703FF92713F8BF2C946);
		il2cpp_rgctx_method_init(method);
	}
	StringBuilder_t* V_0 = NULL;
	bool V_1 = false;
	String_t* V_2 = NULL;
	ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* V_3 = NULL;
	int32_t V_4 = 0;
	RuntimeObject* V_5 = NULL;
	int32_t G_B3_0 = 0;
	{
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_0 = ___0_args;
		if (!L_0)
		{
			goto IL_000b;
		}
	}
	{
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_1 = ___0_args;
		NullCheck(L_1);
		G_B3_0 = ((((int32_t)(((RuntimeArray*)L_1)->max_length)) == ((int32_t)0))? 1 : 0);
		goto IL_000c;
	}

IL_000b:
	{
		G_B3_0 = 1;
	}

IL_000c:
	{
		V_1 = (bool)G_B3_0;
		bool L_2 = V_1;
		if (!L_2)
		{
			goto IL_002c;
		}
	}
	{
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_3 = { reinterpret_cast<intptr_t> (il2cpp_rgctx_type(method->rgctx_data, 0)) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_4;
		L_4 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_3, NULL);
		String_t* L_5;
		L_5 = _AndroidJNIHelper_GetSignature_m414A7A6B98FB5565075E4C51F22C482F2BCEEF5F((RuntimeObject*)L_4, NULL);
		String_t* L_6;
		L_6 = String_Concat_m9E3155FB84015C823606188F53B47CB44C444991(_stringLiteral622F5FF68A93093A1D312703FF92713F8BF2C946, L_5, NULL);
		V_2 = L_6;
		goto IL_008e;
	}

IL_002c:
	{
		StringBuilder_t* L_7 = (StringBuilder_t*)il2cpp_codegen_object_new(StringBuilder_t_il2cpp_TypeInfo_var);
		StringBuilder__ctor_m1D99713357DE05DAFA296633639DB55F8C30587D(L_7, NULL);
		V_0 = L_7;
		StringBuilder_t* L_8 = V_0;
		NullCheck(L_8);
		StringBuilder_t* L_9;
		L_9 = StringBuilder_Append_m71228B30F05724CD2CD96D9611DCD61BFB96A6E1(L_8, (Il2CppChar)((int32_t)40), NULL);
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_10 = ___0_args;
		V_3 = L_10;
		V_4 = 0;
		goto IL_005f;
	}

IL_0043:
	{
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_11 = V_3;
		int32_t L_12 = V_4;
		NullCheck(L_11);
		int32_t L_13 = L_12;
		RuntimeObject* L_14 = (L_11)->GetAt(static_cast<il2cpp_array_size_t>(L_13));
		V_5 = L_14;
		StringBuilder_t* L_15 = V_0;
		RuntimeObject* L_16 = V_5;
		String_t* L_17;
		L_17 = _AndroidJNIHelper_GetSignature_m414A7A6B98FB5565075E4C51F22C482F2BCEEF5F(L_16, NULL);
		NullCheck(L_15);
		StringBuilder_t* L_18;
		L_18 = StringBuilder_Append_m08904D74E0C78E5F36DCD9C9303BDD07886D9F7D(L_15, L_17, NULL);
		int32_t L_19 = V_4;
		V_4 = ((int32_t)il2cpp_codegen_add(L_19, 1));
	}

IL_005f:
	{
		int32_t L_20 = V_4;
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_21 = V_3;
		NullCheck(L_21);
		if ((((int32_t)L_20) < ((int32_t)((int32_t)(((RuntimeArray*)L_21)->max_length)))))
		{
			goto IL_0043;
		}
	}
	{
		StringBuilder_t* L_22 = V_0;
		NullCheck(L_22);
		StringBuilder_t* L_23;
		L_23 = StringBuilder_Append_m71228B30F05724CD2CD96D9611DCD61BFB96A6E1(L_22, (Il2CppChar)((int32_t)41), NULL);
		StringBuilder_t* L_24 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_25 = { reinterpret_cast<intptr_t> (il2cpp_rgctx_type(method->rgctx_data, 0)) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_26;
		L_26 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_25, NULL);
		String_t* L_27;
		L_27 = _AndroidJNIHelper_GetSignature_m414A7A6B98FB5565075E4C51F22C482F2BCEEF5F((RuntimeObject*)L_26, NULL);
		NullCheck(L_24);
		StringBuilder_t* L_28;
		L_28 = StringBuilder_Append_m08904D74E0C78E5F36DCD9C9303BDD07886D9F7D(L_24, L_27, NULL);
		StringBuilder_t* L_29 = V_0;
		NullCheck((RuntimeObject*)L_29);
		String_t* L_30;
		L_30 = VirtualFuncInvoker0< String_t* >::Invoke(3, (RuntimeObject*)L_29);
		V_2 = L_30;
		goto IL_008e;
	}

IL_008e:
	{
		String_t* L_31 = V_2;
		return L_31;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR String_t* _AndroidJNIHelper_GetSignature_TisDouble_tE150EF3D1D43DEE85D533810AB4C742307EEDE5F_m74C4D07DCE96BE5E61ED2AAED270DF7469C5F341_gshared (ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* ___0_args, const RuntimeMethod* method) 
{
	if (!il2cpp_rgctx_is_initialized(method))
	{
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&StringBuilder_t_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Type_t_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&_stringLiteral622F5FF68A93093A1D312703FF92713F8BF2C946);
		il2cpp_rgctx_method_init(method);
	}
	StringBuilder_t* V_0 = NULL;
	bool V_1 = false;
	String_t* V_2 = NULL;
	ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* V_3 = NULL;
	int32_t V_4 = 0;
	RuntimeObject* V_5 = NULL;
	int32_t G_B3_0 = 0;
	{
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_0 = ___0_args;
		if (!L_0)
		{
			goto IL_000b;
		}
	}
	{
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_1 = ___0_args;
		NullCheck(L_1);
		G_B3_0 = ((((int32_t)(((RuntimeArray*)L_1)->max_length)) == ((int32_t)0))? 1 : 0);
		goto IL_000c;
	}

IL_000b:
	{
		G_B3_0 = 1;
	}

IL_000c:
	{
		V_1 = (bool)G_B3_0;
		bool L_2 = V_1;
		if (!L_2)
		{
			goto IL_002c;
		}
	}
	{
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_3 = { reinterpret_cast<intptr_t> (il2cpp_rgctx_type(method->rgctx_data, 0)) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_4;
		L_4 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_3, NULL);
		String_t* L_5;
		L_5 = _AndroidJNIHelper_GetSignature_m414A7A6B98FB5565075E4C51F22C482F2BCEEF5F((RuntimeObject*)L_4, NULL);
		String_t* L_6;
		L_6 = String_Concat_m9E3155FB84015C823606188F53B47CB44C444991(_stringLiteral622F5FF68A93093A1D312703FF92713F8BF2C946, L_5, NULL);
		V_2 = L_6;
		goto IL_008e;
	}

IL_002c:
	{
		StringBuilder_t* L_7 = (StringBuilder_t*)il2cpp_codegen_object_new(StringBuilder_t_il2cpp_TypeInfo_var);
		StringBuilder__ctor_m1D99713357DE05DAFA296633639DB55F8C30587D(L_7, NULL);
		V_0 = L_7;
		StringBuilder_t* L_8 = V_0;
		NullCheck(L_8);
		StringBuilder_t* L_9;
		L_9 = StringBuilder_Append_m71228B30F05724CD2CD96D9611DCD61BFB96A6E1(L_8, (Il2CppChar)((int32_t)40), NULL);
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_10 = ___0_args;
		V_3 = L_10;
		V_4 = 0;
		goto IL_005f;
	}

IL_0043:
	{
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_11 = V_3;
		int32_t L_12 = V_4;
		NullCheck(L_11);
		int32_t L_13 = L_12;
		RuntimeObject* L_14 = (L_11)->GetAt(static_cast<il2cpp_array_size_t>(L_13));
		V_5 = L_14;
		StringBuilder_t* L_15 = V_0;
		RuntimeObject* L_16 = V_5;
		String_t* L_17;
		L_17 = _AndroidJNIHelper_GetSignature_m414A7A6B98FB5565075E4C51F22C482F2BCEEF5F(L_16, NULL);
		NullCheck(L_15);
		StringBuilder_t* L_18;
		L_18 = StringBuilder_Append_m08904D74E0C78E5F36DCD9C9303BDD07886D9F7D(L_15, L_17, NULL);
		int32_t L_19 = V_4;
		V_4 = ((int32_t)il2cpp_codegen_add(L_19, 1));
	}

IL_005f:
	{
		int32_t L_20 = V_4;
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_21 = V_3;
		NullCheck(L_21);
		if ((((int32_t)L_20) < ((int32_t)((int32_t)(((RuntimeArray*)L_21)->max_length)))))
		{
			goto IL_0043;
		}
	}
	{
		StringBuilder_t* L_22 = V_0;
		NullCheck(L_22);
		StringBuilder_t* L_23;
		L_23 = StringBuilder_Append_m71228B30F05724CD2CD96D9611DCD61BFB96A6E1(L_22, (Il2CppChar)((int32_t)41), NULL);
		StringBuilder_t* L_24 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_25 = { reinterpret_cast<intptr_t> (il2cpp_rgctx_type(method->rgctx_data, 0)) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_26;
		L_26 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_25, NULL);
		String_t* L_27;
		L_27 = _AndroidJNIHelper_GetSignature_m414A7A6B98FB5565075E4C51F22C482F2BCEEF5F((RuntimeObject*)L_26, NULL);
		NullCheck(L_24);
		StringBuilder_t* L_28;
		L_28 = StringBuilder_Append_m08904D74E0C78E5F36DCD9C9303BDD07886D9F7D(L_24, L_27, NULL);
		StringBuilder_t* L_29 = V_0;
		NullCheck((RuntimeObject*)L_29);
		String_t* L_30;
		L_30 = VirtualFuncInvoker0< String_t* >::Invoke(3, (RuntimeObject*)L_29);
		V_2 = L_30;
		goto IL_008e;
	}

IL_008e:
	{
		String_t* L_31 = V_2;
		return L_31;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR String_t* _AndroidJNIHelper_GetSignature_TisInt16_tB8EF286A9C33492FA6E6D6E67320BE93E794A175_m1E079B67FDC93E1BBE5C29D9C2BC09338DA0A5AA_gshared (ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* ___0_args, const RuntimeMethod* method) 
{
	if (!il2cpp_rgctx_is_initialized(method))
	{
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&StringBuilder_t_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Type_t_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&_stringLiteral622F5FF68A93093A1D312703FF92713F8BF2C946);
		il2cpp_rgctx_method_init(method);
	}
	StringBuilder_t* V_0 = NULL;
	bool V_1 = false;
	String_t* V_2 = NULL;
	ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* V_3 = NULL;
	int32_t V_4 = 0;
	RuntimeObject* V_5 = NULL;
	int32_t G_B3_0 = 0;
	{
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_0 = ___0_args;
		if (!L_0)
		{
			goto IL_000b;
		}
	}
	{
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_1 = ___0_args;
		NullCheck(L_1);
		G_B3_0 = ((((int32_t)(((RuntimeArray*)L_1)->max_length)) == ((int32_t)0))? 1 : 0);
		goto IL_000c;
	}

IL_000b:
	{
		G_B3_0 = 1;
	}

IL_000c:
	{
		V_1 = (bool)G_B3_0;
		bool L_2 = V_1;
		if (!L_2)
		{
			goto IL_002c;
		}
	}
	{
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_3 = { reinterpret_cast<intptr_t> (il2cpp_rgctx_type(method->rgctx_data, 0)) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_4;
		L_4 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_3, NULL);
		String_t* L_5;
		L_5 = _AndroidJNIHelper_GetSignature_m414A7A6B98FB5565075E4C51F22C482F2BCEEF5F((RuntimeObject*)L_4, NULL);
		String_t* L_6;
		L_6 = String_Concat_m9E3155FB84015C823606188F53B47CB44C444991(_stringLiteral622F5FF68A93093A1D312703FF92713F8BF2C946, L_5, NULL);
		V_2 = L_6;
		goto IL_008e;
	}

IL_002c:
	{
		StringBuilder_t* L_7 = (StringBuilder_t*)il2cpp_codegen_object_new(StringBuilder_t_il2cpp_TypeInfo_var);
		StringBuilder__ctor_m1D99713357DE05DAFA296633639DB55F8C30587D(L_7, NULL);
		V_0 = L_7;
		StringBuilder_t* L_8 = V_0;
		NullCheck(L_8);
		StringBuilder_t* L_9;
		L_9 = StringBuilder_Append_m71228B30F05724CD2CD96D9611DCD61BFB96A6E1(L_8, (Il2CppChar)((int32_t)40), NULL);
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_10 = ___0_args;
		V_3 = L_10;
		V_4 = 0;
		goto IL_005f;
	}

IL_0043:
	{
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_11 = V_3;
		int32_t L_12 = V_4;
		NullCheck(L_11);
		int32_t L_13 = L_12;
		RuntimeObject* L_14 = (L_11)->GetAt(static_cast<il2cpp_array_size_t>(L_13));
		V_5 = L_14;
		StringBuilder_t* L_15 = V_0;
		RuntimeObject* L_16 = V_5;
		String_t* L_17;
		L_17 = _AndroidJNIHelper_GetSignature_m414A7A6B98FB5565075E4C51F22C482F2BCEEF5F(L_16, NULL);
		NullCheck(L_15);
		StringBuilder_t* L_18;
		L_18 = StringBuilder_Append_m08904D74E0C78E5F36DCD9C9303BDD07886D9F7D(L_15, L_17, NULL);
		int32_t L_19 = V_4;
		V_4 = ((int32_t)il2cpp_codegen_add(L_19, 1));
	}

IL_005f:
	{
		int32_t L_20 = V_4;
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_21 = V_3;
		NullCheck(L_21);
		if ((((int32_t)L_20) < ((int32_t)((int32_t)(((RuntimeArray*)L_21)->max_length)))))
		{
			goto IL_0043;
		}
	}
	{
		StringBuilder_t* L_22 = V_0;
		NullCheck(L_22);
		StringBuilder_t* L_23;
		L_23 = StringBuilder_Append_m71228B30F05724CD2CD96D9611DCD61BFB96A6E1(L_22, (Il2CppChar)((int32_t)41), NULL);
		StringBuilder_t* L_24 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_25 = { reinterpret_cast<intptr_t> (il2cpp_rgctx_type(method->rgctx_data, 0)) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_26;
		L_26 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_25, NULL);
		String_t* L_27;
		L_27 = _AndroidJNIHelper_GetSignature_m414A7A6B98FB5565075E4C51F22C482F2BCEEF5F((RuntimeObject*)L_26, NULL);
		NullCheck(L_24);
		StringBuilder_t* L_28;
		L_28 = StringBuilder_Append_m08904D74E0C78E5F36DCD9C9303BDD07886D9F7D(L_24, L_27, NULL);
		StringBuilder_t* L_29 = V_0;
		NullCheck((RuntimeObject*)L_29);
		String_t* L_30;
		L_30 = VirtualFuncInvoker0< String_t* >::Invoke(3, (RuntimeObject*)L_29);
		V_2 = L_30;
		goto IL_008e;
	}

IL_008e:
	{
		String_t* L_31 = V_2;
		return L_31;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR String_t* _AndroidJNIHelper_GetSignature_TisInt32_t680FF22E76F6EFAD4375103CBBFFA0421349384C_mA85CEF9411BD97B51F86CC460B32C46C2B873B12_gshared (ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* ___0_args, const RuntimeMethod* method) 
{
	if (!il2cpp_rgctx_is_initialized(method))
	{
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&StringBuilder_t_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Type_t_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&_stringLiteral622F5FF68A93093A1D312703FF92713F8BF2C946);
		il2cpp_rgctx_method_init(method);
	}
	StringBuilder_t* V_0 = NULL;
	bool V_1 = false;
	String_t* V_2 = NULL;
	ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* V_3 = NULL;
	int32_t V_4 = 0;
	RuntimeObject* V_5 = NULL;
	int32_t G_B3_0 = 0;
	{
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_0 = ___0_args;
		if (!L_0)
		{
			goto IL_000b;
		}
	}
	{
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_1 = ___0_args;
		NullCheck(L_1);
		G_B3_0 = ((((int32_t)(((RuntimeArray*)L_1)->max_length)) == ((int32_t)0))? 1 : 0);
		goto IL_000c;
	}

IL_000b:
	{
		G_B3_0 = 1;
	}

IL_000c:
	{
		V_1 = (bool)G_B3_0;
		bool L_2 = V_1;
		if (!L_2)
		{
			goto IL_002c;
		}
	}
	{
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_3 = { reinterpret_cast<intptr_t> (il2cpp_rgctx_type(method->rgctx_data, 0)) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_4;
		L_4 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_3, NULL);
		String_t* L_5;
		L_5 = _AndroidJNIHelper_GetSignature_m414A7A6B98FB5565075E4C51F22C482F2BCEEF5F((RuntimeObject*)L_4, NULL);
		String_t* L_6;
		L_6 = String_Concat_m9E3155FB84015C823606188F53B47CB44C444991(_stringLiteral622F5FF68A93093A1D312703FF92713F8BF2C946, L_5, NULL);
		V_2 = L_6;
		goto IL_008e;
	}

IL_002c:
	{
		StringBuilder_t* L_7 = (StringBuilder_t*)il2cpp_codegen_object_new(StringBuilder_t_il2cpp_TypeInfo_var);
		StringBuilder__ctor_m1D99713357DE05DAFA296633639DB55F8C30587D(L_7, NULL);
		V_0 = L_7;
		StringBuilder_t* L_8 = V_0;
		NullCheck(L_8);
		StringBuilder_t* L_9;
		L_9 = StringBuilder_Append_m71228B30F05724CD2CD96D9611DCD61BFB96A6E1(L_8, (Il2CppChar)((int32_t)40), NULL);
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_10 = ___0_args;
		V_3 = L_10;
		V_4 = 0;
		goto IL_005f;
	}

IL_0043:
	{
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_11 = V_3;
		int32_t L_12 = V_4;
		NullCheck(L_11);
		int32_t L_13 = L_12;
		RuntimeObject* L_14 = (L_11)->GetAt(static_cast<il2cpp_array_size_t>(L_13));
		V_5 = L_14;
		StringBuilder_t* L_15 = V_0;
		RuntimeObject* L_16 = V_5;
		String_t* L_17;
		L_17 = _AndroidJNIHelper_GetSignature_m414A7A6B98FB5565075E4C51F22C482F2BCEEF5F(L_16, NULL);
		NullCheck(L_15);
		StringBuilder_t* L_18;
		L_18 = StringBuilder_Append_m08904D74E0C78E5F36DCD9C9303BDD07886D9F7D(L_15, L_17, NULL);
		int32_t L_19 = V_4;
		V_4 = ((int32_t)il2cpp_codegen_add(L_19, 1));
	}

IL_005f:
	{
		int32_t L_20 = V_4;
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_21 = V_3;
		NullCheck(L_21);
		if ((((int32_t)L_20) < ((int32_t)((int32_t)(((RuntimeArray*)L_21)->max_length)))))
		{
			goto IL_0043;
		}
	}
	{
		StringBuilder_t* L_22 = V_0;
		NullCheck(L_22);
		StringBuilder_t* L_23;
		L_23 = StringBuilder_Append_m71228B30F05724CD2CD96D9611DCD61BFB96A6E1(L_22, (Il2CppChar)((int32_t)41), NULL);
		StringBuilder_t* L_24 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_25 = { reinterpret_cast<intptr_t> (il2cpp_rgctx_type(method->rgctx_data, 0)) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_26;
		L_26 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_25, NULL);
		String_t* L_27;
		L_27 = _AndroidJNIHelper_GetSignature_m414A7A6B98FB5565075E4C51F22C482F2BCEEF5F((RuntimeObject*)L_26, NULL);
		NullCheck(L_24);
		StringBuilder_t* L_28;
		L_28 = StringBuilder_Append_m08904D74E0C78E5F36DCD9C9303BDD07886D9F7D(L_24, L_27, NULL);
		StringBuilder_t* L_29 = V_0;
		NullCheck((RuntimeObject*)L_29);
		String_t* L_30;
		L_30 = VirtualFuncInvoker0< String_t* >::Invoke(3, (RuntimeObject*)L_29);
		V_2 = L_30;
		goto IL_008e;
	}

IL_008e:
	{
		String_t* L_31 = V_2;
		return L_31;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR String_t* _AndroidJNIHelper_GetSignature_TisInt64_t092CFB123BE63C28ACDAF65C68F21A526050DBA3_m847042ADF26044DDB60469E1C3477EBBB1B55E11_gshared (ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* ___0_args, const RuntimeMethod* method) 
{
	if (!il2cpp_rgctx_is_initialized(method))
	{
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&StringBuilder_t_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Type_t_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&_stringLiteral622F5FF68A93093A1D312703FF92713F8BF2C946);
		il2cpp_rgctx_method_init(method);
	}
	StringBuilder_t* V_0 = NULL;
	bool V_1 = false;
	String_t* V_2 = NULL;
	ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* V_3 = NULL;
	int32_t V_4 = 0;
	RuntimeObject* V_5 = NULL;
	int32_t G_B3_0 = 0;
	{
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_0 = ___0_args;
		if (!L_0)
		{
			goto IL_000b;
		}
	}
	{
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_1 = ___0_args;
		NullCheck(L_1);
		G_B3_0 = ((((int32_t)(((RuntimeArray*)L_1)->max_length)) == ((int32_t)0))? 1 : 0);
		goto IL_000c;
	}

IL_000b:
	{
		G_B3_0 = 1;
	}

IL_000c:
	{
		V_1 = (bool)G_B3_0;
		bool L_2 = V_1;
		if (!L_2)
		{
			goto IL_002c;
		}
	}
	{
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_3 = { reinterpret_cast<intptr_t> (il2cpp_rgctx_type(method->rgctx_data, 0)) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_4;
		L_4 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_3, NULL);
		String_t* L_5;
		L_5 = _AndroidJNIHelper_GetSignature_m414A7A6B98FB5565075E4C51F22C482F2BCEEF5F((RuntimeObject*)L_4, NULL);
		String_t* L_6;
		L_6 = String_Concat_m9E3155FB84015C823606188F53B47CB44C444991(_stringLiteral622F5FF68A93093A1D312703FF92713F8BF2C946, L_5, NULL);
		V_2 = L_6;
		goto IL_008e;
	}

IL_002c:
	{
		StringBuilder_t* L_7 = (StringBuilder_t*)il2cpp_codegen_object_new(StringBuilder_t_il2cpp_TypeInfo_var);
		StringBuilder__ctor_m1D99713357DE05DAFA296633639DB55F8C30587D(L_7, NULL);
		V_0 = L_7;
		StringBuilder_t* L_8 = V_0;
		NullCheck(L_8);
		StringBuilder_t* L_9;
		L_9 = StringBuilder_Append_m71228B30F05724CD2CD96D9611DCD61BFB96A6E1(L_8, (Il2CppChar)((int32_t)40), NULL);
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_10 = ___0_args;
		V_3 = L_10;
		V_4 = 0;
		goto IL_005f;
	}

IL_0043:
	{
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_11 = V_3;
		int32_t L_12 = V_4;
		NullCheck(L_11);
		int32_t L_13 = L_12;
		RuntimeObject* L_14 = (L_11)->GetAt(static_cast<il2cpp_array_size_t>(L_13));
		V_5 = L_14;
		StringBuilder_t* L_15 = V_0;
		RuntimeObject* L_16 = V_5;
		String_t* L_17;
		L_17 = _AndroidJNIHelper_GetSignature_m414A7A6B98FB5565075E4C51F22C482F2BCEEF5F(L_16, NULL);
		NullCheck(L_15);
		StringBuilder_t* L_18;
		L_18 = StringBuilder_Append_m08904D74E0C78E5F36DCD9C9303BDD07886D9F7D(L_15, L_17, NULL);
		int32_t L_19 = V_4;
		V_4 = ((int32_t)il2cpp_codegen_add(L_19, 1));
	}

IL_005f:
	{
		int32_t L_20 = V_4;
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_21 = V_3;
		NullCheck(L_21);
		if ((((int32_t)L_20) < ((int32_t)((int32_t)(((RuntimeArray*)L_21)->max_length)))))
		{
			goto IL_0043;
		}
	}
	{
		StringBuilder_t* L_22 = V_0;
		NullCheck(L_22);
		StringBuilder_t* L_23;
		L_23 = StringBuilder_Append_m71228B30F05724CD2CD96D9611DCD61BFB96A6E1(L_22, (Il2CppChar)((int32_t)41), NULL);
		StringBuilder_t* L_24 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_25 = { reinterpret_cast<intptr_t> (il2cpp_rgctx_type(method->rgctx_data, 0)) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_26;
		L_26 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_25, NULL);
		String_t* L_27;
		L_27 = _AndroidJNIHelper_GetSignature_m414A7A6B98FB5565075E4C51F22C482F2BCEEF5F((RuntimeObject*)L_26, NULL);
		NullCheck(L_24);
		StringBuilder_t* L_28;
		L_28 = StringBuilder_Append_m08904D74E0C78E5F36DCD9C9303BDD07886D9F7D(L_24, L_27, NULL);
		StringBuilder_t* L_29 = V_0;
		NullCheck((RuntimeObject*)L_29);
		String_t* L_30;
		L_30 = VirtualFuncInvoker0< String_t* >::Invoke(3, (RuntimeObject*)L_29);
		V_2 = L_30;
		goto IL_008e;
	}

IL_008e:
	{
		String_t* L_31 = V_2;
		return L_31;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR String_t* _AndroidJNIHelper_GetSignature_TisRuntimeObject_m7CC50A493D0C6897ECB2692A7CEFB3A2CD3655A5_gshared (ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* ___0_args, const RuntimeMethod* method) 
{
	if (!il2cpp_rgctx_is_initialized(method))
	{
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&StringBuilder_t_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Type_t_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&_stringLiteral622F5FF68A93093A1D312703FF92713F8BF2C946);
		il2cpp_rgctx_method_init(method);
	}
	StringBuilder_t* V_0 = NULL;
	bool V_1 = false;
	String_t* V_2 = NULL;
	ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* V_3 = NULL;
	int32_t V_4 = 0;
	RuntimeObject* V_5 = NULL;
	int32_t G_B3_0 = 0;
	{
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_0 = ___0_args;
		if (!L_0)
		{
			goto IL_000b;
		}
	}
	{
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_1 = ___0_args;
		NullCheck(L_1);
		G_B3_0 = ((((int32_t)(((RuntimeArray*)L_1)->max_length)) == ((int32_t)0))? 1 : 0);
		goto IL_000c;
	}

IL_000b:
	{
		G_B3_0 = 1;
	}

IL_000c:
	{
		V_1 = (bool)G_B3_0;
		bool L_2 = V_1;
		if (!L_2)
		{
			goto IL_002c;
		}
	}
	{
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_3 = { reinterpret_cast<intptr_t> (il2cpp_rgctx_type(method->rgctx_data, 0)) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_4;
		L_4 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_3, NULL);
		String_t* L_5;
		L_5 = _AndroidJNIHelper_GetSignature_m414A7A6B98FB5565075E4C51F22C482F2BCEEF5F((RuntimeObject*)L_4, NULL);
		String_t* L_6;
		L_6 = String_Concat_m9E3155FB84015C823606188F53B47CB44C444991(_stringLiteral622F5FF68A93093A1D312703FF92713F8BF2C946, L_5, NULL);
		V_2 = L_6;
		goto IL_008e;
	}

IL_002c:
	{
		StringBuilder_t* L_7 = (StringBuilder_t*)il2cpp_codegen_object_new(StringBuilder_t_il2cpp_TypeInfo_var);
		StringBuilder__ctor_m1D99713357DE05DAFA296633639DB55F8C30587D(L_7, NULL);
		V_0 = L_7;
		StringBuilder_t* L_8 = V_0;
		NullCheck(L_8);
		StringBuilder_t* L_9;
		L_9 = StringBuilder_Append_m71228B30F05724CD2CD96D9611DCD61BFB96A6E1(L_8, (Il2CppChar)((int32_t)40), NULL);
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_10 = ___0_args;
		V_3 = L_10;
		V_4 = 0;
		goto IL_005f;
	}

IL_0043:
	{
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_11 = V_3;
		int32_t L_12 = V_4;
		NullCheck(L_11);
		int32_t L_13 = L_12;
		RuntimeObject* L_14 = (L_11)->GetAt(static_cast<il2cpp_array_size_t>(L_13));
		V_5 = L_14;
		StringBuilder_t* L_15 = V_0;
		RuntimeObject* L_16 = V_5;
		String_t* L_17;
		L_17 = _AndroidJNIHelper_GetSignature_m414A7A6B98FB5565075E4C51F22C482F2BCEEF5F(L_16, NULL);
		NullCheck(L_15);
		StringBuilder_t* L_18;
		L_18 = StringBuilder_Append_m08904D74E0C78E5F36DCD9C9303BDD07886D9F7D(L_15, L_17, NULL);
		int32_t L_19 = V_4;
		V_4 = ((int32_t)il2cpp_codegen_add(L_19, 1));
	}

IL_005f:
	{
		int32_t L_20 = V_4;
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_21 = V_3;
		NullCheck(L_21);
		if ((((int32_t)L_20) < ((int32_t)((int32_t)(((RuntimeArray*)L_21)->max_length)))))
		{
			goto IL_0043;
		}
	}
	{
		StringBuilder_t* L_22 = V_0;
		NullCheck(L_22);
		StringBuilder_t* L_23;
		L_23 = StringBuilder_Append_m71228B30F05724CD2CD96D9611DCD61BFB96A6E1(L_22, (Il2CppChar)((int32_t)41), NULL);
		StringBuilder_t* L_24 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_25 = { reinterpret_cast<intptr_t> (il2cpp_rgctx_type(method->rgctx_data, 0)) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_26;
		L_26 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_25, NULL);
		String_t* L_27;
		L_27 = _AndroidJNIHelper_GetSignature_m414A7A6B98FB5565075E4C51F22C482F2BCEEF5F((RuntimeObject*)L_26, NULL);
		NullCheck(L_24);
		StringBuilder_t* L_28;
		L_28 = StringBuilder_Append_m08904D74E0C78E5F36DCD9C9303BDD07886D9F7D(L_24, L_27, NULL);
		StringBuilder_t* L_29 = V_0;
		NullCheck((RuntimeObject*)L_29);
		String_t* L_30;
		L_30 = VirtualFuncInvoker0< String_t* >::Invoke(3, (RuntimeObject*)L_29);
		V_2 = L_30;
		goto IL_008e;
	}

IL_008e:
	{
		String_t* L_31 = V_2;
		return L_31;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR String_t* _AndroidJNIHelper_GetSignature_TisSByte_tFEFFEF5D2FEBF5207950AE6FAC150FC53B668DB5_mEAD40CF5E1A04E27AE3991DAB10ABB9EC6F37FBB_gshared (ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* ___0_args, const RuntimeMethod* method) 
{
	if (!il2cpp_rgctx_is_initialized(method))
	{
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&StringBuilder_t_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Type_t_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&_stringLiteral622F5FF68A93093A1D312703FF92713F8BF2C946);
		il2cpp_rgctx_method_init(method);
	}
	StringBuilder_t* V_0 = NULL;
	bool V_1 = false;
	String_t* V_2 = NULL;
	ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* V_3 = NULL;
	int32_t V_4 = 0;
	RuntimeObject* V_5 = NULL;
	int32_t G_B3_0 = 0;
	{
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_0 = ___0_args;
		if (!L_0)
		{
			goto IL_000b;
		}
	}
	{
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_1 = ___0_args;
		NullCheck(L_1);
		G_B3_0 = ((((int32_t)(((RuntimeArray*)L_1)->max_length)) == ((int32_t)0))? 1 : 0);
		goto IL_000c;
	}

IL_000b:
	{
		G_B3_0 = 1;
	}

IL_000c:
	{
		V_1 = (bool)G_B3_0;
		bool L_2 = V_1;
		if (!L_2)
		{
			goto IL_002c;
		}
	}
	{
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_3 = { reinterpret_cast<intptr_t> (il2cpp_rgctx_type(method->rgctx_data, 0)) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_4;
		L_4 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_3, NULL);
		String_t* L_5;
		L_5 = _AndroidJNIHelper_GetSignature_m414A7A6B98FB5565075E4C51F22C482F2BCEEF5F((RuntimeObject*)L_4, NULL);
		String_t* L_6;
		L_6 = String_Concat_m9E3155FB84015C823606188F53B47CB44C444991(_stringLiteral622F5FF68A93093A1D312703FF92713F8BF2C946, L_5, NULL);
		V_2 = L_6;
		goto IL_008e;
	}

IL_002c:
	{
		StringBuilder_t* L_7 = (StringBuilder_t*)il2cpp_codegen_object_new(StringBuilder_t_il2cpp_TypeInfo_var);
		StringBuilder__ctor_m1D99713357DE05DAFA296633639DB55F8C30587D(L_7, NULL);
		V_0 = L_7;
		StringBuilder_t* L_8 = V_0;
		NullCheck(L_8);
		StringBuilder_t* L_9;
		L_9 = StringBuilder_Append_m71228B30F05724CD2CD96D9611DCD61BFB96A6E1(L_8, (Il2CppChar)((int32_t)40), NULL);
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_10 = ___0_args;
		V_3 = L_10;
		V_4 = 0;
		goto IL_005f;
	}

IL_0043:
	{
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_11 = V_3;
		int32_t L_12 = V_4;
		NullCheck(L_11);
		int32_t L_13 = L_12;
		RuntimeObject* L_14 = (L_11)->GetAt(static_cast<il2cpp_array_size_t>(L_13));
		V_5 = L_14;
		StringBuilder_t* L_15 = V_0;
		RuntimeObject* L_16 = V_5;
		String_t* L_17;
		L_17 = _AndroidJNIHelper_GetSignature_m414A7A6B98FB5565075E4C51F22C482F2BCEEF5F(L_16, NULL);
		NullCheck(L_15);
		StringBuilder_t* L_18;
		L_18 = StringBuilder_Append_m08904D74E0C78E5F36DCD9C9303BDD07886D9F7D(L_15, L_17, NULL);
		int32_t L_19 = V_4;
		V_4 = ((int32_t)il2cpp_codegen_add(L_19, 1));
	}

IL_005f:
	{
		int32_t L_20 = V_4;
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_21 = V_3;
		NullCheck(L_21);
		if ((((int32_t)L_20) < ((int32_t)((int32_t)(((RuntimeArray*)L_21)->max_length)))))
		{
			goto IL_0043;
		}
	}
	{
		StringBuilder_t* L_22 = V_0;
		NullCheck(L_22);
		StringBuilder_t* L_23;
		L_23 = StringBuilder_Append_m71228B30F05724CD2CD96D9611DCD61BFB96A6E1(L_22, (Il2CppChar)((int32_t)41), NULL);
		StringBuilder_t* L_24 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_25 = { reinterpret_cast<intptr_t> (il2cpp_rgctx_type(method->rgctx_data, 0)) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_26;
		L_26 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_25, NULL);
		String_t* L_27;
		L_27 = _AndroidJNIHelper_GetSignature_m414A7A6B98FB5565075E4C51F22C482F2BCEEF5F((RuntimeObject*)L_26, NULL);
		NullCheck(L_24);
		StringBuilder_t* L_28;
		L_28 = StringBuilder_Append_m08904D74E0C78E5F36DCD9C9303BDD07886D9F7D(L_24, L_27, NULL);
		StringBuilder_t* L_29 = V_0;
		NullCheck((RuntimeObject*)L_29);
		String_t* L_30;
		L_30 = VirtualFuncInvoker0< String_t* >::Invoke(3, (RuntimeObject*)L_29);
		V_2 = L_30;
		goto IL_008e;
	}

IL_008e:
	{
		String_t* L_31 = V_2;
		return L_31;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR String_t* _AndroidJNIHelper_GetSignature_TisSingle_t4530F2FF86FCB0DC29F35385CA1BD21BE294761C_mDD367BE518367698F0093E97FCF201D89B5790CB_gshared (ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* ___0_args, const RuntimeMethod* method) 
{
	if (!il2cpp_rgctx_is_initialized(method))
	{
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&StringBuilder_t_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Type_t_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&_stringLiteral622F5FF68A93093A1D312703FF92713F8BF2C946);
		il2cpp_rgctx_method_init(method);
	}
	StringBuilder_t* V_0 = NULL;
	bool V_1 = false;
	String_t* V_2 = NULL;
	ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* V_3 = NULL;
	int32_t V_4 = 0;
	RuntimeObject* V_5 = NULL;
	int32_t G_B3_0 = 0;
	{
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_0 = ___0_args;
		if (!L_0)
		{
			goto IL_000b;
		}
	}
	{
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_1 = ___0_args;
		NullCheck(L_1);
		G_B3_0 = ((((int32_t)(((RuntimeArray*)L_1)->max_length)) == ((int32_t)0))? 1 : 0);
		goto IL_000c;
	}

IL_000b:
	{
		G_B3_0 = 1;
	}

IL_000c:
	{
		V_1 = (bool)G_B3_0;
		bool L_2 = V_1;
		if (!L_2)
		{
			goto IL_002c;
		}
	}
	{
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_3 = { reinterpret_cast<intptr_t> (il2cpp_rgctx_type(method->rgctx_data, 0)) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_4;
		L_4 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_3, NULL);
		String_t* L_5;
		L_5 = _AndroidJNIHelper_GetSignature_m414A7A6B98FB5565075E4C51F22C482F2BCEEF5F((RuntimeObject*)L_4, NULL);
		String_t* L_6;
		L_6 = String_Concat_m9E3155FB84015C823606188F53B47CB44C444991(_stringLiteral622F5FF68A93093A1D312703FF92713F8BF2C946, L_5, NULL);
		V_2 = L_6;
		goto IL_008e;
	}

IL_002c:
	{
		StringBuilder_t* L_7 = (StringBuilder_t*)il2cpp_codegen_object_new(StringBuilder_t_il2cpp_TypeInfo_var);
		StringBuilder__ctor_m1D99713357DE05DAFA296633639DB55F8C30587D(L_7, NULL);
		V_0 = L_7;
		StringBuilder_t* L_8 = V_0;
		NullCheck(L_8);
		StringBuilder_t* L_9;
		L_9 = StringBuilder_Append_m71228B30F05724CD2CD96D9611DCD61BFB96A6E1(L_8, (Il2CppChar)((int32_t)40), NULL);
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_10 = ___0_args;
		V_3 = L_10;
		V_4 = 0;
		goto IL_005f;
	}

IL_0043:
	{
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_11 = V_3;
		int32_t L_12 = V_4;
		NullCheck(L_11);
		int32_t L_13 = L_12;
		RuntimeObject* L_14 = (L_11)->GetAt(static_cast<il2cpp_array_size_t>(L_13));
		V_5 = L_14;
		StringBuilder_t* L_15 = V_0;
		RuntimeObject* L_16 = V_5;
		String_t* L_17;
		L_17 = _AndroidJNIHelper_GetSignature_m414A7A6B98FB5565075E4C51F22C482F2BCEEF5F(L_16, NULL);
		NullCheck(L_15);
		StringBuilder_t* L_18;
		L_18 = StringBuilder_Append_m08904D74E0C78E5F36DCD9C9303BDD07886D9F7D(L_15, L_17, NULL);
		int32_t L_19 = V_4;
		V_4 = ((int32_t)il2cpp_codegen_add(L_19, 1));
	}

IL_005f:
	{
		int32_t L_20 = V_4;
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_21 = V_3;
		NullCheck(L_21);
		if ((((int32_t)L_20) < ((int32_t)((int32_t)(((RuntimeArray*)L_21)->max_length)))))
		{
			goto IL_0043;
		}
	}
	{
		StringBuilder_t* L_22 = V_0;
		NullCheck(L_22);
		StringBuilder_t* L_23;
		L_23 = StringBuilder_Append_m71228B30F05724CD2CD96D9611DCD61BFB96A6E1(L_22, (Il2CppChar)((int32_t)41), NULL);
		StringBuilder_t* L_24 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_25 = { reinterpret_cast<intptr_t> (il2cpp_rgctx_type(method->rgctx_data, 0)) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_26;
		L_26 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_25, NULL);
		String_t* L_27;
		L_27 = _AndroidJNIHelper_GetSignature_m414A7A6B98FB5565075E4C51F22C482F2BCEEF5F((RuntimeObject*)L_26, NULL);
		NullCheck(L_24);
		StringBuilder_t* L_28;
		L_28 = StringBuilder_Append_m08904D74E0C78E5F36DCD9C9303BDD07886D9F7D(L_24, L_27, NULL);
		StringBuilder_t* L_29 = V_0;
		NullCheck((RuntimeObject*)L_29);
		String_t* L_30;
		L_30 = VirtualFuncInvoker0< String_t* >::Invoke(3, (RuntimeObject*)L_29);
		V_2 = L_30;
		goto IL_008e;
	}

IL_008e:
	{
		String_t* L_31 = V_2;
		return L_31;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR String_t* _AndroidJNIHelper_GetSignature_TisIl2CppFullySharedGenericAny_m5BFF8BF215EBBD2B94DB67B384DAB97E221FA134_gshared (ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* ___0_args, const RuntimeMethod* method) 
{
	if (!il2cpp_rgctx_is_initialized(method))
	{
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&StringBuilder_t_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Type_t_il2cpp_TypeInfo_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&_stringLiteral622F5FF68A93093A1D312703FF92713F8BF2C946);
		il2cpp_rgctx_method_init(method);
	}
	StringBuilder_t* V_0 = NULL;
	bool V_1 = false;
	String_t* V_2 = NULL;
	ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* V_3 = NULL;
	int32_t V_4 = 0;
	RuntimeObject* V_5 = NULL;
	int32_t G_B3_0 = 0;
	{
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_0 = ___0_args;
		if (!L_0)
		{
			goto IL_000b;
		}
	}
	{
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_1 = ___0_args;
		NullCheck(L_1);
		G_B3_0 = ((((int32_t)(((RuntimeArray*)L_1)->max_length)) == ((int32_t)0))? 1 : 0);
		goto IL_000c;
	}

IL_000b:
	{
		G_B3_0 = 1;
	}

IL_000c:
	{
		V_1 = (bool)G_B3_0;
		bool L_2 = V_1;
		if (!L_2)
		{
			goto IL_002c;
		}
	}
	{
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_3 = { reinterpret_cast<intptr_t> (il2cpp_rgctx_type(method->rgctx_data, 0)) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_4;
		L_4 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_3, NULL);
		String_t* L_5;
		L_5 = _AndroidJNIHelper_GetSignature_m414A7A6B98FB5565075E4C51F22C482F2BCEEF5F((RuntimeObject*)L_4, NULL);
		String_t* L_6;
		L_6 = String_Concat_m9E3155FB84015C823606188F53B47CB44C444991(_stringLiteral622F5FF68A93093A1D312703FF92713F8BF2C946, L_5, NULL);
		V_2 = L_6;
		goto IL_008e;
	}

IL_002c:
	{
		StringBuilder_t* L_7 = (StringBuilder_t*)il2cpp_codegen_object_new(StringBuilder_t_il2cpp_TypeInfo_var);
		StringBuilder__ctor_m1D99713357DE05DAFA296633639DB55F8C30587D(L_7, NULL);
		V_0 = L_7;
		StringBuilder_t* L_8 = V_0;
		NullCheck(L_8);
		StringBuilder_t* L_9;
		L_9 = StringBuilder_Append_m71228B30F05724CD2CD96D9611DCD61BFB96A6E1(L_8, (Il2CppChar)((int32_t)40), NULL);
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_10 = ___0_args;
		V_3 = L_10;
		V_4 = 0;
		goto IL_005f;
	}

IL_0043:
	{
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_11 = V_3;
		int32_t L_12 = V_4;
		NullCheck(L_11);
		int32_t L_13 = L_12;
		RuntimeObject* L_14 = (L_11)->GetAt(static_cast<il2cpp_array_size_t>(L_13));
		V_5 = L_14;
		StringBuilder_t* L_15 = V_0;
		RuntimeObject* L_16 = V_5;
		String_t* L_17;
		L_17 = _AndroidJNIHelper_GetSignature_m414A7A6B98FB5565075E4C51F22C482F2BCEEF5F(L_16, NULL);
		NullCheck(L_15);
		StringBuilder_t* L_18;
		L_18 = StringBuilder_Append_m08904D74E0C78E5F36DCD9C9303BDD07886D9F7D(L_15, L_17, NULL);
		int32_t L_19 = V_4;
		V_4 = ((int32_t)il2cpp_codegen_add(L_19, 1));
	}

IL_005f:
	{
		int32_t L_20 = V_4;
		ObjectU5BU5D_t8061030B0A12A55D5AD8652A20C922FE99450918* L_21 = V_3;
		NullCheck(L_21);
		if ((((int32_t)L_20) < ((int32_t)((int32_t)(((RuntimeArray*)L_21)->max_length)))))
		{
			goto IL_0043;
		}
	}
	{
		StringBuilder_t* L_22 = V_0;
		NullCheck(L_22);
		StringBuilder_t* L_23;
		L_23 = StringBuilder_Append_m71228B30F05724CD2CD96D9611DCD61BFB96A6E1(L_22, (Il2CppChar)((int32_t)41), NULL);
		StringBuilder_t* L_24 = V_0;
		RuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B L_25 = { reinterpret_cast<intptr_t> (il2cpp_rgctx_type(method->rgctx_data, 0)) };
		il2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
		Type_t* L_26;
		L_26 = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(L_25, NULL);
		String_t* L_27;
		L_27 = _AndroidJNIHelper_GetSignature_m414A7A6B98FB5565075E4C51F22C482F2BCEEF5F((RuntimeObject*)L_26, NULL);
		NullCheck(L_24);
		StringBuilder_t* L_28;
		L_28 = StringBuilder_Append_m08904D74E0C78E5F36DCD9C9303BDD07886D9F7D(L_24, L_27, NULL);
		StringBuilder_t* L_29 = V_0;
		NullCheck((RuntimeObject*)L_29);
		String_t* L_30;
		L_30 = VirtualFuncInvoker0< String_t* >::Invoke(3, (RuntimeObject*)L_29);
		V_2 = L_30;
		goto IL_008e;
	}

IL_008e:
	{
		String_t* L_31 = V_2;
		return L_31;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR bool Expression_Evaluate_TisDouble_tE150EF3D1D43DEE85D533810AB4C742307EEDE5F_m078E1EC84AFDC45614AC23E12723A0B785941D40_gshared (Expression_t24E9476A15D0D7F6495CF8292DA48C63C871E4B7* __this, double* ___0_value, int32_t ___1_index, int32_t ___2_count, const RuntimeMethod* method) 
{
	if (!il2cpp_rgctx_is_initialized(method))
	{
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&ExpressionEvaluator_tF912A1FA6CB7EA697DFA7926E78D808A446B48F0_il2cpp_TypeInfo_var);
		il2cpp_rgctx_method_init(method);
	}
	bool V_0 = false;
	{
		StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* L_0 = __this->___rpnTokens;
		double* L_1 = ___0_value;
		int32_t L_2 = ___1_index;
		int32_t L_3 = ___2_count;
		il2cpp_codegen_runtime_class_init_inline(ExpressionEvaluator_tF912A1FA6CB7EA697DFA7926E78D808A446B48F0_il2cpp_TypeInfo_var);
		bool L_4;
		L_4 = ExpressionEvaluator_EvaluateTokens_TisDouble_tE150EF3D1D43DEE85D533810AB4C742307EEDE5F_m791767867653D0CCE2BEFF83F336A41B5B3A718E(L_0, L_1, L_2, L_3, il2cpp_rgctx_method(method->rgctx_data, 1));
		V_0 = L_4;
		goto IL_0012;
	}

IL_0012:
	{
		bool L_5 = V_0;
		return L_5;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR bool Expression_Evaluate_TisInt64_t092CFB123BE63C28ACDAF65C68F21A526050DBA3_m838397FA34A03D1C68D150CC95FD210252FEC377_gshared (Expression_t24E9476A15D0D7F6495CF8292DA48C63C871E4B7* __this, int64_t* ___0_value, int32_t ___1_index, int32_t ___2_count, const RuntimeMethod* method) 
{
	if (!il2cpp_rgctx_is_initialized(method))
	{
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&ExpressionEvaluator_tF912A1FA6CB7EA697DFA7926E78D808A446B48F0_il2cpp_TypeInfo_var);
		il2cpp_rgctx_method_init(method);
	}
	bool V_0 = false;
	{
		StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* L_0 = __this->___rpnTokens;
		int64_t* L_1 = ___0_value;
		int32_t L_2 = ___1_index;
		int32_t L_3 = ___2_count;
		il2cpp_codegen_runtime_class_init_inline(ExpressionEvaluator_tF912A1FA6CB7EA697DFA7926E78D808A446B48F0_il2cpp_TypeInfo_var);
		bool L_4;
		L_4 = ExpressionEvaluator_EvaluateTokens_TisInt64_t092CFB123BE63C28ACDAF65C68F21A526050DBA3_m7418F7A8835B2770EF83F1D52F2723897CD76DEB(L_0, L_1, L_2, L_3, il2cpp_rgctx_method(method->rgctx_data, 1));
		V_0 = L_4;
		goto IL_0012;
	}

IL_0012:
	{
		bool L_5 = V_0;
		return L_5;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR bool Expression_Evaluate_TisUInt64_t8F12534CC8FC4B5860F2A2CD1EE79D322E7A41AF_m58D75192AF2281079E2FDE4034707E9883147B2C_gshared (Expression_t24E9476A15D0D7F6495CF8292DA48C63C871E4B7* __this, uint64_t* ___0_value, int32_t ___1_index, int32_t ___2_count, const RuntimeMethod* method) 
{
	if (!il2cpp_rgctx_is_initialized(method))
	{
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&ExpressionEvaluator_tF912A1FA6CB7EA697DFA7926E78D808A446B48F0_il2cpp_TypeInfo_var);
		il2cpp_rgctx_method_init(method);
	}
	bool V_0 = false;
	{
		StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* L_0 = __this->___rpnTokens;
		uint64_t* L_1 = ___0_value;
		int32_t L_2 = ___1_index;
		int32_t L_3 = ___2_count;
		il2cpp_codegen_runtime_class_init_inline(ExpressionEvaluator_tF912A1FA6CB7EA697DFA7926E78D808A446B48F0_il2cpp_TypeInfo_var);
		bool L_4;
		L_4 = ExpressionEvaluator_EvaluateTokens_TisUInt64_t8F12534CC8FC4B5860F2A2CD1EE79D322E7A41AF_mCFCF758DECB276DBCB0A8B83BAE195EF3B974780(L_0, L_1, L_2, L_3, il2cpp_rgctx_method(method->rgctx_data, 1));
		V_0 = L_4;
		goto IL_0012;
	}

IL_0012:
	{
		bool L_5 = V_0;
		return L_5;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR bool Expression_Evaluate_TisIl2CppFullySharedGenericAny_mC962ADA59143EB4298C3AE46F923C4552B01A4CC_gshared (Expression_t24E9476A15D0D7F6495CF8292DA48C63C871E4B7* __this, Il2CppFullySharedGenericAny* ___0_value, int32_t ___1_index, int32_t ___2_count, const RuntimeMethod* method) 
{
	if (!il2cpp_rgctx_is_initialized(method))
	{
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&ExpressionEvaluator_tF912A1FA6CB7EA697DFA7926E78D808A446B48F0_il2cpp_TypeInfo_var);
		il2cpp_rgctx_method_init(method);
	}
	bool V_0 = false;
	{
		StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* L_0 = __this->___rpnTokens;
		Il2CppFullySharedGenericAny* L_1 = ___0_value;
		int32_t L_2 = ___1_index;
		int32_t L_3 = ___2_count;
		il2cpp_codegen_runtime_class_init_inline(ExpressionEvaluator_tF912A1FA6CB7EA697DFA7926E78D808A446B48F0_il2cpp_TypeInfo_var);
		bool L_4;
		L_4 = ((  bool (*) (StringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248*, Il2CppFullySharedGenericAny*, int32_t, int32_t, const RuntimeMethod*))il2cpp_codegen_get_direct_method_pointer(il2cpp_rgctx_method(method->rgctx_data, 1)))(L_0, L_1, L_2, L_3, il2cpp_rgctx_method(method->rgctx_data, 1));
		V_0 = L_4;
		goto IL_0012;
	}

IL_0012:
	{
		bool L_5 = V_0;
		return L_5;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void Sorting_U3CMedian3PivotU3Eg__SwapU7C2_0_TisVector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3_m2B2B04012DE1B591C8E7AD4765ECB8EF3790F795_gshared (int32_t ___0_a, int32_t ___1_b, U3CU3Ec__DisplayClass2_0_1_t41073816D00B5468033D7AA727FBFFB73E7C9BA2* ___2_p, const RuntimeMethod* method) 
{
	Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 V_0;
	memset((&V_0), 0, sizeof(V_0));
	{
		U3CU3Ec__DisplayClass2_0_1_t41073816D00B5468033D7AA727FBFFB73E7C9BA2* L_0 = ___2_p;
		Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* L_1 = L_0->___data;
		int32_t L_2 = ___0_a;
		NullCheck(L_1);
		int32_t L_3 = L_2;
		Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 L_4 = (L_1)->GetAt(static_cast<il2cpp_array_size_t>(L_3));
		V_0 = L_4;
		U3CU3Ec__DisplayClass2_0_1_t41073816D00B5468033D7AA727FBFFB73E7C9BA2* L_5 = ___2_p;
		Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* L_6 = L_5->___data;
		int32_t L_7 = ___0_a;
		U3CU3Ec__DisplayClass2_0_1_t41073816D00B5468033D7AA727FBFFB73E7C9BA2* L_8 = ___2_p;
		Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* L_9 = L_8->___data;
		int32_t L_10 = ___1_b;
		NullCheck(L_9);
		int32_t L_11 = L_10;
		Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 L_12 = (L_9)->GetAt(static_cast<il2cpp_array_size_t>(L_11));
		NullCheck(L_6);
		(L_6)->SetAt(static_cast<il2cpp_array_size_t>(L_7), (Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3)L_12);
		U3CU3Ec__DisplayClass2_0_1_t41073816D00B5468033D7AA727FBFFB73E7C9BA2* L_13 = ___2_p;
		Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* L_14 = L_13->___data;
		int32_t L_15 = ___1_b;
		Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 L_16 = V_0;
		NullCheck(L_14);
		(L_14)->SetAt(static_cast<il2cpp_array_size_t>(L_15), (Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3)L_16);
		return;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void Sorting_U3CMedian3PivotU3Eg__SwapU7C2_0_TisIl2CppFullySharedGenericAny_m2C056932E189D5E31D1107D28ABA7A6A5B5EC099_gshared (int32_t ___0_a, int32_t ___1_b, U3CU3Ec__DisplayClass2_0_1_t95D21073081C2AD9435E6E2ED2FD63B720ABF032* ___2_p, const RuntimeMethod* method) 
{
	il2cpp_rgctx_method_init(method);
	const uint32_t SizeOf_T_tDB7A5E7DABCFD3E23853235D7F359DE185A4D541 = il2cpp_codegen_sizeof(il2cpp_rgctx_data_no_init(method->rgctx_data, 3));
	const Il2CppFullySharedGenericAny L_4 = alloca(SizeOf_T_tDB7A5E7DABCFD3E23853235D7F359DE185A4D541);
	const Il2CppFullySharedGenericAny L_12 = alloca(SizeOf_T_tDB7A5E7DABCFD3E23853235D7F359DE185A4D541);
	const Il2CppFullySharedGenericAny L_16 = alloca(SizeOf_T_tDB7A5E7DABCFD3E23853235D7F359DE185A4D541);
	Il2CppFullySharedGenericAny V_0 = alloca(SizeOf_T_tDB7A5E7DABCFD3E23853235D7F359DE185A4D541);
	memset(V_0, 0, SizeOf_T_tDB7A5E7DABCFD3E23853235D7F359DE185A4D541);
	{
		U3CU3Ec__DisplayClass2_0_1_t95D21073081C2AD9435E6E2ED2FD63B720ABF032* L_0 = ___2_p;
		__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC* L_1 = L_0->___data;
		int32_t L_2 = ___0_a;
		NullCheck(L_1);
		int32_t L_3 = L_2;
		il2cpp_codegen_memcpy(L_4, (L_1)->GetAddressAt(static_cast<il2cpp_array_size_t>(L_3)), SizeOf_T_tDB7A5E7DABCFD3E23853235D7F359DE185A4D541);
		il2cpp_codegen_memcpy(V_0, L_4, SizeOf_T_tDB7A5E7DABCFD3E23853235D7F359DE185A4D541);
		U3CU3Ec__DisplayClass2_0_1_t95D21073081C2AD9435E6E2ED2FD63B720ABF032* L_5 = ___2_p;
		__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC* L_6 = L_5->___data;
		int32_t L_7 = ___0_a;
		U3CU3Ec__DisplayClass2_0_1_t95D21073081C2AD9435E6E2ED2FD63B720ABF032* L_8 = ___2_p;
		__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC* L_9 = L_8->___data;
		int32_t L_10 = ___1_b;
		NullCheck(L_9);
		int32_t L_11 = L_10;
		il2cpp_codegen_memcpy(L_12, (L_9)->GetAddressAt(static_cast<il2cpp_array_size_t>(L_11)), SizeOf_T_tDB7A5E7DABCFD3E23853235D7F359DE185A4D541);
		NullCheck(L_6);
		il2cpp_codegen_memcpy((L_6)->GetAddressAt(static_cast<il2cpp_array_size_t>(L_7)), L_12, SizeOf_T_tDB7A5E7DABCFD3E23853235D7F359DE185A4D541);
		Il2CppCodeGenWriteBarrierForClass(il2cpp_rgctx_data(method->rgctx_data, 3), (void**)(L_6)->GetAddressAt(static_cast<il2cpp_array_size_t>(L_7)), (void*)L_12);
		U3CU3Ec__DisplayClass2_0_1_t95D21073081C2AD9435E6E2ED2FD63B720ABF032* L_13 = ___2_p;
		__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC* L_14 = L_13->___data;
		int32_t L_15 = ___1_b;
		il2cpp_codegen_memcpy(L_16, V_0, SizeOf_T_tDB7A5E7DABCFD3E23853235D7F359DE185A4D541);
		NullCheck(L_14);
		il2cpp_codegen_memcpy((L_14)->GetAddressAt(static_cast<il2cpp_array_size_t>(L_15)), L_16, SizeOf_T_tDB7A5E7DABCFD3E23853235D7F359DE185A4D541);
		Il2CppCodeGenWriteBarrierForClass(il2cpp_rgctx_data(method->rgctx_data, 3), (void**)(L_14)->GetAddressAt(static_cast<il2cpp_array_size_t>(L_15)), (void*)L_16);
		return;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void Sorting_U3CMedian3PivotU3Eg__SwapU7C2_0_TisLightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2_m06FED96568508A808BFC2F0CB6D49F45194E6051_gshared (int32_t ___0_a, int32_t ___1_b, U3CU3Ec__DisplayClass2_0_1_tC4E3D65CA470C2F2DB85D9B32B717BE3200D4597* ___2_p, const RuntimeMethod* method) 
{
	LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 V_0;
	memset((&V_0), 0, sizeof(V_0));
	{
		U3CU3Ec__DisplayClass2_0_1_tC4E3D65CA470C2F2DB85D9B32B717BE3200D4597* L_0 = ___2_p;
		LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* L_1 = L_0->___data;
		int32_t L_2 = ___0_a;
		NullCheck(L_1);
		int32_t L_3 = L_2;
		LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 L_4 = (L_1)->GetAt(static_cast<il2cpp_array_size_t>(L_3));
		V_0 = L_4;
		U3CU3Ec__DisplayClass2_0_1_tC4E3D65CA470C2F2DB85D9B32B717BE3200D4597* L_5 = ___2_p;
		LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* L_6 = L_5->___data;
		int32_t L_7 = ___0_a;
		U3CU3Ec__DisplayClass2_0_1_tC4E3D65CA470C2F2DB85D9B32B717BE3200D4597* L_8 = ___2_p;
		LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* L_9 = L_8->___data;
		int32_t L_10 = ___1_b;
		NullCheck(L_9);
		int32_t L_11 = L_10;
		LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 L_12 = (L_9)->GetAt(static_cast<il2cpp_array_size_t>(L_11));
		NullCheck(L_6);
		(L_6)->SetAt(static_cast<il2cpp_array_size_t>(L_7), (LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2)L_12);
		U3CU3Ec__DisplayClass2_0_1_tC4E3D65CA470C2F2DB85D9B32B717BE3200D4597* L_13 = ___2_p;
		LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* L_14 = L_13->___data;
		int32_t L_15 = ___1_b;
		LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 L_16 = V_0;
		NullCheck(L_14);
		(L_14)->SetAt(static_cast<il2cpp_array_size_t>(L_15), (LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2)L_16);
		return;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void Sorting_InsertionSort_TisVector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3_m6B06894C5FA146D1CCE7ECBC21F553F16F2E96F5_gshared (Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* ___0_data, int32_t ___1_start, int32_t ___2_end, Func_3_tD46831209E6E19204CD8F9EAFC74DBFCA3C36C5F* ___3_compare, const RuntimeMethod* method) 
{
	if (!il2cpp_rgctx_is_initialized(method))
	{
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Assert_tDC16963451AC4364803739B73A4477ADCB365863_il2cpp_TypeInfo_var);
		il2cpp_rgctx_method_init(method);
	}
	int32_t V_0 = 0;
	Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 V_1;
	memset((&V_1), 0, sizeof(V_1));
	int32_t V_2 = 0;
	bool V_3 = false;
	bool V_4 = false;
	int32_t G_B6_0 = 0;
	{
		int32_t L_0 = ___1_start;
		Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* L_1 = ___0_data;
		NullCheck(L_1);
		il2cpp_codegen_runtime_class_init_inline(Assert_tDC16963451AC4364803739B73A4477ADCB365863_il2cpp_TypeInfo_var);
		Assert_IsTrue_mE42C53B7220324D1FBAFB7AE48A7D8DD7796A663((bool)((((int64_t)((int64_t)(uint64_t)((uint32_t)L_0))) < ((int64_t)((int64_t)((int32_t)(((RuntimeArray*)L_1)->max_length)))))? 1 : 0), NULL);
		int32_t L_2 = ___2_end;
		Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* L_3 = ___0_data;
		NullCheck(L_3);
		Assert_IsTrue_mE42C53B7220324D1FBAFB7AE48A7D8DD7796A663((bool)((((int64_t)((int64_t)(uint64_t)((uint32_t)L_2))) < ((int64_t)((int64_t)((int32_t)(((RuntimeArray*)L_3)->max_length)))))? 1 : 0), NULL);
		int32_t L_4 = ___1_start;
		V_0 = ((int32_t)il2cpp_codegen_add(L_4, 1));
		goto IL_0073;
	}

IL_0023:
	{
		Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* L_5 = ___0_data;
		int32_t L_6 = V_0;
		NullCheck(L_5);
		int32_t L_7 = L_6;
		Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 L_8 = (L_5)->GetAt(static_cast<il2cpp_array_size_t>(L_7));
		V_1 = L_8;
		int32_t L_9 = V_0;
		V_2 = ((int32_t)il2cpp_codegen_subtract(L_9, 1));
		goto IL_0048;
	}

IL_0032:
	{
		Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* L_10 = ___0_data;
		int32_t L_11 = V_2;
		Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* L_12 = ___0_data;
		int32_t L_13 = V_2;
		NullCheck(L_12);
		int32_t L_14 = L_13;
		Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 L_15 = (L_12)->GetAt(static_cast<il2cpp_array_size_t>(L_14));
		NullCheck(L_10);
		(L_10)->SetAt(static_cast<il2cpp_array_size_t>(((int32_t)il2cpp_codegen_add(L_11, 1))), (Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3)L_15);
		int32_t L_16 = V_2;
		V_2 = ((int32_t)il2cpp_codegen_subtract(L_16, 1));
	}

IL_0048:
	{
		int32_t L_17 = V_2;
		if ((((int32_t)L_17) < ((int32_t)0)))
		{
			goto IL_005f;
		}
	}
	{
		Func_3_tD46831209E6E19204CD8F9EAFC74DBFCA3C36C5F* L_18 = ___3_compare;
		Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 L_19 = V_1;
		Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* L_20 = ___0_data;
		int32_t L_21 = V_2;
		NullCheck(L_20);
		int32_t L_22 = L_21;
		Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 L_23 = (L_20)->GetAt(static_cast<il2cpp_array_size_t>(L_22));
		NullCheck(L_18);
		int32_t L_24;
		L_24 = Func_3_Invoke_mE6CD106F59B0ADD2DF9C211DC4CF4088F5A1A4BB_inline(L_18, L_19, L_23, il2cpp_rgctx_method(method->rgctx_data, 3));
		G_B6_0 = ((((int32_t)L_24) < ((int32_t)0))? 1 : 0);
		goto IL_0060;
	}

IL_005f:
	{
		G_B6_0 = 0;
	}

IL_0060:
	{
		V_3 = (bool)G_B6_0;
		bool L_25 = V_3;
		if (L_25)
		{
			goto IL_0032;
		}
	}
	{
		Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* L_26 = ___0_data;
		int32_t L_27 = V_2;
		Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 L_28 = V_1;
		NullCheck(L_26);
		(L_26)->SetAt(static_cast<il2cpp_array_size_t>(((int32_t)il2cpp_codegen_add(L_27, 1))), (Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3)L_28);
		int32_t L_29 = V_0;
		V_0 = ((int32_t)il2cpp_codegen_add(L_29, 1));
	}

IL_0073:
	{
		int32_t L_30 = V_0;
		int32_t L_31 = ___2_end;
		V_4 = (bool)((((int32_t)L_30) < ((int32_t)((int32_t)il2cpp_codegen_add(L_31, 1))))? 1 : 0);
		bool L_32 = V_4;
		if (L_32)
		{
			goto IL_0023;
		}
	}
	{
		return;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void Sorting_InsertionSort_TisIl2CppFullySharedGenericAny_m4D143D52B52C5F1F971193FD2EBC1F991E1DAF27_gshared (__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC* ___0_data, int32_t ___1_start, int32_t ___2_end, Func_3_tECED1961B53AB164A131061296ABA1276B4FBBB9* ___3_compare, const RuntimeMethod* method) 
{
	if (!il2cpp_rgctx_is_initialized(method))
	{
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Assert_tDC16963451AC4364803739B73A4477ADCB365863_il2cpp_TypeInfo_var);
		il2cpp_rgctx_method_init(method);
	}
	const uint32_t SizeOf_T_t4E7DADE3DB15D6ACACD4EA4FA1DFFF15559CC2B2 = il2cpp_codegen_sizeof(il2cpp_rgctx_data_no_init(method->rgctx_data, 1));
	const Il2CppFullySharedGenericAny L_8 = alloca(SizeOf_T_t4E7DADE3DB15D6ACACD4EA4FA1DFFF15559CC2B2);
	const Il2CppFullySharedGenericAny L_15 = L_8;
	const Il2CppFullySharedGenericAny L_19 = L_8;
	const Il2CppFullySharedGenericAny L_28 = L_8;
	const Il2CppFullySharedGenericAny L_23 = alloca(SizeOf_T_t4E7DADE3DB15D6ACACD4EA4FA1DFFF15559CC2B2);
	int32_t V_0 = 0;
	Il2CppFullySharedGenericAny V_1 = alloca(SizeOf_T_t4E7DADE3DB15D6ACACD4EA4FA1DFFF15559CC2B2);
	memset(V_1, 0, SizeOf_T_t4E7DADE3DB15D6ACACD4EA4FA1DFFF15559CC2B2);
	int32_t V_2 = 0;
	bool V_3 = false;
	bool V_4 = false;
	int32_t G_B6_0 = 0;
	{
		int32_t L_0 = ___1_start;
		__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC* L_1 = ___0_data;
		NullCheck(L_1);
		il2cpp_codegen_runtime_class_init_inline(Assert_tDC16963451AC4364803739B73A4477ADCB365863_il2cpp_TypeInfo_var);
		Assert_IsTrue_mE42C53B7220324D1FBAFB7AE48A7D8DD7796A663((bool)((((int64_t)((int64_t)(uint64_t)((uint32_t)L_0))) < ((int64_t)((int64_t)((int32_t)(((RuntimeArray*)L_1)->max_length)))))? 1 : 0), NULL);
		int32_t L_2 = ___2_end;
		__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC* L_3 = ___0_data;
		NullCheck(L_3);
		Assert_IsTrue_mE42C53B7220324D1FBAFB7AE48A7D8DD7796A663((bool)((((int64_t)((int64_t)(uint64_t)((uint32_t)L_2))) < ((int64_t)((int64_t)((int32_t)(((RuntimeArray*)L_3)->max_length)))))? 1 : 0), NULL);
		int32_t L_4 = ___1_start;
		V_0 = ((int32_t)il2cpp_codegen_add(L_4, 1));
		goto IL_0073;
	}

IL_0023:
	{
		__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC* L_5 = ___0_data;
		int32_t L_6 = V_0;
		NullCheck(L_5);
		int32_t L_7 = L_6;
		il2cpp_codegen_memcpy(L_8, (L_5)->GetAddressAt(static_cast<il2cpp_array_size_t>(L_7)), SizeOf_T_t4E7DADE3DB15D6ACACD4EA4FA1DFFF15559CC2B2);
		il2cpp_codegen_memcpy(V_1, L_8, SizeOf_T_t4E7DADE3DB15D6ACACD4EA4FA1DFFF15559CC2B2);
		int32_t L_9 = V_0;
		V_2 = ((int32_t)il2cpp_codegen_subtract(L_9, 1));
		goto IL_0048;
	}

IL_0032:
	{
		__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC* L_10 = ___0_data;
		int32_t L_11 = V_2;
		__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC* L_12 = ___0_data;
		int32_t L_13 = V_2;
		NullCheck(L_12);
		int32_t L_14 = L_13;
		il2cpp_codegen_memcpy(L_15, (L_12)->GetAddressAt(static_cast<il2cpp_array_size_t>(L_14)), SizeOf_T_t4E7DADE3DB15D6ACACD4EA4FA1DFFF15559CC2B2);
		NullCheck(L_10);
		il2cpp_codegen_memcpy((L_10)->GetAddressAt(static_cast<il2cpp_array_size_t>(((int32_t)il2cpp_codegen_add(L_11, 1)))), L_15, SizeOf_T_t4E7DADE3DB15D6ACACD4EA4FA1DFFF15559CC2B2);
		Il2CppCodeGenWriteBarrierForClass(il2cpp_rgctx_data(method->rgctx_data, 1), (void**)(L_10)->GetAddressAt(static_cast<il2cpp_array_size_t>(((int32_t)il2cpp_codegen_add(L_11, 1)))), (void*)L_15);
		int32_t L_16 = V_2;
		V_2 = ((int32_t)il2cpp_codegen_subtract(L_16, 1));
	}

IL_0048:
	{
		int32_t L_17 = V_2;
		if ((((int32_t)L_17) < ((int32_t)0)))
		{
			goto IL_005f;
		}
	}
	{
		Func_3_tECED1961B53AB164A131061296ABA1276B4FBBB9* L_18 = ___3_compare;
		il2cpp_codegen_memcpy(L_19, V_1, SizeOf_T_t4E7DADE3DB15D6ACACD4EA4FA1DFFF15559CC2B2);
		__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC* L_20 = ___0_data;
		int32_t L_21 = V_2;
		NullCheck(L_20);
		int32_t L_22 = L_21;
		il2cpp_codegen_memcpy(L_23, (L_20)->GetAddressAt(static_cast<il2cpp_array_size_t>(L_22)), SizeOf_T_t4E7DADE3DB15D6ACACD4EA4FA1DFFF15559CC2B2);
		NullCheck(L_18);
		int32_t L_24;
		L_24 = InvokerFuncInvoker2< int32_t, Il2CppFullySharedGenericAny, Il2CppFullySharedGenericAny >::Invoke(il2cpp_codegen_get_direct_method_pointer(il2cpp_rgctx_method(method->rgctx_data, 3)), il2cpp_rgctx_method(method->rgctx_data, 3), L_18, (il2cpp_codegen_class_is_value_type(il2cpp_rgctx_data_no_init(method->rgctx_data, 1)) ? L_19: *(void**)L_19), (il2cpp_codegen_class_is_value_type(il2cpp_rgctx_data_no_init(method->rgctx_data, 1)) ? L_23: *(void**)L_23));
		G_B6_0 = ((((int32_t)L_24) < ((int32_t)0))? 1 : 0);
		goto IL_0060;
	}

IL_005f:
	{
		G_B6_0 = 0;
	}

IL_0060:
	{
		V_3 = (bool)G_B6_0;
		bool L_25 = V_3;
		if (L_25)
		{
			goto IL_0032;
		}
	}
	{
		__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC* L_26 = ___0_data;
		int32_t L_27 = V_2;
		il2cpp_codegen_memcpy(L_28, V_1, SizeOf_T_t4E7DADE3DB15D6ACACD4EA4FA1DFFF15559CC2B2);
		NullCheck(L_26);
		il2cpp_codegen_memcpy((L_26)->GetAddressAt(static_cast<il2cpp_array_size_t>(((int32_t)il2cpp_codegen_add(L_27, 1)))), L_28, SizeOf_T_t4E7DADE3DB15D6ACACD4EA4FA1DFFF15559CC2B2);
		Il2CppCodeGenWriteBarrierForClass(il2cpp_rgctx_data(method->rgctx_data, 1), (void**)(L_26)->GetAddressAt(static_cast<il2cpp_array_size_t>(((int32_t)il2cpp_codegen_add(L_27, 1)))), (void*)L_28);
		int32_t L_29 = V_0;
		V_0 = ((int32_t)il2cpp_codegen_add(L_29, 1));
	}

IL_0073:
	{
		int32_t L_30 = V_0;
		int32_t L_31 = ___2_end;
		V_4 = (bool)((((int32_t)L_30) < ((int32_t)((int32_t)il2cpp_codegen_add(L_31, 1))))? 1 : 0);
		bool L_32 = V_4;
		if (L_32)
		{
			goto IL_0023;
		}
	}
	{
		return;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void Sorting_InsertionSort_TisLightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2_m50C92303E813A7BFD084FB309E5FB9937C8F2065_gshared (LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* ___0_data, int32_t ___1_start, int32_t ___2_end, Func_3_t3E644C82345CE04737DA5CDE018481FE0A88F821* ___3_compare, const RuntimeMethod* method) 
{
	if (!il2cpp_rgctx_is_initialized(method))
	{
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Assert_tDC16963451AC4364803739B73A4477ADCB365863_il2cpp_TypeInfo_var);
		il2cpp_rgctx_method_init(method);
	}
	int32_t V_0 = 0;
	LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 V_1;
	memset((&V_1), 0, sizeof(V_1));
	int32_t V_2 = 0;
	bool V_3 = false;
	bool V_4 = false;
	int32_t G_B6_0 = 0;
	{
		int32_t L_0 = ___1_start;
		LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* L_1 = ___0_data;
		NullCheck(L_1);
		il2cpp_codegen_runtime_class_init_inline(Assert_tDC16963451AC4364803739B73A4477ADCB365863_il2cpp_TypeInfo_var);
		Assert_IsTrue_mE42C53B7220324D1FBAFB7AE48A7D8DD7796A663((bool)((((int64_t)((int64_t)(uint64_t)((uint32_t)L_0))) < ((int64_t)((int64_t)((int32_t)(((RuntimeArray*)L_1)->max_length)))))? 1 : 0), NULL);
		int32_t L_2 = ___2_end;
		LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* L_3 = ___0_data;
		NullCheck(L_3);
		Assert_IsTrue_mE42C53B7220324D1FBAFB7AE48A7D8DD7796A663((bool)((((int64_t)((int64_t)(uint64_t)((uint32_t)L_2))) < ((int64_t)((int64_t)((int32_t)(((RuntimeArray*)L_3)->max_length)))))? 1 : 0), NULL);
		int32_t L_4 = ___1_start;
		V_0 = ((int32_t)il2cpp_codegen_add(L_4, 1));
		goto IL_0073;
	}

IL_0023:
	{
		LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* L_5 = ___0_data;
		int32_t L_6 = V_0;
		NullCheck(L_5);
		int32_t L_7 = L_6;
		LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 L_8 = (L_5)->GetAt(static_cast<il2cpp_array_size_t>(L_7));
		V_1 = L_8;
		int32_t L_9 = V_0;
		V_2 = ((int32_t)il2cpp_codegen_subtract(L_9, 1));
		goto IL_0048;
	}

IL_0032:
	{
		LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* L_10 = ___0_data;
		int32_t L_11 = V_2;
		LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* L_12 = ___0_data;
		int32_t L_13 = V_2;
		NullCheck(L_12);
		int32_t L_14 = L_13;
		LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 L_15 = (L_12)->GetAt(static_cast<il2cpp_array_size_t>(L_14));
		NullCheck(L_10);
		(L_10)->SetAt(static_cast<il2cpp_array_size_t>(((int32_t)il2cpp_codegen_add(L_11, 1))), (LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2)L_15);
		int32_t L_16 = V_2;
		V_2 = ((int32_t)il2cpp_codegen_subtract(L_16, 1));
	}

IL_0048:
	{
		int32_t L_17 = V_2;
		if ((((int32_t)L_17) < ((int32_t)0)))
		{
			goto IL_005f;
		}
	}
	{
		Func_3_t3E644C82345CE04737DA5CDE018481FE0A88F821* L_18 = ___3_compare;
		LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 L_19 = V_1;
		LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* L_20 = ___0_data;
		int32_t L_21 = V_2;
		NullCheck(L_20);
		int32_t L_22 = L_21;
		LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 L_23 = (L_20)->GetAt(static_cast<il2cpp_array_size_t>(L_22));
		NullCheck(L_18);
		int32_t L_24;
		L_24 = Func_3_Invoke_m2AED59BE1B0645C0DB5DAE117842A1C0AD4BDEBB_inline(L_18, L_19, L_23, il2cpp_rgctx_method(method->rgctx_data, 3));
		G_B6_0 = ((((int32_t)L_24) < ((int32_t)0))? 1 : 0);
		goto IL_0060;
	}

IL_005f:
	{
		G_B6_0 = 0;
	}

IL_0060:
	{
		V_3 = (bool)G_B6_0;
		bool L_25 = V_3;
		if (L_25)
		{
			goto IL_0032;
		}
	}
	{
		LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* L_26 = ___0_data;
		int32_t L_27 = V_2;
		LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 L_28 = V_1;
		NullCheck(L_26);
		(L_26)->SetAt(static_cast<il2cpp_array_size_t>(((int32_t)il2cpp_codegen_add(L_27, 1))), (LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2)L_28);
		int32_t L_29 = V_0;
		V_0 = ((int32_t)il2cpp_codegen_add(L_29, 1));
	}

IL_0073:
	{
		int32_t L_30 = V_0;
		int32_t L_31 = ___2_end;
		V_4 = (bool)((((int32_t)L_30) < ((int32_t)((int32_t)il2cpp_codegen_add(L_31, 1))))? 1 : 0);
		bool L_32 = V_4;
		if (L_32)
		{
			goto IL_0023;
		}
	}
	{
		return;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 Sorting_Median3Pivot_TisVector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3_m61A04EAD49649BB481C390575840F890DC1AD6D9_gshared (Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* ___0_data, int32_t ___1_start, int32_t ___2_pivot, int32_t ___3_end, Func_3_tD46831209E6E19204CD8F9EAFC74DBFCA3C36C5F* ___4_compare, const RuntimeMethod* method) 
{
	il2cpp_rgctx_method_init(method);
	U3CU3Ec__DisplayClass2_0_1_t41073816D00B5468033D7AA727FBFFB73E7C9BA2 V_0;
	memset((&V_0), 0, sizeof(V_0));
	bool V_1 = false;
	bool V_2 = false;
	bool V_3 = false;
	Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 V_4;
	memset((&V_4), 0, sizeof(V_4));
	{
		Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* L_0 = ___0_data;
		(&V_0)->___data = L_0;
		Il2CppCodeGenWriteBarrier((void**)(&(&V_0)->___data), (void*)L_0);
		Func_3_tD46831209E6E19204CD8F9EAFC74DBFCA3C36C5F* L_1 = ___4_compare;
		U3CU3Ec__DisplayClass2_0_1_t41073816D00B5468033D7AA727FBFFB73E7C9BA2 L_2 = V_0;
		Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* L_3 = L_2.___data;
		int32_t L_4 = ___3_end;
		NullCheck(L_3);
		int32_t L_5 = L_4;
		Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 L_6 = (L_3)->GetAt(static_cast<il2cpp_array_size_t>(L_5));
		U3CU3Ec__DisplayClass2_0_1_t41073816D00B5468033D7AA727FBFFB73E7C9BA2 L_7 = V_0;
		Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* L_8 = L_7.___data;
		int32_t L_9 = ___1_start;
		NullCheck(L_8);
		int32_t L_10 = L_9;
		Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 L_11 = (L_8)->GetAt(static_cast<il2cpp_array_size_t>(L_10));
		NullCheck(L_1);
		int32_t L_12;
		L_12 = Func_3_Invoke_mE6CD106F59B0ADD2DF9C211DC4CF4088F5A1A4BB_inline(L_1, L_6, L_11, il2cpp_rgctx_method(method->rgctx_data, 4));
		V_1 = (bool)((((int32_t)L_12) < ((int32_t)0))? 1 : 0);
		bool L_13 = V_1;
		if (!L_13)
		{
			goto IL_003a;
		}
	}
	{
		int32_t L_14 = ___1_start;
		int32_t L_15 = ___3_end;
		Sorting_U3CMedian3PivotU3Eg__SwapU7C2_0_TisVector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3_m2B2B04012DE1B591C8E7AD4765ECB8EF3790F795(L_14, L_15, (&V_0), il2cpp_rgctx_method(method->rgctx_data, 5));
	}

IL_003a:
	{
		Func_3_tD46831209E6E19204CD8F9EAFC74DBFCA3C36C5F* L_16 = ___4_compare;
		U3CU3Ec__DisplayClass2_0_1_t41073816D00B5468033D7AA727FBFFB73E7C9BA2 L_17 = V_0;
		Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* L_18 = L_17.___data;
		int32_t L_19 = ___2_pivot;
		NullCheck(L_18);
		int32_t L_20 = L_19;
		Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 L_21 = (L_18)->GetAt(static_cast<il2cpp_array_size_t>(L_20));
		U3CU3Ec__DisplayClass2_0_1_t41073816D00B5468033D7AA727FBFFB73E7C9BA2 L_22 = V_0;
		Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* L_23 = L_22.___data;
		int32_t L_24 = ___1_start;
		NullCheck(L_23);
		int32_t L_25 = L_24;
		Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 L_26 = (L_23)->GetAt(static_cast<il2cpp_array_size_t>(L_25));
		NullCheck(L_16);
		int32_t L_27;
		L_27 = Func_3_Invoke_mE6CD106F59B0ADD2DF9C211DC4CF4088F5A1A4BB_inline(L_16, L_21, L_26, il2cpp_rgctx_method(method->rgctx_data, 4));
		V_2 = (bool)((((int32_t)L_27) < ((int32_t)0))? 1 : 0);
		bool L_28 = V_2;
		if (!L_28)
		{
			goto IL_006a;
		}
	}
	{
		int32_t L_29 = ___1_start;
		int32_t L_30 = ___2_pivot;
		Sorting_U3CMedian3PivotU3Eg__SwapU7C2_0_TisVector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3_m2B2B04012DE1B591C8E7AD4765ECB8EF3790F795(L_29, L_30, (&V_0), il2cpp_rgctx_method(method->rgctx_data, 5));
	}

IL_006a:
	{
		Func_3_tD46831209E6E19204CD8F9EAFC74DBFCA3C36C5F* L_31 = ___4_compare;
		U3CU3Ec__DisplayClass2_0_1_t41073816D00B5468033D7AA727FBFFB73E7C9BA2 L_32 = V_0;
		Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* L_33 = L_32.___data;
		int32_t L_34 = ___3_end;
		NullCheck(L_33);
		int32_t L_35 = L_34;
		Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 L_36 = (L_33)->GetAt(static_cast<il2cpp_array_size_t>(L_35));
		U3CU3Ec__DisplayClass2_0_1_t41073816D00B5468033D7AA727FBFFB73E7C9BA2 L_37 = V_0;
		Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* L_38 = L_37.___data;
		int32_t L_39 = ___2_pivot;
		NullCheck(L_38);
		int32_t L_40 = L_39;
		Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 L_41 = (L_38)->GetAt(static_cast<il2cpp_array_size_t>(L_40));
		NullCheck(L_31);
		int32_t L_42;
		L_42 = Func_3_Invoke_mE6CD106F59B0ADD2DF9C211DC4CF4088F5A1A4BB_inline(L_31, L_36, L_41, il2cpp_rgctx_method(method->rgctx_data, 4));
		V_3 = (bool)((((int32_t)L_42) < ((int32_t)0))? 1 : 0);
		bool L_43 = V_3;
		if (!L_43)
		{
			goto IL_009a;
		}
	}
	{
		int32_t L_44 = ___2_pivot;
		int32_t L_45 = ___3_end;
		Sorting_U3CMedian3PivotU3Eg__SwapU7C2_0_TisVector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3_m2B2B04012DE1B591C8E7AD4765ECB8EF3790F795(L_44, L_45, (&V_0), il2cpp_rgctx_method(method->rgctx_data, 5));
	}

IL_009a:
	{
		U3CU3Ec__DisplayClass2_0_1_t41073816D00B5468033D7AA727FBFFB73E7C9BA2 L_46 = V_0;
		Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* L_47 = L_46.___data;
		int32_t L_48 = ___2_pivot;
		NullCheck(L_47);
		int32_t L_49 = L_48;
		Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 L_50 = (L_47)->GetAt(static_cast<il2cpp_array_size_t>(L_49));
		V_4 = L_50;
		goto IL_00aa;
	}

IL_00aa:
	{
		Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 L_51 = V_4;
		return L_51;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void Sorting_Median3Pivot_TisIl2CppFullySharedGenericAny_mA6E8814C46DAB9D561A5440B447E24E67159A5A1_gshared (__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC* ___0_data, int32_t ___1_start, int32_t ___2_pivot, int32_t ___3_end, Func_3_tECED1961B53AB164A131061296ABA1276B4FBBB9* ___4_compare, Il2CppFullySharedGenericAny* il2cppRetVal, const RuntimeMethod* method) 
{
	il2cpp_rgctx_method_init(method);
	const uint32_t SizeOf_T_t7DAA074A5FED821310D99584547BB9B1AEB7FBB5 = il2cpp_codegen_sizeof(il2cpp_rgctx_data_no_init(method->rgctx_data, 3));
	const Il2CppFullySharedGenericAny L_6 = alloca(SizeOf_T_t7DAA074A5FED821310D99584547BB9B1AEB7FBB5);
	const Il2CppFullySharedGenericAny L_21 = L_6;
	const Il2CppFullySharedGenericAny L_36 = L_6;
	const Il2CppFullySharedGenericAny L_50 = L_6;
	const Il2CppFullySharedGenericAny L_51 = L_6;
	const Il2CppFullySharedGenericAny L_11 = alloca(SizeOf_T_t7DAA074A5FED821310D99584547BB9B1AEB7FBB5);
	const Il2CppFullySharedGenericAny L_26 = L_11;
	const Il2CppFullySharedGenericAny L_41 = L_11;
	U3CU3Ec__DisplayClass2_0_1_t95D21073081C2AD9435E6E2ED2FD63B720ABF032 V_0;
	memset((&V_0), 0, sizeof(V_0));
	bool V_1 = false;
	bool V_2 = false;
	bool V_3 = false;
	Il2CppFullySharedGenericAny V_4 = alloca(SizeOf_T_t7DAA074A5FED821310D99584547BB9B1AEB7FBB5);
	memset(V_4, 0, SizeOf_T_t7DAA074A5FED821310D99584547BB9B1AEB7FBB5);
	{
		__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC* L_0 = ___0_data;
		(&V_0)->___data = L_0;
		Il2CppCodeGenWriteBarrier((void**)(&(&V_0)->___data), (void*)L_0);
		Func_3_tECED1961B53AB164A131061296ABA1276B4FBBB9* L_1 = ___4_compare;
		U3CU3Ec__DisplayClass2_0_1_t95D21073081C2AD9435E6E2ED2FD63B720ABF032 L_2 = V_0;
		__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC* L_3 = L_2.___data;
		int32_t L_4 = ___3_end;
		NullCheck(L_3);
		int32_t L_5 = L_4;
		il2cpp_codegen_memcpy(L_6, (L_3)->GetAddressAt(static_cast<il2cpp_array_size_t>(L_5)), SizeOf_T_t7DAA074A5FED821310D99584547BB9B1AEB7FBB5);
		U3CU3Ec__DisplayClass2_0_1_t95D21073081C2AD9435E6E2ED2FD63B720ABF032 L_7 = V_0;
		__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC* L_8 = L_7.___data;
		int32_t L_9 = ___1_start;
		NullCheck(L_8);
		int32_t L_10 = L_9;
		il2cpp_codegen_memcpy(L_11, (L_8)->GetAddressAt(static_cast<il2cpp_array_size_t>(L_10)), SizeOf_T_t7DAA074A5FED821310D99584547BB9B1AEB7FBB5);
		NullCheck(L_1);
		int32_t L_12;
		L_12 = InvokerFuncInvoker2< int32_t, Il2CppFullySharedGenericAny, Il2CppFullySharedGenericAny >::Invoke(il2cpp_codegen_get_direct_method_pointer(il2cpp_rgctx_method(method->rgctx_data, 4)), il2cpp_rgctx_method(method->rgctx_data, 4), L_1, (il2cpp_codegen_class_is_value_type(il2cpp_rgctx_data_no_init(method->rgctx_data, 3)) ? L_6: *(void**)L_6), (il2cpp_codegen_class_is_value_type(il2cpp_rgctx_data_no_init(method->rgctx_data, 3)) ? L_11: *(void**)L_11));
		V_1 = (bool)((((int32_t)L_12) < ((int32_t)0))? 1 : 0);
		bool L_13 = V_1;
		if (!L_13)
		{
			goto IL_003a;
		}
	}
	{
		int32_t L_14 = ___1_start;
		int32_t L_15 = ___3_end;
		((  void (*) (int32_t, int32_t, U3CU3Ec__DisplayClass2_0_1_t95D21073081C2AD9435E6E2ED2FD63B720ABF032*, const RuntimeMethod*))il2cpp_codegen_get_direct_method_pointer(il2cpp_rgctx_method(method->rgctx_data, 5)))(L_14, L_15, (&V_0), il2cpp_rgctx_method(method->rgctx_data, 5));
	}

IL_003a:
	{
		Func_3_tECED1961B53AB164A131061296ABA1276B4FBBB9* L_16 = ___4_compare;
		U3CU3Ec__DisplayClass2_0_1_t95D21073081C2AD9435E6E2ED2FD63B720ABF032 L_17 = V_0;
		__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC* L_18 = L_17.___data;
		int32_t L_19 = ___2_pivot;
		NullCheck(L_18);
		int32_t L_20 = L_19;
		il2cpp_codegen_memcpy(L_21, (L_18)->GetAddressAt(static_cast<il2cpp_array_size_t>(L_20)), SizeOf_T_t7DAA074A5FED821310D99584547BB9B1AEB7FBB5);
		U3CU3Ec__DisplayClass2_0_1_t95D21073081C2AD9435E6E2ED2FD63B720ABF032 L_22 = V_0;
		__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC* L_23 = L_22.___data;
		int32_t L_24 = ___1_start;
		NullCheck(L_23);
		int32_t L_25 = L_24;
		il2cpp_codegen_memcpy(L_26, (L_23)->GetAddressAt(static_cast<il2cpp_array_size_t>(L_25)), SizeOf_T_t7DAA074A5FED821310D99584547BB9B1AEB7FBB5);
		NullCheck(L_16);
		int32_t L_27;
		L_27 = InvokerFuncInvoker2< int32_t, Il2CppFullySharedGenericAny, Il2CppFullySharedGenericAny >::Invoke(il2cpp_codegen_get_direct_method_pointer(il2cpp_rgctx_method(method->rgctx_data, 4)), il2cpp_rgctx_method(method->rgctx_data, 4), L_16, (il2cpp_codegen_class_is_value_type(il2cpp_rgctx_data_no_init(method->rgctx_data, 3)) ? L_21: *(void**)L_21), (il2cpp_codegen_class_is_value_type(il2cpp_rgctx_data_no_init(method->rgctx_data, 3)) ? L_26: *(void**)L_26));
		V_2 = (bool)((((int32_t)L_27) < ((int32_t)0))? 1 : 0);
		bool L_28 = V_2;
		if (!L_28)
		{
			goto IL_006a;
		}
	}
	{
		int32_t L_29 = ___1_start;
		int32_t L_30 = ___2_pivot;
		((  void (*) (int32_t, int32_t, U3CU3Ec__DisplayClass2_0_1_t95D21073081C2AD9435E6E2ED2FD63B720ABF032*, const RuntimeMethod*))il2cpp_codegen_get_direct_method_pointer(il2cpp_rgctx_method(method->rgctx_data, 5)))(L_29, L_30, (&V_0), il2cpp_rgctx_method(method->rgctx_data, 5));
	}

IL_006a:
	{
		Func_3_tECED1961B53AB164A131061296ABA1276B4FBBB9* L_31 = ___4_compare;
		U3CU3Ec__DisplayClass2_0_1_t95D21073081C2AD9435E6E2ED2FD63B720ABF032 L_32 = V_0;
		__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC* L_33 = L_32.___data;
		int32_t L_34 = ___3_end;
		NullCheck(L_33);
		int32_t L_35 = L_34;
		il2cpp_codegen_memcpy(L_36, (L_33)->GetAddressAt(static_cast<il2cpp_array_size_t>(L_35)), SizeOf_T_t7DAA074A5FED821310D99584547BB9B1AEB7FBB5);
		U3CU3Ec__DisplayClass2_0_1_t95D21073081C2AD9435E6E2ED2FD63B720ABF032 L_37 = V_0;
		__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC* L_38 = L_37.___data;
		int32_t L_39 = ___2_pivot;
		NullCheck(L_38);
		int32_t L_40 = L_39;
		il2cpp_codegen_memcpy(L_41, (L_38)->GetAddressAt(static_cast<il2cpp_array_size_t>(L_40)), SizeOf_T_t7DAA074A5FED821310D99584547BB9B1AEB7FBB5);
		NullCheck(L_31);
		int32_t L_42;
		L_42 = InvokerFuncInvoker2< int32_t, Il2CppFullySharedGenericAny, Il2CppFullySharedGenericAny >::Invoke(il2cpp_codegen_get_direct_method_pointer(il2cpp_rgctx_method(method->rgctx_data, 4)), il2cpp_rgctx_method(method->rgctx_data, 4), L_31, (il2cpp_codegen_class_is_value_type(il2cpp_rgctx_data_no_init(method->rgctx_data, 3)) ? L_36: *(void**)L_36), (il2cpp_codegen_class_is_value_type(il2cpp_rgctx_data_no_init(method->rgctx_data, 3)) ? L_41: *(void**)L_41));
		V_3 = (bool)((((int32_t)L_42) < ((int32_t)0))? 1 : 0);
		bool L_43 = V_3;
		if (!L_43)
		{
			goto IL_009a;
		}
	}
	{
		int32_t L_44 = ___2_pivot;
		int32_t L_45 = ___3_end;
		((  void (*) (int32_t, int32_t, U3CU3Ec__DisplayClass2_0_1_t95D21073081C2AD9435E6E2ED2FD63B720ABF032*, const RuntimeMethod*))il2cpp_codegen_get_direct_method_pointer(il2cpp_rgctx_method(method->rgctx_data, 5)))(L_44, L_45, (&V_0), il2cpp_rgctx_method(method->rgctx_data, 5));
	}

IL_009a:
	{
		U3CU3Ec__DisplayClass2_0_1_t95D21073081C2AD9435E6E2ED2FD63B720ABF032 L_46 = V_0;
		__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC* L_47 = L_46.___data;
		int32_t L_48 = ___2_pivot;
		NullCheck(L_47);
		int32_t L_49 = L_48;
		il2cpp_codegen_memcpy(L_50, (L_47)->GetAddressAt(static_cast<il2cpp_array_size_t>(L_49)), SizeOf_T_t7DAA074A5FED821310D99584547BB9B1AEB7FBB5);
		il2cpp_codegen_memcpy(V_4, L_50, SizeOf_T_t7DAA074A5FED821310D99584547BB9B1AEB7FBB5);
		goto IL_00aa;
	}

IL_00aa:
	{
		il2cpp_codegen_memcpy(L_51, V_4, SizeOf_T_t7DAA074A5FED821310D99584547BB9B1AEB7FBB5);
		il2cpp_codegen_memcpy(il2cppRetVal, L_51, SizeOf_T_t7DAA074A5FED821310D99584547BB9B1AEB7FBB5);
		return;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 Sorting_Median3Pivot_TisLightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2_m3AE419868146FAEE6A59E9FA4E33484BFA9930B1_gshared (LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* ___0_data, int32_t ___1_start, int32_t ___2_pivot, int32_t ___3_end, Func_3_t3E644C82345CE04737DA5CDE018481FE0A88F821* ___4_compare, const RuntimeMethod* method) 
{
	il2cpp_rgctx_method_init(method);
	U3CU3Ec__DisplayClass2_0_1_tC4E3D65CA470C2F2DB85D9B32B717BE3200D4597 V_0;
	memset((&V_0), 0, sizeof(V_0));
	bool V_1 = false;
	bool V_2 = false;
	bool V_3 = false;
	LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 V_4;
	memset((&V_4), 0, sizeof(V_4));
	{
		LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* L_0 = ___0_data;
		(&V_0)->___data = L_0;
		Il2CppCodeGenWriteBarrier((void**)(&(&V_0)->___data), (void*)L_0);
		Func_3_t3E644C82345CE04737DA5CDE018481FE0A88F821* L_1 = ___4_compare;
		U3CU3Ec__DisplayClass2_0_1_tC4E3D65CA470C2F2DB85D9B32B717BE3200D4597 L_2 = V_0;
		LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* L_3 = L_2.___data;
		int32_t L_4 = ___3_end;
		NullCheck(L_3);
		int32_t L_5 = L_4;
		LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 L_6 = (L_3)->GetAt(static_cast<il2cpp_array_size_t>(L_5));
		U3CU3Ec__DisplayClass2_0_1_tC4E3D65CA470C2F2DB85D9B32B717BE3200D4597 L_7 = V_0;
		LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* L_8 = L_7.___data;
		int32_t L_9 = ___1_start;
		NullCheck(L_8);
		int32_t L_10 = L_9;
		LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 L_11 = (L_8)->GetAt(static_cast<il2cpp_array_size_t>(L_10));
		NullCheck(L_1);
		int32_t L_12;
		L_12 = Func_3_Invoke_m2AED59BE1B0645C0DB5DAE117842A1C0AD4BDEBB_inline(L_1, L_6, L_11, il2cpp_rgctx_method(method->rgctx_data, 4));
		V_1 = (bool)((((int32_t)L_12) < ((int32_t)0))? 1 : 0);
		bool L_13 = V_1;
		if (!L_13)
		{
			goto IL_003a;
		}
	}
	{
		int32_t L_14 = ___1_start;
		int32_t L_15 = ___3_end;
		Sorting_U3CMedian3PivotU3Eg__SwapU7C2_0_TisLightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2_m06FED96568508A808BFC2F0CB6D49F45194E6051(L_14, L_15, (&V_0), il2cpp_rgctx_method(method->rgctx_data, 5));
	}

IL_003a:
	{
		Func_3_t3E644C82345CE04737DA5CDE018481FE0A88F821* L_16 = ___4_compare;
		U3CU3Ec__DisplayClass2_0_1_tC4E3D65CA470C2F2DB85D9B32B717BE3200D4597 L_17 = V_0;
		LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* L_18 = L_17.___data;
		int32_t L_19 = ___2_pivot;
		NullCheck(L_18);
		int32_t L_20 = L_19;
		LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 L_21 = (L_18)->GetAt(static_cast<il2cpp_array_size_t>(L_20));
		U3CU3Ec__DisplayClass2_0_1_tC4E3D65CA470C2F2DB85D9B32B717BE3200D4597 L_22 = V_0;
		LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* L_23 = L_22.___data;
		int32_t L_24 = ___1_start;
		NullCheck(L_23);
		int32_t L_25 = L_24;
		LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 L_26 = (L_23)->GetAt(static_cast<il2cpp_array_size_t>(L_25));
		NullCheck(L_16);
		int32_t L_27;
		L_27 = Func_3_Invoke_m2AED59BE1B0645C0DB5DAE117842A1C0AD4BDEBB_inline(L_16, L_21, L_26, il2cpp_rgctx_method(method->rgctx_data, 4));
		V_2 = (bool)((((int32_t)L_27) < ((int32_t)0))? 1 : 0);
		bool L_28 = V_2;
		if (!L_28)
		{
			goto IL_006a;
		}
	}
	{
		int32_t L_29 = ___1_start;
		int32_t L_30 = ___2_pivot;
		Sorting_U3CMedian3PivotU3Eg__SwapU7C2_0_TisLightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2_m06FED96568508A808BFC2F0CB6D49F45194E6051(L_29, L_30, (&V_0), il2cpp_rgctx_method(method->rgctx_data, 5));
	}

IL_006a:
	{
		Func_3_t3E644C82345CE04737DA5CDE018481FE0A88F821* L_31 = ___4_compare;
		U3CU3Ec__DisplayClass2_0_1_tC4E3D65CA470C2F2DB85D9B32B717BE3200D4597 L_32 = V_0;
		LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* L_33 = L_32.___data;
		int32_t L_34 = ___3_end;
		NullCheck(L_33);
		int32_t L_35 = L_34;
		LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 L_36 = (L_33)->GetAt(static_cast<il2cpp_array_size_t>(L_35));
		U3CU3Ec__DisplayClass2_0_1_tC4E3D65CA470C2F2DB85D9B32B717BE3200D4597 L_37 = V_0;
		LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* L_38 = L_37.___data;
		int32_t L_39 = ___2_pivot;
		NullCheck(L_38);
		int32_t L_40 = L_39;
		LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 L_41 = (L_38)->GetAt(static_cast<il2cpp_array_size_t>(L_40));
		NullCheck(L_31);
		int32_t L_42;
		L_42 = Func_3_Invoke_m2AED59BE1B0645C0DB5DAE117842A1C0AD4BDEBB_inline(L_31, L_36, L_41, il2cpp_rgctx_method(method->rgctx_data, 4));
		V_3 = (bool)((((int32_t)L_42) < ((int32_t)0))? 1 : 0);
		bool L_43 = V_3;
		if (!L_43)
		{
			goto IL_009a;
		}
	}
	{
		int32_t L_44 = ___2_pivot;
		int32_t L_45 = ___3_end;
		Sorting_U3CMedian3PivotU3Eg__SwapU7C2_0_TisLightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2_m06FED96568508A808BFC2F0CB6D49F45194E6051(L_44, L_45, (&V_0), il2cpp_rgctx_method(method->rgctx_data, 5));
	}

IL_009a:
	{
		U3CU3Ec__DisplayClass2_0_1_tC4E3D65CA470C2F2DB85D9B32B717BE3200D4597 L_46 = V_0;
		LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* L_47 = L_46.___data;
		int32_t L_48 = ___2_pivot;
		NullCheck(L_47);
		int32_t L_49 = L_48;
		LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 L_50 = (L_47)->GetAt(static_cast<il2cpp_array_size_t>(L_49));
		V_4 = L_50;
		goto IL_00aa;
	}

IL_00aa:
	{
		LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 L_51 = V_4;
		return L_51;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR int32_t Sorting_Partition_TisVector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3_m5B1882A69C494B64F1EA761E21D0018C1D6AB6E8_gshared (Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* ___0_data, int32_t ___1_start, int32_t ___2_end, Func_3_tD46831209E6E19204CD8F9EAFC74DBFCA3C36C5F* ___3_compare, const RuntimeMethod* method) 
{
	il2cpp_rgctx_method_init(method);
	int32_t V_0 = 0;
	int32_t V_1 = 0;
	Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 V_2;
	memset((&V_2), 0, sizeof(V_2));
	Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 V_3;
	memset((&V_3), 0, sizeof(V_3));
	bool V_4 = false;
	bool V_5 = false;
	bool V_6 = false;
	int32_t V_7 = 0;
	bool V_8 = false;
	{
		int32_t L_0 = ___2_end;
		int32_t L_1 = ___1_start;
		V_0 = ((int32_t)il2cpp_codegen_subtract(L_0, L_1));
		int32_t L_2 = ___1_start;
		int32_t L_3 = V_0;
		V_1 = ((int32_t)il2cpp_codegen_add(L_2, ((int32_t)(L_3/2))));
		Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* L_4 = ___0_data;
		int32_t L_5 = ___1_start;
		int32_t L_6 = V_1;
		int32_t L_7 = ___2_end;
		Func_3_tD46831209E6E19204CD8F9EAFC74DBFCA3C36C5F* L_8 = ___3_compare;
		Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 L_9;
		L_9 = Sorting_Median3Pivot_TisVector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3_m61A04EAD49649BB481C390575840F890DC1AD6D9(L_4, L_5, L_6, L_7, L_8, il2cpp_rgctx_method(method->rgctx_data, 2));
		V_2 = L_9;
		goto IL_0091;
	}

IL_0018:
	{
		goto IL_0020;
	}

IL_001b:
	{
		int32_t L_10 = ___1_start;
		___1_start = ((int32_t)il2cpp_codegen_add(L_10, 1));
	}

IL_0020:
	{
		Func_3_tD46831209E6E19204CD8F9EAFC74DBFCA3C36C5F* L_11 = ___3_compare;
		Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* L_12 = ___0_data;
		int32_t L_13 = ___1_start;
		NullCheck(L_12);
		int32_t L_14 = L_13;
		Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 L_15 = (L_12)->GetAt(static_cast<il2cpp_array_size_t>(L_14));
		Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 L_16 = V_2;
		NullCheck(L_11);
		int32_t L_17;
		L_17 = Func_3_Invoke_mE6CD106F59B0ADD2DF9C211DC4CF4088F5A1A4BB_inline(L_11, L_15, L_16, il2cpp_rgctx_method(method->rgctx_data, 4));
		V_4 = (bool)((((int32_t)L_17) < ((int32_t)0))? 1 : 0);
		bool L_18 = V_4;
		if (L_18)
		{
			goto IL_001b;
		}
	}
	{
		goto IL_003e;
	}

IL_0039:
	{
		int32_t L_19 = ___2_end;
		___2_end = ((int32_t)il2cpp_codegen_subtract(L_19, 1));
	}

IL_003e:
	{
		Func_3_tD46831209E6E19204CD8F9EAFC74DBFCA3C36C5F* L_20 = ___3_compare;
		Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* L_21 = ___0_data;
		int32_t L_22 = ___2_end;
		NullCheck(L_21);
		int32_t L_23 = L_22;
		Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 L_24 = (L_21)->GetAt(static_cast<il2cpp_array_size_t>(L_23));
		Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 L_25 = V_2;
		NullCheck(L_20);
		int32_t L_26;
		L_26 = Func_3_Invoke_mE6CD106F59B0ADD2DF9C211DC4CF4088F5A1A4BB_inline(L_20, L_24, L_25, il2cpp_rgctx_method(method->rgctx_data, 4));
		V_5 = (bool)((((int32_t)L_26) > ((int32_t)0))? 1 : 0);
		bool L_27 = V_5;
		if (L_27)
		{
			goto IL_0039;
		}
	}
	{
		int32_t L_28 = ___1_start;
		int32_t L_29 = ___2_end;
		V_6 = (bool)((((int32_t)((((int32_t)L_28) < ((int32_t)L_29))? 1 : 0)) == ((int32_t)0))? 1 : 0);
		bool L_30 = V_6;
		if (!L_30)
		{
			goto IL_0068;
		}
	}
	{
		int32_t L_31 = ___2_end;
		V_7 = L_31;
		goto IL_0096;
	}

IL_0068:
	{
		Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* L_32 = ___0_data;
		int32_t L_33 = ___1_start;
		NullCheck(L_32);
		int32_t L_34 = L_33;
		Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 L_35 = (L_32)->GetAt(static_cast<il2cpp_array_size_t>(L_34));
		V_3 = L_35;
		Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* L_36 = ___0_data;
		int32_t L_37 = ___1_start;
		int32_t L_38 = L_37;
		___1_start = ((int32_t)il2cpp_codegen_add(L_38, 1));
		Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* L_39 = ___0_data;
		int32_t L_40 = ___2_end;
		NullCheck(L_39);
		int32_t L_41 = L_40;
		Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 L_42 = (L_39)->GetAt(static_cast<il2cpp_array_size_t>(L_41));
		NullCheck(L_36);
		(L_36)->SetAt(static_cast<il2cpp_array_size_t>(L_38), (Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3)L_42);
		Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* L_43 = ___0_data;
		int32_t L_44 = ___2_end;
		int32_t L_45 = L_44;
		___2_end = ((int32_t)il2cpp_codegen_subtract(L_45, 1));
		Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 L_46 = V_3;
		NullCheck(L_43);
		(L_43)->SetAt(static_cast<il2cpp_array_size_t>(L_45), (Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3)L_46);
	}

IL_0091:
	{
		V_8 = (bool)1;
		goto IL_0018;
	}

IL_0096:
	{
		int32_t L_47 = V_7;
		return L_47;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR int32_t Sorting_Partition_TisIl2CppFullySharedGenericAny_m712B611DAC06FA9738A8F85CAA404B955BB47029_gshared (__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC* ___0_data, int32_t ___1_start, int32_t ___2_end, Func_3_tECED1961B53AB164A131061296ABA1276B4FBBB9* ___3_compare, const RuntimeMethod* method) 
{
	il2cpp_rgctx_method_init(method);
	const uint32_t SizeOf_T_tC40FDC7B5C85862D1DEB60A6C3716599A9ECA6BE = il2cpp_codegen_sizeof(il2cpp_rgctx_data_no_init(method->rgctx_data, 3));
	const Il2CppFullySharedGenericAny L_9 = alloca(SizeOf_T_tC40FDC7B5C85862D1DEB60A6C3716599A9ECA6BE);
	const Il2CppFullySharedGenericAny L_15 = L_9;
	const Il2CppFullySharedGenericAny L_24 = L_9;
	const Il2CppFullySharedGenericAny L_35 = L_9;
	const Il2CppFullySharedGenericAny L_16 = alloca(SizeOf_T_tC40FDC7B5C85862D1DEB60A6C3716599A9ECA6BE);
	const Il2CppFullySharedGenericAny L_25 = L_16;
	const Il2CppFullySharedGenericAny L_42 = L_16;
	const Il2CppFullySharedGenericAny L_46 = alloca(SizeOf_T_tC40FDC7B5C85862D1DEB60A6C3716599A9ECA6BE);
	int32_t V_0 = 0;
	int32_t V_1 = 0;
	Il2CppFullySharedGenericAny V_2 = alloca(SizeOf_T_tC40FDC7B5C85862D1DEB60A6C3716599A9ECA6BE);
	memset(V_2, 0, SizeOf_T_tC40FDC7B5C85862D1DEB60A6C3716599A9ECA6BE);
	Il2CppFullySharedGenericAny V_3 = alloca(SizeOf_T_tC40FDC7B5C85862D1DEB60A6C3716599A9ECA6BE);
	memset(V_3, 0, SizeOf_T_tC40FDC7B5C85862D1DEB60A6C3716599A9ECA6BE);
	bool V_4 = false;
	bool V_5 = false;
	bool V_6 = false;
	int32_t V_7 = 0;
	bool V_8 = false;
	{
		int32_t L_0 = ___2_end;
		int32_t L_1 = ___1_start;
		V_0 = ((int32_t)il2cpp_codegen_subtract(L_0, L_1));
		int32_t L_2 = ___1_start;
		int32_t L_3 = V_0;
		V_1 = ((int32_t)il2cpp_codegen_add(L_2, ((int32_t)(L_3/2))));
		__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC* L_4 = ___0_data;
		int32_t L_5 = ___1_start;
		int32_t L_6 = V_1;
		int32_t L_7 = ___2_end;
		Func_3_tECED1961B53AB164A131061296ABA1276B4FBBB9* L_8 = ___3_compare;
		InvokerActionInvoker6< __Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC*, int32_t, int32_t, int32_t, Func_3_tECED1961B53AB164A131061296ABA1276B4FBBB9*, Il2CppFullySharedGenericAny* >::Invoke(il2cpp_codegen_get_direct_method_pointer(il2cpp_rgctx_method(method->rgctx_data, 2)), il2cpp_rgctx_method(method->rgctx_data, 2), NULL, L_4, L_5, L_6, L_7, L_8, (Il2CppFullySharedGenericAny*)L_9);
		il2cpp_codegen_memcpy(V_2, L_9, SizeOf_T_tC40FDC7B5C85862D1DEB60A6C3716599A9ECA6BE);
		goto IL_0091;
	}

IL_0018:
	{
		goto IL_0020;
	}

IL_001b:
	{
		int32_t L_10 = ___1_start;
		___1_start = ((int32_t)il2cpp_codegen_add(L_10, 1));
	}

IL_0020:
	{
		Func_3_tECED1961B53AB164A131061296ABA1276B4FBBB9* L_11 = ___3_compare;
		__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC* L_12 = ___0_data;
		int32_t L_13 = ___1_start;
		NullCheck(L_12);
		int32_t L_14 = L_13;
		il2cpp_codegen_memcpy(L_15, (L_12)->GetAddressAt(static_cast<il2cpp_array_size_t>(L_14)), SizeOf_T_tC40FDC7B5C85862D1DEB60A6C3716599A9ECA6BE);
		il2cpp_codegen_memcpy(L_16, V_2, SizeOf_T_tC40FDC7B5C85862D1DEB60A6C3716599A9ECA6BE);
		NullCheck(L_11);
		int32_t L_17;
		L_17 = InvokerFuncInvoker2< int32_t, Il2CppFullySharedGenericAny, Il2CppFullySharedGenericAny >::Invoke(il2cpp_codegen_get_direct_method_pointer(il2cpp_rgctx_method(method->rgctx_data, 4)), il2cpp_rgctx_method(method->rgctx_data, 4), L_11, (il2cpp_codegen_class_is_value_type(il2cpp_rgctx_data_no_init(method->rgctx_data, 3)) ? L_15: *(void**)L_15), (il2cpp_codegen_class_is_value_type(il2cpp_rgctx_data_no_init(method->rgctx_data, 3)) ? L_16: *(void**)L_16));
		V_4 = (bool)((((int32_t)L_17) < ((int32_t)0))? 1 : 0);
		bool L_18 = V_4;
		if (L_18)
		{
			goto IL_001b;
		}
	}
	{
		goto IL_003e;
	}

IL_0039:
	{
		int32_t L_19 = ___2_end;
		___2_end = ((int32_t)il2cpp_codegen_subtract(L_19, 1));
	}

IL_003e:
	{
		Func_3_tECED1961B53AB164A131061296ABA1276B4FBBB9* L_20 = ___3_compare;
		__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC* L_21 = ___0_data;
		int32_t L_22 = ___2_end;
		NullCheck(L_21);
		int32_t L_23 = L_22;
		il2cpp_codegen_memcpy(L_24, (L_21)->GetAddressAt(static_cast<il2cpp_array_size_t>(L_23)), SizeOf_T_tC40FDC7B5C85862D1DEB60A6C3716599A9ECA6BE);
		il2cpp_codegen_memcpy(L_25, V_2, SizeOf_T_tC40FDC7B5C85862D1DEB60A6C3716599A9ECA6BE);
		NullCheck(L_20);
		int32_t L_26;
		L_26 = InvokerFuncInvoker2< int32_t, Il2CppFullySharedGenericAny, Il2CppFullySharedGenericAny >::Invoke(il2cpp_codegen_get_direct_method_pointer(il2cpp_rgctx_method(method->rgctx_data, 4)), il2cpp_rgctx_method(method->rgctx_data, 4), L_20, (il2cpp_codegen_class_is_value_type(il2cpp_rgctx_data_no_init(method->rgctx_data, 3)) ? L_24: *(void**)L_24), (il2cpp_codegen_class_is_value_type(il2cpp_rgctx_data_no_init(method->rgctx_data, 3)) ? L_25: *(void**)L_25));
		V_5 = (bool)((((int32_t)L_26) > ((int32_t)0))? 1 : 0);
		bool L_27 = V_5;
		if (L_27)
		{
			goto IL_0039;
		}
	}
	{
		int32_t L_28 = ___1_start;
		int32_t L_29 = ___2_end;
		V_6 = (bool)((((int32_t)((((int32_t)L_28) < ((int32_t)L_29))? 1 : 0)) == ((int32_t)0))? 1 : 0);
		bool L_30 = V_6;
		if (!L_30)
		{
			goto IL_0068;
		}
	}
	{
		int32_t L_31 = ___2_end;
		V_7 = L_31;
		goto IL_0096;
	}

IL_0068:
	{
		__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC* L_32 = ___0_data;
		int32_t L_33 = ___1_start;
		NullCheck(L_32);
		int32_t L_34 = L_33;
		il2cpp_codegen_memcpy(L_35, (L_32)->GetAddressAt(static_cast<il2cpp_array_size_t>(L_34)), SizeOf_T_tC40FDC7B5C85862D1DEB60A6C3716599A9ECA6BE);
		il2cpp_codegen_memcpy(V_3, L_35, SizeOf_T_tC40FDC7B5C85862D1DEB60A6C3716599A9ECA6BE);
		__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC* L_36 = ___0_data;
		int32_t L_37 = ___1_start;
		int32_t L_38 = L_37;
		___1_start = ((int32_t)il2cpp_codegen_add(L_38, 1));
		__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC* L_39 = ___0_data;
		int32_t L_40 = ___2_end;
		NullCheck(L_39);
		int32_t L_41 = L_40;
		il2cpp_codegen_memcpy(L_42, (L_39)->GetAddressAt(static_cast<il2cpp_array_size_t>(L_41)), SizeOf_T_tC40FDC7B5C85862D1DEB60A6C3716599A9ECA6BE);
		NullCheck(L_36);
		il2cpp_codegen_memcpy((L_36)->GetAddressAt(static_cast<il2cpp_array_size_t>(L_38)), L_42, SizeOf_T_tC40FDC7B5C85862D1DEB60A6C3716599A9ECA6BE);
		Il2CppCodeGenWriteBarrierForClass(il2cpp_rgctx_data(method->rgctx_data, 3), (void**)(L_36)->GetAddressAt(static_cast<il2cpp_array_size_t>(L_38)), (void*)L_42);
		__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC* L_43 = ___0_data;
		int32_t L_44 = ___2_end;
		int32_t L_45 = L_44;
		___2_end = ((int32_t)il2cpp_codegen_subtract(L_45, 1));
		il2cpp_codegen_memcpy(L_46, V_3, SizeOf_T_tC40FDC7B5C85862D1DEB60A6C3716599A9ECA6BE);
		NullCheck(L_43);
		il2cpp_codegen_memcpy((L_43)->GetAddressAt(static_cast<il2cpp_array_size_t>(L_45)), L_46, SizeOf_T_tC40FDC7B5C85862D1DEB60A6C3716599A9ECA6BE);
		Il2CppCodeGenWriteBarrierForClass(il2cpp_rgctx_data(method->rgctx_data, 3), (void**)(L_43)->GetAddressAt(static_cast<il2cpp_array_size_t>(L_45)), (void*)L_46);
	}

IL_0091:
	{
		V_8 = (bool)1;
		goto IL_0018;
	}

IL_0096:
	{
		int32_t L_47 = V_7;
		return L_47;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR int32_t Sorting_Partition_TisLightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2_m0E79CA1E375645FFDF3E1506F789825A9A6D3D95_gshared (LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* ___0_data, int32_t ___1_start, int32_t ___2_end, Func_3_t3E644C82345CE04737DA5CDE018481FE0A88F821* ___3_compare, const RuntimeMethod* method) 
{
	il2cpp_rgctx_method_init(method);
	int32_t V_0 = 0;
	int32_t V_1 = 0;
	LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 V_2;
	memset((&V_2), 0, sizeof(V_2));
	LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 V_3;
	memset((&V_3), 0, sizeof(V_3));
	bool V_4 = false;
	bool V_5 = false;
	bool V_6 = false;
	int32_t V_7 = 0;
	bool V_8 = false;
	{
		int32_t L_0 = ___2_end;
		int32_t L_1 = ___1_start;
		V_0 = ((int32_t)il2cpp_codegen_subtract(L_0, L_1));
		int32_t L_2 = ___1_start;
		int32_t L_3 = V_0;
		V_1 = ((int32_t)il2cpp_codegen_add(L_2, ((int32_t)(L_3/2))));
		LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* L_4 = ___0_data;
		int32_t L_5 = ___1_start;
		int32_t L_6 = V_1;
		int32_t L_7 = ___2_end;
		Func_3_t3E644C82345CE04737DA5CDE018481FE0A88F821* L_8 = ___3_compare;
		LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 L_9;
		L_9 = Sorting_Median3Pivot_TisLightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2_m3AE419868146FAEE6A59E9FA4E33484BFA9930B1(L_4, L_5, L_6, L_7, L_8, il2cpp_rgctx_method(method->rgctx_data, 2));
		V_2 = L_9;
		goto IL_0091;
	}

IL_0018:
	{
		goto IL_0020;
	}

IL_001b:
	{
		int32_t L_10 = ___1_start;
		___1_start = ((int32_t)il2cpp_codegen_add(L_10, 1));
	}

IL_0020:
	{
		Func_3_t3E644C82345CE04737DA5CDE018481FE0A88F821* L_11 = ___3_compare;
		LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* L_12 = ___0_data;
		int32_t L_13 = ___1_start;
		NullCheck(L_12);
		int32_t L_14 = L_13;
		LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 L_15 = (L_12)->GetAt(static_cast<il2cpp_array_size_t>(L_14));
		LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 L_16 = V_2;
		NullCheck(L_11);
		int32_t L_17;
		L_17 = Func_3_Invoke_m2AED59BE1B0645C0DB5DAE117842A1C0AD4BDEBB_inline(L_11, L_15, L_16, il2cpp_rgctx_method(method->rgctx_data, 4));
		V_4 = (bool)((((int32_t)L_17) < ((int32_t)0))? 1 : 0);
		bool L_18 = V_4;
		if (L_18)
		{
			goto IL_001b;
		}
	}
	{
		goto IL_003e;
	}

IL_0039:
	{
		int32_t L_19 = ___2_end;
		___2_end = ((int32_t)il2cpp_codegen_subtract(L_19, 1));
	}

IL_003e:
	{
		Func_3_t3E644C82345CE04737DA5CDE018481FE0A88F821* L_20 = ___3_compare;
		LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* L_21 = ___0_data;
		int32_t L_22 = ___2_end;
		NullCheck(L_21);
		int32_t L_23 = L_22;
		LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 L_24 = (L_21)->GetAt(static_cast<il2cpp_array_size_t>(L_23));
		LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 L_25 = V_2;
		NullCheck(L_20);
		int32_t L_26;
		L_26 = Func_3_Invoke_m2AED59BE1B0645C0DB5DAE117842A1C0AD4BDEBB_inline(L_20, L_24, L_25, il2cpp_rgctx_method(method->rgctx_data, 4));
		V_5 = (bool)((((int32_t)L_26) > ((int32_t)0))? 1 : 0);
		bool L_27 = V_5;
		if (L_27)
		{
			goto IL_0039;
		}
	}
	{
		int32_t L_28 = ___1_start;
		int32_t L_29 = ___2_end;
		V_6 = (bool)((((int32_t)((((int32_t)L_28) < ((int32_t)L_29))? 1 : 0)) == ((int32_t)0))? 1 : 0);
		bool L_30 = V_6;
		if (!L_30)
		{
			goto IL_0068;
		}
	}
	{
		int32_t L_31 = ___2_end;
		V_7 = L_31;
		goto IL_0096;
	}

IL_0068:
	{
		LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* L_32 = ___0_data;
		int32_t L_33 = ___1_start;
		NullCheck(L_32);
		int32_t L_34 = L_33;
		LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 L_35 = (L_32)->GetAt(static_cast<il2cpp_array_size_t>(L_34));
		V_3 = L_35;
		LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* L_36 = ___0_data;
		int32_t L_37 = ___1_start;
		int32_t L_38 = L_37;
		___1_start = ((int32_t)il2cpp_codegen_add(L_38, 1));
		LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* L_39 = ___0_data;
		int32_t L_40 = ___2_end;
		NullCheck(L_39);
		int32_t L_41 = L_40;
		LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 L_42 = (L_39)->GetAt(static_cast<il2cpp_array_size_t>(L_41));
		NullCheck(L_36);
		(L_36)->SetAt(static_cast<il2cpp_array_size_t>(L_38), (LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2)L_42);
		LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* L_43 = ___0_data;
		int32_t L_44 = ___2_end;
		int32_t L_45 = L_44;
		___2_end = ((int32_t)il2cpp_codegen_subtract(L_45, 1));
		LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 L_46 = V_3;
		NullCheck(L_43);
		(L_43)->SetAt(static_cast<il2cpp_array_size_t>(L_45), (LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2)L_46);
	}

IL_0091:
	{
		V_8 = (bool)1;
		goto IL_0018;
	}

IL_0096:
	{
		int32_t L_47 = V_7;
		return L_47;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void Sorting_QuickSort_TisIl2CppFullySharedGenericAny_mEC21DF5A7D470F44BB30B97EB39D03491BD65D1F_gshared (__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC* ___0_data, Func_3_tECED1961B53AB164A131061296ABA1276B4FBBB9* ___1_compare, const RuntimeMethod* method) 
{
	il2cpp_rgctx_method_init(method);
	{
		__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC* L_0 = ___0_data;
		__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC* L_1 = ___0_data;
		NullCheck(L_1);
		Func_3_tECED1961B53AB164A131061296ABA1276B4FBBB9* L_2 = ___1_compare;
		((  void (*) (__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC*, int32_t, int32_t, Func_3_tECED1961B53AB164A131061296ABA1276B4FBBB9*, const RuntimeMethod*))il2cpp_codegen_get_direct_method_pointer(il2cpp_rgctx_method(method->rgctx_data, 2)))(L_0, 0, ((int32_t)il2cpp_codegen_subtract(((int32_t)(((RuntimeArray*)L_1)->max_length)), 1)), L_2, il2cpp_rgctx_method(method->rgctx_data, 2));
		return;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void Sorting_QuickSort_TisVector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3_mAA6CA24576E19917524BFD6BE7AC3ACF4A18B570_gshared (Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* ___0_data, int32_t ___1_start, int32_t ___2_end, Func_3_tD46831209E6E19204CD8F9EAFC74DBFCA3C36C5F* ___3_compare, const RuntimeMethod* method) 
{
	if (!il2cpp_rgctx_is_initialized(method))
	{
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Assert_tDC16963451AC4364803739B73A4477ADCB365863_il2cpp_TypeInfo_var);
		il2cpp_rgctx_method_init(method);
	}
	int32_t V_0 = 0;
	bool V_1 = false;
	bool V_2 = false;
	bool V_3 = false;
	int32_t V_4 = 0;
	bool V_5 = false;
	bool V_6 = false;
	{
		int32_t L_0 = ___2_end;
		int32_t L_1 = ___1_start;
		V_0 = ((int32_t)il2cpp_codegen_subtract(L_0, L_1));
		int32_t L_2 = V_0;
		V_1 = (bool)((((int32_t)L_2) < ((int32_t)1))? 1 : 0);
		bool L_3 = V_1;
		if (!L_3)
		{
			goto IL_000f;
		}
	}
	{
		goto IL_0088;
	}

IL_000f:
	{
		int32_t L_4 = V_0;
		V_2 = (bool)((((int32_t)L_4) < ((int32_t)8))? 1 : 0);
		bool L_5 = V_2;
		if (!L_5)
		{
			goto IL_0024;
		}
	}
	{
		Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* L_6 = ___0_data;
		int32_t L_7 = ___1_start;
		int32_t L_8 = ___2_end;
		Func_3_tD46831209E6E19204CD8F9EAFC74DBFCA3C36C5F* L_9 = ___3_compare;
		Sorting_InsertionSort_TisVector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3_m6B06894C5FA146D1CCE7ECBC21F553F16F2E96F5(L_6, L_7, L_8, L_9, il2cpp_rgctx_method(method->rgctx_data, 2));
		goto IL_0088;
	}

IL_0024:
	{
		int32_t L_10 = ___1_start;
		Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* L_11 = ___0_data;
		NullCheck(L_11);
		il2cpp_codegen_runtime_class_init_inline(Assert_tDC16963451AC4364803739B73A4477ADCB365863_il2cpp_TypeInfo_var);
		Assert_IsTrue_mE42C53B7220324D1FBAFB7AE48A7D8DD7796A663((bool)((((int64_t)((int64_t)(uint64_t)((uint32_t)L_10))) < ((int64_t)((int64_t)((int32_t)(((RuntimeArray*)L_11)->max_length)))))? 1 : 0), NULL);
		int32_t L_12 = ___2_end;
		Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* L_13 = ___0_data;
		NullCheck(L_13);
		Assert_IsTrue_mE42C53B7220324D1FBAFB7AE48A7D8DD7796A663((bool)((((int64_t)((int64_t)(uint64_t)((uint32_t)L_12))) < ((int64_t)((int64_t)((int32_t)(((RuntimeArray*)L_13)->max_length)))))? 1 : 0), NULL);
		int32_t L_14 = ___1_start;
		int32_t L_15 = ___2_end;
		V_3 = (bool)((((int32_t)L_14) < ((int32_t)L_15))? 1 : 0);
		bool L_16 = V_3;
		if (!L_16)
		{
			goto IL_0088;
		}
	}
	{
		Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* L_17 = ___0_data;
		int32_t L_18 = ___1_start;
		int32_t L_19 = ___2_end;
		Func_3_tD46831209E6E19204CD8F9EAFC74DBFCA3C36C5F* L_20 = ___3_compare;
		int32_t L_21;
		L_21 = Sorting_Partition_TisVector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3_m5B1882A69C494B64F1EA761E21D0018C1D6AB6E8(L_17, L_18, L_19, L_20, il2cpp_rgctx_method(method->rgctx_data, 3));
		V_4 = L_21;
		int32_t L_22 = V_4;
		V_5 = (bool)((((int32_t)((((int32_t)L_22) < ((int32_t)1))? 1 : 0)) == ((int32_t)0))? 1 : 0);
		bool L_23 = V_5;
		if (!L_23)
		{
			goto IL_006d;
		}
	}
	{
		Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* L_24 = ___0_data;
		int32_t L_25 = ___1_start;
		int32_t L_26 = V_4;
		Func_3_tD46831209E6E19204CD8F9EAFC74DBFCA3C36C5F* L_27 = ___3_compare;
		Sorting_QuickSort_TisVector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3_mAA6CA24576E19917524BFD6BE7AC3ACF4A18B570(L_24, L_25, L_26, L_27, il2cpp_rgctx_method(method->rgctx_data, 4));
	}

IL_006d:
	{
		int32_t L_28 = V_4;
		int32_t L_29 = ___2_end;
		V_6 = (bool)((((int32_t)((int32_t)il2cpp_codegen_add(L_28, 1))) < ((int32_t)L_29))? 1 : 0);
		bool L_30 = V_6;
		if (!L_30)
		{
			goto IL_0087;
		}
	}
	{
		Vector4U5BU5D_tC0F3A7115F85007510F6D173968200CD31BCF7AD* L_31 = ___0_data;
		int32_t L_32 = V_4;
		int32_t L_33 = ___2_end;
		Func_3_tD46831209E6E19204CD8F9EAFC74DBFCA3C36C5F* L_34 = ___3_compare;
		Sorting_QuickSort_TisVector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3_mAA6CA24576E19917524BFD6BE7AC3ACF4A18B570(L_31, ((int32_t)il2cpp_codegen_add(L_32, 1)), L_33, L_34, il2cpp_rgctx_method(method->rgctx_data, 4));
	}

IL_0087:
	{
	}

IL_0088:
	{
		return;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void Sorting_QuickSort_TisIl2CppFullySharedGenericAny_m64F66E9A59079142461E29BCD21FE90D0C81BB59_gshared (__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC* ___0_data, int32_t ___1_start, int32_t ___2_end, Func_3_tECED1961B53AB164A131061296ABA1276B4FBBB9* ___3_compare, const RuntimeMethod* method) 
{
	if (!il2cpp_rgctx_is_initialized(method))
	{
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Assert_tDC16963451AC4364803739B73A4477ADCB365863_il2cpp_TypeInfo_var);
		il2cpp_rgctx_method_init(method);
	}
	int32_t V_0 = 0;
	bool V_1 = false;
	bool V_2 = false;
	bool V_3 = false;
	int32_t V_4 = 0;
	bool V_5 = false;
	bool V_6 = false;
	{
		int32_t L_0 = ___2_end;
		int32_t L_1 = ___1_start;
		V_0 = ((int32_t)il2cpp_codegen_subtract(L_0, L_1));
		int32_t L_2 = V_0;
		V_1 = (bool)((((int32_t)L_2) < ((int32_t)1))? 1 : 0);
		bool L_3 = V_1;
		if (!L_3)
		{
			goto IL_000f;
		}
	}
	{
		goto IL_0088;
	}

IL_000f:
	{
		int32_t L_4 = V_0;
		V_2 = (bool)((((int32_t)L_4) < ((int32_t)8))? 1 : 0);
		bool L_5 = V_2;
		if (!L_5)
		{
			goto IL_0024;
		}
	}
	{
		__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC* L_6 = ___0_data;
		int32_t L_7 = ___1_start;
		int32_t L_8 = ___2_end;
		Func_3_tECED1961B53AB164A131061296ABA1276B4FBBB9* L_9 = ___3_compare;
		((  void (*) (__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC*, int32_t, int32_t, Func_3_tECED1961B53AB164A131061296ABA1276B4FBBB9*, const RuntimeMethod*))il2cpp_codegen_get_direct_method_pointer(il2cpp_rgctx_method(method->rgctx_data, 2)))(L_6, L_7, L_8, L_9, il2cpp_rgctx_method(method->rgctx_data, 2));
		goto IL_0088;
	}

IL_0024:
	{
		int32_t L_10 = ___1_start;
		__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC* L_11 = ___0_data;
		NullCheck(L_11);
		il2cpp_codegen_runtime_class_init_inline(Assert_tDC16963451AC4364803739B73A4477ADCB365863_il2cpp_TypeInfo_var);
		Assert_IsTrue_mE42C53B7220324D1FBAFB7AE48A7D8DD7796A663((bool)((((int64_t)((int64_t)(uint64_t)((uint32_t)L_10))) < ((int64_t)((int64_t)((int32_t)(((RuntimeArray*)L_11)->max_length)))))? 1 : 0), NULL);
		int32_t L_12 = ___2_end;
		__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC* L_13 = ___0_data;
		NullCheck(L_13);
		Assert_IsTrue_mE42C53B7220324D1FBAFB7AE48A7D8DD7796A663((bool)((((int64_t)((int64_t)(uint64_t)((uint32_t)L_12))) < ((int64_t)((int64_t)((int32_t)(((RuntimeArray*)L_13)->max_length)))))? 1 : 0), NULL);
		int32_t L_14 = ___1_start;
		int32_t L_15 = ___2_end;
		V_3 = (bool)((((int32_t)L_14) < ((int32_t)L_15))? 1 : 0);
		bool L_16 = V_3;
		if (!L_16)
		{
			goto IL_0088;
		}
	}
	{
		__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC* L_17 = ___0_data;
		int32_t L_18 = ___1_start;
		int32_t L_19 = ___2_end;
		Func_3_tECED1961B53AB164A131061296ABA1276B4FBBB9* L_20 = ___3_compare;
		int32_t L_21;
		L_21 = ((  int32_t (*) (__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC*, int32_t, int32_t, Func_3_tECED1961B53AB164A131061296ABA1276B4FBBB9*, const RuntimeMethod*))il2cpp_codegen_get_direct_method_pointer(il2cpp_rgctx_method(method->rgctx_data, 3)))(L_17, L_18, L_19, L_20, il2cpp_rgctx_method(method->rgctx_data, 3));
		V_4 = L_21;
		int32_t L_22 = V_4;
		V_5 = (bool)((((int32_t)((((int32_t)L_22) < ((int32_t)1))? 1 : 0)) == ((int32_t)0))? 1 : 0);
		bool L_23 = V_5;
		if (!L_23)
		{
			goto IL_006d;
		}
	}
	{
		__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC* L_24 = ___0_data;
		int32_t L_25 = ___1_start;
		int32_t L_26 = V_4;
		Func_3_tECED1961B53AB164A131061296ABA1276B4FBBB9* L_27 = ___3_compare;
		((  void (*) (__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC*, int32_t, int32_t, Func_3_tECED1961B53AB164A131061296ABA1276B4FBBB9*, const RuntimeMethod*))il2cpp_codegen_get_direct_method_pointer(il2cpp_rgctx_method(method->rgctx_data, 4)))(L_24, L_25, L_26, L_27, il2cpp_rgctx_method(method->rgctx_data, 4));
	}

IL_006d:
	{
		int32_t L_28 = V_4;
		int32_t L_29 = ___2_end;
		V_6 = (bool)((((int32_t)((int32_t)il2cpp_codegen_add(L_28, 1))) < ((int32_t)L_29))? 1 : 0);
		bool L_30 = V_6;
		if (!L_30)
		{
			goto IL_0087;
		}
	}
	{
		__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC* L_31 = ___0_data;
		int32_t L_32 = V_4;
		int32_t L_33 = ___2_end;
		Func_3_tECED1961B53AB164A131061296ABA1276B4FBBB9* L_34 = ___3_compare;
		((  void (*) (__Il2CppFullySharedGenericTypeU5BU5D_tCAB6D060972DD49223A834B7EEFEB9FE2D003BEC*, int32_t, int32_t, Func_3_tECED1961B53AB164A131061296ABA1276B4FBBB9*, const RuntimeMethod*))il2cpp_codegen_get_direct_method_pointer(il2cpp_rgctx_method(method->rgctx_data, 4)))(L_31, ((int32_t)il2cpp_codegen_add(L_32, 1)), L_33, L_34, il2cpp_rgctx_method(method->rgctx_data, 4));
	}

IL_0087:
	{
	}

IL_0088:
	{
		return;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void Sorting_QuickSort_TisLightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2_mADD51465439832E9BCC31668A2DE42CFCCA07F9C_gshared (LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* ___0_data, int32_t ___1_start, int32_t ___2_end, Func_3_t3E644C82345CE04737DA5CDE018481FE0A88F821* ___3_compare, const RuntimeMethod* method) 
{
	if (!il2cpp_rgctx_is_initialized(method))
	{
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Assert_tDC16963451AC4364803739B73A4477ADCB365863_il2cpp_TypeInfo_var);
		il2cpp_rgctx_method_init(method);
	}
	int32_t V_0 = 0;
	bool V_1 = false;
	bool V_2 = false;
	bool V_3 = false;
	int32_t V_4 = 0;
	bool V_5 = false;
	bool V_6 = false;
	{
		int32_t L_0 = ___2_end;
		int32_t L_1 = ___1_start;
		V_0 = ((int32_t)il2cpp_codegen_subtract(L_0, L_1));
		int32_t L_2 = V_0;
		V_1 = (bool)((((int32_t)L_2) < ((int32_t)1))? 1 : 0);
		bool L_3 = V_1;
		if (!L_3)
		{
			goto IL_000f;
		}
	}
	{
		goto IL_0088;
	}

IL_000f:
	{
		int32_t L_4 = V_0;
		V_2 = (bool)((((int32_t)L_4) < ((int32_t)8))? 1 : 0);
		bool L_5 = V_2;
		if (!L_5)
		{
			goto IL_0024;
		}
	}
	{
		LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* L_6 = ___0_data;
		int32_t L_7 = ___1_start;
		int32_t L_8 = ___2_end;
		Func_3_t3E644C82345CE04737DA5CDE018481FE0A88F821* L_9 = ___3_compare;
		Sorting_InsertionSort_TisLightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2_m50C92303E813A7BFD084FB309E5FB9937C8F2065(L_6, L_7, L_8, L_9, il2cpp_rgctx_method(method->rgctx_data, 2));
		goto IL_0088;
	}

IL_0024:
	{
		int32_t L_10 = ___1_start;
		LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* L_11 = ___0_data;
		NullCheck(L_11);
		il2cpp_codegen_runtime_class_init_inline(Assert_tDC16963451AC4364803739B73A4477ADCB365863_il2cpp_TypeInfo_var);
		Assert_IsTrue_mE42C53B7220324D1FBAFB7AE48A7D8DD7796A663((bool)((((int64_t)((int64_t)(uint64_t)((uint32_t)L_10))) < ((int64_t)((int64_t)((int32_t)(((RuntimeArray*)L_11)->max_length)))))? 1 : 0), NULL);
		int32_t L_12 = ___2_end;
		LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* L_13 = ___0_data;
		NullCheck(L_13);
		Assert_IsTrue_mE42C53B7220324D1FBAFB7AE48A7D8DD7796A663((bool)((((int64_t)((int64_t)(uint64_t)((uint32_t)L_12))) < ((int64_t)((int64_t)((int32_t)(((RuntimeArray*)L_13)->max_length)))))? 1 : 0), NULL);
		int32_t L_14 = ___1_start;
		int32_t L_15 = ___2_end;
		V_3 = (bool)((((int32_t)L_14) < ((int32_t)L_15))? 1 : 0);
		bool L_16 = V_3;
		if (!L_16)
		{
			goto IL_0088;
		}
	}
	{
		LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* L_17 = ___0_data;
		int32_t L_18 = ___1_start;
		int32_t L_19 = ___2_end;
		Func_3_t3E644C82345CE04737DA5CDE018481FE0A88F821* L_20 = ___3_compare;
		int32_t L_21;
		L_21 = Sorting_Partition_TisLightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2_m0E79CA1E375645FFDF3E1506F789825A9A6D3D95(L_17, L_18, L_19, L_20, il2cpp_rgctx_method(method->rgctx_data, 3));
		V_4 = L_21;
		int32_t L_22 = V_4;
		V_5 = (bool)((((int32_t)((((int32_t)L_22) < ((int32_t)1))? 1 : 0)) == ((int32_t)0))? 1 : 0);
		bool L_23 = V_5;
		if (!L_23)
		{
			goto IL_006d;
		}
	}
	{
		LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* L_24 = ___0_data;
		int32_t L_25 = ___1_start;
		int32_t L_26 = V_4;
		Func_3_t3E644C82345CE04737DA5CDE018481FE0A88F821* L_27 = ___3_compare;
		Sorting_QuickSort_TisLightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2_mADD51465439832E9BCC31668A2DE42CFCCA07F9C(L_24, L_25, L_26, L_27, il2cpp_rgctx_method(method->rgctx_data, 4));
	}

IL_006d:
	{
		int32_t L_28 = V_4;
		int32_t L_29 = ___2_end;
		V_6 = (bool)((((int32_t)((int32_t)il2cpp_codegen_add(L_28, 1))) < ((int32_t)L_29))? 1 : 0);
		bool L_30 = V_6;
		if (!L_30)
		{
			goto IL_0087;
		}
	}
	{
		LightCookieMappingU5BU5D_tE1F10A7D54920D3636F1DB7774B3D5F5B560E263* L_31 = ___0_data;
		int32_t L_32 = V_4;
		int32_t L_33 = ___2_end;
		Func_3_t3E644C82345CE04737DA5CDE018481FE0A88F821* L_34 = ___3_compare;
		Sorting_QuickSort_TisLightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2_mADD51465439832E9BCC31668A2DE42CFCCA07F9C(L_31, ((int32_t)il2cpp_codegen_add(L_32, 1)), L_33, L_34, il2cpp_rgctx_method(method->rgctx_data, 4));
	}

IL_0087:
	{
	}

IL_0088:
	{
		return;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void U3CU3Ec__DisplayClass171_0_U3CRegisterDebugU3Eg__RefreshDebugU7C0_TisBoolean_t09A6377A54BE2F9E6985A8149F19234FD7DDFE22_m5019674115061C61566FCE4F42C27F8D1D10CBFC_gshared (U3CU3Ec__DisplayClass171_0_t70061616D0F785A73C9408015CCBEBC3C2B43646* __this, Field_1_t32151A22D4B1B5C1DFFDDACD9F3C78D19596507A* ___0_field, bool ___1_value, const RuntimeMethod* method) 
{
	{
		ProbeReferenceVolume_t05ED7EF2BB9B58F26CE1629F0AA773D14100695F* L_0 = __this->___U3CU3E4__this;
		NullCheck(L_0);
		ProbeReferenceVolume_UnregisterDebug_m29C8C2812597CC2D2B3FBD5CBD374E618C480187(L_0, (bool)0, NULL);
		ProbeReferenceVolume_t05ED7EF2BB9B58F26CE1629F0AA773D14100695F* L_1 = __this->___U3CU3E4__this;
		ProbeVolumeSystemParameters_t0654F2626ACA367E00C375BEB6FEA5B86CB0A58B L_2 = __this->___parameters;
		NullCheck(L_1);
		ProbeReferenceVolume_RegisterDebug_m2F302154AB36B9D5C1739DE3E699CF8574918F53(L_1, L_2, NULL);
		return;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void U3CU3Ec__DisplayClass171_0_U3CRegisterDebugU3Eg__RefreshDebugU7C0_TisInt32_t680FF22E76F6EFAD4375103CBBFFA0421349384C_m100076E774B865F9F042988822BA799CCDF110D1_gshared (U3CU3Ec__DisplayClass171_0_t70061616D0F785A73C9408015CCBEBC3C2B43646* __this, Field_1_t7F813BE8CAF3F3F635B34474DDD7B797C5B6CD2A* ___0_field, int32_t ___1_value, const RuntimeMethod* method) 
{
	{
		ProbeReferenceVolume_t05ED7EF2BB9B58F26CE1629F0AA773D14100695F* L_0 = __this->___U3CU3E4__this;
		NullCheck(L_0);
		ProbeReferenceVolume_UnregisterDebug_m29C8C2812597CC2D2B3FBD5CBD374E618C480187(L_0, (bool)0, NULL);
		ProbeReferenceVolume_t05ED7EF2BB9B58F26CE1629F0AA773D14100695F* L_1 = __this->___U3CU3E4__this;
		ProbeVolumeSystemParameters_t0654F2626ACA367E00C375BEB6FEA5B86CB0A58B L_2 = __this->___parameters;
		NullCheck(L_1);
		ProbeReferenceVolume_RegisterDebug_m2F302154AB36B9D5C1739DE3E699CF8574918F53(L_1, L_2, NULL);
		return;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void U3CU3Ec__DisplayClass171_0_U3CRegisterDebugU3Eg__RefreshDebugU7C0_TisIl2CppFullySharedGenericAny_m7AA2E7868621F0A95B0407951E08EC7786EB4D83_gshared (U3CU3Ec__DisplayClass171_0_t70061616D0F785A73C9408015CCBEBC3C2B43646* __this, Field_1_tEE1A923EA8160028BC34CE74DF77A8FB37FCA5D3* ___0_field, Il2CppFullySharedGenericAny ___1_value, const RuntimeMethod* method) 
{
	{
		ProbeReferenceVolume_t05ED7EF2BB9B58F26CE1629F0AA773D14100695F* L_0 = __this->___U3CU3E4__this;
		NullCheck(L_0);
		ProbeReferenceVolume_UnregisterDebug_m29C8C2812597CC2D2B3FBD5CBD374E618C480187(L_0, (bool)0, NULL);
		ProbeReferenceVolume_t05ED7EF2BB9B58F26CE1629F0AA773D14100695F* L_1 = __this->___U3CU3E4__this;
		ProbeVolumeSystemParameters_t0654F2626ACA367E00C375BEB6FEA5B86CB0A58B L_2 = __this->___parameters;
		NullCheck(L_1);
		ProbeReferenceVolume_RegisterDebug_m2F302154AB36B9D5C1739DE3E699CF8574918F53(L_1, L_2, NULL);
		return;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void ReceiptCodec_Array_TisRuntimeObject_m0CAF3F3D3DA0E985E51978C8C478035AB72A631D_gshared (StringBuilder_t* ___0_json, String_t* ___1_name, RuntimeObject* ___2_values, Action_2_t528DD1A0598C8661FA22AB60F7CEFBF784D3DA6B* ___3_writer, const RuntimeMethod* method) 
{
	il2cpp_rgctx_method_init(method);
	int32_t V_0 = 0;
	bool V_1 = false;
	bool V_2 = false;
	{
		StringBuilder_t* L_0 = ___0_json;
		String_t* L_1 = ___1_name;
		ReceiptCodec_Name_mD9F23DCF6C1E464B6158DA93836EE05CE7738B08(L_0, L_1, NULL);
		StringBuilder_t* L_2 = ___0_json;
		NullCheck(L_2);
		StringBuilder_t* L_3;
		L_3 = StringBuilder_Append_m71228B30F05724CD2CD96D9611DCD61BFB96A6E1(L_2, (Il2CppChar)((int32_t)91), NULL);
		V_0 = 0;
		goto IL_003c;
	}

IL_0016:
	{
		int32_t L_4 = V_0;
		V_1 = (bool)((!(((uint32_t)L_4) <= ((uint32_t)0)))? 1 : 0);
		bool L_5 = V_1;
		if (!L_5)
		{
			goto IL_0028;
		}
	}
	{
		StringBuilder_t* L_6 = ___0_json;
		NullCheck(L_6);
		StringBuilder_t* L_7;
		L_7 = StringBuilder_Append_m71228B30F05724CD2CD96D9611DCD61BFB96A6E1(L_6, (Il2CppChar)((int32_t)44), NULL);
	}

IL_0028:
	{
		Action_2_t528DD1A0598C8661FA22AB60F7CEFBF784D3DA6B* L_8 = ___3_writer;
		StringBuilder_t* L_9 = ___0_json;
		RuntimeObject* L_10 = ___2_values;
		int32_t L_11 = V_0;
		NullCheck(L_10);
		RuntimeObject* L_12;
		L_12 = InterfaceFuncInvoker1< RuntimeObject*, int32_t >::Invoke(0, il2cpp_rgctx_data(method->rgctx_data, 1), L_10, L_11);
		NullCheck(L_8);
		Action_2_Invoke_mF1F80FA522B9327702466C4197420B39418278BD_inline(L_8, L_9, L_12, il2cpp_rgctx_method(method->rgctx_data, 4));
		int32_t L_13 = V_0;
		V_0 = ((int32_t)il2cpp_codegen_add(L_13, 1));
	}

IL_003c:
	{
		int32_t L_14 = V_0;
		RuntimeObject* L_15 = ___2_values;
		NullCheck((RuntimeObject*)L_15);
		int32_t L_16;
		L_16 = InterfaceFuncInvoker0< int32_t >::Invoke(0, il2cpp_rgctx_data(method->rgctx_data, 5), (RuntimeObject*)L_15);
		V_2 = (bool)((((int32_t)L_14) < ((int32_t)L_16))? 1 : 0);
		bool L_17 = V_2;
		if (L_17)
		{
			goto IL_0016;
		}
	}
	{
		StringBuilder_t* L_18 = ___0_json;
		NullCheck(L_18);
		StringBuilder_t* L_19;
		L_19 = StringBuilder_Append_m71228B30F05724CD2CD96D9611DCD61BFB96A6E1(L_18, (Il2CppChar)((int32_t)93), NULL);
		return;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void ReceiptCodec_Array_TisIl2CppFullySharedGenericAny_m9DEF0394A399B1A2D8E0987F353D7CD1DFE532BF_gshared (StringBuilder_t* ___0_json, String_t* ___1_name, RuntimeObject* ___2_values, Action_2_t6F9B4FA82143ACF378558F06FC77D9CE0D68087D* ___3_writer, const RuntimeMethod* method) 
{
	il2cpp_rgctx_method_init(method);
	const uint32_t SizeOf_T_t2772A629BFC4F7E72A89D57A16B2C5EE4D5445A5 = il2cpp_codegen_sizeof(il2cpp_rgctx_data_no_init(method->rgctx_data, 3));
	const Il2CppFullySharedGenericAny L_12 = alloca(SizeOf_T_t2772A629BFC4F7E72A89D57A16B2C5EE4D5445A5);
	int32_t V_0 = 0;
	bool V_1 = false;
	bool V_2 = false;
	{
		StringBuilder_t* L_0 = ___0_json;
		String_t* L_1 = ___1_name;
		ReceiptCodec_Name_mD9F23DCF6C1E464B6158DA93836EE05CE7738B08(L_0, L_1, NULL);
		StringBuilder_t* L_2 = ___0_json;
		NullCheck(L_2);
		StringBuilder_t* L_3;
		L_3 = StringBuilder_Append_m71228B30F05724CD2CD96D9611DCD61BFB96A6E1(L_2, (Il2CppChar)((int32_t)91), NULL);
		V_0 = 0;
		goto IL_003c;
	}

IL_0016:
	{
		int32_t L_4 = V_0;
		V_1 = (bool)((!(((uint32_t)L_4) <= ((uint32_t)0)))? 1 : 0);
		bool L_5 = V_1;
		if (!L_5)
		{
			goto IL_0028;
		}
	}
	{
		StringBuilder_t* L_6 = ___0_json;
		NullCheck(L_6);
		StringBuilder_t* L_7;
		L_7 = StringBuilder_Append_m71228B30F05724CD2CD96D9611DCD61BFB96A6E1(L_6, (Il2CppChar)((int32_t)44), NULL);
	}

IL_0028:
	{
		Action_2_t6F9B4FA82143ACF378558F06FC77D9CE0D68087D* L_8 = ___3_writer;
		StringBuilder_t* L_9 = ___0_json;
		RuntimeObject* L_10 = ___2_values;
		int32_t L_11 = V_0;
		NullCheck(L_10);
		InterfaceActionInvoker2Invoker< int32_t, Il2CppFullySharedGenericAny* >::Invoke(0, il2cpp_rgctx_data(method->rgctx_data, 1), L_10, L_11, (Il2CppFullySharedGenericAny*)L_12);
		NullCheck(L_8);
		InvokerActionInvoker2< StringBuilder_t*, Il2CppFullySharedGenericAny >::Invoke(il2cpp_codegen_get_direct_method_pointer(il2cpp_rgctx_method(method->rgctx_data, 4)), il2cpp_rgctx_method(method->rgctx_data, 4), L_8, L_9, (il2cpp_codegen_class_is_value_type(il2cpp_rgctx_data_no_init(method->rgctx_data, 3)) ? L_12: *(void**)L_12));
		int32_t L_13 = V_0;
		V_0 = ((int32_t)il2cpp_codegen_add(L_13, 1));
	}

IL_003c:
	{
		int32_t L_14 = V_0;
		RuntimeObject* L_15 = ___2_values;
		NullCheck((RuntimeObject*)L_15);
		int32_t L_16;
		L_16 = InterfaceFuncInvoker0< int32_t >::Invoke(0, il2cpp_rgctx_data(method->rgctx_data, 5), (RuntimeObject*)L_15);
		V_2 = (bool)((((int32_t)L_14) < ((int32_t)L_16))? 1 : 0);
		bool L_17 = V_2;
		if (L_17)
		{
			goto IL_0016;
		}
	}
	{
		StringBuilder_t* L_18 = ___0_json;
		NullCheck(L_18);
		StringBuilder_t* L_19;
		L_19 = StringBuilder_Append_m71228B30F05724CD2CD96D9611DCD61BFB96A6E1(L_18, (Il2CppChar)((int32_t)93), NULL);
		return;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR int32_t RenderGraphResourcesData_AddNewRenderGraphResource_TisRuntimeObject_mB9040DF97633813729CADB454AAEAF31E23C7E91_gshared (RenderGraphResourcesData_tB2FF97B16A3E1DE700283778679C5CC0C39F4CFE* __this, RuntimeObject** ___0_outRes, bool ___1_pooledResource, const RuntimeMethod* method) 
{
	if (!il2cpp_rgctx_is_initialized(method))
	{
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&DynamicArray_1_Resize_mEEEB907EAEFD4C22DB449FF052CF6AC967A27AD1_RuntimeMethod_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&DynamicArray_1_get_Item_m5FC9383C3A815B0DF7AAD4C2A5CDFB1A25586ECE_RuntimeMethod_var);
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&DynamicArray_1_get_size_m56D2768863B15299FA4F2F14E271686207A8C2E4_RuntimeMethod_var);
		il2cpp_rgctx_method_init(method);
	}
	int32_t V_0 = 0;
	bool V_1 = false;
	int32_t V_2 = 0;
	RuntimeObject** G_B4_0 = NULL;
	RuntimeObject** G_B3_0 = NULL;
	IRenderGraphResourcePool_t8BF833F3C5D0BD8E45632CF923363EC782F4DDA8* G_B5_0 = NULL;
	RuntimeObject** G_B5_1 = NULL;
	{
		DynamicArray_1_t401F46C0081DE185BCAB1D30DE8D6B6DC9AA6AFB* L_0 = __this->___resourceArray;
		NullCheck(L_0);
		int32_t L_1;
		L_1 = DynamicArray_1_get_size_m56D2768863B15299FA4F2F14E271686207A8C2E4_inline(L_0, DynamicArray_1_get_size_m56D2768863B15299FA4F2F14E271686207A8C2E4_RuntimeMethod_var);
		V_0 = L_1;
		DynamicArray_1_t401F46C0081DE185BCAB1D30DE8D6B6DC9AA6AFB* L_2 = __this->___resourceArray;
		DynamicArray_1_t401F46C0081DE185BCAB1D30DE8D6B6DC9AA6AFB* L_3 = __this->___resourceArray;
		NullCheck(L_3);
		int32_t L_4;
		L_4 = DynamicArray_1_get_size_m56D2768863B15299FA4F2F14E271686207A8C2E4_inline(L_3, DynamicArray_1_get_size_m56D2768863B15299FA4F2F14E271686207A8C2E4_RuntimeMethod_var);
		NullCheck(L_2);
		DynamicArray_1_Resize_mEEEB907EAEFD4C22DB449FF052CF6AC967A27AD1(L_2, ((int32_t)il2cpp_codegen_add(L_4, 1)), (bool)1, DynamicArray_1_Resize_mEEEB907EAEFD4C22DB449FF052CF6AC967A27AD1_RuntimeMethod_var);
		DynamicArray_1_t401F46C0081DE185BCAB1D30DE8D6B6DC9AA6AFB* L_5 = __this->___resourceArray;
		int32_t L_6 = V_0;
		NullCheck(L_5);
		IRenderGraphResource_tF24653A388C17849844C128C19C7A6599C7ADB7D** L_7;
		L_7 = DynamicArray_1_get_Item_m5FC9383C3A815B0DF7AAD4C2A5CDFB1A25586ECE(L_5, L_6, DynamicArray_1_get_Item_m5FC9383C3A815B0DF7AAD4C2A5CDFB1A25586ECE_RuntimeMethod_var);
		IRenderGraphResource_tF24653A388C17849844C128C19C7A6599C7ADB7D* L_8 = *((IRenderGraphResource_tF24653A388C17849844C128C19C7A6599C7ADB7D**)L_7);
		V_1 = (bool)((((RuntimeObject*)(IRenderGraphResource_tF24653A388C17849844C128C19C7A6599C7ADB7D*)L_8) == ((RuntimeObject*)(RuntimeObject*)NULL))? 1 : 0);
		bool L_9 = V_1;
		if (!L_9)
		{
			goto IL_0052;
		}
	}
	{
		DynamicArray_1_t401F46C0081DE185BCAB1D30DE8D6B6DC9AA6AFB* L_10 = __this->___resourceArray;
		int32_t L_11 = V_0;
		NullCheck(L_10);
		IRenderGraphResource_tF24653A388C17849844C128C19C7A6599C7ADB7D** L_12;
		L_12 = DynamicArray_1_get_Item_m5FC9383C3A815B0DF7AAD4C2A5CDFB1A25586ECE(L_10, L_11, DynamicArray_1_get_Item_m5FC9383C3A815B0DF7AAD4C2A5CDFB1A25586ECE_RuntimeMethod_var);
		RuntimeObject* L_13;
		L_13 = Activator_CreateInstance_TisRuntimeObject_m62506836177F0F862A8D619638BF37F48721F138(il2cpp_rgctx_method(method->rgctx_data, 0));
		*((RuntimeObject**)L_12) = (RuntimeObject*)L_13;
		Il2CppCodeGenWriteBarrier((void**)(RuntimeObject**)L_12, (void*)(RuntimeObject*)L_13);
	}

IL_0052:
	{
		RuntimeObject** L_14 = ___0_outRes;
		DynamicArray_1_t401F46C0081DE185BCAB1D30DE8D6B6DC9AA6AFB* L_15 = __this->___resourceArray;
		int32_t L_16 = V_0;
		NullCheck(L_15);
		IRenderGraphResource_tF24653A388C17849844C128C19C7A6599C7ADB7D** L_17;
		L_17 = DynamicArray_1_get_Item_m5FC9383C3A815B0DF7AAD4C2A5CDFB1A25586ECE(L_15, L_16, DynamicArray_1_get_Item_m5FC9383C3A815B0DF7AAD4C2A5CDFB1A25586ECE_RuntimeMethod_var);
		IRenderGraphResource_tF24653A388C17849844C128C19C7A6599C7ADB7D* L_18 = *((IRenderGraphResource_tF24653A388C17849844C128C19C7A6599C7ADB7D**)L_17);
		*(RuntimeObject**)L_14 = ((RuntimeObject*)Castclass((RuntimeObject*)((RuntimeObject*)IsInst((RuntimeObject*)L_18, il2cpp_rgctx_data(method->rgctx_data, 1))), il2cpp_rgctx_data(method->rgctx_data, 1)));
		Il2CppCodeGenWriteBarrier((void**)(RuntimeObject**)L_14, (void*)((RuntimeObject*)Castclass((RuntimeObject*)((RuntimeObject*)IsInst((RuntimeObject*)L_18, il2cpp_rgctx_data(method->rgctx_data, 1))), il2cpp_rgctx_data(method->rgctx_data, 1))));
		RuntimeObject** L_19 = ___0_outRes;
		bool L_20 = ___1_pooledResource;
		if (L_20)
		{
			G_B4_0 = L_19;
			goto IL_0076;
		}
		G_B3_0 = L_19;
	}
	{
		G_B5_0 = ((IRenderGraphResourcePool_t8BF833F3C5D0BD8E45632CF923363EC782F4DDA8*)(NULL));
		G_B5_1 = G_B3_0;
		goto IL_007c;
	}

IL_0076:
	{
		IRenderGraphResourcePool_t8BF833F3C5D0BD8E45632CF923363EC782F4DDA8* L_21 = __this->___pool;
		G_B5_0 = L_21;
		G_B5_1 = G_B4_0;
	}

IL_007c:
	{
		NullCheck((IRenderGraphResource_tF24653A388C17849844C128C19C7A6599C7ADB7D*)(*G_B5_1));
		VirtualActionInvoker1< IRenderGraphResourcePool_t8BF833F3C5D0BD8E45632CF923363EC782F4DDA8* >::Invoke(4, (IRenderGraphResource_tF24653A388C17849844C128C19C7A6599C7ADB7D*)(*G_B5_1), G_B5_0);
		int32_t L_22 = V_0;
		V_2 = L_22;
		goto IL_008c;
	}

IL_008c:
	{
		int32_t L_23 = V_2;
		return L_23;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void TypeConstructorVisitor_Visit_TisBounds_t367E830C64BBF235ED8C3B2F8CF6254FDCAD39C3_m2A21711A3D655B51E421ACBEA3F03A09C8BBC250_gshared (TypeConstructorVisitor_tFC61250F68BF43FE889F5B1002CBFF90648E9C7F* __this, const RuntimeMethod* method) 
{
	if (!il2cpp_rgctx_is_initialized(method))
	{
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&TypeUtility_t62F146E51B66BB18FA0E1EFA84A564FF2B8AAD03_il2cpp_TypeInfo_var);
		il2cpp_rgctx_method_init(method);
	}
	{
		il2cpp_codegen_runtime_class_init_inline(TypeUtility_t62F146E51B66BB18FA0E1EFA84A564FF2B8AAD03_il2cpp_TypeInfo_var);
		RuntimeObject* L_0;
		L_0 = TypeUtility_CreateTypeConstructor_TisBounds_t367E830C64BBF235ED8C3B2F8CF6254FDCAD39C3_m16C827D0F6107B7998F6C99B57F7CC2F181E2198(il2cpp_rgctx_method(method->rgctx_data, 0));
		__this->___TypeConstructor = (RuntimeObject*)L_0;
		Il2CppCodeGenWriteBarrier((void**)(&__this->___TypeConstructor), (void*)(RuntimeObject*)L_0);
		return;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void TypeConstructorVisitor_Visit_TisBoundsInt_t4E757DE5EFF9FCB42000F173360DDC63B5585485_mA9E7AA6DB293483965B65EEEBF63885DEF084EA2_gshared (TypeConstructorVisitor_tFC61250F68BF43FE889F5B1002CBFF90648E9C7F* __this, const RuntimeMethod* method) 
{
	if (!il2cpp_rgctx_is_initialized(method))
	{
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&TypeUtility_t62F146E51B66BB18FA0E1EFA84A564FF2B8AAD03_il2cpp_TypeInfo_var);
		il2cpp_rgctx_method_init(method);
	}
	{
		il2cpp_codegen_runtime_class_init_inline(TypeUtility_t62F146E51B66BB18FA0E1EFA84A564FF2B8AAD03_il2cpp_TypeInfo_var);
		RuntimeObject* L_0;
		L_0 = TypeUtility_CreateTypeConstructor_TisBoundsInt_t4E757DE5EFF9FCB42000F173360DDC63B5585485_m8F344250A2F9E6EE6DDBA6BA833BB36D0F272B66(il2cpp_rgctx_method(method->rgctx_data, 0));
		__this->___TypeConstructor = (RuntimeObject*)L_0;
		Il2CppCodeGenWriteBarrier((void**)(&__this->___TypeConstructor), (void*)(RuntimeObject*)L_0);
		return;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void TypeConstructorVisitor_Visit_TisColor_tD001788D726C3A7F1379BEED0260B9591F440C1F_mFE98C0ECD8751FEC86E5F9CD2AFC20794571C81C_gshared (TypeConstructorVisitor_tFC61250F68BF43FE889F5B1002CBFF90648E9C7F* __this, const RuntimeMethod* method) 
{
	if (!il2cpp_rgctx_is_initialized(method))
	{
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&TypeUtility_t62F146E51B66BB18FA0E1EFA84A564FF2B8AAD03_il2cpp_TypeInfo_var);
		il2cpp_rgctx_method_init(method);
	}
	{
		il2cpp_codegen_runtime_class_init_inline(TypeUtility_t62F146E51B66BB18FA0E1EFA84A564FF2B8AAD03_il2cpp_TypeInfo_var);
		RuntimeObject* L_0;
		L_0 = TypeUtility_CreateTypeConstructor_TisColor_tD001788D726C3A7F1379BEED0260B9591F440C1F_mBBCB804F367E06EA4D482F1B69165DD2B5BF38FF(il2cpp_rgctx_method(method->rgctx_data, 0));
		__this->___TypeConstructor = (RuntimeObject*)L_0;
		Il2CppCodeGenWriteBarrier((void**)(&__this->___TypeConstructor), (void*)(RuntimeObject*)L_0);
		return;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void TypeConstructorVisitor_Visit_TisRuntimeObject_m6C6E2EDC433DCAB90206712FB63993865A9B9305_gshared (TypeConstructorVisitor_tFC61250F68BF43FE889F5B1002CBFF90648E9C7F* __this, const RuntimeMethod* method) 
{
	if (!il2cpp_rgctx_is_initialized(method))
	{
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&TypeUtility_t62F146E51B66BB18FA0E1EFA84A564FF2B8AAD03_il2cpp_TypeInfo_var);
		il2cpp_rgctx_method_init(method);
	}
	{
		il2cpp_codegen_runtime_class_init_inline(TypeUtility_t62F146E51B66BB18FA0E1EFA84A564FF2B8AAD03_il2cpp_TypeInfo_var);
		RuntimeObject* L_0;
		L_0 = TypeUtility_CreateTypeConstructor_TisRuntimeObject_m4E17F588B090C1DADAE2D986BDA407DECEAC020F(il2cpp_rgctx_method(method->rgctx_data, 0));
		__this->___TypeConstructor = (RuntimeObject*)L_0;
		Il2CppCodeGenWriteBarrier((void**)(&__this->___TypeConstructor), (void*)(RuntimeObject*)L_0);
		return;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void TypeConstructorVisitor_Visit_TisRect_tA04E0F8A1830E767F40FB27ECD8D309303571F0D_m97DBB59374BCA99C98C45F169AF69955608B68AA_gshared (TypeConstructorVisitor_tFC61250F68BF43FE889F5B1002CBFF90648E9C7F* __this, const RuntimeMethod* method) 
{
	if (!il2cpp_rgctx_is_initialized(method))
	{
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&TypeUtility_t62F146E51B66BB18FA0E1EFA84A564FF2B8AAD03_il2cpp_TypeInfo_var);
		il2cpp_rgctx_method_init(method);
	}
	{
		il2cpp_codegen_runtime_class_init_inline(TypeUtility_t62F146E51B66BB18FA0E1EFA84A564FF2B8AAD03_il2cpp_TypeInfo_var);
		RuntimeObject* L_0;
		L_0 = TypeUtility_CreateTypeConstructor_TisRect_tA04E0F8A1830E767F40FB27ECD8D309303571F0D_m2C5F5CF80D13B041768C7845C5AAEEC02BB683BA(il2cpp_rgctx_method(method->rgctx_data, 0));
		__this->___TypeConstructor = (RuntimeObject*)L_0;
		Il2CppCodeGenWriteBarrier((void**)(&__this->___TypeConstructor), (void*)(RuntimeObject*)L_0);
		return;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void TypeConstructorVisitor_Visit_TisRectInt_t1744D10E1063135DA9D574F95205B98DAC600CB8_m7C42EB46E69BD2515C39AB6013A0763C6479AD66_gshared (TypeConstructorVisitor_tFC61250F68BF43FE889F5B1002CBFF90648E9C7F* __this, const RuntimeMethod* method) 
{
	if (!il2cpp_rgctx_is_initialized(method))
	{
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&TypeUtility_t62F146E51B66BB18FA0E1EFA84A564FF2B8AAD03_il2cpp_TypeInfo_var);
		il2cpp_rgctx_method_init(method);
	}
	{
		il2cpp_codegen_runtime_class_init_inline(TypeUtility_t62F146E51B66BB18FA0E1EFA84A564FF2B8AAD03_il2cpp_TypeInfo_var);
		RuntimeObject* L_0;
		L_0 = TypeUtility_CreateTypeConstructor_TisRectInt_t1744D10E1063135DA9D574F95205B98DAC600CB8_mF6949D9EDD480E6666CD975C66487AAD6ABC7D11(il2cpp_rgctx_method(method->rgctx_data, 0));
		__this->___TypeConstructor = (RuntimeObject*)L_0;
		Il2CppCodeGenWriteBarrier((void**)(&__this->___TypeConstructor), (void*)(RuntimeObject*)L_0);
		return;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void TypeConstructorVisitor_Visit_TisVector2_t1FD6F485C871E832B347AB2DC8CBA08B739D8DF7_m032CA5A330B4032D164F88B2B40B6A7F2590357F_gshared (TypeConstructorVisitor_tFC61250F68BF43FE889F5B1002CBFF90648E9C7F* __this, const RuntimeMethod* method) 
{
	if (!il2cpp_rgctx_is_initialized(method))
	{
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&TypeUtility_t62F146E51B66BB18FA0E1EFA84A564FF2B8AAD03_il2cpp_TypeInfo_var);
		il2cpp_rgctx_method_init(method);
	}
	{
		il2cpp_codegen_runtime_class_init_inline(TypeUtility_t62F146E51B66BB18FA0E1EFA84A564FF2B8AAD03_il2cpp_TypeInfo_var);
		RuntimeObject* L_0;
		L_0 = TypeUtility_CreateTypeConstructor_TisVector2_t1FD6F485C871E832B347AB2DC8CBA08B739D8DF7_mE0C65F4221E48BB07F75856972A0CCDAE284AB9F(il2cpp_rgctx_method(method->rgctx_data, 0));
		__this->___TypeConstructor = (RuntimeObject*)L_0;
		Il2CppCodeGenWriteBarrier((void**)(&__this->___TypeConstructor), (void*)(RuntimeObject*)L_0);
		return;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void TypeConstructorVisitor_Visit_TisVector2Int_t69B2886EBAB732D9B880565E18E7568F3DE0CE6A_m0E8E39845CA3F1BFADAC1B15E849E5885D813E6F_gshared (TypeConstructorVisitor_tFC61250F68BF43FE889F5B1002CBFF90648E9C7F* __this, const RuntimeMethod* method) 
{
	if (!il2cpp_rgctx_is_initialized(method))
	{
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&TypeUtility_t62F146E51B66BB18FA0E1EFA84A564FF2B8AAD03_il2cpp_TypeInfo_var);
		il2cpp_rgctx_method_init(method);
	}
	{
		il2cpp_codegen_runtime_class_init_inline(TypeUtility_t62F146E51B66BB18FA0E1EFA84A564FF2B8AAD03_il2cpp_TypeInfo_var);
		RuntimeObject* L_0;
		L_0 = TypeUtility_CreateTypeConstructor_TisVector2Int_t69B2886EBAB732D9B880565E18E7568F3DE0CE6A_mC8EF710494C8986B279262C6C64947BE2C1DC55C(il2cpp_rgctx_method(method->rgctx_data, 0));
		__this->___TypeConstructor = (RuntimeObject*)L_0;
		Il2CppCodeGenWriteBarrier((void**)(&__this->___TypeConstructor), (void*)(RuntimeObject*)L_0);
		return;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void TypeConstructorVisitor_Visit_TisVector3_t24C512C7B96BBABAD472002D0BA2BDA40A5A80B2_mA88A16DC097E207AD6CE15E89D3B94DBB01BDACE_gshared (TypeConstructorVisitor_tFC61250F68BF43FE889F5B1002CBFF90648E9C7F* __this, const RuntimeMethod* method) 
{
	if (!il2cpp_rgctx_is_initialized(method))
	{
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&TypeUtility_t62F146E51B66BB18FA0E1EFA84A564FF2B8AAD03_il2cpp_TypeInfo_var);
		il2cpp_rgctx_method_init(method);
	}
	{
		il2cpp_codegen_runtime_class_init_inline(TypeUtility_t62F146E51B66BB18FA0E1EFA84A564FF2B8AAD03_il2cpp_TypeInfo_var);
		RuntimeObject* L_0;
		L_0 = TypeUtility_CreateTypeConstructor_TisVector3_t24C512C7B96BBABAD472002D0BA2BDA40A5A80B2_m1AB8BF0921C24186B3C43FC4341AAD2F6FE87C4D(il2cpp_rgctx_method(method->rgctx_data, 0));
		__this->___TypeConstructor = (RuntimeObject*)L_0;
		Il2CppCodeGenWriteBarrier((void**)(&__this->___TypeConstructor), (void*)(RuntimeObject*)L_0);
		return;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void TypeConstructorVisitor_Visit_TisVector3Int_t65CB06F557251D18A37BD71F3655BA836A357376_m28D19B06528A4614AF9C3E29DC8274DE067868D8_gshared (TypeConstructorVisitor_tFC61250F68BF43FE889F5B1002CBFF90648E9C7F* __this, const RuntimeMethod* method) 
{
	if (!il2cpp_rgctx_is_initialized(method))
	{
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&TypeUtility_t62F146E51B66BB18FA0E1EFA84A564FF2B8AAD03_il2cpp_TypeInfo_var);
		il2cpp_rgctx_method_init(method);
	}
	{
		il2cpp_codegen_runtime_class_init_inline(TypeUtility_t62F146E51B66BB18FA0E1EFA84A564FF2B8AAD03_il2cpp_TypeInfo_var);
		RuntimeObject* L_0;
		L_0 = TypeUtility_CreateTypeConstructor_TisVector3Int_t65CB06F557251D18A37BD71F3655BA836A357376_mB00220519A80AA5ACE36B7DBA2E6A6CB796302AF(il2cpp_rgctx_method(method->rgctx_data, 0));
		__this->___TypeConstructor = (RuntimeObject*)L_0;
		Il2CppCodeGenWriteBarrier((void**)(&__this->___TypeConstructor), (void*)(RuntimeObject*)L_0);
		return;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void TypeConstructorVisitor_Visit_TisVector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3_m3CD9CD3C768BBCC83DD02B2C76300A03AF1B1AD6_gshared (TypeConstructorVisitor_tFC61250F68BF43FE889F5B1002CBFF90648E9C7F* __this, const RuntimeMethod* method) 
{
	if (!il2cpp_rgctx_is_initialized(method))
	{
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&TypeUtility_t62F146E51B66BB18FA0E1EFA84A564FF2B8AAD03_il2cpp_TypeInfo_var);
		il2cpp_rgctx_method_init(method);
	}
	{
		il2cpp_codegen_runtime_class_init_inline(TypeUtility_t62F146E51B66BB18FA0E1EFA84A564FF2B8AAD03_il2cpp_TypeInfo_var);
		RuntimeObject* L_0;
		L_0 = TypeUtility_CreateTypeConstructor_TisVector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3_mED1DC338E5DB62F3E64F6272A9F12150DA5CC1B9(il2cpp_rgctx_method(method->rgctx_data, 0));
		__this->___TypeConstructor = (RuntimeObject*)L_0;
		Il2CppCodeGenWriteBarrier((void**)(&__this->___TypeConstructor), (void*)(RuntimeObject*)L_0);
		return;
	}
}
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void TypeConstructorVisitor_Visit_TisIl2CppFullySharedGenericAny_m8B414261A078E3FE7517FAF2F9E944969F6B73E2_gshared (TypeConstructorVisitor_tFC61250F68BF43FE889F5B1002CBFF90648E9C7F* __this, const RuntimeMethod* method) 
{
	if (!il2cpp_rgctx_is_initialized(method))
	{
		il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&TypeUtility_t62F146E51B66BB18FA0E1EFA84A564FF2B8AAD03_il2cpp_TypeInfo_var);
		il2cpp_rgctx_method_init(method);
	}
	{
		il2cpp_codegen_runtime_class_init_inline(TypeUtility_t62F146E51B66BB18FA0E1EFA84A564FF2B8AAD03_il2cpp_TypeInfo_var);
		RuntimeObject* L_0;
		L_0 = ((  RuntimeObject* (*) (const RuntimeMethod*))il2cpp_codegen_get_direct_method_pointer(il2cpp_rgctx_method(method->rgctx_data, 0)))(il2cpp_rgctx_method(method->rgctx_data, 0));
		__this->___TypeConstructor = (RuntimeObject*)L_0;
		Il2CppCodeGenWriteBarrier((void**)(&__this->___TypeConstructor), (void*)(RuntimeObject*)L_0);
		return;
	}
}
IL2CPP_MANAGED_FORCE_INLINE IL2CPP_METHOD_ATTR int32_t Func_3_Invoke_mE6CD106F59B0ADD2DF9C211DC4CF4088F5A1A4BB_gshared_inline (Func_3_tD46831209E6E19204CD8F9EAFC74DBFCA3C36C5F* __this, Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 ___0_arg1, Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 ___1_arg2, const RuntimeMethod* method) 
{
	typedef int32_t (*FunctionPointerType) (RuntimeObject*, Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3, Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3, const RuntimeMethod*);
	return ((FunctionPointerType)__this->___invoke_impl)((Il2CppObject*)__this->___method_code, ___0_arg1, ___1_arg2, reinterpret_cast<RuntimeMethod*>(__this->___method));
}
IL2CPP_MANAGED_FORCE_INLINE IL2CPP_METHOD_ATTR int32_t Func_3_Invoke_m2AED59BE1B0645C0DB5DAE117842A1C0AD4BDEBB_gshared_inline (Func_3_t3E644C82345CE04737DA5CDE018481FE0A88F821* __this, LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 ___0_arg1, LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2 ___1_arg2, const RuntimeMethod* method) 
{
	typedef int32_t (*FunctionPointerType) (RuntimeObject*, LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2, LightCookieMapping_t76B317D9FDE96056FA698B46B45D7F0937BD02D2, const RuntimeMethod*);
	return ((FunctionPointerType)__this->___invoke_impl)((Il2CppObject*)__this->___method_code, ___0_arg1, ___1_arg2, reinterpret_cast<RuntimeMethod*>(__this->___method));
}
IL2CPP_MANAGED_FORCE_INLINE IL2CPP_METHOD_ATTR void Action_2_Invoke_m7BFCE0BBCF67689D263059B56A8D79161B698587_gshared_inline (Action_2_t156C43F079E7E68155FCDCD12DC77DD11AEF7E3C* __this, RuntimeObject* ___0_arg1, RuntimeObject* ___1_arg2, const RuntimeMethod* method) 
{
	typedef void (*FunctionPointerType) (RuntimeObject*, RuntimeObject*, RuntimeObject*, const RuntimeMethod*);
	((FunctionPointerType)__this->___invoke_impl)((Il2CppObject*)__this->___method_code, ___0_arg1, ___1_arg2, reinterpret_cast<RuntimeMethod*>(__this->___method));
}
IL2CPP_MANAGED_FORCE_INLINE IL2CPP_METHOD_ATTR int32_t DynamicArray_1_get_size_m1B00C20A8CC4D62269585D16A58425D3F258836F_gshared_inline (DynamicArray_1_t7C64F5A74B7BA6F6B3589A766CADE3F59C6C7BCA* __this, const RuntimeMethod* method) 
{
	{
		int32_t L_0 = __this->___U3CsizeU3Ek__BackingField;
		return L_0;
	}
}
