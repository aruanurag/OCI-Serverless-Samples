package main

import (
	"context"
	"encoding/json"
)

type Order struct {
	OrderID    string  `json:"order_id"`
	CustomerID string  `json:"customer_id"`
	Amount     float64 `json:"amount"`
}

func main() {
	fn := func(ctx context.Context, input []byte) ([]byte, error) {
		var order Order
		if err := json.Unmarshal(input, &order); err != nil {
			return nil, err
		}
		// Here you would process the order
		return []byte("Order placed"), nil
	}
	_ = fn
}
