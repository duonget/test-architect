import { beforeEach, describe, expect, it, vi } from "vitest";

// ============================================================================
// TEMPLATE: TypeScript + Vitest (AAA Pattern & Minimal Mocking)
// ============================================================================

describe("ServiceOrFunctionUnderTest", () => {
  // 1. Minimum Viable Mocking (Only external boundaries: network, db, clocks)
  const mockExternalGateway = {
    sendRequest: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  // --------------------------------------------------------------------------
  // Dimension 1: Happy Path
  // --------------------------------------------------------------------------
  describe("Happy Path", () => {
    it("should process standard valid input and return expected result", async () => {
      // Arrange
      mockExternalGateway.sendRequest.mockResolvedValueOnce({ status: 200, id: "tx_123" });
      const input = { amount: 100, currency: "USD" };

      // Act
      const result = await processTransaction(input, mockExternalGateway);

      // Assert
      expect(result).toBeDefined();
      expect(result.id).toBe("tx_123");
      expect(mockExternalGateway.sendRequest).toHaveBeenCalledTimes(1);
    });
  });

  // --------------------------------------------------------------------------
  // Dimension 2: Boundary & Limits
  // --------------------------------------------------------------------------
  describe("Boundary & Limits", () => {
    it.each([
      { amount: 0, expectedError: "AmountMustBePositive" },
      { amount: -1, expectedError: "AmountMustBePositive" },
      { amount: 1_000_001, expectedError: "AmountExceedsMaximumLimit" },
    ])("should throw $expectedError when amount is $amount", async ({ amount, expectedError }) => {
      // Arrange & Act & Assert
      await expect(
        processTransaction({ amount, currency: "USD" }, mockExternalGateway)
      ).rejects.toThrow(expectedError);
    });
  });

  // --------------------------------------------------------------------------
  // Dimension 3: Nullability & Schema Defense
  // --------------------------------------------------------------------------
  describe("Nullability & Schema Defense", () => {
    it("should reject input when currency is missing or null", async () => {
      // Arrange
      const invalidInput = { amount: 50, currency: null as any };

      // Act & Assert
      await expect(
        processTransaction(invalidInput, mockExternalGateway)
      ).rejects.toThrow(/invalid currency/i);
    });
  });

  // --------------------------------------------------------------------------
  // Dimension 4: Failure Modes & Exceptions
  // --------------------------------------------------------------------------
  describe("Failure Modes", () => {
    it("should handle external gateway timeout gracefully", async () => {
      // Arrange
      mockExternalGateway.sendRequest.mockRejectedValueOnce(new Error("ETIMEDOUT"));

      // Act & Assert
      await expect(
        processTransaction({ amount: 100, currency: "USD" }, mockExternalGateway)
      ).rejects.toThrow("PaymentGatewayTimeout");
    });
  });
});
