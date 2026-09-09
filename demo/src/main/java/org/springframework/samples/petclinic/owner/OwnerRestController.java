package org.springframework.samples.petclinic.owner;

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
 * REST controller for Owner Management (TRACE demo excerpt).
 * 원본: spring-petclinic-rest (Apache-2.0), 데모용으로 축약·개변.
 */
@RestController
@RequestMapping("/owners")
public class OwnerRestController {

    private final OwnerRepository owners;

    public OwnerRestController(OwnerRepository owners) {
        this.owners = owners;
    }

    @GetMapping
    public List<OwnerDto> listOwners() {
        return owners.findAllDtos();
    }

    @GetMapping("/{ownerId}")
    public ResponseEntity<OwnerDto> getOwner(@PathVariable int ownerId) {
        OwnerDto dto = owners.findDtoById(ownerId);
        if (dto == null) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(dto);
    }

    @PostMapping
    public ResponseEntity<OwnerDto> addOwner(@Valid @RequestBody OwnerDto owner) {
        OwnerDto saved = owners.save(owner);
        return ResponseEntity.status(HttpStatus.CREATED).body(saved);
    }
}
