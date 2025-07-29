package main

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"os"

	fdk "github.com/fnproject/fdk-go"
	"github.com/oracle/oci-go-sdk/v65/common"
	"github.com/oracle/oci-go-sdk/v65/queue"
)

type Order struct {
	OrderID    string  `json:"order_id"`
	CustomerID string  `json:"customer_id"`
	Amount     float64 `json:"amount"`
}

func main() {
	fdk.Handle(fdk.HandlerFunc(placeOrderHandler))
}

func placeOrderHandler(ctx context.Context, in io.Reader, out io.Writer) {
	var order Order
	if err := json.NewDecoder(in).Decode(&order); err != nil {
		fdk.WriteStatus(out, 400)
		fmt.Fprintf(out, `{"error": "Invalid input: %v"}`, err)
		return
	}

	queueURL := os.Getenv("QUEUE_URL")
	if queueURL == "" {
		fdk.WriteStatus(out, 500)
		fmt.Fprint(out, `{"error": "QUEUE_URL not set"}`)
		return
	}

	provider, err := common.DefaultConfigProvider()
	if err != nil {
		fdk.WriteStatus(out, 500)
		fmt.Fprintf(out, `{"error": "Failed to get OCI config: %v"}`, err)
		return
	}

	queueClient, err := queue.NewQueueClientWithConfigurationProvider(provider)
	if err != nil {
		fdk.WriteStatus(out, 500)
		fmt.Fprintf(out, `{"error": "Failed to create queue client: %v"}`, err)
		return
	}

	orderBytes, err := json.Marshal(order)
	if err != nil {
		fdk.WriteStatus(out, 500)
		fmt.Fprintf(out, `{"error": "Failed to marshal order: %v"}`, err)
		return
	}

	putReq := queue.PutMessagesRequest{
		QueueId: &queueURL,
		PutMessagesDetails: queue.PutMessagesDetails{
			Messages: []queue.PutMessagesDetailsEntry{{
				Content: common.String(string(orderBytes)),
			}},
		},
	}
	_, err = queueClient.PutMessages(ctx, putReq)
	if err != nil {
		fdk.WriteStatus(out, 500)
		fmt.Fprintf(out, `{"error": "Failed to send message to queue: %v"}`, err)
		return
	}

	fdk.WriteStatus(out, 200)
	fmt.Fprint(out, `{"message": "Order placed successfully"}`)
}
