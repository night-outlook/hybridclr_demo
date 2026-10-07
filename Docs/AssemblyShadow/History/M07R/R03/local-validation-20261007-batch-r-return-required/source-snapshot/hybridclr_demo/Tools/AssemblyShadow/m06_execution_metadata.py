"""M06 byte-derived execution metadata. No managed code is loaded or executed.

The old M05 decoder/domain is not changed. Unsupported metadata fails closed.
Portable PDB symbols are independently decoded, not inferred from proof prose.
"""
from __future__ import annotations

import base64
import hashlib
from dataclasses import dataclass
from pathlib import Path
import uuid

from m04_metadata import Reader
from m05_types import MethodProof, Signature, IL_OPS, reflection_escape
from shadow_tools import VerificationError, require


@dataclass(frozen=True)
class Shape:
    full: str
    reflection: str
    assembly: str
    arguments: tuple = ()
    element: object = None
    suffix: str = ""

    @property
    def qualified(self):
        return self.reflection + ", " + (self.assembly or "<<<NULL>>>")

    def evidence(self):
        return dict(assembly=self.assembly, type=self.reflection)


OPS = dict(IL_OPS)
for start, names in (
    (0x46, "ldind.i1 ldind.u1 ldind.i2 ldind.u2 ldind.i4 ldind.u4 ldind.i8 ldind.i ldind.r4 ldind.r8 ldind.ref stind.ref stind.i1 stind.i2 stind.i4 stind.i8 stind.r4 stind.r8 add sub mul div div.un rem rem.un and or xor shl shr shr.un neg not conv.i1 conv.i2 conv.i4 conv.i8 conv.r4 conv.r8 conv.u4 conv.u8"),
    (0x90, "ldelem.i1 ldelem.u1 ldelem.i2 ldelem.u2 ldelem.i4 ldelem.u4 ldelem.i8 ldelem.i ldelem.r4 ldelem.r8 ldelem.ref stelem.i stelem.i1 stelem.i2 stelem.i4 stelem.i8 stelem.r4 stelem.r8 stelem.ref"),
    (0x82, "conv.ovf.i1.un conv.ovf.i2.un conv.ovf.i4.un conv.ovf.i8.un conv.ovf.u1.un conv.ovf.u2.un conv.ovf.u4.un conv.ovf.u8.un conv.ovf.i.un conv.ovf.u.un"),
    (0xb3, "conv.ovf.i1 conv.ovf.u1 conv.ovf.i2 conv.ovf.u2 conv.ovf.i4 conv.ovf.u4 conv.ovf.i8 conv.ovf.u8"),
    (0xd1, "conv.u2 conv.u1 conv.i conv.ovf.i conv.ovf.u add.ovf add.ovf.un mul.ovf mul.ovf.un sub.ovf sub.ovf.un endfinally"),
):
    OPS.update({start + i: (name, "") for i, name in enumerate(names.split())})
OPS.update({0x29:("calli","token"), 0x22:("ldc.r4","float4"), 0x23:("ldc.r8","float8"),
            0x76:("conv.r.un",""), 0xa3:("ldelem","token"), 0xa4:("stelem","token"),
            0xc2:("refanyval","token"), 0xc3:("ckfinite",""), 0xc6:("mkrefany","token"),
            0xdd:("leave","branch4"), 0xde:("leave.s","branch1"), 0xdf:("stind.i",""), 0xe0:("conv.u",""),
            0xfe00:("arglist",""), 0xfe06:("ldftn","token"), 0xfe07:("ldvirtftn","token"),
            0xfe0f:("localloc",""), 0xfe11:("endfilter",""), 0xfe12:("unaligned.","uint1"),
            0xfe13:("volatile.",""), 0xfe14:("tail.",""), 0xfe16:("constrained.","token"),
            0xfe17:("cpblk",""), 0xfe18:("initblk",""), 0xfe1a:("rethrow",""),
            0xfe1c:("sizeof","token"), 0xfe1d:("refanytype",""), 0xfe1e:("readonly.","")})
