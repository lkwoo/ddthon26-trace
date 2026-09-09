// PetClinic (TRACE demo excerpt) — spring-petclinic-rest (Apache-2.0), 데모용 축약.
package org.springframework.samples.petclinic.vet;

import org.springframework.samples.petclinic.model.NamedEntity;

import jakarta.persistence.Entity;
import jakarta.persistence.Table;

/**
 * A veterinary specialty (e.g. radiology, surgery).
 */
@Entity
@Table(name = "specialties")
public class Specialty extends NamedEntity {
}
