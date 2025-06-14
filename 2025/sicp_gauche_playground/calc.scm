(use srfi-1)
(define history '())

(define (square x) (* x x))
(define (log! expr val) (set! history (append history (list expr val))) val)

(define (add . xs) (log! `(add ,@xs) (fold + 0 xs)))
(define (sub x . xs) (log! `(sub ,x ,@xs) (fold - x xs)))
(define (mul . xs) (log! `(mul ,@xs) (fold * 1 xs)))
(define (div x . xs) (log! `(div ,x ,@xs) (fold / x xs)))

(define + add) (define - sub) (define * mul) (define / div)

(define (hist) history)

(define (main _)
  (format #t "Loaded calc.scm - ex: (+ 1 2 3) (hist)~%") 0)

