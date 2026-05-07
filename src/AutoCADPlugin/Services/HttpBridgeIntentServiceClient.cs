using System.Net.Http.Json;
using VibeDraw.AutoCADPlugin.Contracts;

namespace VibeDraw.AutoCADPlugin.Services;

public sealed class HttpBridgeIntentServiceClient(HttpClient httpClient) : IIntentServiceClient
{
    public async Task<ParseInitialIntentResponse> ParseInitialIntentAsync(
        ParseInitialIntentRequest request,
        CancellationToken cancellationToken = default)
    {
        using var response = await httpClient.PostAsJsonAsync(
            "intent/parse-initial",
            request,
            cancellationToken);
        response.EnsureSuccessStatusCode();

        var payload = await response.Content.ReadFromJsonAsync<ParseInitialIntentResponse>(cancellationToken);
        return payload ?? throw new InvalidDataException("The intent service returned an empty response.");
    }
}
