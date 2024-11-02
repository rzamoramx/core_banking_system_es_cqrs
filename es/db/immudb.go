package db

import (
	"context"
	"encoding/json"
	"fmt"
	"strings"

	"github.com/codenotary/immudb/pkg/api/schema"
	immudb "github.com/codenotary/immudb/pkg/client"
	"ivansoft.com/corebank/eventsource/store/models"
)

// ImmuClientInterface defines only the methods we actually use, this is useful for mocking
type ImmuClientInterface interface {
	OpenSession(ctx context.Context, user []byte, pass []byte, database string) error
	CloseSession(ctx context.Context) error
	VerifiedGet(ctx context.Context, key []byte, opts ...immudb.GetOption) (*schema.Entry, error)
	VerifiedSet(ctx context.Context, key []byte, value []byte) (*schema.TxHeader, error)
	WithOptions(options *immudb.Options) ImmuClientInterface
}

type Immudb struct {
	Client ImmuClientInterface //immudb.ImmuClient
	Ctx    context.Context
}

// ImmuClientWrapper wraps the immudb.ImmuClient to implement the ImmuClientInterface
type ImmuClientWrapper struct {
	client immudb.ImmuClient
}

func NewImmuClientWrapper(client immudb.ImmuClient) ImmuClientInterface {
	return &ImmuClientWrapper{client: client}
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

	realClient := immudb.NewClient().WithOptions(opts)
	wrappedClient := NewImmuClientWrapper(realClient)

	err := wrappedClient.OpenSession(ctx, []byte(user), []byte(pwd), database)
	if err != nil {
		return nil, fmt.Errorf("failed to open session: %v", err)
	}

	return &Immudb{
		Client: wrappedClient,
		Ctx:    ctx,
	}, nil

	/*client := immudb.NewClient().WithOptions(opts)

	err := openSession(ctx, client, user, pwd, database)
	if err != nil {
		return nil, fmt.Errorf("failed to open session: %v", err)
	}

	return &Immudb{
		Client: client,
		Ctx:    ctx,
	}, nil*/
}

func (cl *Immudb) Get(req *models.GetRequest) (*models.GetResponse, error) {
	entry, err := cl.Client.VerifiedGet(cl.Ctx, []byte(req.Key))
	if err != nil {
		if strings.Contains(err.Error(), "key not found") {
			return nil, nil
		}

		return nil, fmt.Errorf("failed to get value: %v", err)
	}

	// Ensure the entry is not nil
	if entry == nil {
		return nil, fmt.Errorf("entry is nil")
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

	tx, err := cl.Client.VerifiedSet(cl.Ctx, []byte(req.Key), b)
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
	return cl.Client.CloseSession(cl.Ctx)
}

func (w *ImmuClientWrapper) OpenSession(ctx context.Context, user []byte, pass []byte, database string) error {
	return w.client.OpenSession(ctx, user, pass, database)
}

func (w *ImmuClientWrapper) CloseSession(ctx context.Context) error {
	return w.client.CloseSession(ctx)
}

func (w *ImmuClientWrapper) VerifiedGet(ctx context.Context, key []byte, opts ...immudb.GetOption) (*schema.Entry, error) {
	return w.client.VerifiedGet(ctx, key, opts...)
}

func (w *ImmuClientWrapper) VerifiedSet(ctx context.Context, key []byte, value []byte) (*schema.TxHeader, error) {
	return w.client.VerifiedSet(ctx, key, value)
}

func (w *ImmuClientWrapper) WithOptions(options *immudb.Options) ImmuClientInterface {
	return NewImmuClientWrapper(w.client.WithOptions(options))
}

/*func openSession(ctx context.Context,
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
}*/
