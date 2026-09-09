// PetClinic (TRACE demo excerpt) — spring-petclinic-rest (Apache-2.0), 데모용 축약.
package org.springframework.samples.petclinic.vet;

import org.springframework.stereotype.Component;

/**
 * Maps the Vet entity to its DTO.
 */
@Component
public class VetMapper {

    public VetDto toDto(Vet vet) {
        if (vet == null) {
            return null;
        }
        VetDto dto = new VetDto();
        dto.setId(vet.getId());
        dto.setFirstName(vet.getFirstName());
        dto.setLastName(vet.getLastName());
        for (Specialty specialty : vet.getSpecialties()) {
            dto.getSpecialties().add(specialty.getName());
        }
        return dto;
    }
}
