// PetClinic (TRACE demo excerpt) — spring-petclinic-rest (Apache-2.0), 데모용 축약.
package org.springframework.samples.petclinic.visit;

import org.springframework.stereotype.Component;

/**
 * Maps between the Visit entity and its DTO.
 */
@Component
public class VisitMapper {

    public VisitDto toDto(Visit visit) {
        if (visit == null) {
            return null;
        }
        VisitDto dto = new VisitDto();
        dto.setId(visit.getId());
        dto.setDate(visit.getDate());
        dto.setDescription(visit.getDescription());
        return dto;
    }

    public Visit toEntity(VisitDto dto) {
        if (dto == null) {
            return null;
        }
        Visit visit = new Visit();
        visit.setId(dto.getId());
        visit.setDate(dto.getDate());
        visit.setDescription(dto.getDescription());
        return visit;
    }
}
