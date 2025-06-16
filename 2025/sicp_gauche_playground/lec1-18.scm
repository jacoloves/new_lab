(define (double x) (+ x x))
(define (halve x) (/ x 2))

(define (fast-mul a b)
  (define (iter a b acc)
    (cond ((= b 0) acc)
          ((even? b) (iter (double a) (halve b) acc))
          (else      (iter a (- b 1) (+ acc a)))))
  (iter a b 0))
