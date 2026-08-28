"""Independent bounded ECMA-335 type proof for M05; never executes a DLL.

Uses the accepted PE/root reader, not its assembly claims, to traverse actual
TypeDef, TypeRef, NestedClass and GenericParam rows. Row order is retained only
as enumeration evidence; it is not a logical type identity.
"""
from __future__ import annotations

import hashlib
import base64
from pathlib import Path

from m04_metadata import Reader, TABLES, CODED, _metadata, read_identity_bytes
from shadow_tools import VerificationError, require


TYPE_FIELDS = "fullName namespaceName name nestingPath genericArity kind isExported"
INVENTORY_FIELDS = "assemblyName types"


def reflection_escape(value):
    return "".join("\\" + c if c in "\\,+[]*&" else c for c in value)


class CliTables:
    def __init__(self, data, label="<DLL bytes>"):
        self.label = str(label)
        require(type(data) in (bytes, bytearray) and len(data) <= 512 * 1024 * 1024, f"{label}: invalid/oversized DLL bytes")
        self.data = bytes(data)
        self.streams = _metadata(self.data, label)
        self.reader = Reader(self.streams.get("#~", self.streams.get("#-")), label)
        t = self.reader
        heaps, valid = t.number(6, 1), t.number(8, 8)
        require(not valid >> len(TABLES), f"{label}: unsupported CLI tables")
        self.counts, cursor = [0] * len(TABLES), 24
        for index in range(len(TABLES)):
            if valid & (1 << index):
                self.counts[index] = t.number(cursor, 4); cursor += 4
                require(self.counts[index] <= 10_000_000, f"{label}: oversized CLI table")
        require(self.counts[0] == self.counts[32] == 1, f"{label}: requires one Module and Assembly")
        require(0 < self.counts[2] <= 1_000_000, f"{label}: invalid TypeDef count")
        require(not any(self.counts[n] for n in (3, 5, 7, 19, 22)), f"{label}: unsupported pointer tables")

        def width(column):
            if isinstance(column, int): return 4 if self.counts[column] >= 65536 else 2
            if column in ("u2", "u4"): return int(column[1:])
            if column in ("s", "b", "g"): return 4 if heaps & {"s": 1, "g": 2, "b": 4}[column] else 2
            bits, targets = CODED[column]
            return 4 if max(self.counts[target] for target in targets) >= 1 << (16 - bits) else 2

        self.offsets, self.widths = [], []
        for index, schema in enumerate(TABLES):
            sizes = [width(column) for column in schema]
            self.offsets.append(cursor); self.widths.append(sizes)
            size = self.counts[index] * sum(sizes)
            t.block(cursor, size); cursor += size

    def row(self, table, rid):
        require(type(rid) is int and 1 <= rid <= self.counts[table], f"{self.label}: table {table} RID out of bounds")
        p = self.offsets[table] + (rid - 1) * sum(self.widths[table])
        values = []
        for size in self.widths[table]:
            values.append(self.reader.number(p, size)); p += size
        return values

    def string(self, index):
        heap = self.streams["#Strings"]
        require(0 <= index < len(heap), f"{self.label}: string index out of bounds")
        end = heap.find(b"\0", index, min(len(heap), index + 65536))
        require(end >= 0, f"{self.label}: unterminated/oversized CLI string")
        try: return heap[index:end].decode("utf-8", errors="strict")
        except UnicodeDecodeError as error: raise VerificationError(f"{self.label}: invalid UTF-8 CLI string") from error

    def coded(self, value, kind, nullable=False):
        if value == 0 and nullable: return None
        bits, targets = CODED[kind]
        tag, rid = value & ((1 << bits) - 1), value >> bits
        require(tag < len(targets) and 0 < rid <= self.counts[targets[tag]], f"{self.label}: invalid {kind} coded index")
        return targets[tag], rid

    def blob(self, index, heap_name="#Blob"):
        heap = self.streams.get(heap_name, b"")
        reader = Signature(heap, self.label, index)
        size = reader.compressed()
        return reader.take(size)

    def type_inventory(self):
        identity = read_identity_bytes(self.data, self.label)
        owner = identity["name"]
        refs = identity["referenceIdentities"]
        definitions = {rid: self.row(2, rid) for rid in range(1, self.counts[2] + 1)}
        names = {rid: self.string(row[1]) for rid, row in definitions.items()}
        namespaces = {rid: self.string(row[2]) for rid, row in definitions.items()}
        require(names[1] == "<Module>" and namespaces[1] == "" and definitions[1][3] == 0,
                f"{self.label}: missing global Module TypeDef")
        require(all(name and "\r" not in name and "\n" not in name for name in names.values()), f"{self.label}: invalid TypeDef name")
        require(all("\r" not in ns and "\n" not in ns for ns in namespaces.values()), f"{self.label}: invalid TypeDef namespace")
        for column, table in ((4, 4), (5, 6)):
            starts = [row[column] for row in definitions.values()] + [self.counts[table] + 1]
            require(starts[0] == 1 and starts == sorted(starts) and all(1 <= n <= self.counts[table] + 1 for n in starts),
                    f"{self.label}: TypeDef field/method range is invalid")
        parents = {}
        for rid in range(1, self.counts[41] + 1):
            child, parent = self.row(41, rid)
            require(child in definitions and parent in definitions and child != parent and child != 1 and parent != 1 and child not in parents,
                    f"{self.label}: invalid/duplicate NestedClass ownership")
            parents[child] = parent
        chains = {}
        for rid, row in definitions.items():
            require((rid in parents) == ((row[0] & 7) >= 2), f"{self.label}: NestedClass visibility/ownership differs")
            chain, seen, cursor = [], set(), rid
            while cursor in parents:
                require(cursor not in seen and len(chain) < 256, f"{self.label}: cyclic/oversized nesting chain")
                seen.add(cursor); cursor = parents[cursor]; chain.insert(0, cursor)
            chains[rid] = chain

        parameters = {}
        for rid in range(1, self.counts[42] + 1):
            number, flags, coded_owner, name = self.row(42, rid)
            kind, target = self.coded(coded_owner, "TypeOrMethodDef")
            self.string(name)
            numbers = parameters.setdefault((kind, target), set())
            require(number not in numbers, f"{self.label}: duplicate GenericParam number")
            numbers.add(number)
        for numbers in parameters.values():
            require(numbers == set(range(len(numbers))), f"{self.label}: non-contiguous GenericParam numbers")
        for rid in range(1, self.counts[44] + 1):
            param, constraint = self.row(44, rid)
            self.row(42, param); self.coded(constraint, "TypeDefOrRef")

        def reference_scope(rid, seen=()):
            require(rid not in seen and len(seen) < 256, f"{self.label}: cyclic/oversized TypeRef scope")
            scope, name, namespace = self.row(1, rid)
            # Validate names even when this reference cannot affect type kind.
            self.string(name); self.string(namespace)
            if scope == 0: return owner
            table, target = self.coded(scope, "ResolutionScope")
            if table == 35: return refs[target - 1]["name"]
            if table == 1: return reference_scope(target, (*seen, rid))
            if table == 26: self.string(self.row(26, target)[0])
            return owner

        ref_owners = {rid: reference_scope(rid) for rid in range(1, self.counts[1] + 1)}
        # The pinned Unity corlib is mscorlib. The other standard names retain
        # dnlib's usual corlib semantics for standalone ECMA test fixtures.
        corlibs = {"mscorlib", "System.Private.CoreLib", "System.Runtime", "netstandard"}
        def kind_of(rid):
            flags, _, _, extends, _, _ = definitions[rid]
            target = self.coded(extends, "TypeDefOrRef", nullable=True)
            if flags & 0x20: return "interface"
            if target and target[0] in (1, 2):
                table, index = target
                if table == 1:
                    _, ni, nsi = self.row(1, index)
                    base_name, base_namespace, base_owner = self.string(ni), self.string(nsi), ref_owners[index]
                else:
                    base_name, base_namespace, base_owner = names[index], namespaces[index], owner
                if base_owner in corlibs and base_namespace == "System":
                    if base_name == "Enum": return "enum"
                    if base_name == "ValueType" and not (owner in corlibs and namespaces[rid] == "System" and names[rid] == "Enum"):
                        return "valuetype"
            return "class"

        types, seen = [], set()
        for rid, row in definitions.items():
            kind = kind_of(rid)
            if rid == 1: continue
            chain = chains[rid]
            # dnlib ReflectionFullName retains each TypeDef's own namespace,
            # including nonempty namespaces on generated nested definitions.
            full_name = "+".join((reflection_escape(namespaces[n]) + "." if namespaces[n] else "") +
                                 reflection_escape(names[n]) for n in (*chain, rid))
            require(full_name not in seen, f"{self.label}: duplicate logical type definition")
            seen.add(full_name)
            exported = all((definitions[n][0] & 7) == (2 if n in parents else 1) for n in (*chain, rid))
            types.append(dict(fullName=full_name, namespaceName=namespaces[rid], name=names[rid],
                              nestingPath=[names[n] for n in chain], genericArity=len(parameters.get((2, rid), ())),
                              kind=kind, isExported=exported))
        return dict(assemblyName=owner, types=types)


