using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;
using System.Text.Json.Serialization;
using MemoryPack;

namespace MemoryPackRepacker;

public enum MediaType { None, Audio, Video, Texture }

[MemoryPackable]
public partial class TableBundle {
    public string Name { get; set; } = string.Empty;
    public long Size { get; set; }
    public long Crc { get; set; }
    public bool isInbuild { get; set; }
    public bool isChanged { get; set; }
    public bool IsPrologue { get; set; }
    public bool IsSplitDownload { get; set; }
    public List<string> Includes { get; set; } = new();
}

[MemoryPackable]
public partial class TablePatchPack {
    public string Name { get; set; } = string.Empty;
    public long Size { get; set; }
    public long Crc { get; set; }
    public bool IsPrologue { get; set; }
    public TableBundle[] BundleFiles { get; set; } = Array.Empty<TableBundle>();
}

[MemoryPackable]
public partial class TableCatalog {
    public Dictionary<string, TableBundle> Table { get; set; } = new();
    public Dictionary<string, TablePatchPack> TablePack { get; set; } = new();
}

[MemoryPackable]
public partial class Media {
    [JsonPropertyName("path")] public string Path { get; set; } = string.Empty;
    public string FileName { get; set; } = string.Empty;
    public long Bytes { get; set; }
    public long Crc { get; set; }
    public bool IsPrologue { get; set; }
    public bool IsSplitDownload { get; set; }
    public MediaType MediaType { get; set; }
}

[MemoryPackable]
public partial class MediaCatalog {
    public Dictionary<string, Media> Table { get; set; } = new();
}

[MemoryPackable]
public partial class BundleFile {
    public string Name { get; set; } = string.Empty;
    public long Size { get; set; }
    public bool IsPrologue { get; set; }
    public long Crc { get; set; }
    public bool IsSplitDownload { get; set; }
    public ulong FileHash { get; set; }
    public string Signature { get; set; } = string.Empty;
}

[MemoryPackable]
public partial class BundlePatchPack {
    public string PackName { get; set; } = string.Empty;
    public long PackSize { get; set; }
    public long Crc { get; set; }
    public bool IsPrologue { get; set; }
    public bool IsSplitDownload { get; set; }
    public BundleFile[] BundleFiles { get; set; } = Array.Empty<BundleFile>();
}

[MemoryPackable]
public partial class BundlePatchPackInfo {
    public string Milestone { get; set; } = string.Empty;
    public int PatchVersion { get; set; }
    public BundlePatchPack[] FullPatchPacks { get; set; } = Array.Empty<BundlePatchPack>();
    public BundlePatchPack[] UpdatePacks { get; set; } = Array.Empty<BundlePatchPack>();
}

class Program {
    static void Main(string[] args) {
        if (args.Length < 4) return;

        string mode = args[0].ToLower();
        string type = args[1].ToLower();
        string inputPath = args[2];
        string outputPath = args[3];

        try {
            var options = new JsonSerializerOptions { 
                WriteIndented = true, 
                Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping 
            };

            if (mode == "deserialize") {
                byte[] data = File.ReadAllBytes(inputPath);
                string json = type switch {
                    "table" => JsonSerializer.Serialize(MemoryPackSerializer.Deserialize<TableCatalog>(data), options),
                    "media" => JsonSerializer.Serialize(MemoryPackSerializer.Deserialize<MediaCatalog>(data), options),
                    "bundle" => JsonSerializer.Serialize(MemoryPackSerializer.Deserialize<BundlePatchPackInfo>(data), options),
                    _ => ""
                };
                File.WriteAllText(outputPath, json);
            } 
            else if (mode == "serialize") {
                string json = File.ReadAllText(inputPath);
                byte[]? bin = type switch {
                    "table" => MemoryPackSerializer.Serialize(JsonSerializer.Deserialize<TableCatalog>(json)),
                    "media" => MemoryPackSerializer.Serialize(JsonSerializer.Deserialize<MediaCatalog>(json)),
                    "bundle" => MemoryPackSerializer.Serialize(JsonSerializer.Deserialize<BundlePatchPackInfo>(json)),
                    _ => null
                };
                if (bin != null) File.WriteAllBytes(outputPath, bin);
            }
        } catch (Exception ex) {
            Console.WriteLine(ex.Message);
        }
    }
}
