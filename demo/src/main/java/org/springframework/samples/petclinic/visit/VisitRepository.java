// PetClinic (TRACE demo excerpt) — spring-petclinic-rest (Apache-2.0), 데모용 축약.
package org.springframework.samples.petclinic.visit;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;

/**
 * Spring Data repository for the Visit entity.
 */
public interface VisitRepository extends JpaRepository<Visit, Integer> {

    List<Visit> findByPetId(Integer petId);
}
