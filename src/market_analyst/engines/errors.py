class InsufficientHistoryError(ValueError):
    def __init__(self, have: int, need: int):
        self.have, self.need = have, need
        super().__init__(f"داده ناکافی: {have} روز موجود، حداقل {need} روز لازم است")