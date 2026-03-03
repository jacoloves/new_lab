(define (accumulate-iter combiner null-value term a next b)
    (define (iter x acc)
        (if (> x b)
            acc
            (iter (next x) (combiner acc (term x)))))
    (iter a null-value))