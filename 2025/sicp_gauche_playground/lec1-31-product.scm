(define (product term a next b)
  (if (> a b)
      1
      (* (term a)
         (product term (next a) next b))))

(define (product-iter term a next b)
  (define (iter x acc)
    (if (> x b)
        acc
        (iter (next x) (* acc (term x)))))
    (iter a 1))