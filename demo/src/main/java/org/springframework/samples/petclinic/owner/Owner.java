package org.springframework.samples.petclinic.owner;

import java.util.ArrayList;
import java.util.List;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

/**
 * PetClinic Owner entity (TRACE demo excerpt).
 * 원본: spring-petclinic-rest (Apache-2.0), 데모용으로 축약·개변.
 *
 * 의도적 충돌 맥락:
 *   - telephone: @Size(max = 10) -> 요구(20)와 불일치 (충돌 C-1)
 *   - email 필드 없음            -> 요구 REQ-2(email 필수) 미반영 (충돌 C-3)
 */
@Entity
@Table(name = "owners")
public class Owner {

    private Integer id;

    @NotBlank
    @Size(max = 30)
    @Column(name = "first_name")
    private String firstName;

    @NotBlank
    @Size(max = 30)
    @Column(name = "last_name")
    private String lastName;

    @Size(max = 255)
    private String address;

    @Size(max = 80)
    private String city;

    // 충돌 C-1: 요구사항은 최대 20자(국제 형식)이나 구현은 10자.
    @Size(max = 10)
    private String telephone;

    // NOTE(demo): email 필드 없음 — 요구 REQ-2(모든 Owner는 email 필수) 미반영 (충돌 C-3)

    private final List<Pet> pets = new ArrayList<>();

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getFirstName() {
        return firstName;
    }

    public void setFirstName(String firstName) {
        this.firstName = firstName;
    }

    public String getLastName() {
        return lastName;
    }

    public void setLastName(String lastName) {
        this.lastName = lastName;
    }

    public String getAddress() {
        return address;
    }

    public void setAddress(String address) {
        this.address = address;
    }

    public String getCity() {
        return city;
    }

    public void setCity(String city) {
        this.city = city;
    }

    public String getTelephone() {
        return telephone;
    }

    public void setTelephone(String telephone) {
        this.telephone = telephone;
    }

    public List<Pet> getPets() {
        return pets;
    }
}
