// PetClinic (TRACE demo excerpt) — spring-petclinic-rest (Apache-2.0), 데모용 축약.
package org.springframework.samples.petclinic.vet;

import java.util.List;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * Application service for Vet lookups.
 */
@Service
public class VetService {

    private final VetRepository vets;
    private final VetMapper mapper;

    public VetService(VetRepository vets, VetMapper mapper) {
        this.vets = vets;
        this.mapper = mapper;
    }

    @Transactional(readOnly = true)
    public List<VetDto> findAll() {
        return vets.findAll().stream().map(mapper::toDto).toList();
    }

    @Transactional(readOnly = true)
    public VetDto findById(int vetId) {
        Vet vet = vets.findById(vetId)
                .orElseThrow(() -> new IllegalArgumentException("Vet not found: " + vetId));
        return mapper.toDto(vet);
    }
}
