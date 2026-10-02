import { beforeEach, describe, expect, it, vi } from "vitest";
import { PaymentGatewayClient, PaymentRequest, PaymentService } from "./payment.js";

describe("PaymentService (Architect-Engineered Suite)", () => {
  let mockGateway: PaymentGatewayClient;
  let service: PaymentService;

  beforeEach(() => {
    // Only mock the external gateway boundary
    mockGateway = {
      charge: vi.fn().mockResolvedValue({ gatewayId: "gtw_tx_999" }),
    };
    service = new PaymentService(mockGateway);
  });

  // ==========================================================================
  // Dimension 1: Happy Path
  // ==========================================================================
  describe("Happy Path", () => {
    it("TC-01: should process standard valid USD payment successfully", async () => {
      // Arrange
      const req: PaymentRequest = {
        idempotencyKey: "key-12345",
        amountCents: 5000,
        currency: "USD",
        customerId: "cust_abc",
      };

      // Act
      const receipt = await service.processPayment(req);

      // Assert
      expect(receipt.status).toBe("SUCCESS");
      expect(receipt.transactionId).toBe("gtw_tx_999");
      expect(receipt.amountCents).toBe(5000);
      expect(mockGateway.charge).toHaveBeenCalledTimes(1);
      expect(mockGateway.charge).toHaveBeenCalledWith(5000, "USD", "cust_abc", "key-12345");
    });

    it.each(["USD", "EUR", "VND"])("TC-02: should accept supported currency %s", async (currency) => {
      // Arrange & Act
      const receipt = await service.processPayment({
        idempotencyKey: `key-${currency}`,
        amountCents: 1000,
        currency,
        customerId: "cust_1",
      });

      // Assert
      expect(receipt.status).toBe("SUCCESS");
    });
  });

  // ==========================================================================
  // Dimension 2: Boundary & Limits
  // ==========================================================================
  describe("Boundary & Limits", () => {
    it("TC-03: should accept the minimum valid amount of 1 cent", async () => {
      const receipt = await service.processPayment({
        idempotencyKey: "min-cent",
        amountCents: 1,
        currency: "USD",
        customerId: "cust_min",
      });
      expect(receipt.status).toBe("SUCCESS");
    });

    it.each([0, -1, -5000])("TC-04/05: should reject non-positive amount %d", async (amount) => {
      await expect(
        service.processPayment({
          idempotencyKey: "invalid-amt",
          amountCents: amount,
          currency: "USD",
          customerId: "cust_1",
        })
      ).rejects.toThrow(/invalidamount/i);
    });

    it("TC-06: should accept exactly maximum limit of $10,000 (1,000,000 cents)", async () => {
      const receipt = await service.processPayment({
        idempotencyKey: "max-limit",
        amountCents: 1_000_000,
        currency: "USD",
        customerId: "cust_max",
      });
      expect(receipt.status).toBe("SUCCESS");
    });

    it("TC-07: should reject amount exceeding maximum limit by 1 cent", async () => {
      await expect(
        service.processPayment({
          idempotencyKey: "over-max",
          amountCents: 1_000_001,
          currency: "USD",
          customerId: "cust_max",
        })
      ).rejects.toThrow(/amountexceedslimit/i);
    });
  });

  // ==========================================================================
  // Dimension 3: Nullability & Schema
  // ==========================================================================
  describe("Nullability & Schema Defense", () => {
    it("TC-08a: should reject a null request", async () => {
      await expect(service.processPayment(null as any)).rejects.toThrow("InvalidPaymentRequest");
      expect(mockGateway.charge).not.toHaveBeenCalled();
    });

    it.each(["", "   ", null as any])("TC-08: should reject empty idempotency key %s", async (key) => {
      await expect(
        service.processPayment({
          idempotencyKey: key,
          amountCents: 1000,
          currency: "USD",
          customerId: "cust_1",
        })
      ).rejects.toThrow(/missingidempotencykey/i);
    });

    it("TC-09: should reject unsupported currency", async () => {
      await expect(
        service.processPayment({
          idempotencyKey: "valid-key",
          amountCents: 1000,
          currency: "GBP",
          customerId: "cust_1",
        })
      ).rejects.toThrow(/unsupportedcurrency/i);
    });

    it.each([NaN, 1.5, undefined as any])("TC-09a: should reject malformed amount %s", async (amount) => {
      await expect(
        service.processPayment({
          idempotencyKey: "malformed-amount",
          amountCents: amount,
          currency: "USD",
          customerId: "cust_1",
        })
      ).rejects.toThrow(/invalidamount/i);
      expect(mockGateway.charge).not.toHaveBeenCalled();
    });

    it("TC-09b: should reject an empty customer ID", async () => {
      await expect(
        service.processPayment({
          idempotencyKey: "missing-customer",
          amountCents: 1000,
          currency: "USD",
          customerId: "  ",
        })
      ).rejects.toThrow(/missingcustomerid/i);
      expect(mockGateway.charge).not.toHaveBeenCalled();
    });

    it("TC-09c: should normalize currency before charging", async () => {
      await service.processPayment({
        idempotencyKey: "lowercase-currency",
        amountCents: 1000,
        currency: " usd ",
        customerId: "cust_1",
      });

      expect(mockGateway.charge).toHaveBeenCalledWith(1000, "USD", "cust_1", "lowercase-currency");
    });

    it("TC-09d: should charge the validated amount even if the caller mutates its request", async () => {
      const request: PaymentRequest = {
        idempotencyKey: "mutable-request",
        amountCents: 1000,
        currency: "USD",
        customerId: "cust_1",
      };

      const result = service.processPayment(request);
      request.amountCents = 1_000_001;
      const receipt = await result;

      expect(mockGateway.charge).toHaveBeenCalledWith(1000, "USD", "cust_1", "mutable-request");
      expect(receipt.amountCents).toBe(1000);
    });
  });

  // ==========================================================================
  // Dimension 4 & 5: Failure Modes & Idempotency
  // ==========================================================================
  describe("Failure Modes & Idempotency", () => {
    it("TC-10: should not cache idempotency key if external gateway fails", async () => {
      // Arrange: gateway throws
      (mockGateway.charge as any).mockRejectedValueOnce(new Error("Gateway500"));

      // Act & Assert 1st call
      await expect(
        service.processPayment({
          idempotencyKey: "fail-retry-key",
          amountCents: 1000,
          currency: "USD",
          customerId: "cust_1",
        })
      ).rejects.toThrow("Gateway500");

      // Act & Assert 2nd call: should retry gateway, not return broken cached receipt
      (mockGateway.charge as any).mockResolvedValueOnce({ gatewayId: "gtw_retry_ok" });
      const receipt = await service.processPayment({
        idempotencyKey: "fail-retry-key",
        amountCents: 1000,
        currency: "USD",
        customerId: "cust_1",
      });
      expect(receipt.transactionId).toBe("gtw_retry_ok");
      expect(mockGateway.charge).toHaveBeenCalledTimes(2);
    });

    it("TC-11: should share one in-flight charge between concurrent duplicate requests", async () => {
      // Arrange
      const req: PaymentRequest = {
        idempotencyKey: "idem-double-click",
        amountCents: 2500,
        currency: "USD",
        customerId: "cust_double",
      };

      let resolveCharge!: (value: { gatewayId: string }) => void;
      (mockGateway.charge as any).mockReturnValueOnce(
        new Promise((resolve) => {
          resolveCharge = resolve;
        })
      );

      // Act: Both requests overlap before the gateway responds.
      const first = service.processPayment(req);
      const second = service.processPayment(req);
      await vi.waitFor(() => expect(mockGateway.charge).toHaveBeenCalledTimes(1));
      resolveCharge({ gatewayId: "gtw_concurrent" });
      const [res1, res2] = await Promise.all([first, second]);

      // Assert
      expect(res1).toEqual(res2);
      expect(mockGateway.charge).toHaveBeenCalledTimes(1);
    });

    it("TC-12: should reject reuse of an idempotency key with a different payload", async () => {
      await service.processPayment({
        idempotencyKey: "conflicting-key",
        amountCents: 1000,
        currency: "USD",
        customerId: "cust_1",
      });

      await expect(
        service.processPayment({
          idempotencyKey: "conflicting-key",
          amountCents: 2000,
          currency: "USD",
          customerId: "cust_1",
        })
      ).rejects.toThrow("IdempotencyKeyConflict");
      expect(mockGateway.charge).toHaveBeenCalledTimes(1);
    });
  });
});
