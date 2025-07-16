package main

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"os"

	fdk "github.com/fnproject/fdk-go"
	"github.com/oracle/nosql-go-sdk/nosqldb"
	"github.com/oracle/nosql-go-sdk/nosqldb/auth/iam"
	"github.com/oracle/nosql-go-sdk/nosqldb/common"
	"github.com/oracle/nosql-go-sdk/nosqldb/types"
)

type CustomerInfo struct {
	ID      string `json:"id"`
	Name    string `json:"name"`
	Address string `json:"address"`
	Email   string `json:"email"`
	Phone   string `json:"phone"`
}

func main() {
	fdk.Handle(fdk.HandlerFunc(myHandler))
}

func myHandler(ctx context.Context, in io.Reader, out io.Writer) {
	// Parse input for customer ID
	var req struct {
		ID string `json:"id"`
	}
	_ = json.NewDecoder(in).Decode(&req)
	if req.ID == "" {
		req.ID = "123" // fallback or default
	}

	// Set up NoSQL client using resource principal (for OCI Functions)
	provider, err := iam.NewSignatureProviderWithResourcePrincipal(os.Getenv("COMPARTMENT_ID"))
	if err != nil {
		errWrap := fmt.Errorf("failed to create resource principal provider: %w", err)
		log.Printf("%v", errWrap)
		httpError(out, "Internal error", 500, errWrap)
		return
	}
	cfg := nosqldb.Config{
		Region:                common.Region(os.Getenv("OCI_REGION")),
		AuthorizationProvider: provider,
	}
	client, err := nosqldb.NewClient(cfg)
	if err != nil {
		errWrap := fmt.Errorf("failed to create NoSQL client: %w", err)
		log.Printf("%v", errWrap)
		httpError(out, "Internal error", 500, errWrap)
		return
	}
	defer client.Close()

	// Build the primary key
	key := &types.MapValue{}
	key.Put("customerId", req.ID)

	// Read from the table
	tableName := os.Getenv("NOSQL_TABLE_NAME")
	if tableName == "" {
		tableName = "customer_info" // fallback to default
	}
	getReq := &nosqldb.GetRequest{
		TableName: tableName,
		Key:       key,
	}
	getRes, err := client.Get(getReq)
	if err != nil {
		errWrap := fmt.Errorf("failed to get row: %w", err)
		log.Printf("%v", errWrap)
		httpError(out, "Internal error", 500, errWrap)
		return
	}
	if !getRes.RowExists() {
		errWrap := fmt.Errorf("customer not found for id: %s", req.ID)
		log.Printf("%v", errWrap)
		httpError(out, "Customer not found", 404, errWrap)
		return
	}

	// Map result to struct
	var info CustomerInfo
	b, _ := json.Marshal(getRes.Value.Map())
	_ = json.Unmarshal(b, &info)

	json.NewEncoder(out).Encode(info)
}

func httpError(out io.Writer, msg string, code int, err error) {
	errMsg := ""
	if err != nil {
		errMsg = err.Error()
	}
	json.NewEncoder(out).Encode(map[string]interface{}{
		"error":   msg,
		"status":  code,
		"details": errMsg,
	})
}
