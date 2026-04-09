package com.scholarshiptracker.backend.repository;

import com.scholarshiptracker.backend.domain.entity.Scholarship;
import com.scholarshiptracker.backend.domain.entity.ScholarshipStatus;
import java.util.List;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface ScholarshipRepository extends JpaRepository<Scholarship, Long> {

	boolean existsByUrl(String url);

	List<Scholarship> findByStatusOrStatusIsNullOrderByDeadlineAsc(ScholarshipStatus status);

	List<Scholarship> findByStatusInOrStatusIsNullOrderByDeadlineAsc(List<ScholarshipStatus> statuses);

    Page<Scholarship> findByCountryContainingIgnoreCase(String country, Pageable pageable);
}
