package com.ivansoft.java.core.bank.aggregates.controllers;

import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.GetMapping;

@RestController
public class PingController {
    @GetMapping(value="/")
    public String ping(){
        return "Pong!";
    }
}
