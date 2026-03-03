(define (expmod base exp m)
  (cond ((= exp 0) 1)
        ((even? exp)
         (let ((half (expmod base (/ exp 2) m)))
           (remainder (* half half) m))
         (else (remainder (* base (expmod base (- exp 1) m)) m)))))

(define (camichael? n)
  (define (iter a)
    (cond ((= a n) #t)
          ((= (expmod a n n) a) (iter (+ a 1)))
          (else #f)))
  (iter 1))

(define carmichael-list '(561 1105 1729 2465 2821 6601))
(define control-list '(15 21 25 33))

(map (lambda (n) (list n (camichael? n))) carmichael-list)

(map (lambda (n) (list n (camichael? n))) control-list)
