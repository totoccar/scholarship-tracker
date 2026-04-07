package com.scholarshiptracker.backend.controller;

import com.scholarshiptracker.backend.domain.entity.Scholarship;
import com.scholarshiptracker.backend.service.ScholarshipService;
import jakarta.validation.Valid;
import java.net.URI;
import java.util.List;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.support.ServletUriComponentsBuilder;

@RestController
@RequestMapping("/api/v1/scholarships")
@RequiredArgsConstructor
public class ScholarshipController {

    private final ScholarshipService scholarshipService;

    @GetMapping
    public ResponseEntity<List<Scholarship>> getAll() {
        return ResponseEntity.ok(scholarshipService.findAll());
    }

    @GetMapping("/{id}")
    public ResponseEntity<Scholarship> getById(@PathVariable Long id) {
        return ResponseEntity.ok(scholarshipService.findById(id));
    }

    @PostMapping
    public ResponseEntity<Scholarship> create(@Valid @RequestBody Scholarship scholarship) {
        Scholarship created = scholarshipService.create(scholarship);
        URI location = ServletUriComponentsBuilder.fromCurrentRequest()
                .path("/{id}")
                .buildAndExpand(created.getId())
                .toUri();
        return ResponseEntity.created(location).body(created);
    }

    @PutMapping("/{id}")
    public ResponseEntity<Scholarship> update(@PathVariable Long id, @Valid @RequestBody Scholarship scholarship) {
        return ResponseEntity.ok(scholarshipService.update(id, scholarship));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        scholarshipService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
