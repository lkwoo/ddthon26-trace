package org.springframework.samples.petclinic.owner;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;
import jakarta.validation.constraints.Digits;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

/**
 * Simple JavaBean domain object representing an owner.
 * (Spring PetClinic REST — Owner fragment; 발췌·데모용)
 */
@Entity
@Table(name = "owners")
public class Owner {

    @Column(name = "first_name")
    @NotBlank
    private String firstName;

    @Column(name = "last_name")
    @NotBlank
    private String lastName;

    @Column(name = "address")
    @NotBlank
    private String address;

    @Column(name = "city")
    @NotBlank
    private String city;

    /**
     * Owner contact telephone. Registration requires a reachable number.
     * NOTE: 구현상 최대 길이 10자리로 제한된다.
     */
    @Column(name = "telephone")
    @NotBlank
    @Digits(fraction = 0, integer = 10)
    @Size(max = 10)
    private String telephone;

    public String getTelephone() {
        return this.telephone;
    }

    public void setTelephone(String telephone) {
        this.telephone = telephone;
    }
}
