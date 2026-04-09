package com.scholarshiptracker.backend.service.impl;

import com.scholarshiptracker.backend.domain.entity.Scholarship;
import com.scholarshiptracker.backend.domain.entity.ScholarshipStatus;
import com.scholarshiptracker.backend.repository.ScholarshipRepository;
import com.scholarshiptracker.backend.service.ScholarshipService;
import java.util.Arrays;
import java.util.List;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class ScholarshipServiceImpl implements ScholarshipService {

    private final ScholarshipRepository scholarshipRepository;

    @Override
    public List<Scholarship> findAll() {
        return scholarshipRepository.findByStatusInOrStatusIsNullOrderByDeadlineAsc(
                Arrays.asList(ScholarshipStatus.APPROVED, ScholarshipStatus.REVIEW)
        );
    }

    @Override
    public Page<Scholarship> searchByCountry(String country, int page, int size) {
        Pageable pageable = PageRequest.of(page, size, Sort.by("deadline").ascending());
        if (country == null || country.isBlank()) {
            return scholarshipRepository.findAll(pageable);
        }
        return scholarshipRepository.findByCountryContainingIgnoreCase(country.trim(), pageable);
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
        scholarship.setCountry(normalizeCountry(scholarship.getCountry()));
        if (scholarship.getStatus() == null) {
            scholarship.setStatus(ScholarshipStatus.PENDING);
        }
        if (scholarship.getBenefits() == null) {
            scholarship.setBenefits("");
        }
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
        existing.setCountry(normalizeCountry(scholarship.getCountry()));
        existing.setDeadline(scholarship.getDeadline());
        existing.setUrl(normalizedUrl);
        existing.setStatus(scholarship.getStatus() == null ? ScholarshipStatus.PENDING : scholarship.getStatus());
        existing.setBenefits(scholarship.getBenefits() == null ? "" : scholarship.getBenefits());
        existing.setLogoUrl(scholarship.getLogoUrl());
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

    private String normalizeCountry(String country) {
        if (country == null || country.isBlank()) {
            return "Global";
        }
        return country.trim();
    }
}
