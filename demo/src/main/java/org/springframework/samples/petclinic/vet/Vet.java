package org.springframework.samples.petclinic.vet;

import java.util.HashSet;
import java.util.Set;

import jakarta.persistence.Entity;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.JoinTable;
import jakarta.persistence.ManyToMany;
import jakarta.persistence.Table;

import org.springframework.samples.petclinic.model.Person;

/**
 * PetClinic Vet(수의사) entity (TRACE demo excerpt).
 * 원본: spring-petclinic-rest (Apache-2.0), 데모용으로 축약·개변.
 *
 * 의도적 충돌 맥락 (충돌 C-5, policy_conflict):
 *   vet-directory-spec.pdf 는 "모든 수의사는 최소 1개 이상의 전문분야(Specialty)를 가져야 한다"고
 *   규정하지만, 아래 specialties 컬렉션에는 최소 개수 제약(예: 최소 1개)이 걸려 있지 않다.
 *   빈 전문분야로도 저장이 가능하다 => 정책-구현 불일치.
 */
@Entity
@Table(name = "vets")
public class Vet extends Person {

    // 충돌 C-5: 명세는 최소 1개 필수이나, 구현에는 최소 개수 제약이 없음(빈 집합 허용).
    @ManyToMany(fetch = jakarta.persistence.FetchType.EAGER)
    @JoinTable(name = "vet_specialties",
            joinColumns = @JoinColumn(name = "vet_id"),
            inverseJoinColumns = @JoinColumn(name = "specialty_id"))
    private Set<Specialty> specialties = new HashSet<>();

    public Set<Specialty> getSpecialties() {
        return specialties;
    }

    public void addSpecialty(Specialty specialty) {
        this.specialties.add(specialty);
    }

    public int getNrOfSpecialties() {
        return specialties.size();
    }
}
