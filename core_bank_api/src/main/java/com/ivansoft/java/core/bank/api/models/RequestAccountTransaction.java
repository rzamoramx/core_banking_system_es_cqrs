package com.ivansoft.java.core.bank.api.models;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class RequestAccountTransaction {
    @JsonProperty("account_id")
    private String accountId;

    @JsonProperty("amount")
    private Double amount;

    @JsonProperty("transaction_type")
    private TransactionType transactionType;
}

