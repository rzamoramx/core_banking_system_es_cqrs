package db

import (
	"context"
	"encoding/json"
	"fmt"

	immudb "github.com/codenotary/immudb/pkg/client"
	"ivansoft.com/corebank/eventsource/store/models"
)

type Immudb struct {
	client immudb.ImmuClient
	ctx    context.Context
}

func NewImmudb(host string,
	port int,
	user string,
	pwd string,
	database string) (*Immudb, error) {
	ctx := context.Background()
	opts := immudb.DefaultOptions().
		WithAddress(host).
		WithPort(port)

	client := immudb.NewClient().WithOptions(opts)
	err := openSession(ctx, client, user, pwd, database)
	if err != nil {
		return nil, fmt.Errorf("failed to open session: %v", err)
	}

	return &Immudb{
		client: client,
		ctx:    ctx,
	}, nil
}

func (cl *Immudb) Get(req *models.GetRequest) (*models.GetResponse, error) {
	entry, err := cl.client.VerifiedGet(cl.ctx, []byte(req.Key))
	if err != nil {
		return nil, fmt.Errorf("failed to get value: %v", err)
	}

	return &models.GetResponse{
		Data: entry.Value,
	}, nil
}

func (cl *Immudb) Set(req *models.SetRequest) (int, error) {
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

	tx, err := cl.client.VerifiedSet(cl.ctx, []byte(req.Key), b)
	if err != nil {
		return 0, fmt.Errorf("failed to set value: %v", err)
	}

	return int(tx.Id), nil
}

func (cl *Immudb) SaveEvent(accountId string, eventJSON []byte) error {
	_, err := cl.Set(&models.SetRequest{
		Key:   accountId,
		Value: eventJSON,
	})
	return err
}

func (cl *Immudb) GetEvent(accountId string) ([]byte, error) {
	resp, err := cl.Get(&models.GetRequest{
		Key: accountId,
	})
	if err != nil {
		return nil, err
	}
	return resp.Data, nil
}

func (cl *Immudb) Close() error {
	return cl.client.CloseSession(cl.ctx)
}

func openSession(ctx context.Context,
	client immudb.ImmuClient,
	user string,
	pwd string,
	database string) error {
	return client.OpenSession(
		ctx,
		[]byte(user),
		[]byte(pwd),
		database,
	)
}
