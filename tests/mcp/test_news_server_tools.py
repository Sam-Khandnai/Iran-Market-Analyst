from market_analyst.mcp_servers import news_server


async def test_get_news_sentiment_tool_returns_neutral_stub():
    result = await news_server.get_news_sentiment("فولاد")
    assert result["sentiment"] == "neutral"
    assert result["coverage"] == 0.0