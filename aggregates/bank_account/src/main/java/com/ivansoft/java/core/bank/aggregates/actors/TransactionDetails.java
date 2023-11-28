package com.ivansoft.java.core.bank.aggregates.actors;

import com.ivansoft.java.core.bank.api.models.TransactionType;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;


@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class TransactionDetails {
    private TransactionType type;
    private Double amount;
}