def read_type_inventory_bytes(data, label="<DLL bytes>"):
    return CliTables(data, label).type_inventory()


def read_type_inventory(path, expected_sha256=None, expected_assembly=None):
    path = Path(path)
    require(path.is_absolute() and path.is_file(), f"{path}: missing absolute type-inventory DLL")
    require(str(path) == str(path.resolve()) and not any(p.is_symlink() for p in (path, *path.parents)), f"{path}: aliased/symlinked type-inventory DLL")
    require(path.stat().st_size <= 512 * 1024 * 1024, f"{path}: oversized type-inventory DLL")
    data = path.read_bytes()
    require(expected_sha256 is None or hashlib.sha256(data).hexdigest() == expected_sha256, f"{path}: type-inventory DLL hash differs")
    result = read_type_inventory_bytes(data, path)
    require(expected_assembly is None or result["assemblyName"] == expected_assembly, f"{path}: type-inventory assembly identity differs")
    return result


class Signature:
    def __init__(self, data, label, position=0):
        self.data, self.label, self.position = data, label, position

    def take(self, count):
        require(count >= 0 and 0 <= self.position <= len(self.data) - count, f"{self.label}: truncated CLI signature/operand")
        value = self.data[self.position:self.position + count]; self.position += count
        return value

    def byte(self): return self.take(1)[0]

    def compressed(self):
        first = self.byte()
        if first < 0x80: return first
        if first < 0xc0:
            value = ((first & 63) << 8) | self.byte()
            require(value >= 0x80, f"{self.label}: noncanonical compressed integer")
            return value
        require(first < 0xe0, f"{self.label}: invalid compressed integer")
        value = ((first & 31) << 24) | int.from_bytes(self.take(3), "big")
        require(value >= 0x4000, f"{self.label}: noncanonical compressed integer")
        return value


