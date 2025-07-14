package main

import (
	"context"
	"encoding/json"
)

type CustomerInfo struct {
	ID   string `json:"id"`
	Name string `json:"name"`
}

func main() {
	// OCI Functions entrypoint
	fn := func(ctx context.Context, input []byte) ([]byte, error) {
		// For GET, input is usually empty or contains query params
		info := CustomerInfo{ID: "123", Name: "John Doe"}
		return json.Marshal(info)
	}
	// OCI Functions Go handler registration
	_ = fn
}
