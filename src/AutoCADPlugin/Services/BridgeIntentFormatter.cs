using VibeDraw.AutoCADPlugin.Contracts;
using VibeDraw.AutoCADPlugin.Models;

namespace VibeDraw.AutoCADPlugin.Services;

public static class BridgeIntentFormatter
{
    public static IReadOnlyList<ParameterRow> ToParameterRows(BridgeIntentDto intent)
    {
        var rows = new List<ParameterRow>
        {
            new("Bridge Type", intent.BridgeType),
            new("Material", intent.Material),
            new("Spans (m)", string.Join(" + ", intent.SpansM)),
            new("Deck Width (m)", intent.DeckWidthM.ToString("0.###")),
            new("Requested Drawings", string.Join(", ", intent.RequestedDrawings)),
        };

        if (!string.IsNullOrWhiteSpace(intent.AlignmentType))
        {
            rows.Add(new("Alignment", intent.AlignmentType));
        }

        if (!string.IsNullOrWhiteSpace(intent.StartStation))
        {
            rows.Add(new("Start Station", intent.StartStation));
        }

        if (!string.IsNullOrWhiteSpace(intent.Superstructure?.SectionType))
        {
            rows.Add(new("Section Type", intent.Superstructure.SectionType));
        }

        if (!string.IsNullOrWhiteSpace(intent.Superstructure?.GirderDepthPolicy))
        {
            rows.Add(new("Girder Depth Policy", intent.Superstructure.GirderDepthPolicy));
        }

        if (!string.IsNullOrWhiteSpace(intent.Substructure?.PierType))
        {
            rows.Add(new("Pier Type", intent.Substructure.PierType));
        }

        if (!string.IsNullOrWhiteSpace(intent.Substructure?.AbutmentType))
        {
            rows.Add(new("Abutment Type", intent.Substructure.AbutmentType));
        }

        return rows;
    }
}
