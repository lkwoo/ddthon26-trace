// PetClinic (TRACE demo excerpt) — spring-petclinic-rest (Apache-2.0), 데모용 축약.
package org.springframework.samples.petclinic.owner;

import java.util.List;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * Application service for Owner Management.
 */
@Service
public class OwnerService {

    private final OwnerRepository owners;

    public OwnerService(OwnerRepository owners) {
        this.owners = owners;
    }

    @Transactional(readOnly = true)
    public List<OwnerDto> findAll() {
        return owners.findAllDtos();
    }

    @Transactional(readOnly = true)
    public OwnerDto findById(int ownerId) {
        OwnerDto dto = owners.findDtoById(ownerId);
        if (dto == null) {
            throw new IllegalArgumentException("Owner not found: " + ownerId);
        }
        return dto;
    }

    @Transactional
    public OwnerDto save(OwnerDto owner) {
        return owners.save(owner);
    }
}
