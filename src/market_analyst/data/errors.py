class DataError(Exception):
    """پایه خطاهای لایه داده."""


class TSETMCError(DataError):
    """خطای غیرقابل‌تلاش‌مجدد از TSETMC."""


class TransientError(TSETMCError):
    """خطای موقت (شبکه، 429، 5xx) که retry می‌شود."""


class SymbolNotFound(DataError):
    def __init__(self, symbol: str, suggestions: list[str] | None = None):
        self.symbol = symbol
        self.suggestions = suggestions or []
        super().__init__(f"نماد «{symbol}» پیدا نشد. پیشنهادها: {self.suggestions}")