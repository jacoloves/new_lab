(define (filterd-accumulate combiner null-value term a next b predicate)
    (cond ((> a b) null-value)
          ((predicate a)
           (combiner (term a)
                     (fileterd-accumulate combiner null-value
                                          teerm (next a) next b predicate)))
           (else
            (fileterd-accumulate combiner null-value
                                 term (next a) next b predicate))))