for code, name in enumerate("ldarg ldarga starg ldloc ldloca stloc".split()):
    OPS[0x0e + code] = (name + ".s", "var1")
    OPS[0xfe09 + code] = (name, "var2")


class ExecutionMetadata(MethodProof):
    def __init__(self, data, label="<DLL>"):
        super().__init__(data, label)
        refs = self.identity["referenceIdentities"]
        core = [r["fullName"] for r in refs if r["name"] in ("mscorlib", "System.Private.CoreLib")]
        if not core: core = [r["fullName"] for r in refs if r["name"] == "netstandard"]
        self.core = core[0] if len(core) == 1 else self.identity["fullName"] if self.identity["name"] == "mscorlib" else ""
        self.generic_names = {}
        self.context_type = self.context_method = None
        self.type_arguments = self.method_arguments = ()
        for rid in range(1, self.tables.counts[42] + 1):
            ordinal, _, owner, name = self.tables.row(42, rid)
            kind, target = self.tables.coded(owner, "TypeOrMethodDef")
            self.generic_names.setdefault((kind, target), []).append((ordinal, self.tables.string(name)))
        for key, names in self.generic_names.items():
            names.sort()
            require([n for n, _ in names] == list(range(len(names))), f"{label}: malformed generic parameter order")
            self.generic_names[key] = [n for _, n in names]

    def shape_identity(self, table, rid):
        if table == 27:
            sig = Signature(self.tables.blob(self.tables.row(27, rid)[0]), self.label)
            value = self.shape(sig)
            require(sig.position == len(sig.data), f"{self.label}: trailing TypeSpec")
            return value
        full, assembly = self.type_identity(table, rid)
        reflected = self.reflection_type_identity(table, rid)[0]
        return Shape(full, reflected, assembly)

    def shape(self, sig, depth=0):
        require(depth < 128, f"{self.label}: signature depth limit")
        code = sig.byte()
        primitives = {1:"Void",2:"Boolean",3:"Char",4:"SByte",5:"Byte",6:"Int16",7:"UInt16",8:"Int32",9:"UInt32",10:"Int64",11:"UInt64",12:"Single",13:"Double",14:"String",22:"TypedReference",24:"IntPtr",25:"UIntPtr",28:"Object"}
        if code in primitives:
            require(self.core, f"{self.label}: unproved core library signature owner")
            name = "System." + primitives[code]
            return Shape(name, name, self.core)
        if code in (17, 18): return self.shape_identity(*self.tables.coded(sig.compressed(), "TypeDefOrRef"))
        if code in (19, 30):
            index = sig.compressed()
            arguments = self.type_arguments if code == 19 else self.method_arguments
            if index < len(arguments): return arguments[index]
            names = self.generic_names.get((2, self.context_type) if code == 19 else (6, self.context_method), [])
            name = names[index] if index < len(names) else ("!" if code == 19 else "!!") + str(index)
            return Shape(name, name, "")
        if code in (15, 16, 29, 69):
            value = self.shape(sig, depth + 1)
            suffix = {15:"*",16:"&",29:"[]",69:" pinned"}[code]
            return Shape(value.full + suffix, value.reflection + suffix, value.assembly,element=value,suffix=suffix)
        if code in (31, 32):
            modifier = self.shape_identity(*self.tables.coded(sig.compressed(), "TypeDefOrRef"))
            value = self.shape(sig, depth + 1)
            return Shape(value.full + (" modreq(" if code == 31 else " modopt(") + modifier.full + ")", value.reflection, value.assembly)
        if code == 21:
            definition = self.shape(sig, depth + 1)
            count = sig.compressed(); require(count <= 256, f"{self.label}: generic argument bound")
            args = [self.shape(sig, depth + 1) for _ in range(count)]
            return Shape(definition.full + "<" + ",".join(a.full for a in args) + ">",
                         definition.reflection + "[" + ",".join("[" + a.qualified + "]" for a in args) + "]", definition.assembly, tuple(args))
        if code == 20:
            value = self.shape(sig, depth + 1)
            rank, sizes = sig.compressed(), sig.compressed()
            require(0 < rank <= 32 and sizes == 0 and sig.compressed() == 0, f"{self.label}: unsupported explicit array bounds")
            suffix = "[*]" if rank == 1 else "[" + "," * (rank - 1) + "]"
            return Shape(value.full + suffix, value.reflection + suffix, value.assembly,element=value,suffix=suffix)
        raise VerificationError(f"{self.label}: unsupported execution signature 0x{code:x}")

    def method_signature(self, blob):
        sig = Signature(self.tables.blob(blob), self.label)
        convention = sig.byte()
        require(convention & 15 in (0, 1, 2, 3, 4, 5), f"{self.label}: unsupported method convention")
        arity = sig.compressed() if convention & 16 else 0
        count = sig.compressed(); require(count < 65536, f"{self.label}: signature parameter bound")
        result = self.shape(sig); parameters = []; sentinel = []
        for _ in range(count):
            if sig.position < len(sig.data) and sig.data[sig.position] == 65: sig.byte(); parameters, sentinel = sentinel, parameters
            parameters.append(self.shape(sig))
        require(sig.position == len(sig.data), f"{self.label}: trailing method signature")
        require(not sentinel, f"{self.label}: vararg sentinel unsupported in execution proof")
        return convention, arity, result, parameters

    def member_shape(self, table, rid):
        args = []
        if table == 43:
            method, blob = self.tables.row(43, rid)
            target = self.tables.coded(method, "MethodDefOrRef")
            sig = Signature(self.tables.blob(blob), self.label)
            require(sig.byte() == 10, f"{self.label}: invalid generic instantiation signature")
            count = sig.compressed(); require(count <= 256, f"{self.label}: oversized MethodSpec")
            args = [self.shape(sig) for _ in range(count)]
            require(sig.position == len(sig.data), f"{self.label}: trailing MethodSpec")
            table, rid = target
        if table == 6:
            row = self.tables.row(6, rid); owner = self.shape_identity(2, self.method_owners[rid]); name, blob = row[3:5]; field = False
        elif table == 4:
            _, name, blob = self.tables.row(4, rid); owner = self.shape_identity(2, self.field_owners[rid]); field = True
        elif table == 10:
            parent, name, blob = self.tables.row(10, rid); owner = self.shape_identity(*self.tables.coded(parent, "MemberRefParent")); field = self.tables.blob(blob)[0] == 6
        else: raise VerificationError(f"{self.label}: unsupported member token {table}")
        name = self.tables.string(name)
        old_type_args, old_method_args = self.type_arguments, self.method_arguments
        self.type_arguments, self.method_arguments = owner.arguments, tuple(args)
        if field:
            sig = Signature(self.tables.blob(blob), self.label); require(sig.byte() == 6, f"{self.label}: field signature")
            result = self.shape(sig); require(sig.position == len(sig.data), f"{self.label}: trailing field signature")
            self.type_arguments, self.method_arguments = old_type_args, old_method_args
            # dnlib MemberRef implements IMethod even for a field signature;
            # the captured formatter tests IMethod before IField.
            return "method" if table == 10 else "field", result.full + " " + owner.full + "::" + name, owner, []
        _, arity, result, parameters = self.method_signature(blob)
        self.type_arguments, self.method_arguments = old_type_args, old_method_args
        generic = args or [Shape(n, n, "") for n in self.generic_names.get((table, rid), ["!!" + str(i) for i in range(arity)])]
        full = result.full + " " + owner.full + "::" + name + ("<" + ",".join(a.full for a in generic) + ">" if generic else "") + "(" + ",".join(a.full for a in parameters) + ")"
        return "method", full, owner, args

    def body(self, rid):
        rva = self.tables.row(6, rid)[0]
        if not rva: return [], [], [], [], False, 0
        r = Reader(self.data, self.label); p = self.rva(rva, 1); first = r.number(p, 1)
        if first & 3 == 2: flags, start, size, stack, locals_token = 18, p + 1, first >> 2, 8, 0
        else:
            flags = r.number(p, 2); require(flags & 3 == 3 and flags >> 12 == 3, f"{self.label}: invalid fat body")
            start, size, stack, locals_token = p + 12, r.number(p + 4, 4), r.number(p + 2, 2), r.number(p + 8, 4)
        require(size <= 1_000_000, f"{self.label}: method body size bound")
        self.rva(rva, start - p + size)
        locals_ = []
        if locals_token:
            require(locals_token >> 24 == 17, f"{self.label}: invalid local signature token")
            sig = Signature(self.tables.blob(self.tables.row(17, locals_token & 0xffffff)[0]), self.label)
            require(sig.byte() == 7, f"{self.label}: invalid local signature")
            count = sig.compressed(); require(count <= 65536, f"{self.label}: local count bound")
            locals_ = [self.shape(sig) for _ in range(count)]
            require(sig.position == len(sig.data), f"{self.label}: trailing locals signature")
        convention, _, _, parameters = self.method_signature(self.tables.row(6, rid)[4])
        if convention & 32:
            this = self.shape_identity(2, self.method_owners[rid]); parameters.insert(0, this)
        code = Signature(r.block(start, size), self.label); rows = []; offsets = []
        while code.position < size:
            offsets.append(code.position); op = code.byte(); op = 0xfe00 | code.byte() if op == 0xfe else op
            require(op in OPS, f"{self.label}: unsupported opcode {op:x}")
            name, operand = OPS[op]; value = ""
            if operand == "token":
                token = int.from_bytes(code.take(4), "little"); table, target = token >> 24, token & 0xffffff
                if name == "ldstr":
                    require(table == 0x70, f"{self.label}: invalid string token"); raw = self.tables.blob(target, "#US")
                    require(len(raw) % 2 == 1 and raw[-1] in (0, 1), f"{self.label}: invalid user string")
                    value = " utf8:" + base64.b64encode(raw[:-1].decode("utf-16-le", errors="strict").encode()).decode()
                elif table in (4, 6, 10, 43):
                    kind, full, owner, args = self.member_shape(table, target)
                    value = " " + kind + ":" + full + " @" + owner.qualified + (" args:" + "|".join(a.qualified for a in args) if table == 43 else "")
                elif table in (1, 2, 27): value = " type:" + self.shape_identity(table, target).qualified
                elif table == 17 and name == "calli":
                    conv, arity, result, params = self.method_signature(self.tables.row(17, target)[0])
                    value = " signature:" + str(conv) + ":" + str(arity) + ":" + result.qualified + "(" + "|".join(a.qualified for a in params) + ") after:"
                else: raise VerificationError(f"{self.label}: unsupported IL token {token:x}")
            elif operand.startswith("branch"):
                width = int(operand[-1]); distance = int.from_bytes(code.take(width), "little", signed=True); value = (code.position + distance,)
            elif operand == "switch":
                count = int.from_bytes(code.take(4), "little"); require(count <= 65536, f"{self.label}: switch bound")
                distances = [int.from_bytes(code.take(4), "little", signed=True) for _ in range(count)]; value = [code.position + d for d in distances]
            elif operand.startswith("var"):
                index = int.from_bytes(code.take(int(operand[-1])), "little")
                values, kind = (locals_, "local") if "loc" in name else (parameters, "parameter")
                require(index < len(values), f"{self.label}: {kind} operand out of range")
                value = " " + kind + ":" + str(index) + ":" + values[index].qualified
            elif operand.startswith("float"):
                width = int(operand[-1]); value = " r" + str(width) + ":" + format(int.from_bytes(code.take(width), "little"), "0" + str(width * 2) + "x")
            elif operand.startswith(("int", "uint")):
                width = int(operand[-1]); number = int.from_bytes(code.take(width), "little", signed=not operand.startswith("u"))
                value = " System." + ({1:"SByte",4:"Int32",8:"Int64"}[width] if not operand.startswith("u") else "Byte") + ":" + str(number)
            elif operand: raise VerificationError(f"{self.label}: unsupported operand {operand}")
            rows.append((name, value))
        positions = {offset: i for i, offset in enumerate(offsets)}
        def boundary(offset, end=False):
            if end and offset == size: return len(rows)
            require(offset in positions, f"{self.label}: IL/EH target outside instruction boundary")
            return positions[offset]
        instructions = []
        for index, (name, value) in enumerate(rows):
            if isinstance(value, tuple): value = " branch:" + str(boundary(value[0]))
            elif isinstance(value, list): value = " switch:" + ",".join(str(boundary(n)) for n in value)
            instructions.append(f"{index:04d}:" + name + value)
        handlers = []
        if flags & 8:
            section = (start + size + 3) & ~3; more = True
            while more:
                kind = r.number(section, 1); more = bool(kind & 128); fat = bool(kind & 64)
                require(kind & 63 == 1, f"{self.label}: unsupported method data section")
                length = r.number(section + 1, 3 if fat else 1); width = 24 if fat else 12
                require(length >= 4 and (length - 4) % width == 0, f"{self.label}: invalid EH section size")
                self.rva(rva + section - p, length)
                for offset in range(section + 4, section + length, width):
                    if fat: fields = [r.number(offset + i * 4, 4) for i in range(6)]
                    else: fields = [r.number(offset,2),r.number(offset+2,2),r.number(offset+4,1),r.number(offset+5,2),r.number(offset+7,1),r.number(offset+8,4)]
                    mode, ts, tl, hs, hl, extra = fields
                    require(mode in (0, 1, 2, 4), f"{self.label}: invalid EH kind")
                    catch = self.shape_identity(extra >> 24, extra & 0xffffff).qualified if mode == 0 else ""
                    handlers.append(dict(handlerType={0:"Catch",1:"Filter",2:"Finally",4:"Fault"}[mode],catchType=catch,
                                         tryStart=boundary(ts),tryEnd=boundary(ts+tl,True),handlerStart=boundary(hs),handlerEnd=boundary(hs+hl,True),filterStart=boundary(extra) if mode == 1 else -1))
                section = (section + length + 3) & ~3
        return instructions, handlers, locals_, offsets, bool(flags & 16), stack

    def methods(self, symbols=None):
        output = []
        for rid in range(1, self.tables.counts[6] + 1):
            self.context_type, self.context_method = self.method_owners[rid], rid
            row = self.tables.row(6, rid); convention, arity, result, parameters = self.method_signature(row[4])
            names = self.generic_names.get((6, rid), [])
            require(len(names) == arity, f"{self.label}: generic arity/metadata differs")
            instructions, handlers, locals_, offsets, init, stack = self.body(rid)
            output.append(dict(declaringType=self.shape_identity(2,self.method_owners[rid]).reflection,name=self.tables.string(row[3]),
                signature=self.member_shape(6,rid)[1],metadataToken=0x06000000|rid,genericArity=arity,methodFlags=row[2],implementationFlags=row[1],
                maxStack=stack,isStatic=bool(row[2]&16),hasBody=bool(row[0]),initLocals=init,returnType=result.evidence(),
                parameterTypes=[p.evidence() for p in parameters],genericParameterNames=names,locals=[v.qualified for v in locals_],instructions=instructions,
                exceptionHandlers=handlers,sequencePoints=symbols.points(rid,offsets) if symbols else []))
        return output


