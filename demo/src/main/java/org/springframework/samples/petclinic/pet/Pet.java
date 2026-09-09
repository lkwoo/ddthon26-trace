package org.springframework.samples.petclinic.pet;

import java.time.LocalDate;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

/**
 * PetClinic Pet entity (TRACE demo excerpt).
 * 원본: spring-petclinic-rest (Apache-2.0), 데모용으로 축약·개변.
 *
 * 의도적 충돌 맥락 (충돌 C-2):
 *   maintenance-notes.md 의 PET-RULE-1 은 "birthDate 는 미래 일자를 거부하도록 검증된다"고
 *   명시하지만, 아래 birthDate 필드에는 미래일자 검증 제약/로직이 붙어 있지 않다.
 *   => 문서-구현 드리프트(stale knowledge).
 */
@Entity
@Table(name = "pets")
public class Pet {

    private Integer id;

    @NotBlank
    @Size(max = 30)
    private String name;

    // 충돌 C-2: 미래일자 검증 없음 (maintenance-notes PET-RULE-1 과 드리프트)
    @Column(name = "birth_date")
    private LocalDate birthDate;

    private PetType type;

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

    public LocalDate getBirthDate() {
        return birthDate;
    }

    public void setBirthDate(LocalDate birthDate) {
        this.birthDate = birthDate;
    }

    public PetType getType() {
        return type;
    }

    public void setType(PetType type) {
        this.type = type;
    }
}
