package com.scholarshiptracker.backend.service;

import com.scholarshiptracker.backend.domain.entity.Scholarship;
import org.springframework.data.domain.Page;
import java.util.List;

public interface ScholarshipService {

    List<Scholarship> findAll();

    Page<Scholarship> searchByCountry(String country, int page, int size);

    Scholarship findById(Long id);

    Scholarship create(Scholarship scholarship);

    Scholarship update(Long id, Scholarship scholarship);

    void delete(Long id);
}
