// PetClinic (TRACE demo excerpt) — spring-petclinic-rest (Apache-2.0), 데모용 축약.
package org.springframework.samples.petclinic.visit;

import java.util.List;

import jakarta.validation.Valid;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/**
 * REST controller exposing Visit resources.
 */
@RestController
@RequestMapping("/api/visits")
public class VisitRestController {

    private final VisitRepository visits;
    private final VisitMapper mapper;

    public VisitRestController(VisitRepository visits, VisitMapper mapper) {
        this.visits = visits;
        this.mapper = mapper;
    }

    @GetMapping
    public List<VisitDto> listVisits(@RequestParam(required = false) Integer petId) {
        List<Visit> found = (petId == null) ? visits.findAll() : visits.findByPetId(petId);
        return found.stream().map(mapper::toDto).toList();
    }

    @GetMapping("/{visitId}")
    public ResponseEntity<VisitDto> getVisit(@PathVariable int visitId) {
        return visits.findById(visitId)
                .map(mapper::toDto)
                .map(ResponseEntity::ok)
                .orElseGet(() -> ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<VisitDto> addVisit(@Valid @RequestBody VisitDto visit) {
        Visit saved = visits.save(mapper.toEntity(visit));
        return ResponseEntity.status(HttpStatus.CREATED).body(mapper.toDto(saved));
    }
}
