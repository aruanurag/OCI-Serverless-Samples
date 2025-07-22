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

type Request struct {
	Method string          `json:"method"`
	Data   json.RawMessage `json:"data"`
}

func main() {
	fdk.Handle(fdk.HandlerFunc(myHandler))
}

// myHandler dispatches requests based on the method specified in the request body.
func myHandler(ctx context.Context, in io.Reader, out io.Writer) {
	// Parse the request to get the HTTP method
	var req Request
	if err := json.NewDecoder(in).Decode(&req); err != nil && err != io.EOF {
		log.Printf("failed to parse request: %v", err)
		httpError(out, "Invalid input", 400, err)
		return
	}

	httpCtx, ok := fdk.GetContext(ctx).(fdk.HTTPContext)
	if !ok {
		// optionally, this may be a good idea
		fdk.WriteStatus(out, 400)
		fdk.SetHeader(out, "Content-Type", "application/json")
		io.WriteString(out, `{"error":"function not invoked via http trigger"}`)
		return
	}

	// Get the HTTP method from the request
	httpMethod := httpCtx.RequestMethod()

	client, err := setupNoSQLClient()
	if err != nil {
		log.Printf("%v", err)
		httpError(out, "Internal error", 500, err)
		return
	}
	defer client.Close()

	tableName := getTableName()

	switch httpMethod {
	case "GET":
		handleGetRequest(ctx, req.Data, out, client, tableName)
	case "POST":
		handlePostRequest(ctx, req.Data, out, client, tableName)
	default:
		err := fmt.Errorf("unsupported HTTP method: %s", httpMethod)
		log.Printf("%v", err)
		httpError(out, "Method not allowed", 405, err)
	}
}

// setupNoSQLClient initializes the Oracle NoSQL client with resource principal authentication.
func setupNoSQLClient() (*nosqldb.Client, error) {
	provider, err := iam.NewSignatureProviderWithResourcePrincipal(os.Getenv("COMPARTMENT_ID"))
	if err != nil {
		return nil, fmt.Errorf("failed to create resource principal provider: %w", err)
	}
	cfg := nosqldb.Config{
		Region:                common.Region(os.Getenv("OCI_REGION")),
		AuthorizationProvider: provider,
	}
	client, err := nosqldb.NewClient(cfg)
	if err != nil {
		return nil, fmt.Errorf("failed to create NoSQL client: %w", err)
	}
	return client, nil
}

// getTableName retrieves the table name from environment or returns default.
func getTableName() string {
	tableName := os.Getenv("NOSQL_TABLE_NAME")
	if tableName == "" {
		return "customer_info"
	}
	return tableName
}

// parseGetRequest parses the input for a GET request from the request body.
func parseGetRequest(in []byte) (string, error) {
	var req struct {
		ID string `json:"id"`
	}
	if len(in) > 0 {
		if err := json.Unmarshal(in, &req); err != nil {
			return "", fmt.Errorf("failed to parse input: %w", err)
		}
	}
	if req.ID == "" {
		req.ID = "123" // fallback or default
	}
	return req.ID, nil
}

// parsePostRequest parses the input for a POST request, returning the CustomerInfo.
func parsePostRequest(in []byte) (CustomerInfo, error) {
	var info CustomerInfo
	if err := json.Unmarshal(in, &info); err != nil {
		return CustomerInfo{}, fmt.Errorf("failed to parse input: %w", err)
	}
	if info.ID == "" {
		return CustomerInfo{}, fmt.Errorf("customer ID is required")
	}
	return info, nil
}

// getCustomer retrieves a customer record from the NoSQL database by ID.
func getCustomer(client *nosqldb.Client, tableName, customerID string) (CustomerInfo, error) {
	key := &types.MapValue{}
	key.Put("customerId", customerID)

	getReq := &nosqldb.GetRequest{
		TableName: tableName,
		Key:       key,
	}
	getRes, err := client.Get(getReq)
	if err != nil {
		return CustomerInfo{}, fmt.Errorf("failed to get row: %w", err)
	}
	if !getRes.RowExists() {
		return CustomerInfo{}, fmt.Errorf("customer not found for id: %s", customerID)
	}

	var info CustomerInfo
	b, err := json.Marshal(getRes.Value.Map())
	if err != nil {
		return CustomerInfo{}, fmt.Errorf("failed to marshal result: %w", err)
	}
	if err := json.Unmarshal(b, &info); err != nil {
		return CustomerInfo{}, fmt.Errorf("failed to unmarshal result: %w", err)
	}
	return info, nil
}

// putCustomer inserts or updates a customer record in the NoSQL database.
func putCustomer(client *nosqldb.Client, tableName string, info CustomerInfo) error {
	row := &types.MapValue{}
	row.Put("customerId", info.ID)
	row.Put("id", info.ID)
	row.Put("name", info.Name)
	row.Put("address", info.Address)
	row.Put("email", info.Email)
	row.Put("phone", info.Phone)

	putReq := &nosqldb.PutRequest{
		TableName: tableName,
		Value:     row,
	}
	_, err := client.Put(putReq)
	if err != nil {
		return fmt.Errorf("failed to put row: %w", err)
	}
	return nil
}

// handleGetRequest processes GET requests to retrieve customer data.
func handleGetRequest(ctx context.Context, in []byte, out io.Writer, client *nosqldb.Client, tableName string) {
	customerID, err := parseGetRequest(in)
	if err != nil {
		log.Printf("%v", err)
		httpError(out, "Invalid input", 400, err)
		return
	}

	info, err := getCustomer(client, tableName, customerID)
	if err != nil {
		log.Printf("%v", err)
		if err.Error() == fmt.Sprintf("customer not found for id: %s", customerID) {
			httpError(out, "Customer not found", 404, err)
		} else {
			httpError(out, "Internal error", 500, err)
		}
		return
	}

	writeSuccessResponse(out, info)
}

// handlePostRequest processes POST requests to create or update customer data.
func handlePostRequest(ctx context.Context, in []byte, out io.Writer, client *nosqldb.Client, tableName string) {
	info, err := parsePostRequest(in)
	if err != nil {
		log.Printf("%v", err)
		httpError(out, "Invalid input", 400, err)
		return
	}

	if err := putCustomer(client, tableName, info); err != nil {
		log.Printf("%v", err)
		httpError(out, "Internal error", 500, err)
		return
	}

	writeSuccessResponse(out, map[string]interface{}{
		"message": "Customer created or updated successfully",
		"data":    info,
	})
}

// writeSuccessResponse writes a JSON success response to the output.
func writeSuccessResponse(out io.Writer, data interface{}) {
	if err := json.NewEncoder(out).Encode(data); err != nil {
		log.Printf("failed to write response: %v", err)
	}
}

// httpError writes a JSON error response to the output.
func httpError(out io.Writer, msg string, code int, err error) {
	errMsg := ""
	if err != nil {
		errMsg = err.Error()
	}
	if err := json.NewEncoder(out).Encode(map[string]interface{}{
		"error":   msg,
		"status":  code,
		"details": errMsg,
	}); err != nil {
		log.Printf("failed to write error response: %v", err)
	}
}