METHOD_SELECTION = (
    ("System.Reflection.RuntimeModule", "GetType", ("System.String", "System.Boolean", "System.Boolean")),
    ("System.Reflection.RuntimeModule", "GetTypes", ()),
    ("System.Reflection.RuntimeModule", "get_Assembly", ()),
    ("System.Reflection.RuntimeAssembly", "GetManifestModuleInternal", ()),
    ("System.Reflection.Assembly", "InternalGetType", ("System.Reflection.Module", "System.String", "System.Boolean", "System.Boolean")),
    ("System.Reflection.RuntimeModule", "InternalGetTypes", ("System.IntPtr",)),
)


class MethodProof:
    """Small independent decoder for the pinned module-wrapper evidence.

    Unknown operand/signature forms fail closed. This is not a general IL
    verifier; control-flow labels are checked against instruction boundaries.
    """
    def __init__(self, data, label):
        self.tables, self.label, self.data = CliTables(data, label), label, data
        self.reflection_scope = None
        self.inventory = self.tables.type_inventory()
        self.reflection_names = {1: "<Module>", **{rid: row["fullName"] for rid, row in enumerate(self.inventory["types"], 2)}}
        self.identity = read_identity_bytes(data, label)
        self.method_owners, self.field_owners = {}, {}
        parents = dict(self.tables.row(41, rid) for rid in range(1, self.tables.counts[41] + 1))
        self.type_names = {}
        def type_name(rid):
            if rid not in self.type_names:
                row = self.tables.row(2, rid)
                name, namespace = self.tables.string(row[1]), self.tables.string(row[2])
                self.type_names[rid] = type_name(parents[rid]) + "/" + name if rid in parents else (namespace + "." if namespace else "") + name
            return self.type_names[rid]
        for rid in range(1, self.tables.counts[2] + 1): type_name(rid)
        for rid in range(1, self.tables.counts[2] + 1):
            row = self.tables.row(2, rid)
            following = self.tables.row(2, rid + 1) if rid < self.tables.counts[2] else [0, 0, 0, 0, self.tables.counts[4] + 1, self.tables.counts[6] + 1]
            for index in range(row[4], following[4]): self.field_owners[index] = rid
            for index in range(row[5], following[5]): self.method_owners[index] = rid

    def type_identity(self, table, rid, seen=()):
        require((table, rid) not in seen and len(seen) < 256, f"{self.label}: cyclic type signature")
        t = self.tables
        if table == 2:
            t.row(table, rid)
            return self.type_names[rid], self.identity["fullName"]
        if table == 1:
            scope, name, namespace = t.row(table, rid)
            name, namespace = t.string(name), t.string(namespace)
            assembly = self.identity["fullName"]
            if scope:
                owner, target = t.coded(scope, "ResolutionScope")
                if owner == 35: assembly = self.identity["referenceIdentities"][target - 1]["fullName"]
                elif owner == 1:
                    parent, assembly = self.type_identity(1, target, (*seen, (table, rid)))
                    return parent + "/" + name, assembly
            return (namespace + "." if namespace else "") + name, assembly
        if table == 27:
            sig = Signature(t.blob(t.row(27, rid)[0]), self.label)
            name = self.sig_type(sig)
            require(sig.position == len(sig.data), f"{self.label}: trailing TypeSpec signature")
            return name, ""
        raise VerificationError(f"{self.label}: unsupported type signature owner")

    def sig_type(self, sig, depth=0):
        require(depth < 128, f"{self.label}: oversized signature recursion")
        code = sig.byte()
        primitives = {1:"Void",2:"Boolean",3:"Char",4:"SByte",5:"Byte",6:"Int16",7:"UInt16",8:"Int32",9:"UInt32",10:"Int64",11:"UInt64",12:"Single",13:"Double",14:"String",22:"TypedReference",24:"IntPtr",25:"UIntPtr",28:"Object"}
        if code in primitives: return "System." + primitives[code]
        if code in (15, 16, 29): return self.sig_type(sig, depth + 1) + {15:"*",16:"&",29:"[]"}[code]
        if code in (17, 18): return self.type_identity(*self.tables.coded(sig.compressed(), "TypeDefOrRef"))[0]
        if code in (19, 30): return ("!" if code == 19 else "!!") + str(sig.compressed())
        if code == 21:
            definition = self.sig_type(sig, depth + 1)
            count = sig.compressed(); require(count <= 256, f"{self.label}: oversized generic signature")
            return definition + "<" + ",".join(self.sig_type(sig, depth + 1) for _ in range(count)) + ">"
        raise VerificationError(f"{self.label}: unsupported method-witness signature element 0x{code:02x}")

    def signature(self, blob_index, property_signature=False):
        sig = Signature(self.tables.blob(blob_index), self.label)
        convention = sig.byte()
        require(convention & 15 in ((8,) if property_signature else (0, 5)), f"{self.label}: unsupported method calling convention")
        generic_arity = sig.compressed() if convention & 16 else 0
        count = sig.compressed(); require(count <= 1024, f"{self.label}: oversized method signature")
        result = self.sig_type(sig)
        params = [self.sig_type(sig) for _ in range(count)]
        require(sig.position == len(sig.data), f"{self.label}: trailing method signature")
        return result, params, generic_arity, bool(convention & 32)

    def member(self, table, rid):
        t = self.tables
        if table == 6:
            row = t.row(6, rid); owner = (2, self.method_owners[rid]); name, blob_index = row[3:5]
            is_field = False
        elif table == 4:
            _, name, blob_index = t.row(4, rid); owner = (2, self.field_owners[rid]); is_field = True
        elif table == 10:
            parent, name, blob_index = t.row(10, rid); owner = t.coded(parent, "MemberRefParent")
            is_field = bool(t.blob(blob_index) and t.blob(blob_index)[0] == 6)
        else: raise VerificationError(f"{self.label}: unsupported member operand table {table}")
        type_name, assembly_name = self.type_identity(*owner)
        name = t.string(name)
        if is_field:
            sig = Signature(t.blob(blob_index), self.label)
            require(sig.byte() == 6, f"{self.label}: invalid field signature")
            field_type = self.sig_type(sig)
            require(sig.position == len(sig.data), f"{self.label}: trailing field signature")
            full_name = field_type + " " + type_name + "::" + name
            return dict(kind="field", fullName=full_name, assembly=assembly_name, owner=type_name, name=name)
        result, params, arity, instance = self.signature(blob_index)
        require(arity == 0, f"{self.label}: unsupported generic method witness")
        full_name = result + " " + type_name + "::" + name + "(" + ",".join(params) + ")"
        return dict(kind="method", fullName=full_name, assembly=assembly_name, owner=type_name, name=name,
                    returnType=result, parameters=params, instance=instance)

    def rva(self, value, size):
        r = Reader(self.data, self.label)
        pe = r.number(0x3c, 4)
        count, opt_size = r.number(pe + 6, 2), r.number(pe + 20, 2)
        matches = []
        for i in range(count):
            p = pe + 24 + opt_size + i * 40
            start, length, pointer = r.number(p + 12, 4), r.number(p + 16, 4), r.number(p + 20, 4)
            if start <= value and value + size <= start + length: matches.append(pointer + value - start)
        require(len(matches) == 1, f"{self.label}: unmapped/ambiguous method RVA")
        r.block(matches[0], size)
        return matches[0]

    def instructions(self, rid):
        rva = self.tables.row(6, rid)[0]
        p = self.rva(rva, 1)
        r = Reader(self.data, self.label)
        first = r.number(p, 1)
        if first & 3 == 2: start, size = p + 1, first >> 2
        else:
            flags = r.number(p, 2)
            require(flags & 3 == 3 and 3 <= flags >> 12 <= 15, f"{self.label}: invalid method body header")
            start, size = p + (flags >> 12) * 4, r.number(p + 4, 4)
        require(size <= 1_000_000, f"{self.label}: oversized method-witness body")
        self.rva(rva, start - p + size)
        code = Signature(r.block(start, size), self.label)
        rows, positions = [], {}
        while code.position < len(code.data):
            positions[code.position] = len(rows)
            opcode = code.byte()
            if opcode == 0xfe: opcode = 0xfe00 | code.byte()
            require(opcode in IL_OPS, f"{self.label}: unsupported method-witness IL opcode 0x{opcode:x}")
            name, operand = IL_OPS[opcode]
            value = ""
            if operand == "token":
                token = int.from_bytes(code.take(4), "little")
                table, target = token >> 24, token & 0xffffff
                if name == "ldstr":
                    require(table == 0x70, f"{self.label}: invalid user-string token")
                    raw = self.tables.blob(target, "#US")
                    require(len(raw) % 2 == 1 and raw[-1] in (0, 1), f"{self.label}: invalid user-string heap entry")
                    try: text = raw[:-1].decode("utf-16-le", errors="strict")
                    except UnicodeDecodeError as error: raise VerificationError(f"{self.label}: invalid UTF-16 user string") from error
                    value = " utf8:" + base64.b64encode(text.encode("utf-8")).decode("ascii")
                elif table in (4, 6, 10):
                    member = self.member(table, target)
                    value = " " + member["kind"] + ":" + member["fullName"] + " | " + member["assembly"]
                elif table in (1, 2, 27):
                    type_name, assembly = self.type_identity(table, target)
                    require(assembly, f"{self.label}: unsupported TypeSpec assembly-qualified operand")
                    value = " type:" + type_name.replace("/", "+") + ", " + assembly
                else: raise VerificationError(f"{self.label}: unsupported IL metadata operand table {table}")
            elif operand in ("branch1", "branch4"):
                width = 1 if operand == "branch1" else 4
                distance = int.from_bytes(code.take(width), "little", signed=True)
                value = (code.position + distance,)
            elif operand == "switch":
                count = int.from_bytes(code.take(4), "little")
                require(count <= 65536, f"{self.label}: oversized IL switch")
                distances = [int.from_bytes(code.take(4), "little", signed=True) for _ in range(count)]
                value = [code.position + distance for distance in distances]
            elif operand in ("int1", "int4", "int8"):
                value = " " + str(int.from_bytes(code.take(int(operand[-1])), "little", signed=True))
            elif operand:
                raise VerificationError(f"{self.label}: unsupported operand form {operand}")
            rows.append((name, value))
        result = []
        for index, (name, value) in enumerate(rows):
            if type(value) in (tuple, list):
                require(all(target in positions for target in value), f"{self.label}: branch target outside instruction boundaries")
                targets = [positions[target] for target in value]
                value = " ->" + (str(targets[0]) if type(value) is tuple else "[" + ",".join(map(str, targets)) + "]")
            result.append(f"{index:04d}:" + name + value)
        return result

    def witnesses(self):
        result = []
        returns = ("System.Type", "System.Type[]", "System.Reflection.Assembly", "System.Reflection.Module", "System.Type", "System.Type[]")
        for ordinal, (owner, name, parameters) in enumerate(METHOD_SELECTION):
            matches = []
            for rid, type_rid in self.method_owners.items():
                row = self.tables.row(6, rid)
                if self.type_names[type_rid] == owner and self.tables.string(row[3]) == name:
                    method = self.member(6, rid)
                    if tuple(method["parameters"]) == parameters: matches.append((rid, row, method))
            require(len(matches) == 1, f"{self.label}: missing/ambiguous linked module method {owner}::{name}{parameters}")
            rid, row, method = matches[0]
            has_body = row[0] != 0
            require(not has_body or row[1] & 3 == 0, f"{self.label}: non-IL method body")
            require(method["returnType"] == returns[ordinal], f"{self.label}: linked Module return type changed")
            require((has_body and not row[1] & 0x1000 and bool(row[2] & 0x40)) if ordinal < 3 else
                    (not has_body and bool(row[1] & 0x1000)), f"{self.label}: Module wrapper/native flags changed")
            if ordinal >= 3:
                require(bool(row[2] & 0x10) == (ordinal == 5), f"{self.label}: Module entrypoint static/instance flags changed")
            result.append(dict(declaringType=owner, name=name, signature=method["fullName"], hasBody=has_body,
                               implementationFlags=row[1], instructions=self.instructions(rid) if has_body else []))
        for wrapper, native in ((0, 4), (1, 5)):
            suffix = " method:" + result[native]["signature"] + " | " + self.identity["fullName"]
            require(any(line.partition(":")[2] in ("call" + suffix, "callvirt" + suffix) for line in result[wrapper]["instructions"]),
                    f"{self.label}: actual Module wrapper no longer calls its native entrypoint")
        field = "ldfld field:System.Reflection.Assembly System.Reflection.RuntimeModule::assembly | " + self.identity["fullName"]
        require(any(line.partition(":")[2] == field for line in result[2]["instructions"]), f"{self.label}: Module.Assembly wrapper no longer reads assembly field")
        return result

    def fields(self, full_name):
        matches = [rid for rid, name in self.type_names.items() if name == full_name]
        require(len(matches) == 1, f"{self.label}: missing/ambiguous type fields: {full_name}")
        result = []
        for rid, owner in self.field_owners.items():
            if owner == matches[0]:
                flags, name, blob = self.tables.row(4, rid)
                sig = Signature(self.tables.blob(blob), self.label)
                require(sig.byte() == 6, f"{self.label}: invalid field signature")
                field_type = self.sig_type(sig)
                require(sig.position == len(sig.data), f"{self.label}: trailing field signature")
                result.append(dict(name=self.tables.string(name), type=field_type, flags=flags))
        return result

    def reflection_members(self, full_name):
        """Canonical declared signatures, not metadata-token logical keys."""
        matches = [rid for rid, name in self.reflection_names.items() if name == full_name]
        require(len(matches) == 1, f"{self.label}: missing/ambiguous member owner: {full_name}")
        owner = matches[0]; result = []
        def add(name, kind, result_type="", field_type="", parameters=()):
            result.append(dict(declaringType=full_name, memberName=name, memberKind=kind, returnType=result_type,
                               fieldType=field_type, parameterTypes=list(parameters)))
        for rid, type_rid in self.method_owners.items():
            if type_rid == owner:
                row = self.tables.row(6, rid)
                result_type, parameters = self.reflection_signature(row[4])
                add(self.tables.string(row[3]), "method", result_type, parameters=parameters)
        for rid, type_rid in self.field_owners.items():
            if type_rid == owner:
                _, name, blob = self.tables.row(4, rid)
                signature = Signature(self.tables.blob(blob), self.label)
                require(signature.byte() == 6, f"{self.label}: invalid reflected field signature")
                field_type, _ = self.reflection_type(signature)
                require(signature.position == len(signature.data), f"{self.label}: trailing reflected field signature")
                add(self.tables.string(name), "field", field_type=field_type)
        for map_table, table, kind in ((21, 23, "property"), (18, 20, "event")):
            for rid in range(1, self.tables.counts[map_table] + 1):
                parent, start = self.tables.row(map_table, rid)
                stop = self.tables.row(map_table, rid + 1)[1] if rid < self.tables.counts[map_table] else self.tables.counts[table] + 1
                require(1 <= start <= stop <= self.tables.counts[table] + 1 and 1 <= parent <= self.tables.counts[2], f"{self.label}: invalid member map range")
                if parent != owner: continue
                for member_rid in range(start, stop):
                    _, name, signature = self.tables.row(table, member_rid)
                    name = self.tables.string(name)
                    if kind == "property":
                        property_type, parameters = self.reflection_signature(signature, property_signature=True)
                        add(name, kind, property_type, parameters=parameters)
                    else:
                        event_type = self.reflection_type_identity(*self.tables.coded(signature, "TypeDefOrRef"))[0]
                        add(name, kind, field_type=event_type)
        return result

    def reflection_type_identity(self, table, rid):
        if table == 27:
            sig = Signature(self.tables.blob(self.tables.row(27, rid)[0]), self.label)
            result = self.reflection_type(sig)
            require(sig.position == len(sig.data), f"{self.label}: trailing reflected TypeSpec")
            return result
        _, owner = self.type_identity(table, rid)
        if table == 2: return self.reflection_names[rid], owner
        require(table == 1, f"{self.label}: unsupported reflected type identity")
        scope, name, namespace = self.tables.row(1, rid)
        name, namespace = reflection_escape(self.tables.string(name)), reflection_escape(self.tables.string(namespace))
        if scope:
            kind, target = self.tables.coded(scope, "ResolutionScope")
            if kind == 1:
                name=self.reflection_type_identity(1,target)[0]+"+"+name
                return name,self.reflection_scope(name,owner) if self.reflection_scope else owner
        name=(namespace+"." if namespace else "")+name
        return name,self.reflection_scope(name,owner) if self.reflection_scope else owner

    def reflection_type(self, sig, depth=0):
        """CLR FullName spelling including byte-bound generic argument owners."""
        require(depth < 128, f"{self.label}: oversized reflected signature")
        code = sig.byte()
        primitives = {1:"Void",2:"Boolean",3:"Char",4:"SByte",5:"Byte",6:"Int16",7:"UInt16",8:"Int32",9:"UInt32",10:"Int64",11:"UInt64",12:"Single",13:"Double",14:"String",22:"TypedReference",24:"IntPtr",25:"UIntPtr",28:"Object"}
        if code in primitives:
            corlib = self.identity if self.identity["name"] in ("mscorlib","netstandard") else next((row for row in self.identity["referenceIdentities"] if row["name"] in ("mscorlib","netstandard")), None)
            require(corlib is not None, f"{self.label}: reflected primitive lacks byte-bound corlib identity")
            name="System."+primitives[code];owner=corlib["fullName"]
            return name,self.reflection_scope(name,owner) if self.reflection_scope else owner
        if code in (17, 18): return self.reflection_type_identity(*self.tables.coded(sig.compressed(), "TypeDefOrRef"))
        if code in (15, 16, 29):
            name, owner = self.reflection_type(sig, depth + 1)
            return name + {15:"*",16:"&",29:"[]"}[code], owner
        if code == 21:
            name, owner = self.reflection_type(sig, depth + 1)
            count = sig.compressed(); require(0 < count <= 256, f"{self.label}: invalid reflected generic arity")
            arguments = [self.reflection_type(sig, depth + 1) for _ in range(count)]
            return name + "[[" + "],[".join(n + ", " + assembly for n, assembly in arguments) + "]]", owner
        if code == 20:
            name, owner = self.reflection_type(sig, depth + 1)
            rank, sizes = sig.compressed(), sig.compressed()
            require(0 < rank <= 32 and sizes == 0 and sig.compressed() == 0, f"{self.label}: unsupported reflected array bounds")
            return name + ("[*]" if rank == 1 else "[" + "," * (rank - 1) + "]"), owner
        raise VerificationError(f"{self.label}: unsupported reflected signature element 0x{code:02x}")

    def reflection_signature(self, blob, property_signature=False):
        sig = Signature(self.tables.blob(blob), self.label)
        convention = sig.byte()
        require(convention & 15 == (8 if property_signature else 0) and not convention & 16,
                f"{self.label}: unsupported reflected method/property convention")
        count = sig.compressed(); require(count <= 1024, f"{self.label}: oversized reflected parameter list")
        result, _ = self.reflection_type(sig)
        parameters = [self.reflection_type(sig)[0] for _ in range(count)]
        require(sig.position == len(sig.data), f"{self.label}: trailing reflected method signature")
        return result, parameters

    def type_relations(self, full_name):
        """Declared base/interface identities from TypeDef and InterfaceImpl."""
        owners = [rid for rid,name in self.reflection_names.items() if name == full_name]
        require(len(owners) == 1, f"{self.label}: missing/ambiguous relation owner")
        owner = owners[0]
        extends = self.tables.row(2,owner)[3]
        base = self.reflection_type_identity(*self.tables.coded(extends,"TypeDefOrRef")) if extends else None
        interfaces=[]
        for rid in range(1,self.tables.counts[9]+1):
            type_rid,interface=self.tables.row(9,rid)
            self.tables.row(2,type_rid)
            actual=self.reflection_type_identity(*self.tables.coded(interface,"TypeDefOrRef"))
            if type_rid==owner: interfaces.append(actual)
        require(len(interfaces)==len(set(interfaces)),f"{self.label}: duplicate InterfaceImpl identity")
        return dict(base=base,interfaces=interfaces)


