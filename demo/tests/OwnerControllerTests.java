package org.springframework.samples.petclinic.owner;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;

/**
 * Tests for Owner Management (TRACE demo excerpt).
 * 원본: spring-petclinic-rest (Apache-2.0), 데모용으로 축약·개변.
 *
 * 의도적 충돌 맥락 (충돌 C-1 근거 보강):
 *   아래 테스트는 telephone 이 "최대 10자"라는 (요구와 어긋난) 현재 구현 가정을 인코딩한다.
 *   즉, 테스트조차 요구(20자)가 아닌 구현(10자)에 맞춰져 있어 드리프트가 고착되어 있다.
 */
class OwnerControllerTests {

    @Test
    void telephoneMaxLengthIsTen() {
        OwnerDto dto = new OwnerDto();
        dto.setFirstName("George");
        dto.setLastName("Franklin");
        // 현재 구현 가정: telephone 최대 10자 (요구는 20 — 충돌 C-1)
        dto.setTelephone("6085551023"); // 10 chars
        assertThat(dto.getTelephone()).hasSize(10);
    }

    @Test
    void ownerRequiresFirstAndLastName() {
        OwnerDto dto = new OwnerDto();
        dto.setFirstName("George");
        dto.setLastName("Franklin");
        assertThat(dto.getFirstName()).isNotBlank();
        assertThat(dto.getLastName()).isNotBlank();
        // NOTE(demo): email 에 대한 검증이 없다 — 요구 REQ-2 미반영 (충돌 C-3)
    }
}
