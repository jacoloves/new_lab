(define (expmod base exp n)
  (cond ((= exp 0) 1)
        ((even? exp)
         (let ((half (expmod base (/ exp 2) n)))
           (if (= half 0)
             0
             (let ((sq (remainder (* half half) n)))
               (if (and (not (= half 1))
                        (not (= half (- n 1)))
                        (= sq 1))
                 0
                 sq)))))
        (else
          (let ((r (expmod base (- exp 1) n)))
            (if (= r 0) 0
              (remainder (* base r) n))))))

(define (miller-rabin-single n a)
  (= (expmod a (- n 1) n) 1))

(define (fast-prime? n k)
  (cond ((< n 2) #f)
        ((even? n) (= n 2))
        (else
          (define (iter i)
            (cond ((= i 0) #t)
                  ((miller-rabin-single n (+ 2 (random (- n 3))))
                   (iter (- i 1)))
                  (else #f)))
          (iter k))))