# Only the bounded wrapper vocabulary is admitted, never silently skipped.
IL_OPS = {index: (name, "") for index, name in enumerate((
    "nop", "break", "ldarg.0", "ldarg.1", "ldarg.2", "ldarg.3", "ldloc.0", "ldloc.1", "ldloc.2", "ldloc.3",
    "stloc.0", "stloc.1", "stloc.2", "stloc.3"))}
IL_OPS.update({0x14:("ldnull", ""), 0x15:("ldc.i4.m1", ""), 0x1f:("ldc.i4.s", "int1"), 0x20:("ldc.i4", "int4"),
               0x21:("ldc.i8", "int8"), 0x25:("dup", ""), 0x26:("pop", ""), 0x27:("jmp", "token"),
               0x28:("call", "token"), 0x2a:("ret", ""), 0x45:("switch", "switch"),
               0x6f:("callvirt", "token"), 0x70:("cpobj", "token"), 0x71:("ldobj", "token"),
               0x72:("ldstr", "token"), 0x73:("newobj", "token"), 0x74:("castclass", "token"),
               0x75:("isinst", "token"), 0x79:("unbox", "token"), 0x7a:("throw", ""),
               0x7b:("ldfld", "token"), 0x7c:("ldflda", "token"), 0x7d:("stfld", "token"),
               0x7e:("ldsfld", "token"), 0x7f:("ldsflda", "token"), 0x80:("stsfld", "token"),
               0x81:("stobj", "token"), 0x8c:("box", "token"), 0x8d:("newarr", "token"),
               0x8e:("ldlen", ""), 0x8f:("ldelema", "token"), 0xa5:("unbox.any", "token"),
               0xd0:("ldtoken", "token"), 0xfe01:("ceq", ""), 0xfe02:("cgt", ""), 0xfe03:("cgt.un", ""),
               0xfe04:("clt", ""), 0xfe05:("clt.un", ""), 0xfe15:("initobj", "token")})
