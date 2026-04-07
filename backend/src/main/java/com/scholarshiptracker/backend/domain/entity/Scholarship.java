package com.scholarshiptracker.backend.domain.entity;

import jakarta.persistence.CollectionTable;
import jakarta.persistence.Column;
import jakarta.persistence.ElementCollection;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;
import jakarta.validation.constraints.FutureOrPresent;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(
    name = "scholarships",
    uniqueConstraints = @UniqueConstraint(name = "uk_scholarships_url", columnNames = "url")
)
public class Scholarship {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotBlank
    @Size(max = 150)
    @Column(nullable = false, length = 150)
    private String title;

    @NotBlank
    @Size(max = 5000)
    @Column(nullable = false, length = 5000)
    private String description;

    @NotBlank
    @Size(max = 150)
    @Column(nullable = false, length = 150)
    private String provider;

    @NotNull
    @FutureOrPresent
    @Column(nullable = false)
    private LocalDate deadline;

    @NotBlank
    @Pattern(regexp = "^(https?://).+", message = "URL must start with http:// or https://")
    @Column(nullable = false, length = 500, unique = true)
    private String url;

    @ElementCollection(fetch = FetchType.EAGER)
    @CollectionTable(name = "scholarship_tags", joinColumns = @JoinColumn(name = "scholarship_id"))
    @Column(name = "tag", length = 50)
    @Builder.Default
    @Size(max = 15)
    private List<@NotBlank @Size(max = 50) String> tags = new ArrayList<>();
}
