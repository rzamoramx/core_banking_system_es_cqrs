package com.ivansoft.core.bank.account.models;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.io.Serializable;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class Transaction implements Serializable {
    private String id;
    private String accountId;
    private Double amount;
    private TransactionType type;
    private String status;
    private String description;
}
