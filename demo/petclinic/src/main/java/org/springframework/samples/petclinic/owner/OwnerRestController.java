package org.springframework.samples.petclinic.owner;

import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * REST controller for Owner registration (Spring PetClinic REST 발췌·데모용).
 *
 * Owner 등록 엔드포인트. 전화번호는 Owner 엔티티의 제약(@Size max=10)을 그대로 검증한다.
 * NOTE: SMS 인증(휴대폰 검증) 단계는 현재 구현되어 있지 않다.
 */
@RestController
@RequestMapping("/api/owners")
public class OwnerRestController {

    /**
     * Create (register) a new owner.
     * 요청 본문의 telephone 은 Owner 검증 제약을 통과해야 한다(최대 10자리).
     */
    @PostMapping
    public ResponseEntity<Owner> addOwner(@RequestBody @Valid Owner owner) {
        // 저장 로직 생략(데모). SMS 인증 절차 없음.
        return new ResponseEntity<>(owner, HttpStatus.CREATED);
    }
}
