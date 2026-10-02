export interface PaymentRequest {
  idempotencyKey: string;
  amountCents: number;
  currency: string;
  customerId: string;
}

export interface PaymentReceipt {
  transactionId: string;
  status: "SUCCESS" | "FAILED";
  amountCents: number;
  chargedAt: Date;
}

export interface PaymentGatewayClient {
  charge(
    amountCents: number,
    currency: string,
    customerId: string,
    idempotencyKey: string,
  ): Promise<{ gatewayId: string }>;
}

export class PaymentService {
  private operations = new Map<
    string,
    { fingerprint: string; result: Promise<PaymentReceipt> }
  >();

  constructor(private gateway: PaymentGatewayClient) {}

  async processPayment(req: PaymentRequest): Promise<PaymentReceipt> {
    if (!req || typeof req !== "object") {
      throw new Error("InvalidPaymentRequest");
    }

    if (typeof req.idempotencyKey !== "string" || req.idempotencyKey.trim().length === 0) {
      throw new Error("MissingIdempotencyKey");
    }

    if (!Number.isSafeInteger(req.amountCents) || req.amountCents <= 0) {
      throw new Error("InvalidAmount: Must be greater than zero");
    }

    if (req.amountCents > 10_000_00) { // Max $10,000
      throw new Error("AmountExceedsLimit: Maximum single charge is $10,000");
    }

    if (typeof req.currency !== "string" || !["USD", "EUR", "VND"].includes(req.currency.trim().toUpperCase())) {
      throw new Error(`UnsupportedCurrency: ${req.currency}`);
    }

    if (typeof req.customerId !== "string" || req.customerId.trim().length === 0) {
      throw new Error("MissingCustomerId");
    }

    const idempotencyKey = req.idempotencyKey.trim();
    const amountCents = req.amountCents;
    const currency = req.currency.trim().toUpperCase();
    const customerId = req.customerId.trim();
    const fingerprint = JSON.stringify([amountCents, currency, customerId]);
    const existing = this.operations.get(idempotencyKey);

    if (existing) {
      if (existing.fingerprint !== fingerprint) {
        throw new Error("IdempotencyKeyConflict");
      }
      return existing.result;
    }

    let result: Promise<PaymentReceipt>;
    result = Promise.resolve()
      .then(() => this.gateway.charge(amountCents, currency, customerId, idempotencyKey))
      .then((gatewayRes): PaymentReceipt => ({
        transactionId: gatewayRes.gatewayId,
        status: "SUCCESS",
        amountCents,
        chargedAt: new Date(),
      }))
      .catch((error) => {
        if (this.operations.get(idempotencyKey)?.result === result) {
          this.operations.delete(idempotencyKey);
        }
        throw error;
      });

    this.operations.set(idempotencyKey, { fingerprint, result });
    return result;
  }
}
