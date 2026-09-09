// PetClinic (TRACE demo excerpt) — spring-petclinic-rest (Apache-2.0), 데모용 축약.
package org.springframework.samples.petclinic.owner;

import org.springframework.stereotype.Component;

/**
 * Maps between the Owner entity and its DTO.
 */
@Component
public class OwnerMapper {

    public OwnerDto toDto(Owner owner) {
        if (owner == null) {
            return null;
        }
        OwnerDto dto = new OwnerDto();
        dto.setId(owner.getId());
        dto.setFirstName(owner.getFirstName());
        dto.setLastName(owner.getLastName());
        dto.setAddress(owner.getAddress());
        dto.setCity(owner.getCity());
        dto.setTelephone(owner.getTelephone());
        return dto;
    }

    public Owner toEntity(OwnerDto dto) {
        if (dto == null) {
            return null;
        }
        Owner owner = new Owner();
        owner.setId(dto.getId());
        owner.setFirstName(dto.getFirstName());
        owner.setLastName(dto.getLastName());
        owner.setAddress(dto.getAddress());
        owner.setCity(dto.getCity());
        owner.setTelephone(dto.getTelephone());
        return owner;
    }
}
