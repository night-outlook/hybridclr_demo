using System;
using System.Collections.Generic;
using System.Text;

namespace AssemblyShadowDemo
{
    // JsonUtility is retained as the DTO materializer, but this bounded reader
    // establishes the root schema first so omitted fields cannot default to zero.
    internal static class H1CountNativeDiagnosticsJsonReader
    {
        private const int MaximumJsonLength = 4096;
        private static readonly string[] RequiredFields = {
            "schemaVersion", "kind", "diagnosticOnly", "featureEnabled", "featureMode",
            "reservedPages", "mappedPages", "reservationCount", "nextImageId", "nextPageSlot",
            "ordinaryAllocatedCount", "shadowAllocatedCount", "reservedImageCount"
        };

        internal static void Validate(string json)
        {
            if (json.Length > MaximumJsonLength)
                throw new FormatException("H1 count diagnostics JSON exceeds the bounded schema size.");
            new Reader(json).ReadRoot();
        }

        private sealed class Reader
        {
            private readonly string json;
            private int position;

            internal Reader(string json) { this.json = json; }

            internal void ReadRoot()
            {
                Expect('{');
                var fields = new HashSet<string>(StringComparer.Ordinal);
                if (Take('}'))
                    throw Invalid("H1 count diagnostics JSON has no root fields.");

                do
                {
                    string field = ReadString();
                    if (!fields.Add(field))
                        throw Invalid("Duplicate H1 count diagnostics field: " + field);
                    Expect(':');
                    switch (field)
                    {
                        case "schemaVersion": ReadInteger(); break;
                        case "kind": ReadString(); break;
                        case "diagnosticOnly": ReadBoolean(); break;
                        case "featureEnabled": ReadBoolean(); break;
                        case "featureMode": ReadString(); break;
                        case "reservedPages": ReadUnsigned(); break;
                        case "mappedPages": ReadUnsigned(); break;
                        case "reservationCount": ReadUnsigned(); break;
                        case "nextImageId": ReadUnsigned(); break;
                        case "nextPageSlot": ReadUnsigned(); break;
                        case "ordinaryAllocatedCount": ReadUnsigned(); break;
                        case "shadowAllocatedCount": ReadUnsigned(); break;
                        case "reservedImageCount": ReadUnsigned(); break;
                        default: throw Invalid("Unknown H1 count diagnostics root field: " + field);
                    }
                } while (Take(','));
                Expect('}');
                EndDocument();

                foreach (string field in RequiredFields)
                    if (!fields.Contains(field))
                        throw Invalid("Missing H1 count diagnostics root field: " + field);
            }

            private void Expect(char token)
            {
                if (!Take(token)) throw Invalid("Expected '" + token + "'.");
            }

            private bool Take(char token)
            {
                WhiteSpace();
                if (position < json.Length && json[position] == token)
                {
                    ++position;
                    return true;
                }
                return false;
            }

            private void ReadBoolean()
            {
                WhiteSpace();
                if (Match("true") || Match("false")) return;
                throw Invalid("Expected a Boolean token.");
            }

            private int ReadInteger()
            {
                WhiteSpace();
                bool negative = position < json.Length && json[position] == '-';
                if (negative)
                {
                    ++position;
                    if (position == json.Length || json[position] < '0' || json[position] > '9')
                        throw Invalid("Expected a digit immediately after the minus sign.");
                }
                ulong value = ReadUnsigned();
                if ((!negative && value > int.MaxValue) || (negative && value > 2147483648UL))
                    throw Invalid("Integer token is outside Int32 range.");
                return negative ? (value == 2147483648UL ? int.MinValue : -(int)value) : (int)value;
            }

            private ulong ReadUnsigned()
            {
                WhiteSpace();
                if (position == json.Length || json[position] < '0' || json[position] > '9')
                    throw Invalid("Expected an unsigned integer token.");
                bool leadingZero = json[position] == '0';
                int start = position;
                ulong value = 0;
                while (position < json.Length && json[position] >= '0' && json[position] <= '9')
                {
                    uint digit = (uint)(json[position++] - '0');
                    if (value > (ulong.MaxValue - digit) / 10)
                        throw Invalid("Unsigned integer token overflows UInt64.");
                    value = value * 10 + digit;
                }
                if (leadingZero && position - start != 1)
                    throw Invalid("Leading zero in integer token.");
                return value;
            }

            private string ReadString()
            {
                WhiteSpace();
                if (position == json.Length || json[position++] != '"')
                    throw Invalid("Expected a JSON string.");
                var value = new StringBuilder();
                while (position < json.Length)
                {
                    char token = json[position++];
                    if (token == '"') return value.ToString();
                    if (token < 0x20) throw Invalid("Control character in JSON string.");
                    if (token != '\\') { value.Append(token); continue; }
                    if (position == json.Length) throw Invalid("Unterminated JSON escape.");
                    char escaped = json[position++];
                    switch (escaped)
                    {
                        case '"': value.Append('"'); break;
                        case '\\': value.Append('\\'); break;
                        case '/': value.Append('/'); break;
                        case 'b': value.Append('\b'); break;
                        case 'f': value.Append('\f'); break;
                        case 'n': value.Append('\n'); break;
                        case 'r': value.Append('\r'); break;
                        case 't': value.Append('\t'); break;
                        case 'u': value.Append(ReadUnicode()); break;
                        default: throw Invalid("Unknown JSON escape.");
                    }
                }
                throw Invalid("Unterminated JSON string.");
            }

            private void EndDocument()
            {
                WhiteSpace();
                if (position != json.Length)
                    throw Invalid("Trailing JSON content.");
            }

            private bool Match(string token)
            {
                if (position + token.Length > json.Length || string.CompareOrdinal(json, position, token, 0, token.Length) != 0)
                    return false;
                position += token.Length;
                return true;
            }

            private char ReadUnicode()
            {
                if (position + 4 > json.Length) throw Invalid("Incomplete Unicode escape.");
                int value = 0;
                for (int index = 0; index < 4; ++index)
                {
                    int digit = Hex(json[position++]);
                    if (digit < 0) throw Invalid("Invalid Unicode escape.");
                    value = (value << 4) | digit;
                }
                return (char)value;
            }

            private static int Hex(char value)
            {
                if (value >= '0' && value <= '9') return value - '0';
                if (value >= 'a' && value <= 'f') return value - 'a' + 10;
                if (value >= 'A' && value <= 'F') return value - 'A' + 10;
                return -1;
            }

            private void WhiteSpace()
            {
                while (position < json.Length && (json[position] == ' ' || json[position] == '\t' || json[position] == '\r' || json[position] == '\n'))
                    ++position;
            }

            private static FormatException Invalid(string message) { return new FormatException(message); }
        }
    }
}
