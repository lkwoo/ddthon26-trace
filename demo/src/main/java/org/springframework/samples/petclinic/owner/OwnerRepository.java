package org.springframework.samples.petclinic.owner;

import java.util.List;

/**
 * Repository abstraction for Owner persistence (TRACE demo excerpt).
 * 원본: spring-petclinic-rest (Apache-2.0), 데모용으로 축약.
 */
public interface OwnerRepository {

    List<OwnerDto> findAllDtos();

    OwnerDto findDtoById(int ownerId);

    OwnerDto save(OwnerDto owner);
}
