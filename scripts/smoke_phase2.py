import asyncio

from market_analyst.data.service import get_symbol
from market_analyst.engines.technical.engine import TechnicalEngine


async def main(symbol: str = "فولاد") -> None:
    data = await get_symbol(symbol)
    result = TechnicalEngine().analyze(symbol, data.prices)
    print(result.model_dump_json(indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())