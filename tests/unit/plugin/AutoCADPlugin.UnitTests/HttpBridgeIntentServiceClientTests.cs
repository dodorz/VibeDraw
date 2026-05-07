using System.Net;
using System.Net.Http;
using System.Text;
using VibeDraw.AutoCADPlugin.Contracts;
using VibeDraw.AutoCADPlugin.Services;
using Xunit;

namespace VibeDraw.Tests.Unit.Plugin;

public sealed class HttpBridgeIntentServiceClientTests
{
    [Fact]
    public async Task ParseInitialIntentAsyncPostsExpectedPayload()
    {
        var fixtureJson = await File.ReadAllTextAsync(GetContractsFixturePath("parse-initial-intent.response.valid.json"));
        var handler = new FakeHttpMessageHandler(fixtureJson);
        var httpClient = new HttpClient(handler)
        {
            BaseAddress = new Uri("http://localhost:5050/"),
        };
        var client = new HttpBridgeIntentServiceClient(httpClient);

        var response = await client.ParseInitialIntentAsync(new ParseInitialIntentRequest
        {
            Prompt = "Draw canonical bridge",
        });

        Assert.NotNull(handler.LastRequest);
        Assert.Equal(HttpMethod.Post, handler.LastRequest!.Method);
        Assert.Equal("/intent/parse-initial", handler.LastRequest.RequestUri!.AbsolutePath);
        Assert.Equal("continuous_girder", response.Intent.BridgeType);
        Assert.Contains("Alignment is straight.", response.Assumptions);
    }

    private static string GetContractsFixturePath(string fileName)
    {
        return Path.GetFullPath(Path.Combine(
            AppContext.BaseDirectory,
            "..", "..", "..", "..", "..", "..", "..",
            "tests", "contracts", fileName));
    }

    private sealed class FakeHttpMessageHandler(string responseJson) : HttpMessageHandler
    {
        public HttpRequestMessage? LastRequest { get; private set; }

        protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken cancellationToken)
        {
            LastRequest = request;
            var response = new HttpResponseMessage(HttpStatusCode.OK)
            {
                Content = new StringContent(responseJson, Encoding.UTF8, "application/json"),
            };
            return Task.FromResult(response);
        }
    }
}
