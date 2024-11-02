package com.ivansoft.core.bank.api.controllers;

import com.ivansoft.core.bank.account.models.TransactionType;
import com.ivansoft.core.bank.api.actors.BankAccountActorClient;
import com.ivansoft.core.bank.api.models.RequestAccountTransaction;
import com.ivansoft.core.bank.api.models.Response;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.util.ReflectionTestUtils;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyDouble;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class BankAccountControllerTest {

    @Mock
    private BankAccountActorClient bankAccountActorClient;

    @InjectMocks
    private BankAccountController bankAccountController;

    @BeforeEach
    void setUp() {
        ReflectionTestUtils.setField(bankAccountController, "bankAccountActorClient", bankAccountActorClient);
    }

    @Test
    void createTransaction_Success() {
        // Arrange
        RequestAccountTransaction request = new RequestAccountTransaction(
            "test-account",
            100.0,
            TransactionType.DEPOSIT
        );
        when(bankAccountActorClient.doTransaction(
            anyString(),
            any(TransactionType.class),
            anyDouble()
        )).thenReturn("Transaction processed");

        // Act
        Response response = bankAccountController.createTransaction(request);

        // Assert
        assertNotNull(response);
        assertEquals("OK", response.getStatus());
        assertEquals("Transaction created", response.getMessage());
        verify(bankAccountActorClient).doTransaction(
            request.getAccountId(),
            request.getTransactionType(),
            request.getAmount()
        );
    }

    @Test
    void createTransaction_Error() {
        // Arrange
        RequestAccountTransaction request = new RequestAccountTransaction(
            "test-account",
            100.0,
            TransactionType.DEPOSIT
        );
        when(bankAccountActorClient.doTransaction(
            anyString(),
            any(TransactionType.class),
            anyDouble()
        )).thenThrow(new RuntimeException("Transaction failed"));

        // Act
        Response response = bankAccountController.createTransaction(request);

        // Assert
        assertNotNull(response);
        assertEquals("ERROR", response.getStatus());
        assertEquals("Error creating transaction", response.getMessage());
        verify(bankAccountActorClient).doTransaction(
            request.getAccountId(),
            request.getTransactionType(),
            request.getAmount()
        );
    }

    @Test
    void createTransaction_NullRequest() {
        // Act
        Response response = bankAccountController.createTransaction(null);

        // Assert
        assertNotNull(response);
        assertEquals("ERROR", response.getStatus());
        assertEquals("Error creating transaction", response.getMessage());
        verifyNoInteractions(bankAccountActorClient);
    }

    @Test
    void createTransaction_InvalidAmount() {
        // Arrange
        RequestAccountTransaction request = new RequestAccountTransaction(
            "test-account",
            -100.0,  // negative amount
            TransactionType.DEPOSIT
        );

        // Act
        Response response = bankAccountController.createTransaction(request);

        // Assert
        assertNotNull(response);
        verify(bankAccountActorClient).doTransaction(
            request.getAccountId(),
            request.getTransactionType(),
            request.getAmount()
        );
    }

    @Test
    void createTransaction_MissingFields() {
        // Arrange
        RequestAccountTransaction request = new RequestAccountTransaction();
        // All fields are null

        // Act
        Response response = bankAccountController.createTransaction(request);

        // Assert
        assertNotNull(response);
        verify(bankAccountActorClient).doTransaction(
            null,
            null,
            null
        );
    }
}