IL_OPS.update({0x16 + i: (f"ldc.i4.{i}", "") for i in range(9)})
for index, name in enumerate(("br", "brfalse", "brtrue", "beq", "bge", "bgt", "ble", "blt", "bne.un", "bge.un", "bgt.un", "ble.un", "blt.un")):
    IL_OPS[0x2b + index] = (name + ".s", "branch1")
    IL_OPS[0x38 + index] = (name, "branch4")


def read_method_witnesses(path):
    path = Path(path)
    # Same path/size/identity validation as the inventory; no alternate bytes.
    read_type_inventory(path)
    return MethodProof(path.read_bytes(), path).witnesses()


class TypeKeyReader:
    """Validate the pinned native diagnostic key against byte-bound types.

    Length prefixes count UTF-8 bytes, not Python characters. Supported Player
    matrix shapes are definitions, generics, arrays, pointers and qualifiers.
    An unbound name or unsupported shape is an error, never a baseline fallback.
    """
    def __init__(self, text, inventories, identities, closure=(), label="typeKey"):
        require(type(text) is str and 0 < len(text) <= 1_000_000, f"{label}: missing/oversized native type key")
        self.data, self.at = text.encode("utf-8"), 0
        self.inventories, self.identities = inventories, identities
        self.names = {name.casefold(): name for name in inventories}
        self.closure, self.label = set(closure), label

    def take(self, literal):
        raw = literal.encode()
        require(self.data[self.at:self.at + len(raw)] == raw, f"{self.label}: malformed native type key near byte {self.at}")
        self.at += len(raw)

    def starts(self, literal): return self.data[self.at:].startswith(literal.encode())

    def number(self, maximum=65536):
        begin = self.at
        while self.at < len(self.data) and 48 <= self.data[self.at] <= 57: self.at += 1
        raw = self.data[begin:self.at]
        require(raw and len(raw) <= 10 and (len(raw) == 1 or raw[0] != 48), f"{self.label}: invalid/noncanonical key number")
        value = int(raw)
        require(value <= maximum, f"{self.label}: oversized key number")
        return value

    def part(self):
        size = self.number(1_000_000); self.take(":")
        require(self.at + size <= len(self.data), f"{self.label}: truncated length-prefixed key part")
        raw = self.data[self.at:self.at + size]; self.at += size
        try: return raw.decode("utf-8", errors="strict")
        except UnicodeDecodeError as error: raise VerificationError(f"{self.label}: split/invalid UTF-8 key part") from error

    def nested_part(self, depth):
        key = self.part()
        reader = TypeKeyReader(key, self.inventories, self.identities, self.closure, self.label)
        result = reader.shape(depth + 1)
        require(reader.at == len(reader.data), f"{self.label}: trailing composite key bytes")
        return result

    def definition(self):
        self.take("type("); assembly = self.part()
        require(assembly in self.names, f"{self.label}: unbound logical assembly in TypeKey")
        assembly = self.names[assembly]
        declarations = []
        while self.starts("/"):
            self.take("/"); namespace = self.part(); self.take("/"); name = self.part(); self.take("@"); arity = self.number()
            declarations.append((namespace, name, arity))
            require(len(declarations) <= 128, f"{self.label}: oversized declaration chain")
        self.take(")")
        require(declarations, f"{self.label}: empty definition key")
        known = {row["fullName"]: row for row in self.inventories[assembly]}
        full_name, nesting = "", []
        for index, (namespace, name, arity) in enumerate(declarations):
            full_name = ((reflection_escape(namespace) + "." if namespace else "") + reflection_escape(name)) if index == 0 else full_name + "+" + reflection_escape(name)
            row = known.get(full_name)
            require(row is not None and row["namespaceName"] == namespace and row["name"] == name and
                    row["genericArity"] == arity and row["nestingPath"] == nesting,
                    f"{self.label}: definition/nesting/arity absent from actual DLL: {full_name}")
            nesting.append(name)
        return dict(assemblyName=assembly, fullName=full_name, kind=row["kind"], genericArity=arity,
                    genericDefinition=full_name if arity else "", genericArguments=[], elementShape="",
                    containsShadowTypes=assembly in self.closure)

    def shape(self, depth=0):
        require(depth <= 128, f"{self.label}: oversized type shape recursion")
        if self.starts("type("): return self.definition()
        if self.starts("generic("):
            self.take("generic("); result = self.shape(depth + 1); arguments = []
            while self.starts(","):
                self.take(","); arguments.append(self.nested_part(depth))
                require(len(arguments) <= 256, f"{self.label}: oversized type arguments")
            self.take(")")
            require(result["genericArity"] == len(arguments) and arguments, f"{self.label}: generic instance arity mismatch")
            result["genericDefinition"] = result["fullName"]
            result["genericArguments"] = [a["fullName"] for a in arguments]
            result["fullName"] += "[[" + "],[".join(a["fullName"] + ", " + self.identities[a["assemblyName"]]["fullName"] for a in arguments) + "]]"
            result["containsShadowTypes"] |= any(a["containsShadowTypes"] for a in arguments)
            return result
        for form, suffix, element in (("szarray", "[]", "array-rank-1"), ("ptr", "*", "pointer")):
            if self.starts(form + "("):
                self.take(form + "("); result = self.shape(depth + 1); self.take(")")
                result.update(fullName=result["fullName"] + suffix, kind="class", genericArity=0, genericDefinition="", genericArguments=[], elementShape=element)
                return result
        if self.starts("array("):
            self.take("array("); rank = self.number(32); self.take(","); result = self.nested_part(depth)
            require(rank > 0, f"{self.label}: invalid array rank")
            # Managed MakeArrayType matrix uses unsized/unbounded rank arrays.
            self.take(",sizes=bounds=)")
            result.update(fullName=result["fullName"] + ("[*]" if rank == 1 else "[" + "," * (rank - 1) + "]"),
                          kind="class", genericArity=0, genericDefinition="", genericArguments=[], elementShape="array-rank-" + str(rank))
            return result
        if self.starts("qualified("):
            self.take("qualified(")
            attrs = self.number(65535); self.take(","); mods = self.number(63); self.take(","); byref = self.number(1); self.take(","); pinned = self.number(1); self.take(",")
            result = self.shape(depth + 1); self.take(")")
            require(attrs == mods == pinned == 0 and byref == 1, f"{self.label}: unsupported managed diagnostic qualifiers")
            result.update(fullName=result["fullName"] + "&", kind="class", genericArity=0, genericDefinition="", genericArguments=[], elementShape="byref")
            return result
        raise VerificationError(f"{self.label}: unsupported native type shape")

    def read(self):
        result = self.shape()
        require(self.at == len(self.data), f"{self.label}: trailing native type key bytes")
        return result
