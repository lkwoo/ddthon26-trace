// PetClinic (TRACE demo excerpt) — spring-petclinic-rest (Apache-2.0), 데모용 축약.
package org.springframework.samples.petclinic.pet;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;

/**
 * Spring Data repository for the Pet entity.
 */
public interface PetRepository extends JpaRepository<Pet, Integer> {

    List<Pet> findByNameContainingIgnoreCase(String name);
}
