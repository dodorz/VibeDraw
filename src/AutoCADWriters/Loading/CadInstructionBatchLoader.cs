using System.Text.Json;
using VibeDraw.AutoCADWriters.Models;

namespace VibeDraw.AutoCADWriters.Loading;

public static class CadInstructionBatchLoader
{
    public static CadInstructionBatch LoadFromFile(string path)
    {
        using var stream = File.OpenRead(path);
        using var document = JsonDocument.Parse(stream);
        return Load(document.RootElement);
    }

    public static CadInstructionBatch Load(JsonElement root)
    {
        var projectId = root.GetProperty("project_id").GetString()
            ?? throw new InvalidDataException("project_id is required.");
        var drawingId = root.GetProperty("drawing_id").GetString()
            ?? throw new InvalidDataException("drawing_id is required.");
        var instructions = new List<CadInstruction>();

        foreach (var instructionElement in root.GetProperty("instructions").EnumerateArray())
        {
            instructions.Add(ParseInstruction(instructionElement));
        }

        return new CadInstructionBatch(projectId, drawingId, instructions);
    }

    private static CadInstruction ParseInstruction(JsonElement element)
    {
        var kind = element.GetProperty("kind").GetString();
        return kind switch
        {
            "line" => new LineInstruction(
                ReadString(element, "id"),
                ReadString(element, "layer"),
                ReadString(element, "view_id"),
                ReadString(element, "source_component_id"),
                ReadPoint(element, "from"),
                ReadPoint(element, "to")),
            "polyline" => new PolylineInstruction(
                ReadString(element, "id"),
                ReadString(element, "layer"),
                ReadString(element, "view_id"),
                ReadString(element, "source_component_id"),
                ReadPoints(element.GetProperty("points")),
                element.GetProperty("closed").GetBoolean()),
            "text" => new TextInstruction(
                ReadString(element, "id"),
                ReadString(element, "layer"),
                ReadString(element, "view_id"),
                ReadString(element, "source_component_id"),
                ReadPoint(element, "position"),
                ReadString(element, "text"),
                element.GetProperty("height").GetDouble()),
            "aligned_dimension" => new AlignedDimensionInstruction(
                ReadString(element, "id"),
                ReadString(element, "layer"),
                ReadString(element, "view_id"),
                ReadString(element, "source_component_id"),
                ReadPoint(element, "from"),
                ReadPoint(element, "to"),
                ReadPoint(element, "dimension_line_point"),
                ReadString(element, "text")),
            _ => throw new InvalidDataException($"Unsupported instruction kind '{kind}'."),
        };
    }

    private static string ReadString(JsonElement element, string propertyName)
        => element.GetProperty(propertyName).GetString()
           ?? throw new InvalidDataException($"{propertyName} is required.");

    private static Point2D ReadPoint(JsonElement element, string propertyName)
        => ReadPoint(element.GetProperty(propertyName));

    private static Point2D ReadPoint(JsonElement element)
    {
        if (element.GetArrayLength() != 2)
        {
            throw new InvalidDataException("Point must contain exactly two numbers.");
        }

        return new Point2D(element[0].GetDouble(), element[1].GetDouble());
    }

    private static IReadOnlyList<Point2D> ReadPoints(JsonElement element)
    {
        var points = new List<Point2D>();
        foreach (var pointElement in element.EnumerateArray())
        {
            points.Add(ReadPoint(pointElement));
        }

        return points;
    }
}
