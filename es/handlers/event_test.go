package handlers

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/codenotary/immudb/pkg/api/schema"
	"github.com/codenotary/immudb/pkg/client"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"ivansoft.com/corebank/eventsource/store/db"
	"ivansoft.com/corebank/eventsource/store/models"
)

// MockImmuClient is a mock implementation of ImmuClient
type MockImmuClient struct {
	mock.Mock
}

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

func (m *MockImmuClient) WithOptions(options *client.Options) db.ImmuClientInterface {
	args := m.Called(options)
	return args.Get(0).(db.ImmuClientInterface)
}

// MockImmudb is a mock implementation of Immudb
type MockImmudb struct {
	client db.ImmuClientInterface
	ctx    context.Context
}

func NewMockImmudb(client *MockImmuClient) *db.Immudb {
	return &db.Immudb{
		Client: client,
		Ctx:    context.Background(),
	}
}

func (m *MockImmudb) SaveEvent(accountId string, eventJSON []byte) error {
	_, err := m.client.VerifiedSet(context.Background(), []byte(accountId), eventJSON)
	return err
}

func (m *MockImmudb) GetEvent(accountId string) ([]byte, error) {
	entry, err := m.client.VerifiedGet(context.Background(), []byte(accountId))
	if err != nil {
		return nil, err
	}
	return entry.Value, nil
}

// Unit tests
func TestSaveEventHandler(t *testing.T) {
	var testKey = "acc123"
	var expectedValue = []byte(`{"account_id":"acc123","amount":100}`)

	tests := []struct {
		name           string
		requestBody    models.Result
		mockSaveError  error
		mockGetReturn  []byte
		mockGetError   error
		expectedStatus int
	}{
		{
			name: "Success",
			requestBody: models.Result{
				ID:   testKey,
				Data: string(expectedValue),
			},
			mockSaveError:  nil,
			mockGetReturn:  expectedValue,
			mockGetError:   nil,
			expectedStatus: http.StatusOK,
		},
		{
			name: "Save Error",
			requestBody: models.Result{
				ID:   testKey,
				Data: string(expectedValue),
			},
			mockSaveError:  errors.New("save error"),
			mockGetReturn:  nil,
			mockGetError:   nil,
			expectedStatus: http.StatusInternalServerError,
		},
		{
			name: "Get Error",
			requestBody: models.Result{
				ID:   testKey,
				Data: string(expectedValue),
			},
			mockSaveError:  nil,
			mockGetReturn:  nil,
			mockGetError:   errors.New("get error"),
			expectedStatus: http.StatusInternalServerError,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			mockClient := new(MockImmuClient)
			mockImmudb := NewMockImmudb(mockClient)

			// Convert request body to JSON
			body, err := json.Marshal(tt.requestBody)
			assert.NoError(t, err)

			// Create request
			req := httptest.NewRequest(http.MethodPost, "/event", bytes.NewBuffer(body))
			w := httptest.NewRecorder()

			// Set up mock expectations
			if tt.mockSaveError == nil {
				mockClient.On("VerifiedSet", mock.Anything, []byte(testKey), mock.Anything).Return(&schema.TxHeader{Id: 1}, nil)
				if tt.mockGetError == nil {
					mockClient.On("VerifiedGet", mock.Anything, []byte(testKey)).Return(&schema.Entry{Value: expectedValue}, nil)
				} else {
					mockClient.On("VerifiedGet", mock.Anything, []byte(testKey)).Return(&schema.Entry{}, tt.mockGetError)
				}
			} else {
				mockClient.On("VerifiedSet", mock.Anything, []byte(testKey), mock.Anything).Return(nil, tt.mockSaveError)
			}

			// Call handler
			handler := SaveEvent(mockImmudb)
			handler(w, req)

			// Assert response
			assert.Equal(t, tt.expectedStatus, w.Code)
			mockClient.AssertExpectations(t)
		})
	}
}
