// PetClinic (TRACE demo excerpt) — spring-petclinic-rest (Apache-2.0), 데모용 축약.
package org.springframework.samples.petclinic.visit;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.when;

import java.time.LocalDate;
import java.util.List;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class VisitControllerTests {

    @Mock
    private VisitRepository visits;

    @Mock
    private VisitMapper mapper;

    @InjectMocks
    private VisitRestController controller;

    @Test
    void listVisitsByPetFiltersOnPetId() {
        Visit visit = new Visit();
        visit.setDate(LocalDate.of(2024, 1, 10));
        visit.setDescription("annual checkup");
        VisitDto dto = new VisitDto();
        dto.setDescription("annual checkup");
        when(visits.findByPetId(7)).thenReturn(List.of(visit));
        when(mapper.toDto(visit)).thenReturn(dto);

        List<VisitDto> result = controller.listVisits(7);

        assertThat(result).hasSize(1);
        assertThat(result.get(0).getDescription()).isEqualTo("annual checkup");
    }

    @Test
    void listVisitsWithoutPetIdReturnsAll() {
        when(visits.findAll()).thenReturn(List.of());

        List<VisitDto> result = controller.listVisits(null);

        assertThat(result).isEmpty();
    }
}
