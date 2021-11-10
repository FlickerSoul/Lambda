(* CS 384
 In-progress.
    Working Substitiution. Written reduction. Correctly computes succ 1 as two.

    TODO: test Reduction further. 
    Write lambda calculus test terms
*)

fun from_underline_chars_to_string nil =  nil
  | from_underline_chars_to_string (ch::ht) = if ch = #"_" then nil else ch::(from_underline_chars_to_string ht);

fun get_before_underline s = String.implode (from_underline_chars_to_string (String.explode s));

datatype term =
        AP of term * term
      | LM of string * term
      | VA of string
      | string ;


val test1 = AP(LM("zz",AP(LM("zf",AP(VA"zf",VA"zz")),LM("y",VA"zz"))),LM("f",LM("x",VA"x")));

val test2= AP(LM("zero",AP(LM("succ",AP(LM("plus",AP(LM("times",AP(LM("two",AP(AP(VA"times",AP(VA"succ",VA"two")),VA"two")),AP(VA"succ",AP(VA"succ",VA"zero")))),LM("n",LM("m",LM("f",LM("x",AP(AP(VA"n",AP(VA"m",VA"f")),VA"x"))))))),LM("n",LM("m",AP(AP(VA"n",VA"succ"),VA"m"))))),LM("n",LM("f",LM("x",AP(VA"f",AP(AP(VA"n",VA"f"),VA"x"))))))),LM("f",LM("x",VA"x")));

val freshVariableIndex = ref 0;

fun get_fresh_var (t as (VA s)) = 
    let val _ = (freshVariableIndex := (!freshVariableIndex) + 1)
        val i = (!freshVariableIndex)
        val base = get_before_underline s
        in (base ^ "_" ^ (Int.toString i))
    end;

fun substitution (name as VA n) newTerm (oldTerm as (VA r)) = 
  if n = r then newTerm else oldTerm
  | substitution (name as VA replaced) newTerm (oldTerm as (LM (r,body))) = 
    if replaced = r then oldTerm else 
        let val z = get_fresh_var (VA r) 
            in let val t = substitution (VA r) (VA z) body
                in let val newBody = substitution name newTerm t 
                    in LM(z,newBody) end end end
  | substitution name newTerm (oldTerm as AP (er, ee)) = AP(substitution name newTerm er, substitution name newTerm ee);


(* tests substitution:
substitution (VA "x") (VA "s") (AP (VA "x", VA "y"));
substitution (VA "x") (VA "s") (AP(LM("a", LM("y", AP(VA "x", VA "y"))), VA "x"));

substitution (VA "n") (LM ("f", LM ("a", AP (VA "f", VA "a"))))(LM ("f", LM ("a", AP ((VA "n"), AP (VA "f", VA("a")))))) ;
*)

fun isReducible (VA name) = false
  | isReducible (LM (fp, b)) = isReducible b
  | isReducible (AP(ee as (LM (fp,b)), er)) = true
  | isReducible (AP(ee, er)) = if isReducible ee then true else isReducible er;

fun reductionStep (t as VA(name)) = t
  | reductionStep (t as LM(input, body)) = LM(input, reductionStep body)
  | reductionStep (t as AP((er as LM(fp, body)), ee)) = substitution (VA fp) ee body
  | reductionStep (t as AP(ee, er)) = if isReducible ee then AP(reductionStep ee, er)
      else AP(ee, reductionStep er);


(* Jim's sample2.lc. 
val v1 = reductionStep test1;
val v2 = reductionStep v1;
val reduced = reductionStep v2;
val v4 = reductionStep v3;          (* reducing an irreducible term yields same term *)
*)


val succ = LM("n", LM("f", LM("a", AP(AP((VA "n"), (VA "f")),AP((VA "f"), (VA "a"))))));
val one = LM("x", LM("y", AP((VA "x"), (VA "y"))));

val two = AP(succ, one);
val m = reductionStep two;

val n = reductionStep m;
val reducedToTwo = reductionStep n
val q = reductionStep reducedToTwo;         (* reducing an irreducible term yields same term *)



