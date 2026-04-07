package com.scholarshiptracker.backend.service;

import com.scholarshiptracker.backend.domain.entity.Scholarship;
import java.util.List;

public interface ScholarshipService {

    List<Scholarship> findAll();

    Scholarship findById(Long id);

    Scholarship create(Scholarship scholarship);

    Scholarship update(Long id, Scholarship scholarship);

    void delete(Long id);
}
