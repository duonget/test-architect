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
  charge(amountCents: number, currency: string, customerId: string): Promise<{ gatewayId: string }>;
}

export class PaymentService {
  private processedKeys = new Map<string, PaymentReceipt>();

  constructor(private gateway: PaymentGatewayClient) {}

  async processPayment(req: PaymentRequest): Promise<PaymentReceipt> {
    // 1. Validation & Boundaries
    if (!req.idempotencyKey || req.idempotencyKey.trim().length === 0) {
      throw new Error("MissingIdempotencyKey");
    }

    if (req.amountCents <= 0) {
      throw new Error("InvalidAmount: Must be greater than zero");
    }

    if (req.amountCents > 10_000_00) { // Max $10,000
      throw new Error("AmountExceedsLimit: Maximum single charge is $10,000");
    }

    if (!req.currency || !["USD", "EUR", "VND"].includes(req.currency.toUpperCase())) {
      throw new Error(`UnsupportedCurrency: ${req.currency}`);
    }

    // 2. Idempotency Check
    if (this.processedKeys.has(req.idempotencyKey)) {
      return this.processedKeys.get(req.idempotencyKey)!;
    }

    // 3. Process Charge via External Gateway
    const gatewayRes = await this.gateway.charge(req.amountCents, req.currency, req.customerId);

    const receipt: PaymentReceipt = {
      transactionId: gatewayRes.gatewayId,
      status: "SUCCESS",
      amountCents: req.amountCents,
      chargedAt: new Date()
    };

    this.processedKeys.set(req.idempotencyKey, receipt);
    return receipt;
  }
}
