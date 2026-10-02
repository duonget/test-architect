"""Single-process asynchronous idempotency example."""
import asyncio


class Payments:
    def __init__(self, gateway):
        self.gateway = gateway
        self.operations = {}

    async def pay(self, key, amount):
        if not isinstance(key, str) or not key.strip():
            raise ValueError("key")
        if type(amount) is not int or amount <= 0:
            raise ValueError("amount")
        if key in self.operations:
            previous_amount, task = self.operations[key]
            if previous_amount != amount:
                raise ValueError("conflict")
            return await asyncio.shield(task)
        task = asyncio.create_task(self._charge(key, amount))
        self.operations[key] = (amount, task)
        return await asyncio.shield(task)

    async def _charge(self, key, amount):
        try:
            return await self.gateway.charge(key, amount)
        except Exception:
            self.operations.pop(key, None)
            raise
