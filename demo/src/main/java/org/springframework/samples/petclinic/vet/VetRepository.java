// PetClinic (TRACE demo excerpt) — spring-petclinic-rest (Apache-2.0), 데모용 축약.
package org.springframework.samples.petclinic.vet;

import org.springframework.data.jpa.repository.JpaRepository;

/**
 * Spring Data repository for the Vet entity.
 */
public interface VetRepository extends JpaRepository<Vet, Integer> {
}
