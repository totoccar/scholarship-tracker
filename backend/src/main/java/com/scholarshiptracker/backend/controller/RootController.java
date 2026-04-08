package com.scholarshiptracker.backend.controller;

import java.util.Map;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class RootController {

    @GetMapping("/")
    public Map<String, Object> home() {
        return Map.of(
                "name", "Scholarship Tracker API",
                "status", "ok",
                "version", "v1",
                "endpoints", Map.of(
                        "health", "/actuator/health",
                        "scholarships", "/api/v1/scholarships"
                )
        );
    }
}
