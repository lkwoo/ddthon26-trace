package org.springframework.samples.petclinic.pet;

import jakarta.persistence.Entity;
import jakarta.persistence.Table;
import jakarta.validation.constraints.Size;

/**
 * Pet type lookup entity (TRACE demo excerpt).
 * 원본: spring-petclinic-rest (Apache-2.0), 데모용으로 축약.
 */
@Entity
@Table(name = "types")
public class PetType {

    private Integer id;

    @Size(max = 80)
    private String name;

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }
}
