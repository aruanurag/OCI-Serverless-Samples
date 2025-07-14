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
	fn := func(ctx context.Context, input []byte) ([]byte, error) {
		var info CustomerInfo
		if err := json.Unmarshal(input, &info); err != nil {
			return nil, err
		}
		// Here you would save info to a database or similar
		return []byte("Customer info saved"), nil
	}
	_ = fn
}
