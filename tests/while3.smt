(define-fun-rec sum_n ((x Int)) Int
                  (ite (>= x 1)
                       (+ x (sum_n (- x 1)))
                       0))

(define-fun ps ( (x Int) (arg Int) ) Bool
  (or (>= 1 arg) (= x (sum_n (- arg 1)))))
       
(define-fun inv0 ( (x Int) (y Int) (arg Int) ) Bool
  (or (>= 1 arg) (and (<= y arg) (= x (sum_n (- y 1))) (>= y 1))))


(declare-const tmp11 Int)
(declare-const tmp14 Int)
(declare-const tmp8 Int)
(declare-const tmp9 Int)
(declare-const bb Bool)
(declare-const arg Int)
(declare-const tmp1_0 Int)
(declare-const tmp2_1 Int)
(declare-const bb3 Bool)
(declare-const tmp4 Int)
(declare-const tmp5 Int)
(declare-const tmp6 Bool)
(declare-const bb13 Bool)
(declare-const bb7 Bool)



(assert (not (=> (and 

(= bb (and bb3 (inv0 0 1 arg))) 
(= bb3 (=> (and (and (= tmp4 tmp2_1) (= tmp5 arg) (= tmp6 (< tmp2_1 arg))) (inv0 tmp1_0 tmp2_1 arg)) (and bb13 bb7))) 
(= bb7 (=> (and (and (= tmp8 tmp1_0) (= tmp9 tmp2_1) (= tmp11 tmp2_1)) (and (inv0 tmp1_0 tmp2_1 arg) (< tmp2_1 arg))) (inv0 (+ tmp1_0 tmp2_1) (+ tmp2_1 1) arg))) 
(= bb13 (=> (and (= tmp14 tmp1_0) (and (inv0 tmp1_0 tmp2_1 arg) (not (< tmp2_1 arg)))) (ps tmp1_0 arg)))

) 

bb)))

(check-sat)
(get-model)