class PortableSymbols:
    """Portable PDB document and sequence-point reader, with PE CodeView binding."""
    def __init__(self, data, module, label="<PDB>"):
        self.label, self.data = str(label), data
        r = Reader(data, label)
        require(r.block(0,4) == b"BSJB", f"{label}: only portable PDB is supported")
        version_size = r.number(12,4); require(version_size < 4096, f"{label}: version bound")
        cursor = 16 + version_size; cursor = (cursor + 3) & ~3
        count = r.number(cursor+2,2); cursor += 4; require(count <= 32, f"{label}: stream count bound")
        self.streams = {}; spans = []
        for _ in range(count):
            offset, size = r.number(cursor,4), r.number(cursor+4,4); cursor += 8
            end = data.find(b"\0",cursor,cursor+32); require(end >= cursor, f"{label}: malformed stream name")
            name = data[cursor:end].decode("ascii"); cursor = (end+4)&~3
            require(name not in self.streams, f"{label}: duplicate stream")
            self.streams[name] = r.block(offset,size); spans.append((offset,offset+size))
        require(all(start >= cursor for start,_ in spans) and all(a[1] <= b[0] for a,b in zip(sorted(spans),sorted(spans)[1:])), f"{label}: overlapping PDB streams")
        require(all(name in self.streams for name in ("#Pdb","#~","#Blob","#GUID")), f"{label}: missing portable PDB streams")
        pdb = Reader(self.streams["#Pdb"],label); mask = pdb.number(24,8); external = {}; pos=32
        for table in range(64):
            if mask & (1<<table): external[table]=pdb.number(pos,4); pos+=4
        require(pos == len(pdb.data), f"{label}: trailing PDB external tables")
        require(external.get(6,0) == module.tables.counts[6], f"{label}: PDB method row inventory differs")
        self._bind(module, pdb.block(0,20))
        t=Reader(self.streams["#~"],label); heaps=t.number(6,1); valid=t.number(8,8); counts={}; pos=24
        require(not valid & ~sum(1<<n for n in range(48,56)), f"{label}: unsupported PDB tables")
        for table in range(64):
            if valid&(1<<table): counts[table]=t.number(pos,4); pos+=4
        require(counts.get(49,0)==module.tables.counts[6], f"{label}: missing MethodDebugInformation rows")
        schemas={48:("b","g","b","g"),49:(48,"b"),50:(6,53,51,52,"u4","u4"),51:("u2","u2","s"),52:("s","b"),53:(53,"b"),54:(6,6),55:("custom","g","b")}
        all_counts={**external,**counts}; self.rows={}
        for table in range(48,56):
            widths=[]
            for column in schemas[table]:
                if isinstance(column,int): width=4 if all_counts.get(column,0)>=65536 else 2
                elif column in ("u2","u4"): width=int(column[1:])
                elif column=="custom": width=4 if max(all_counts.values(),default=0)>=2048 else 2
                else: width=4 if heaps&{"s":1,"g":2,"b":4}[column] else 2
                widths.append(width)
            self.rows[table]=[]
            require(counts.get(table,0)<=10_000_000,f"{label}: PDB table bound")
            for _ in range(counts.get(table,0)):
                row=[]
                for width in widths: row.append(t.number(pos,width)); pos+=width
                self.rows[table].append(row)
        require(pos<=len(t.data) and not any(t.data[pos:]), f"{label}: trailing PDB table data")
        self.documents=[]
        for name, algorithm, checksum, language in self.rows[48]:
            blob=Signature(self.blob(name),label); separator=chr(blob.byte()); parts=[]
            while blob.position<len(blob.data): parts.append(self.blob(blob.compressed()).decode("utf-8",errors="strict"))
            self.documents.append(dict(document=separator.join(parts),checksumAlgorithm=self.guid(algorithm),checksum=self.blob(checksum).hex()))

    def blob(self,index):
        sig=Signature(self.streams["#Blob"],self.label,index); return sig.take(sig.compressed())

    def guid(self,index):
        if index==0:return str(uuid.UUID(int=0))
        return str(uuid.UUID(bytes_le=Reader(self.streams["#GUID"],self.label).block((index-1)*16,16)))

    def _bind(self,module,identifier):
        r=Reader(module.data,module.label); pe=r.number(0x3c,4); opt=pe+24; magic=r.number(opt,2); directory=96 if magic==0x10b else 112
        address,size=r.number(opt+directory+6*8,4),r.number(opt+directory+6*8+4,4)
        require(address and size%28==0,f"{self.label}: DLL lacks debug directory")
        start=module.rva(address,size); matches=[]
        for offset in range(start,start+size,28):
            if r.number(offset+12,4)!=2:continue
            length,pointer=r.number(offset+16,4),r.number(offset+24,4); body=r.block(pointer,length)
            if body[:4]==b"RSDS":matches.append((body,r.number(offset+4,4)))
        require(len(matches)==1 and len(matches[0][0])>=24 and matches[0][0][4:20]==identifier[:16] and
                matches[0][1]==int.from_bytes(identifier[16:],"little") and int.from_bytes(matches[0][0][20:24],"little")==1,
                f"{self.label}: portable PDB ID differs from actual DLL CodeView")

    @staticmethod
    def signed(sig):
        first=sig.byte()
        if first<128: value,bits=first,7
        elif first<192: value,bits=((first&63)<<8)|sig.byte(),14
        else:
            require(first<224,f"{sig.label}: invalid signed compressed integer")
            value,bits=((first&31)<<24)|int.from_bytes(sig.take(3),"big"),29
        return (value>>1)-(1<<(bits-1)) if value&1 else value>>1

    def points(self,rid,offsets):
        document,index=self.rows[49][rid-1]
        if index==0:return []
        sig=Signature(self.blob(index),self.label); sig.compressed() # local signature RID
        if document==0:document=sig.compressed()
        result=[]; offset=0; previous_line=previous_column=None; first=True
        positions={n:i for i,n in enumerate(offsets)}
        while sig.position<len(sig.data):
            delta=sig.compressed()
            if not first and delta==0: document=sig.compressed();continue
            offset=delta if first else offset+delta;first=False
            lines=sig.compressed(); columns=sig.compressed() if lines==0 else self.signed(sig)
            if lines==0 and columns==0: line=0xFEEFEE;column=0;endline=line;endcolumn=0
            else:
                if previous_line is None:line,column=sig.compressed(),sig.compressed()
                else:line,column=previous_line+self.signed(sig),previous_column+self.signed(sig)
                previous_line,previous_column=line,column;endline=line+lines;endcolumn=column+columns
                require(line>0 and column>=0 and endline>=line and endcolumn>=0,f"{self.label}: invalid sequence point")
            require(1<=document<=len(self.documents) and offset in positions,f"{self.label}: sequence point outside actual IL/document")
            result.append(dict(self.documents[document-1],instructionIndex=positions[offset],ilOffset=offset,startLine=line,startColumn=column,endLine=endline,endColumn=endcolumn))
        return result


