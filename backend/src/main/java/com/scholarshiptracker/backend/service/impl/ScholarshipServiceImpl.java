package com.scholarshiptracker.backend.service.impl;

import com.scholarshiptracker.backend.domain.entity.Scholarship;
import com.scholarshiptracker.backend.repository.ScholarshipRepository;
import com.scholarshiptracker.backend.service.ScholarshipService;
import java.util.List;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class ScholarshipServiceImpl implements ScholarshipService {

    private final ScholarshipRepository scholarshipRepository;

    @Override
    public List<Scholarship> findAll() {
        return scholarshipRepository.findAll();
    }

    @Override
    public Scholarship findById(Long id) {
        return scholarshipRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Scholarship not found with id: " + id));
    }

    @Override
    public Scholarship create(Scholarship scholarship) {
        String normalizedUrl = normalizeUrl(scholarship.getUrl());
        if (scholarshipRepository.existsByUrl(normalizedUrl)) {
            throw new IllegalArgumentException("Scholarship already exists with url: " + normalizedUrl);
        }

        scholarship.setId(null);
        scholarship.setUrl(normalizedUrl);
        return scholarshipRepository.save(scholarship);
    }

    @Override
    public Scholarship update(Long id, Scholarship scholarship) {
        Scholarship existing = findById(id);
        String normalizedUrl = normalizeUrl(scholarship.getUrl());
        if (!existing.getUrl().equals(normalizedUrl) && scholarshipRepository.existsByUrl(normalizedUrl)) {
            throw new IllegalArgumentException("Scholarship already exists with url: " + normalizedUrl);
        }

        existing.setTitle(scholarship.getTitle());
        existing.setDescription(scholarship.getDescription());
        existing.setProvider(scholarship.getProvider());
        existing.setDeadline(scholarship.getDeadline());
        existing.setUrl(normalizedUrl);
        existing.setTags(scholarship.getTags());
        return scholarshipRepository.save(existing);
    }

    @Override
    public void delete(Long id) {
        Scholarship existing = findById(id);
        scholarshipRepository.delete(existing);
    }

    private String normalizeUrl(String url) {
        if (url == null) {
            return null;
        }
        return url.trim();
    }
}
