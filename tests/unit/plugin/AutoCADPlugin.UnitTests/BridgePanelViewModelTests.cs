using VibeDraw.AutoCADPlugin.Fixtures;
using VibeDraw.AutoCADPlugin.Services;
using VibeDraw.AutoCADPlugin.ViewModels;
using Xunit;

namespace VibeDraw.Tests.Unit.Plugin;

public sealed class BridgePanelViewModelTests
{
    [Fact]
    public async Task SubmitPromptAsyncPopulatesAssumptionsQuestionsAndParameters()
    {
        var serviceClient = new FixtureBackedIntentServiceClient(GetContractsFixturePath("parse-initial-intent.response.valid.json"));
        var canonicalPromptProvider = new FileSystemCanonicalPromptProvider(GetPromptFixturePath());
        var viewModel = new BridgePanelViewModel(serviceClient, canonicalPromptProvider);

        await viewModel.SubmitCanonicalPromptAsync();

        Assert.Equal(
            "Draw a prestressed continuous girder bridge with spans 40+70+40 m and bridge width 7.5 m.",
            viewModel.PromptText);
        Assert.NotNull(viewModel.CurrentIntent);
        Assert.Equal("continuous_girder", viewModel.CurrentIntent!.BridgeType);
        Assert.Equal(4, viewModel.Assumptions.Count);
        Assert.Empty(viewModel.Questions);
        Assert.Contains(viewModel.ParameterRows, row => row.Label == "Spans (m)" && row.Value == "40 + 70 + 40");
        Assert.Contains(viewModel.ParameterRows, row => row.Label == "Deck Width (m)" && row.Value == "7.5");
        Assert.NotNull(serviceClient.LastRequest);
        Assert.Equal("parse_initial_intent", serviceClient.LastRequest!.Type);
    }

    [Fact]
    public async Task SubmitPromptAsyncClearsBusyStateAfterFailure()
    {
        var serviceClient = new FixtureBackedIntentServiceClient(GetContractsFixturePath("missing-response.json"));
        var canonicalPromptProvider = new FileSystemCanonicalPromptProvider(GetPromptFixturePath());
        var viewModel = new BridgePanelViewModel(serviceClient, canonicalPromptProvider);

        await Assert.ThrowsAnyAsync<IOException>(() => viewModel.SubmitPromptAsync("bad"));

        Assert.False(viewModel.IsBusy);
        Assert.NotNull(viewModel.LastError);
        Assert.Empty(viewModel.ParameterRows);
    }

    private static string GetPromptFixturePath()
    {
        return Path.GetFullPath(Path.Combine(
            AppContext.BaseDirectory,
            "..", "..", "..", "..", "..", "..", "..",
            "fixtures", "prompts", "canonical-initial-prompt.txt"));
    }

    private static string GetContractsFixturePath(string fileName)
    {
        return Path.GetFullPath(Path.Combine(
            AppContext.BaseDirectory,
            "..", "..", "..", "..", "..", "..", "..",
            "tests", "contracts", fileName));
    }
}
