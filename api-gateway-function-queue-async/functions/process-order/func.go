package main

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"os"

	fdk "github.com/fnproject/fdk-go"
	"github.com/oracle/oci-go-sdk/v65/common"
	ociqueue "github.com/oracle/oci-go-sdk/v65/queue"
)

type Order struct {
	OrderID    string  `json:"order_id"`
	CustomerID string  `json:"customer_id"`
	Amount     float64 `json:"amount"`
}

func main() {
	fdk.Handle(fdk.HandlerFunc(processOrderHandler))
}

func processOrderHandler(ctx context.Context, in io.Reader, out io.Writer) {
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

	queueClient, err := ociqueue.NewQueueClientWithConfigurationProvider(provider)
	if err != nil {
		fdk.WriteStatus(out, 500)
		fmt.Fprintf(out, `{"error": "Failed to create queue client: %v"}`, err)
		return
	}

	// Receive a message from the queue
	req := ociqueue.GetMessagesRequest{
		QueueId: &queueURL,
		GetMessagesDetails: ociqueue.GetMessagesDetails{
			VisibilityInSeconds: common.Int(30),
			Limit:               common.Int(1),
		},
	}
	resp, err := queueClient.GetMessages(ctx, req)
	if err != nil || len(resp.Messages) == 0 {
		fdk.WriteStatus(out, 500)
		fmt.Fprintf(out, `{"error": "Failed to get message from queue: %v"}`, err)
		return
	}
	msg := resp.Messages[0]

	var order Order
	if err := json.Unmarshal([]byte(*msg.Content), &order); err != nil {
		fdk.WriteStatus(out, 400)
		fmt.Fprintf(out, `{"error": "Invalid order message: %v"}`, err)
		return
	}

	// Process the order (in a real application, you might save to database, send notifications, etc.)
	fmt.Printf("Processing order: %s for customer: %s, amount: %.2f\n",
		order.OrderID, order.CustomerID, order.Amount)

	fdk.WriteStatus(out, 200)
	fmt.Fprintf(out, `{"message": "Order processed successfully", "order_id": "%s"}`, order.OrderID)
}
