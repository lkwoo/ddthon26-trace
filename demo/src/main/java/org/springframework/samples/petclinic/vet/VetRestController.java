// PetClinic (TRACE demo excerpt) — spring-petclinic-rest (Apache-2.0), 데모용 축약.
package org.springframework.samples.petclinic.vet;

import java.util.List;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * REST controller exposing read-only Vet resources.
 */
@RestController
@RequestMapping("/api/vets")
public class VetRestController {

    private final VetService vets;

    public VetRestController(VetService vets) {
        this.vets = vets;
    }

    @GetMapping
    public List<VetDto> listVets() {
        return vets.findAll();
    }

    @GetMapping("/{vetId}")
    public ResponseEntity<VetDto> getVet(@PathVariable int vetId) {
        try {
            return ResponseEntity.ok(vets.findById(vetId));
        } catch (IllegalArgumentException ex) {
            return ResponseEntity.notFound().build();
        }
    }
}
