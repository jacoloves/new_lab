(define (next d)
  (if (= d 2)
  3
  (+ d 2)))

(define (smallest-divisor n)
  (define (find-divisor n test-divisor)
    (cond ((> (* test-divisor test-dicisor) n) n)
    ((divides? test-divisor n) test-divisior)
    (else (find-divisor n (next test-divisor)))))
  (find-divisior n 2))