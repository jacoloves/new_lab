(define (factorial n)
  (product-iter (lambda (x) x) 1 (lambda (x) (+ x 1)) n))

(define (pi-wallis n)
  (* 4
    (product-iter
      (lambda (k)
        (/ (* 2 k) (- (* 2 k) 1))
        (* (/ (* 2 k) (+ (* 2 k) 1))))
      1
      (lambda (k) (+ k 1))
      n)))