package com.scholarshiptracker.backend.config;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.ApplicationRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.jdbc.core.JdbcTemplate;

@Slf4j
@Configuration
@RequiredArgsConstructor
public class SchemaRepairConfig {

    private final JdbcTemplate jdbcTemplate;

    @Bean
    public ApplicationRunner schemaRepairRunner() {
        return args -> {
            // Defensive patch for legacy databases where Hibernate update did not add new columns.
            jdbcTemplate.execute("ALTER TABLE scholarships ADD COLUMN IF NOT EXISTS status VARCHAR(20)");
            jdbcTemplate.execute("ALTER TABLE scholarships ADD COLUMN IF NOT EXISTS benefits VARCHAR(500)");
            jdbcTemplate.execute("ALTER TABLE scholarships ADD COLUMN IF NOT EXISTS logo_url VARCHAR(500)");

            jdbcTemplate.execute("UPDATE scholarships SET status = 'PENDING' WHERE status IS NULL");
            jdbcTemplate.execute("UPDATE scholarships SET benefits = '' WHERE benefits IS NULL");

            jdbcTemplate.execute(
                    "CREATE TABLE IF NOT EXISTS scholarship_tags (" +
                            "scholarship_id BIGINT NOT NULL, " +
                            "tag VARCHAR(50)" +
                            ")"
            );

            jdbcTemplate.execute(
                    "DO $$ BEGIN " +
                            "IF NOT EXISTS (" +
                            "SELECT 1 FROM pg_constraint WHERE conname = 'fk_scholarship_tags_scholarship'" +
                            ") THEN " +
                            "ALTER TABLE scholarship_tags " +
                            "ADD CONSTRAINT fk_scholarship_tags_scholarship " +
                            "FOREIGN KEY (scholarship_id) REFERENCES scholarships(id); " +
                            "END IF; " +
                            "END $$"
            );

            log.info("Schema repair check completed");
        };
    }
}