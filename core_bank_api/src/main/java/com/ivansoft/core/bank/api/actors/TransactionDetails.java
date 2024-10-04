package com.ivansoft.core.bank.api.actors;

import com.ivansoft.core.bank.account.models.TransactionType;
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
