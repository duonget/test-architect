package service_test

import (
	"context"
	"errors"
	"testing"
)

// ============================================================================
// TEMPLATE: Go Table-Driven Tests (Idiomatic & Robust)
// ============================================================================

func TestProcessTransaction_TableDriven(t *testing.T) {
	// Table of test scenarios covering multiple dimensions
	tests := []struct {
		name          string
		amount        int64
		currency      string
		mockGatewayFn func(ctx context.Context) error
		wantErr       bool
		expectedErr   error
	}{
		{
			name:     "Happy Path: Valid $50 charge",
			amount:   5000,
			currency: "USD",
			mockGatewayFn: func(ctx context.Context) error {
				return nil
			},
			wantErr: false,
		},
		{
			name:     "Boundary: Zero amount rejected",
			amount:   0,
			currency: "USD",
			mockGatewayFn: nil,
			wantErr:     true,
			expectedErr: ErrInvalidAmount,
		},
		{
			name:     "Boundary: Negative amount rejected",
			amount:   -500,
			currency: "USD",
			mockGatewayFn: nil,
			wantErr:     true,
			expectedErr: ErrInvalidAmount,
		},
		{
			name:     "Nullability: Empty currency rejected",
			amount:   1000,
			currency: "",
			mockGatewayFn: nil,
			wantErr:     true,
			expectedErr: ErrMissingCurrency,
		},
		{
			name:     "Failure Mode: Gateway downstream error",
			amount:   2000,
			currency: "USD",
			mockGatewayFn: func(ctx context.Context) error {
				return errors.New("network gateway unreachable")
			},
			wantErr:     true,
			expectedErr: ErrGatewayFailed,
		},
	}

	for _, tt := range tests {
		tt := tt // capture range variable
		t.Run(tt.name, func(t *testing.T) {
			// Arrange
			mockGW := &mockPaymentGateway{sendFn: tt.mockGatewayFn}
			svc := NewPaymentService(mockGW)

			// Act
			err := svc.Process(context.Background(), tt.amount, tt.currency)

			// Assert
			if (err != nil) != tt.wantErr {
				t.Fatalf("Process() error = %v, wantErr %v", err, tt.wantErr)
			}
			if tt.expectedErr != nil && !errors.Is(err, tt.expectedErr) {
				t.Errorf("Process() expected error %v, got %v", tt.expectedErr, err)
			}
		})
	}
}
