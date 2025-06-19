(use srfi-19)

(define (square x) (* x x))

(define (divides? a b) (= (remainder b a) 0))

(define (find-divisor n test-divisor)
  (cond ((> (square test-divisor) n) n)
        ((divides? test-divisor n) test-divisor)
        (else (find-divisor n (+ test-divisor 1)))))

(define (smallest-divisor n)
  (find-divisor n 2))

(define (prime? n)
  (= n (smallest-divisor n)))

(define (report-prime elapsed)
  (display " *** ")
  (display elapsed) (display " sec"))

(define (start-prime-test n start-time)
  (if (prime? n)
    (report-prime
      (- (time->seconds (current-time))
         (time->seconds start-time)))))

(define (timed-prime-test n)
  (newline)
  (display n)
  (start-prime-test n (current-time)))

(define (search-for-primes start count)
  (define (iter n found)
    (cond ((= found count) 'done)
          ((timed-prime-test n)
           (iter (+ n 2) (+ found 1)))
          (else (iter (+ n 2) found))))
  (iter (if (even? start) (+ start 1) start) 0))
