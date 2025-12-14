(define (timed-prime-test n)
  (newline) (display n)
  (let* ((start (current-time))
         (prime? (fast-prime? n 5)))
    (when prime?
      (display " *** ")
      (display (- (time->seconds (current-time))
                  (time->seconds start)))
      (display " sec"))))
