package com.ivansoft.java.core.bank.aggregates.services;

import com.ivansoft.core.bank.account.models.Transaction;
import com.ivansoft.core.bank.account.models.TransactionType;
import io.dapr.client.DaprClient;
import io.dapr.client.DaprClientBuilder;
import io.dapr.client.domain.CloudEvent;
import io.dapr.client.domain.PublishEventRequest;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.MockedConstruction;
import org.mockito.MockitoAnnotations;
import reactor.core.publisher.Mono;

import java.util.Date;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

class EventSourceServiceTest {

    @Mock
    private DaprClient daprClient;

    private EventSourceService eventSourceService;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
        when(daprClient.publishEvent(any(PublishEventRequest.class))).thenReturn(Mono.empty());
        eventSourceService = new EventSourceService();
    }

    @Test
    void testSuccessfulEventPublishing() throws Exception {
        // Arrange
        Transaction transaction = new Transaction(
            UUID.randomUUID().toString(),
            "test-account",
            100.0,
            TransactionType.DEPOSIT,
            "completed",
            "Test transaction",
            new Date(),
            1
        );

        try (MockedConstruction<DaprClientBuilder> ignored = mockConstruction(DaprClientBuilder.class,
                (mock, context) -> when(mock.build()).thenReturn(daprClient))) {

            // Act
            eventSourceService.publishTransaction(transaction);

            // Assert
            ArgumentCaptor<PublishEventRequest> requestCaptor = ArgumentCaptor.forClass(PublishEventRequest.class);
            verify(daprClient).publishEvent(requestCaptor.capture());

            PublishEventRequest capturedRequest = requestCaptor.getValue();
            assertEquals("eventsource", capturedRequest.getPubsubName());
            assertEquals("transactions", capturedRequest.getTopic());

            CloudEvent<?> cloudEvent = (CloudEvent<?>) capturedRequest.getData();
            assertNotNull(cloudEvent.getId());
            assertEquals("transaction.v1", cloudEvent.getType());
            assertEquals("1", cloudEvent.getSpecversion());
            assertEquals("application/json", cloudEvent.getDatacontenttype());
            assertNotNull(cloudEvent.getData());
        }
    }

    @Test
    void testEventPublishingWithNullTransaction() {
        // Arrange
        Transaction transaction = null;

        try (MockedConstruction<DaprClientBuilder> ignored = mockConstruction(DaprClientBuilder.class,
                (mock, context) -> when(mock.build()).thenReturn(daprClient))) {

            // Act & Assert
            Exception exception = assertThrows(Exception.class, () -> {
                eventSourceService.publishTransaction(transaction);
            });
            assertInstanceOf(NullPointerException.class, exception);
        }
    }

    @Test
    void testEventPublishingWithDaprClientFailure() {
        // Arrange
        Transaction transaction = new Transaction(
            UUID.randomUUID().toString(),
            "test-account",
            100.0,
            TransactionType.DEPOSIT,
            "completed",
            "Test transaction",
            new Date(),
            1
        );

        when(daprClient.publishEvent(any(PublishEventRequest.class)))
            .thenReturn(Mono.error(new RuntimeException("Dapr client error")));

        try (MockedConstruction<DaprClientBuilder> mocked = mockConstruction(DaprClientBuilder.class,
                (mock, context) -> when(mock.build()).thenReturn(daprClient))) {

            // Act & Assert
            Exception exception = assertThrows(Exception.class, () -> {
                eventSourceService.publishTransaction(transaction);
            });
            assertTrue(exception.getMessage().contains("Dapr client error"));
        }
    }

    @Test
    void testCloudEventMetadata() throws Exception {
        // Arrange
        Transaction transaction = new Transaction(
            UUID.randomUUID().toString(),
            "test-account",
            100.0,
            TransactionType.DEPOSIT,
            "completed",
            "Test transaction",
            new Date(),
            1
        );

        try (MockedConstruction<DaprClientBuilder> mocked = mockConstruction(DaprClientBuilder.class,
                (mock, context) -> when(mock.build()).thenReturn(daprClient))) {

            // Act
            eventSourceService.publishTransaction(transaction);

            // Assert
            ArgumentCaptor<PublishEventRequest> requestCaptor = ArgumentCaptor.forClass(PublishEventRequest.class);
            verify(daprClient).publishEvent(requestCaptor.capture());

            PublishEventRequest capturedRequest = requestCaptor.getValue();
            assertEquals("3600", capturedRequest.getMetadata().get("ttlInSeconds"));
            assertEquals(CloudEvent.CONTENT_TYPE, capturedRequest.getContentType());
        }
    }
}