class LinkedSchemaResolver:
    """Closed, exact-identity resolution of linked DTO signatures only.

    Compiler reference facades are never consulted. The caller first finds the
    actual linked counterpart field and proves semantic shape/flags unchanged.
    No leaf may be supplied by an unrelated same-named definition.
    """
    def __init__(self, paths):
        self.paths=dict(paths);self.modules={}
        names=[identity.partition(',')[0].casefold() for identity in self.paths]
        require(len(names)==len(set(names)),"schema: duplicate linked assembly scope")

    def module(self, identity):
        require(identity in self.paths,f"schema: missing exact linked assembly {identity}")
        if identity not in self.modules:
            path=Path(self.paths[identity]);module=ExecutionMetadata(path.read_bytes(),path)
            require(module.identity['fullName']==identity,f"{path}: linked identity differs")
            require(module.tables.counts[0]==1 and all(module.tables.row(38,rid)[0]&1 for rid in range(1,module.tables.counts[38]+1)),f"{path}: multi-module schema assembly")
            self.modules[identity]=module
        return self.modules[identity]

    def definition(self, identity, name, trail=(),arity=0):
        key=(identity,name);require(len(trail)<32 and key not in trail,f"schema: cyclic/deep exported type {name}")
        module=self.module(identity)
        definitions=[rid for rid,full in module.type_names.items() if full==name]
        def exported_name(rid,seen=()):
            require(rid not in seen and len(seen)<32,f"{module.label}: cyclic ExportedType owner")
            _,_,type_name,namespace,implementation=module.tables.row(39,rid)
            table,parent=module.tables.coded(implementation,'Implementation')
            leaf=module.tables.string(type_name)
            if table==39:return exported_name(parent,seen+(rid,))+'/'+leaf
            ns=module.tables.string(namespace);return ns+'.'+leaf if ns else leaf
        exports=[rid for rid in range(1,module.tables.counts[39]+1) if exported_name(rid)==name]
        require(len(definitions)+len(exports)==1,f"{module.label}: missing/duplicate exact type {name}")
        if definitions:
            rid=definitions[0];require(len(module.generic_names.get((2,rid),[]))==arity,f"{module.label}: unconstructed or wrong-arity schema definition")
            if arity:
                base=module.tables.row(2,rid)[3]
                require(base and module.type_identity(*module.tables.coded(base,'TypeDefOrRef'))[0] not in ('System.ValueType','System.Enum'),f"{module.label}: linked List is a value type")
            reflected=module.reflection_type_identity(2,rid)[0]
            return Shape(name,reflected,identity)
        def target(rid,seen=()):
            require(rid not in seen and len(seen)<32,f"{module.label}: cyclic ExportedType forwarding")
            flags,_,_,_,implementation=module.tables.row(39,rid);table,index=module.tables.coded(implementation,'Implementation')
            if table==39:return target(index,seen+(rid,))
            require(table==35 and flags&0x200000,f"{module.label}: unsupported non-forwarded exported type")
            refs=module.identity['referenceIdentities'];require(1<=index<=len(refs),f"{module.label}: invalid forwarder assembly")
            return refs[index-1]['fullName']
        return self.definition(target(exports[0]),name,trail+(key,),arity)

    def resolve(self, shape, depth=0):
        require(depth<64,f"schema: deep signature")
        if shape.element is not None:
            require(shape.suffix=='[]',f"schema: unsupported DTO element shape {shape.full}")
            inner=self.resolve(shape.element,depth+1)
            return Shape(inner.full+'[]',inner.reflection+'[]',inner.assembly,element=inner,suffix='[]')
        if shape.arguments:
            definition_name=shape.full.partition('<')[0]
            require(definition_name=='System.Collections.Generic.List`1' and len(shape.arguments)==1,f"schema: unsupported DTO generic {shape.full}")
            definition=self.definition(shape.assembly,definition_name,arity=1)
            argument=self.resolve(shape.arguments[0],depth+1)
            return Shape(definition.full+'<'+argument.full+'>',definition.reflection+'[['+argument.qualified+']]',definition.assembly,(argument,))
        require(shape.assembly and not any(marker in shape.full for marker in (' modreq(', ' modopt(', ' pinned','!')),f"schema: unsupported/open DTO leaf {shape.full}")
        return self.definition(shape.assembly,shape.full)

    def verify_unchanged(self):
        for identity,module in self.modules.items():
            require(hashlib.sha256(Path(self.paths[identity]).read_bytes()).digest()==hashlib.sha256(module.data).digest(),f"schema: linked bytes changed during resolution")


