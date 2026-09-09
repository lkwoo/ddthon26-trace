// PetClinic (TRACE demo excerpt) — spring-petclinic-rest (Apache-2.0), 데모용 축약.
package org.springframework.samples.petclinic.pet;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

import java.util.List;
import java.util.Optional;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

@ExtendWith(MockitoExtension.class)
class PetControllerTests {

    @Mock
    private PetRepository pets;

    @Mock
    private PetMapper mapper;

    @InjectMocks
    private PetRestController controller;

    @Test
    void listPetsReturnsMappedDtos() {
        Pet pet = new Pet();
        pet.setName("Leo");
        PetDto dto = new PetDto();
        dto.setName("Leo");
        when(pets.findAll()).thenReturn(List.of(pet));
        when(mapper.toDto(pet)).thenReturn(dto);

        List<PetDto> result = controller.listPets();

        assertThat(result).hasSize(1);
        assertThat(result.get(0).getName()).isEqualTo("Leo");
    }

    @Test
    void getPetReturnsNotFoundWhenMissing() {
        when(pets.findById(99)).thenReturn(Optional.empty());

        ResponseEntity<PetDto> response = controller.getPet(99);

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.NOT_FOUND);
    }

    @Test
    void addPetReturnsCreated() {
        PetDto dto = new PetDto();
        dto.setName("Basil");
        Pet entity = new Pet();
        when(mapper.toEntity(dto)).thenReturn(entity);
        when(pets.save(any(Pet.class))).thenReturn(entity);
        when(mapper.toDto(entity)).thenReturn(dto);

        ResponseEntity<PetDto> response = controller.addPet(dto);

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        assertThat(response.getBody()).isNotNull();
    }
}
