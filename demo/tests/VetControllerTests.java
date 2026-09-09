// PetClinic (TRACE demo excerpt) — spring-petclinic-rest (Apache-2.0), 데모용 축약.
package org.springframework.samples.petclinic.vet;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.when;

import java.util.List;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

@ExtendWith(MockitoExtension.class)
class VetControllerTests {

    @Mock
    private VetService vets;

    @InjectMocks
    private VetRestController controller;

    @Test
    void listVetsDelegatesToService() {
        VetDto dto = new VetDto();
        dto.setFirstName("James");
        dto.setLastName("Carter");
        when(vets.findAll()).thenReturn(List.of(dto));

        List<VetDto> result = controller.listVets();

        assertThat(result).extracting(VetDto::getLastName).containsExactly("Carter");
    }

    @Test
    void getVetReturnsOkWhenPresent() {
        VetDto dto = new VetDto();
        dto.setId(1);
        when(vets.findById(1)).thenReturn(dto);

        ResponseEntity<VetDto> response = controller.getVet(1);

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody()).isNotNull();
        assertThat(response.getBody().getId()).isEqualTo(1);
    }

    @Test
    void getVetReturnsNotFoundOnUnknownId() {
        when(vets.findById(42)).thenThrow(new IllegalArgumentException("Vet not found: 42"));

        ResponseEntity<VetDto> response = controller.getVet(42);

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.NOT_FOUND);
    }
}
