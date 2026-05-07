using VibeDraw.AutoCADPlugin.Contracts;

namespace VibeDraw.AutoCADPlugin.Services;

public interface IIntentServiceClient
{
    Task<ParseInitialIntentResponse> ParseInitialIntentAsync(
        ParseInitialIntentRequest request,
        CancellationToken cancellationToken = default);
}
