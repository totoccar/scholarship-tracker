package com.scholarshiptracker.backend.config;

import com.scholarshiptracker.backend.domain.entity.Scholarship;
import com.scholarshiptracker.backend.service.ScholarshipService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Profile;

import java.time.LocalDate;
import java.util.List;

@Slf4j
@Configuration
@RequiredArgsConstructor
@Profile("!prod") // Esto evita que se ejecute en producción (el "!" significa NOT prod)
public class DataLoader implements CommandLineRunner {

    private final ScholarshipService scholarshipService;

    @Override
    public void run(String... args) {
        log.info("Verificando existencia de datos iniciales...");
        
        if (scholarshipService.findAll().isEmpty()) {
            log.info("Base de datos vacía. Insertando becas de prueba...");

            Scholarship s1 = Scholarship.builder()
                .title("Beca Fundación Carolina")
                .description("Becas para estudios de postgrado en España.")
                .provider("Fundación Carolina")
                .deadline(LocalDate.now().plusMonths(3))
                .url("https://www.fundacioncarolina.es/becas")
                .tags(List.of("España", "Postgrado", "Sistemas"))
                .build();

            Scholarship s2 = Scholarship.builder()
                .title("Fullbright Scholarship")
                .description("Becas para investigación y maestría en EEUU.")
                .provider("Fullbright")
                .deadline(LocalDate.now().plusMonths(6))
                .url("https://fullbright.edu.ar")
                .tags(List.of("EEUU", "Investigación", "Sistemas"))
                .build();

            scholarshipService.save(s1);
            scholarshipService.save(s2);
            
            log.info(">> Dos becas de prueba han sido cargadas exitosamente.");
        } else {
            log.info("La base de datos ya contiene información. Omitiendo carga inicial.");
        }
    }
}