def schema_fields(module,type_name,resolver):
    """Retain declared AQN and bind resolved AQN to the linked field bytes."""
    linked=resolver.module(module.identity['fullName'])
    def fields_of(owner):
        matches=[rid for rid,name in owner.type_names.items() if name==type_name]
        require(len(matches)==1,f"{owner.label}: missing/duplicate schema owner {type_name}")
        result={}
        for rid,parent in owner.field_owners.items():
            if parent!=matches[0]:continue
            flags,name,blob=owner.tables.row(4,rid)
            if flags&7!=6 or flags&0x10 or flags&0x80:continue
            key=owner.tables.string(name);require(key not in result,f"{owner.label}: duplicate schema field {key}")
            sig=Signature(owner.tables.blob(blob),owner.label);require(sig.byte()==6,f"{owner.label}: invalid field signature")
            shape=owner.shape(sig);require(sig.position==len(sig.data),f"{owner.label}: trailing field signature")
            result[key]=(flags,shape)
        return result
    source_fields=fields_of(module);linked_fields=fields_of(linked)
    require(set(source_fields)==set(linked_fields),f"{module.label}: schema fields changed across linking")
    result=[]
    for name,(flags,shape) in sorted(source_fields.items()):
        linked_flags,linked_shape=linked_fields[name]
        require(flags==linked_flags and shape.full==linked_shape.full,f"{module.label}: linked schema shape/flags differ for {type_name}.{name}")
        result.append(dict(name=name,type=shape.qualified,resolvedType=resolver.resolve(linked_shape).qualified,attributes=flags))
    return result


def read_methods(path, pdb_path=None):
    path = Path(path); module = ExecutionMetadata(path.read_bytes(), path)
    symbols=PortableSymbols(Path(pdb_path).read_bytes(),module,pdb_path) if pdb_path else None
    return module.methods(symbols)
