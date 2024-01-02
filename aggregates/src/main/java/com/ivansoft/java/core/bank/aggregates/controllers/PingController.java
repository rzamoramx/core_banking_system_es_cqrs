package com.ivansoft.java.core.bank.aggregates.controllers;


import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class PingController {

    @GetMapping(value="/")
    //@RequestMapping(value="/",method=RequestMethod.GET)
    public String ping(){
        return "Pong!";
    }
}
