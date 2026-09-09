// PetClinic (TRACE demo excerpt) — spring-petclinic-rest (Apache-2.0), 데모용 축약.
package org.springframework.samples.petclinic.pet;

import java.util.List;

import jakarta.validation.Valid;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * REST controller exposing Pet resources.
 */
@RestController
@RequestMapping("/api/pets")
public class PetRestController {

    private final PetRepository pets;
    private final PetMapper mapper;

    public PetRestController(PetRepository pets, PetMapper mapper) {
        this.pets = pets;
        this.mapper = mapper;
    }

    @GetMapping
    public List<PetDto> listPets() {
        return pets.findAll().stream().map(mapper::toDto).toList();
    }

    @GetMapping("/{petId}")
    public ResponseEntity<PetDto> getPet(@PathVariable int petId) {
        return pets.findById(petId)
                .map(mapper::toDto)
                .map(ResponseEntity::ok)
                .orElseGet(() -> ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<PetDto> addPet(@Valid @RequestBody PetDto pet) {
        Pet saved = pets.save(mapper.toEntity(pet));
        return ResponseEntity.status(HttpStatus.CREATED).body(mapper.toDto(saved));
    }
}
