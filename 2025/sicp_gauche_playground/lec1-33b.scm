(define (filterd-accumulate-iter combiner null-value term
                                 a next b predicate)
    (define (iter x acc)
      (cond ((> x b) acc)
            ((predicate x)
             (iter (next x) (combiner acc (term x))))
            (else
             (iter (next x) acc))))
    (iter a null-value))