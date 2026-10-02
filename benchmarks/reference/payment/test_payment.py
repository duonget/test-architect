import asyncio
import unittest
from unittest.mock import AsyncMock
from solution import Payments


class PaymentTests(unittest.IsolatedAsyncioTestCase):
    async def test_overlap_and_completed_reuse(self):
        # Arrange: hold the external gateway until both callers have started.
        entered = asyncio.Event()
        release = asyncio.Event()

        async def charge(key, amount):
            entered.set()
            await release.wait()
            return "receipt"

        gateway = AsyncMock()
        gateway.charge.side_effect = charge
        service = Payments(gateway)
        first = asyncio.create_task(service.pay("key", 100))
        await entered.wait()
        second = asyncio.create_task(service.pay("key", 100))
        await asyncio.sleep(0)
        release.set()
        # Act
        results = await asyncio.gather(first, second)
        replay = await service.pay("key", 100)
        # Assert
        self.assertEqual(results, ["receipt", "receipt"])
        self.assertEqual(replay, "receipt")
        gateway.charge.assert_awaited_once_with("key", 100)

    async def test_conflict_and_retry(self):
        gateway = AsyncMock()
        gateway.charge.side_effect = [OSError("network"), "receipt"]
        service = Payments(gateway)
        with self.assertRaises(OSError):
            await service.pay("key", 100)
        # Catch unexpected failures as an assertion rather than a harness error.
        try:
            receipt = await service.pay("key", 100)
        except OSError as error:
            self.fail(f"Retry reused a failed operation: {error}")
        self.assertEqual(receipt, "receipt")
        with self.assertRaisesRegex(ValueError, "conflict"):
            await service.pay("key", 200)
        self.assertEqual(gateway.charge.await_count, 2)

    async def test_defense(self):
        gateway = AsyncMock()
        service = Payments(gateway)
        for key, amount in [(None, 1), (" ", 1), ("k", True), ("k", 0), ("k", 1.5)]:
            with self.subTest(key=key, amount=amount), self.assertRaises(ValueError):
                await service.pay(key, amount)
        gateway.charge.assert_not_awaited()

    async def test_pending_conflict_and_caller_cancellation(self):
        entered = asyncio.Event()
        release = asyncio.Event()

        async def charge(key, amount):
            entered.set()
            await release.wait()
            return "receipt"

        gateway = AsyncMock()
        gateway.charge.side_effect = charge
        service = Payments(gateway)
        first = asyncio.create_task(service.pay("key", 100))
        await entered.wait()
        try:
            with self.assertRaisesRegex(ValueError, "conflict"):
                await asyncio.wait_for(service.pay("key", 200), timeout=0.5)
        except asyncio.TimeoutError:
            self.fail("Conflicting request waited for the original charge instead of rejecting")
        first.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await first
        release.set()
        self.assertEqual(await service.pay("key", 100), "receipt")
        gateway.charge.assert_awaited_once_with("key", 100)
