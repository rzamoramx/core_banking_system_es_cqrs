package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"

	immudb "github.com/codenotary/immudb/pkg/client"
)

var (
	client immudb.ImmuClient = nil
)

type SetRequest struct {
	Key         string            `json:"key"`
	Value       any               `json:"value"`
	ETag        *string           `json:"etag,omitempty"`
	Metadata    map[string]string `json:"metadata,omitempty"`
	ContentType *string           `json:"contentType,omitempty"`
}

type GetRequest struct {
	Key      string            `json:"key"`
	Metadata map[string]string `json:"metadata"`
}

type GetResponse struct {
	Data        []byte            `json:"data"`
	ETag        *string           `json:"etag,omitempty"`
	Metadata    map[string]string `json:"metadata"`
	ContentType *string           `json:"contentType,omitempty"`
}

func main() {
	opts := immudb.DefaultOptions().
		WithAddress("localhost").
		WithPort(3322)

	client = immudb.NewClient().WithOptions(opts)
	err := client.OpenSession(
		context.Background(),
		[]byte(`immudb`),
		[]byte(`immudb1`),
		"eventsourcedb",
	)
	if err != nil {
		log.Fatal(err)
	}

	defer client.CloseSession(context.Background())

	fmt.Println("getting data...")
	resp, err := Get(context.Background(), &GetRequest{
		Key: "BCD987a",
	})
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("%s\n", string(resp.Data))
}

func Get(ctx context.Context, req *GetRequest) (*GetResponse, error) {
	entry, err := client.VerifiedGet(ctx, []byte(req.Key))
	if err != nil {
		return nil, fmt.Errorf("failed to get value: %v", err)
	}

	return &GetResponse{
		Data: entry.Value,
	}, nil
}

func Set(ctx context.Context, req *SetRequest) (int, error) {
	var b []byte
	var err error

	if byteSlice, ok := req.Value.([]byte); ok {
		// Special handling for []byte to avoid unnecessary encoding
		b = byteSlice
	} else {
		// Use json.Marshal for all other types
		b, err = json.Marshal(req.Value)
		if err != nil {
			return 0, fmt.Errorf("failed to marshal value: %v", err)
		}
	}

	fmt.Printf("key: %s\n", req.Key)
	fmt.Printf("original value: %#v\n", req.Value)
	fmt.Printf("JSON-encoded value: %s\n", string(b))

	tx, err := client.VerifiedSet(ctx, []byte(req.Key), b)
	if err != nil {
		return 0, fmt.Errorf("failed to set value: %v", err)
	}
	fmt.Printf("tx: %d\n\n", tx.Id)

	return 0, nil
}
