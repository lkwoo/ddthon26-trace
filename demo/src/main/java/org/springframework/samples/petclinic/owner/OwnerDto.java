package org.springframework.samples.petclinic.owner;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

/**
 * Data transfer object for Owner (TRACE demo excerpt).
 *
 * 의도적 충돌 맥락:
 *   - telephone: @Size(max = 10) -> 요구(20)와 불일치 (충돌 C-1)
 *   - email 필드 없음            -> 요구 REQ-2 미반영 (충돌 C-3)
 */
public class OwnerDto {

    private Integer id;

    @NotBlank
    @Size(max = 30)
    private String firstName;

    @NotBlank
    @Size(max = 30)
    private String lastName;

    @Size(max = 255)
    private String address;

    @Size(max = 80)
    private String city;

    @Size(max = 10)
    private String telephone;

    // NOTE(demo): email 필드 없음 (충돌 C-3)

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
}
