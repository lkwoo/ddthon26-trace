// PetClinic (TRACE demo excerpt) — spring-petclinic-rest (Apache-2.0), 데모용 축약.
package org.springframework.samples.petclinic.pet;

import org.springframework.stereotype.Component;

/**
 * Maps between the Pet entity and its DTO.
 */
@Component
public class PetMapper {

    public PetDto toDto(Pet pet) {
        if (pet == null) {
            return null;
        }
        PetDto dto = new PetDto();
        dto.setId(pet.getId());
        dto.setName(pet.getName());
        dto.setBirthDate(pet.getBirthDate());
        if (pet.getType() != null) {
            dto.setTypeId(pet.getType().getId());
        }
        return dto;
    }

    public Pet toEntity(PetDto dto) {
        if (dto == null) {
            return null;
        }
        Pet pet = new Pet();
        pet.setId(dto.getId());
        pet.setName(dto.getName());
        pet.setBirthDate(dto.getBirthDate());
        return pet;
    }
}
