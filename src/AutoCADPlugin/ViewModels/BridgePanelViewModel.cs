using VibeDraw.AutoCADPlugin.Contracts;
using VibeDraw.AutoCADPlugin.Fixtures;
using VibeDraw.AutoCADPlugin.Models;
using VibeDraw.AutoCADPlugin.Services;

namespace VibeDraw.AutoCADPlugin.ViewModels;

public sealed class BridgePanelViewModel(
    IIntentServiceClient intentServiceClient,
    ICanonicalPromptProvider canonicalPromptProvider)
{
    public string PromptText { get; private set; } = string.Empty;

    public bool IsBusy { get; private set; }

    public string? LastError { get; private set; }

    public BridgeIntentDto? CurrentIntent { get; private set; }

    public IReadOnlyList<string> Assumptions { get; private set; } = [];

    public IReadOnlyList<string> Questions { get; private set; } = [];

    public IReadOnlyList<ParameterRow> ParameterRows { get; private set; } = [];

    public async Task SubmitPromptAsync(string prompt, CancellationToken cancellationToken = default)
    {
        PromptText = prompt.Trim();
        LastError = null;
        IsBusy = true;

        try
        {
            var request = new ParseInitialIntentRequest
            {
                Prompt = PromptText,
            };

            var response = await intentServiceClient.ParseInitialIntentAsync(request, cancellationToken);
            ApplyResponse(response);
        }
        catch (Exception ex)
        {
            LastError = ex.Message;
            CurrentIntent = null;
            Assumptions = [];
            Questions = [];
            ParameterRows = [];
            throw;
        }
        finally
        {
            IsBusy = false;
        }
    }

    public Task SubmitCanonicalPromptAsync(CancellationToken cancellationToken = default)
    {
        var canonicalPrompt = canonicalPromptProvider.LoadCanonicalPrompt();
        return SubmitPromptAsync(canonicalPrompt, cancellationToken);
    }

    private void ApplyResponse(ParseInitialIntentResponse response)
    {
        CurrentIntent = response.Intent;
        Assumptions = response.Assumptions;
        Questions = response.Questions;
        ParameterRows = BridgeIntentFormatter.ToParameterRows(response.Intent);
    }
}
