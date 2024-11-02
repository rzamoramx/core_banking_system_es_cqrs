package db

import (
	"context"
	"encoding/json"
	"testing"

	"github.com/codenotary/immudb/pkg/api/schema"
	"github.com/codenotary/immudb/pkg/client"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"ivansoft.com/corebank/eventsource/store/models"
)

// MockImmuClient is a mock implementation of ImmuClient
type MockImmuClient struct {
	mock.Mock
}

// Methods we use in our tests
func (m *MockImmuClient) OpenSession(ctx context.Context, user []byte, pass []byte, database string) error {
	args := m.Called(ctx, user, pass, database)
	return args.Error(0)
}

func (m *MockImmuClient) CloseSession(ctx context.Context) error {
	args := m.Called(ctx)
	return args.Error(0)
}

func (m *MockImmuClient) VerifiedGet(ctx context.Context, key []byte, opts ...client.GetOption) (*schema.Entry, error) {
	args := m.Called(ctx, key)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*schema.Entry), args.Error(1)
}

func (m *MockImmuClient) VerifiedSet(ctx context.Context, key []byte, value []byte) (*schema.TxHeader, error) {
	args := m.Called(ctx, key, value)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*schema.TxHeader), args.Error(1)
}

func (m *MockImmuClient) WithOptions(options *client.Options) ImmuClientInterface {
	args := m.Called(options)
	return args.Get(0).(ImmuClientInterface)
}

// Unit tests
func TestNewImmudb(t *testing.T) {
	mockClient := new(MockImmuClient)
	mockClient.On("WithOptions", mock.Anything).Return(mockClient)
	mockClient.On("OpenSession", mock.Anything, []byte("immudb"), []byte("immudb1"), "defaultdb").Return(nil)

	db, err := NewImmudb("localhost", 3322, "immudb", "immudb1", "defaultdb")

	assert.NoError(t, err)
	assert.NotNil(t, db)
}

func TestSet(t *testing.T) {
	mockClient := new(MockImmuClient)
	db := &Immudb{
		Client: mockClient,
		Ctx:    context.Background(),
	}

	testKey := "testKey"
	testValue := map[string]string{"test": "value"}
	expectedJSON, _ := json.Marshal(testValue)

	mockClient.On("VerifiedSet", mock.Anything, []byte(testKey), expectedJSON).Return(&schema.TxHeader{Id: 1}, nil)

	id, err := db.Set(&models.SetRequest{
		Key:   testKey,
		Value: testValue,
	})

	assert.NoError(t, err)
	assert.Equal(t, 1, id)
	mockClient.AssertExpectations(t)
}

func TestGet(t *testing.T) {
	mockClient := new(MockImmuClient)
	db := &Immudb{
		Client: mockClient,
		Ctx:    context.Background(),
	}

	testKey := "testKey"
	expectedValue := []byte("testValue")

	mockClient.On("VerifiedGet", mock.Anything, []byte(testKey)).Return(&schema.Entry{Value: expectedValue}, nil)

	resp, err := db.Get(&models.GetRequest{
		Key: testKey,
	})

	assert.NoError(t, err)
	assert.Equal(t, expectedValue, resp.Data)
	mockClient.AssertExpectations(t)
}

func TestSaveEvent(t *testing.T) {
	mockClient := new(MockImmuClient)
	db := &Immudb{
		Client: mockClient,
		Ctx:    context.Background(),
	}

	accountID := "test123"
	eventJSON := []byte(`{"account_id":"test123","amount":100}`)

	mockClient.On("VerifiedSet", mock.Anything, []byte(accountID), eventJSON).Return(&schema.TxHeader{Id: 1}, nil)

	err := db.SaveEvent(accountID, eventJSON)

	assert.NoError(t, err)
	mockClient.AssertExpectations(t)
}

func TestGetEvent(t *testing.T) {
	mockClient := new(MockImmuClient)
	db := &Immudb{
		Client: mockClient,
		Ctx:    context.Background(),
	}

	accountID := "test123"
	expectedEvent := []byte(`{"account_id":"test123","amount":100}`)

	mockClient.On("VerifiedGet", mock.Anything, []byte(accountID)).Return(&schema.Entry{Value: expectedEvent}, nil)

	event, err := db.GetEvent(accountID)

	assert.NoError(t, err)
	assert.Equal(t, expectedEvent, event)
	mockClient.AssertExpectations(t)
}

func TestClose(t *testing.T) {
	mockClient := new(MockImmuClient)
	db := &Immudb{
		Client: mockClient,
		Ctx:    context.Background(),
	}

	mockClient.On("CloseSession", mock.Anything).Return(nil)

	err := db.Close()

	assert.NoError(t, err)
	mockClient.AssertExpectations(t)
}
