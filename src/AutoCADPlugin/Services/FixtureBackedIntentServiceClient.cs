using System.Text.Json;
using VibeDraw.AutoCADPlugin.Contracts;

namespace VibeDraw.AutoCADPlugin.Services;

public sealed class FixtureBackedIntentServiceClient(string responseFixturePath) : IIntentServiceClient
{
    private static readonly JsonSerializerOptions SerializerOptions = new()
    {
        PropertyNameCaseInsensitive = true,
    };

    public string ResponseFixturePath { get; } = responseFixturePath;

    public ParseInitialIntentRequest? LastRequest { get; private set; }

    public async Task<ParseInitialIntentResponse> ParseInitialIntentAsync(
        ParseInitialIntentRequest request,
        CancellationToken cancellationToken = default)
    {
        LastRequest = request;

        await using var stream = File.OpenRead(ResponseFixturePath);
        var response = await JsonSerializer.DeserializeAsync<ParseInitialIntentResponse>(
            stream,
            SerializerOptions,
            cancellationToken);

        return response ?? throw new InvalidDataException("Fixture-backed response could not be deserialized.");
    }
}
