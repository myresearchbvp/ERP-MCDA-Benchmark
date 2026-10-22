"""NP11 LFPP models, convex solver checks and rational/interval certificates.

Source: Panjavongroj and Phruksaphanrat, DOI 10.3233/JIFS-221476.
The portable adapter supplies repository-relative inputs and outputs.
See docs/NP11_CRITERION_DELETION.md for the model and certificate definitions.
"""

SOURCE = {'source_sha256': 'c6cb656abfd7c652f7754a8fdd3b36395870ce3ebdd6667399f128837ad62926', 'proof_pages': 15, 'doi': '10.3233/JIFS-221476', 'M': 1000, 'criteria_upper': [{'i': 0, 'j': 1, 'lmu': [0.125, 0.14285714285714285, 0.16666666666666666], 'exact_lmu': '1/8 1/7 1/6'}, {'i': 0, 'j': 2, 'lmu': [0.5, 1.0, 2.0], 'exact_lmu': '1/2 1 2'}, {'i': 0, 'j': 3, 'lmu': [0.25, 0.3333333333333333, 0.5], 'exact_lmu': '1/4 1/3 1/2'}, {'i': 0, 'j': 4, 'lmu': [1.0, 2.0, 3.0], 'exact_lmu': '1 2 3'}, {'i': 0, 'j': 5, 'lmu': [0.1111111111111111, 0.125, 0.14285714285714285], 'exact_lmu': '1/9 1/8 1/7'}, {'i': 1, 'j': 2, 'lmu': [2.0, 3.0, 4.0], 'exact_lmu': '2 3 4'}, {'i': 1, 'j': 3, 'lmu': [3.0, 4.0, 5.0], 'exact_lmu': '3 4 5'}, {'i': 1, 'j': 4, 'lmu': [7.0, 8.0, 9.0], 'exact_lmu': '7 8 9'}, {'i': 1, 'j': 5, 'lmu': [1.0, 2.0, 3.0], 'exact_lmu': '1 2 3'}, {'i': 2, 'j': 3, 'lmu': [0.5, 1.0, 2.0], 'exact_lmu': '1/2 1 2'}, {'i': 2, 'j': 4, 'lmu': [2.0, 3.0, 4.0], 'exact_lmu': '2 3 4'}, {'i': 2, 'j': 5, 'lmu': [0.25, 0.3333333333333333, 0.5], 'exact_lmu': '1/4 1/3 1/2'}, {'i': 3, 'j': 4, 'lmu': [1.0, 2.0, 3.0], 'exact_lmu': '1 2 3'}, {'i': 3, 'j': 5, 'lmu': [0.25, 0.3333333333333333, 0.5], 'exact_lmu': '1/4 1/3 1/2'}, {'i': 4, 'j': 5, 'lmu': [0.14285714285714285, 0.16666666666666666, 0.2], 'exact_lmu': '1/7 1/6 1/5'}], 'criteria_upper_original': [{'i': 0, 'j': 1, 'lmu': [0.125, 0.14285714285714285, 0.16666666666666666], 'exact_lmu': '1/8 1/7 1/6'}, {'i': 0, 'j': 2, 'lmu': [0.5, 1.0, 2.0], 'exact_lmu': '1/2 1 2'}, {'i': 0, 'j': 3, 'lmu': [0.25, 0.3333333333333333, 0.5], 'exact_lmu': '1/4 1/3 1/2'}, {'i': 0, 'j': 4, 'lmu': [1.0, 2.0, 3.0], 'exact_lmu': '1 2 3'}, {'i': 0, 'j': 5, 'lmu': [0.1111111111111111, 0.125, 0.14285714285714285], 'exact_lmu': '1/9 1/8 1/7'}, {'i': 1, 'j': 2, 'lmu': [2.0, 3.0, 4.0], 'exact_lmu': '2 3 4'}, {'i': 1, 'j': 3, 'lmu': [3.0, 4.0, 5.0], 'exact_lmu': '3 4 5'}, {'i': 1, 'j': 4, 'lmu': [7.0, 8.0, 9.0], 'exact_lmu': '7 8 9'}, {'i': 1, 'j': 5, 'lmu': [1.0, 2.0, 3.0], 'exact_lmu': '1 2 3'}, {'i': 2, 'j': 3, 'lmu': [0.5, 1.0, 2.0], 'exact_lmu': '1/2 1 2'}, {'i': 2, 'j': 4, 'lmu': [2.0, 3.0, 4.0], 'exact_lmu': '2 3 4'}, {'i': 2, 'j': 5, 'lmu': [0.25, 0.3333333333333333, 0.5], 'exact_lmu': '1/4 1/3 1/2'}, {'i': 3, 'j': 4, 'lmu': [3.0, 4.0, 5.0], 'exact_lmu': '3 4 5'}, {'i': 3, 'j': 5, 'lmu': [0.25, 0.3333333333333333, 0.5], 'exact_lmu': '1/4 1/3 1/2'}, {'i': 4, 'j': 5, 'lmu': [0.14285714285714285, 0.16666666666666666, 0.2], 'exact_lmu': '1/7 1/6 1/5'}], 'criteria_full_reassessed': [[[1.0, 1.0, 1.0], [0.125, 0.14285714285714285, 0.16666666666666666], [0.5, 1.0, 2.0], [0.25, 0.3333333333333333, 0.5], [1.0, 2.0, 3.0], [0.1111111111111111, 0.125, 0.14285714285714285]], [[6.0, 7.0, 8.0], [1.0, 1.0, 1.0], [2.0, 3.0, 4.0], [3.0, 4.0, 5.0], [7.0, 8.0, 9.0], [1.0, 2.0, 3.0]], [[0.5, 1.0, 2.0], [0.25, 0.3333333333333333, 0.5], [1.0, 1.0, 1.0], [0.5, 1.0, 2.0], [2.0, 3.0, 4.0], [0.25, 0.3333333333333333, 0.5]], [[2.0, 3.0, 4.0], [0.2, 0.25, 0.3333333333333333], [0.5, 1.0, 2.0], [1.0, 1.0, 1.0], [1.0, 2.0, 3.0], [0.25, 0.3333333333333333, 0.5]], [[0.3333333333333333, 0.5, 1.0], [0.1111111111111111, 0.125, 0.14285714285714285], [0.25, 0.3333333333333333, 0.5], [0.3333333333333333, 0.5, 1.0], [1.0, 1.0, 1.0], [0.14285714285714285, 0.16666666666666666, 0.2]], [[7.0, 8.0, 9.0], [0.3333333333333333, 0.5, 1.0], [2.0, 3.0, 4.0], [2.0, 3.0, 4.0], [5.0, 6.0, 7.0], [1.0, 1.0, 1.0]]], 'criteria_full_printed_table_body': [[[1.0, 1.0, 1.0], [0.125, 0.14285714285714285, 0.16666666666666666], [0.5, 1.0, 2.0], [0.25, 0.3333333333333333, 0.5], [1.0, 2.0, 3.0], [0.1111111111111111, 0.125, 0.14285714285714285]], [[6.0, 7.0, 8.0], [1.0, 1.0, 1.0], [2.0, 3.0, 4.0], [3.0, 4.0, 5.0], [7.0, 8.0, 9.0], [1.0, 2.0, 3.0]], [[0.5, 1.0, 2.0], [0.25, 0.3333333333333333, 0.5], [1.0, 1.0, 1.0], [0.5, 1.0, 2.0], [2.0, 3.0, 4.0], [0.25, 0.3333333333333333, 0.5]], [[2.0, 3.0, 4.0], [0.2, 0.25, 0.3333333333333333], [0.5, 1.0, 2.0], [1.0, 1.0, 1.0], [3.0, 4.0, 5.0], [0.25, 0.3333333333333333, 0.5]], [[0.3333333333333333, 0.5, 1.0], [0.1111111111111111, 0.125, 0.14285714285714285], [0.25, 0.3333333333333333, 0.5], [0.3333333333333333, 0.5, 1.0], [1.0, 1.0, 1.0], [0.14285714285714285, 0.16666666666666666, 0.2]], [[7.0, 8.0, 9.0], [0.3333333333333333, 0.5, 1.0], [2.0, 3.0, 4.0], [2.0, 3.0, 4.0], [5.0, 6.0, 7.0], [1.0, 1.0, 1.0]]], 'local_upper': {'C1': [{'i': 0, 'j': 1, 'lmu': [1.0, 2.0, 3.0], 'exact_lmu': '1 2 3'}, {'i': 0, 'j': 2, 'lmu': [0.5, 1.0, 2.0], 'exact_lmu': '1/2 1 2'}, {'i': 0, 'j': 3, 'lmu': [1.0, 2.0, 3.0], 'exact_lmu': '1 2 3'}, {'i': 1, 'j': 2, 'lmu': [0.5, 1.0, 2.0], 'exact_lmu': '1/2 1 2'}, {'i': 1, 'j': 3, 'lmu': [1.0, 2.0, 3.0], 'exact_lmu': '1 2 3'}, {'i': 2, 'j': 3, 'lmu': [1.0, 2.0, 3.0], 'exact_lmu': '1 2 3'}], 'C2': [{'i': 0, 'j': 1, 'lmu': [0.5, 1.0, 2.0], 'exact_lmu': '1/2 1 2'}, {'i': 0, 'j': 2, 'lmu': [0.5, 1.0, 2.0], 'exact_lmu': '1/2 1 2'}, {'i': 0, 'j': 3, 'lmu': [1.0, 2.0, 3.0], 'exact_lmu': '1 2 3'}, {'i': 1, 'j': 2, 'lmu': [0.5, 1.0, 2.0], 'exact_lmu': '1/2 1 2'}, {'i': 1, 'j': 3, 'lmu': [2.0, 3.0, 4.0], 'exact_lmu': '2 3 4'}, {'i': 2, 'j': 3, 'lmu': [2.0, 3.0, 4.0], 'exact_lmu': '2 3 4'}], 'C3': [{'i': 0, 'j': 1, 'lmu': [0.3333333333333333, 0.5, 1.0], 'exact_lmu': '1/3 1/2 1'}, {'i': 0, 'j': 2, 'lmu': [0.5, 1.0, 2.0], 'exact_lmu': '1/2 1 2'}, {'i': 0, 'j': 3, 'lmu': [0.2, 0.25, 0.3333333333333333], 'exact_lmu': '1/5 1/4 1/3'}, {'i': 1, 'j': 2, 'lmu': [0.3333333333333333, 0.5, 1.0], 'exact_lmu': '1/3 1/2 1'}, {'i': 1, 'j': 3, 'lmu': [0.14285714285714285, 0.16666666666666666, 0.2], 'exact_lmu': '1/7 1/6 1/5'}, {'i': 2, 'j': 3, 'lmu': [0.2, 0.25, 0.3333333333333333], 'exact_lmu': '1/5 1/4 1/3'}], 'C4': [{'i': 0, 'j': 1, 'lmu': [1.0, 2.0, 3.0], 'exact_lmu': '1 2 3'}, {'i': 0, 'j': 2, 'lmu': [1.0, 2.0, 3.0], 'exact_lmu': '1 2 3'}, {'i': 0, 'j': 3, 'lmu': [4.0, 5.0, 6.0], 'exact_lmu': '4 5 6'}, {'i': 1, 'j': 2, 'lmu': [0.25, 0.3333333333333333, 0.5], 'exact_lmu': '1/4 1/3 1/2'}, {'i': 1, 'j': 3, 'lmu': [1.0, 2.0, 3.0], 'exact_lmu': '1 2 3'}, {'i': 2, 'j': 3, 'lmu': [3.0, 4.0, 5.0], 'exact_lmu': '3 4 5'}], 'C5': [{'i': 0, 'j': 1, 'lmu': [1.0, 2.0, 3.0], 'exact_lmu': '1 2 3'}, {'i': 0, 'j': 2, 'lmu': [0.5, 1.0, 2.0], 'exact_lmu': '1/2 1 2'}, {'i': 0, 'j': 3, 'lmu': [0.3333333333333333, 0.5, 1.0], 'exact_lmu': '1/3 1/2 1'}, {'i': 1, 'j': 2, 'lmu': [0.3333333333333333, 0.5, 1.0], 'exact_lmu': '1/3 1/2 1'}, {'i': 1, 'j': 3, 'lmu': [0.3333333333333333, 0.5, 1.0], 'exact_lmu': '1/3 1/2 1'}, {'i': 2, 'j': 3, 'lmu': [0.3333333333333333, 0.5, 1.0], 'exact_lmu': '1/3 1/2 1'}], 'C6': [{'i': 0, 'j': 1, 'lmu': [0.3333333333333333, 0.5, 1.0], 'exact_lmu': '1/3 1/2 1'}, {'i': 0, 'j': 2, 'lmu': [0.3333333333333333, 0.5, 1.0], 'exact_lmu': '1/3 1/2 1'}, {'i': 0, 'j': 3, 'lmu': [0.16666666666666666, 0.2, 0.25], 'exact_lmu': '1/6 1/5 1/4'}, {'i': 1, 'j': 2, 'lmu': [0.3333333333333333, 0.5, 1.0], 'exact_lmu': '1/3 1/2 1'}, {'i': 1, 'j': 3, 'lmu': [0.125, 0.14285714285714285, 0.16666666666666666], 'exact_lmu': '1/8 1/7 1/6'}, {'i': 2, 'j': 3, 'lmu': [0.125, 0.14285714285714285, 0.16666666666666666], 'exact_lmu': '1/8 1/7 1/6'}]}, 'local_full': {'C1': [[[1.0, 1.0, 1.0], [1.0, 2.0, 3.0], [0.5, 1.0, 2.0], [1.0, 2.0, 3.0]], [[0.3333333333333333, 0.5, 1.0], [1.0, 1.0, 1.0], [0.5, 1.0, 2.0], [1.0, 2.0, 3.0]], [[0.5, 1.0, 2.0], [0.5, 1.0, 2.0], [1.0, 1.0, 1.0], [1.0, 2.0, 3.0]], [[0.3333333333333333, 0.5, 1.0], [0.3333333333333333, 0.5, 1.0], [0.3333333333333333, 0.5, 1.0], [1.0, 1.0, 1.0]]], 'C2': [[[1.0, 1.0, 1.0], [0.5, 1.0, 2.0], [0.5, 1.0, 2.0], [1.0, 2.0, 3.0]], [[0.5, 1.0, 2.0], [1.0, 1.0, 1.0], [0.5, 1.0, 2.0], [2.0, 3.0, 4.0]], [[0.5, 1.0, 2.0], [0.5, 1.0, 2.0], [1.0, 1.0, 1.0], [2.0, 3.0, 4.0]], [[0.3333333333333333, 0.5, 1.0], [0.25, 0.3333333333333333, 0.5], [0.25, 0.3333333333333333, 0.5], [1.0, 1.0, 1.0]]], 'C3': [[[1.0, 1.0, 1.0], [0.3333333333333333, 0.5, 1.0], [0.5, 1.0, 2.0], [0.2, 0.25, 0.3333333333333333]], [[1.0, 2.0, 3.0], [1.0, 1.0, 1.0], [0.3333333333333333, 0.5, 1.0], [0.14285714285714285, 0.16666666666666666, 0.2]], [[0.5, 1.0, 2.0], [1.0, 2.0, 3.0], [1.0, 1.0, 1.0], [0.2, 0.25, 0.3333333333333333]], [[3.0, 4.0, 5.0], [5.0, 6.0, 7.0], [3.0, 4.0, 5.0], [1.0, 1.0, 1.0]]], 'C4': [[[1.0, 1.0, 1.0], [1.0, 2.0, 3.0], [1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], [[0.3333333333333333, 0.5, 1.0], [1.0, 1.0, 1.0], [0.25, 0.3333333333333333, 0.5], [1.0, 2.0, 3.0]], [[0.3333333333333333, 0.5, 1.0], [2.0, 3.0, 4.0], [1.0, 1.0, 1.0], [3.0, 4.0, 5.0]], [[0.16666666666666666, 0.2, 0.25], [0.3333333333333333, 0.5, 1.0], [0.2, 0.25, 0.3333333333333333], [1.0, 1.0, 1.0]]], 'C5': [[[1.0, 1.0, 1.0], [1.0, 2.0, 3.0], [0.5, 1.0, 2.0], [0.3333333333333333, 0.5, 1.0]], [[0.3333333333333333, 0.5, 1.0], [1.0, 1.0, 1.0], [0.3333333333333333, 0.5, 1.0], [0.3333333333333333, 0.5, 1.0]], [[0.5, 1.0, 2.0], [1.0, 2.0, 3.0], [1.0, 1.0, 1.0], [0.3333333333333333, 0.5, 1.0]], [[1.0, 2.0, 3.0], [1.0, 2.0, 3.0], [1.0, 2.0, 3.0], [1.0, 1.0, 1.0]]], 'C6': [[[1.0, 1.0, 1.0], [0.3333333333333333, 0.5, 1.0], [0.3333333333333333, 0.5, 1.0], [0.16666666666666666, 0.2, 0.25]], [[1.0, 2.0, 3.0], [1.0, 1.0, 1.0], [0.3333333333333333, 0.5, 1.0], [0.125, 0.14285714285714285, 0.16666666666666666]], [[1.0, 2.0, 3.0], [1.0, 2.0, 3.0], [1.0, 1.0, 1.0], [0.125, 0.14285714285714285, 0.16666666666666666]], [[4.0, 5.0, 6.0], [6.0, 7.0, 8.0], [6.0, 7.0, 8.0], [1.0, 1.0, 1.0]]]}, 'source_criteria_table5': [0.0495, 0.3469, 0.099, 0.1087, 0.0495, 0.3465], 'source_criteria_table10': [0.04952, 0.3469, 0.099, 0.1087, 0.04947, 0.3465], 'source_local_table5': [[0.3514, 0.2297, 0.2688, 0.1502], [0.2591, 0.3124, 0.3124, 0.1161], [0.1249, 0.125, 0.1252, 0.6248], [0.4104, 0.1526, 0.3404, 0.0966], [0.239, 0.1563, 0.239, 0.3656], [0.1111, 0.1111, 0.1112, 0.6667]], 'source_criterion_system_contributions_table5': [[0.0174, 0.0114, 0.0133, 0.0074], [0.0899, 0.1084, 0.1084, 0.0403], [0.0124, 0.0124, 0.0124, 0.0619], [0.0446, 0.0166, 0.037, 0.0105], [0.0118, 0.0077, 0.0118, 0.0181], [0.0385, 0.0385, 0.0385, 0.231]], 'source_terminal_table5': [0.2146, 0.1949, 0.2214, 0.3692], 'source_terminal_ranks': [3, 4, 2, 1], 'source_lambda': [{'model': 'criteria', 'value': 0.0019}, {'model': 'C1', 'value': 0.6135}, {'model': 'C2', 'value': 0.7307}, {'model': 'C3', 'value': 0.0025}, {'model': 'C4', 'value': 0.2705}, {'model': 'C5', 'value': 0.6134}, {'model': 'C6', 'value': 0.0013}], 'caveats': ['Table2 body has original a45=(3,4,5) but reciprocal a54=(1/3,1/2,1) of reassessment; explicit reassessment note governs upper-triangle Eq3.', 'Eq4 visually places exp before fraction; interpreted as normalized exp(x), consistent with normalization instruction, text below equation, published weights and implementation.', 'Source text x_i=ln w_i uses an unnormalized precursor: x_i>=0 cannot represent log of a normalized weight below 1.', 'No lambda<=1 bound printed; this is unnecessary at optimum because any lambda>1 is dominated by lambda=1 at same x/slacks.']}

INDEPENDENT_CERTIFICATE_REVIEW_SOURCE = '"""Verify saved NP11 rational/interval certificates.\n\nUses 180-digit Decimal interval arithmetic and exact Fraction operations\nfor dual feasibility and LP reduced-cost checks. No optimizer is invoked.\n"""\nfrom pathlib import Path\nfrom fractions import Fraction as F\nfrom decimal import Decimal as D, localcontext, ROUND_FLOOR, ROUND_CEILING\nimport json,sys,hashlib\n\nP=180\nROOT=Path(__file__).resolve().parents[1]\nIN=ROOT/\'results/reference/robustness/R2C/NP11/face_certificates.json\'\nOUT=Path(__file__).resolve().parent\n\ndef rat(s):return F(s)\ndef enclosure(f):\n f=F(f)\n with localcontext() as c:\n  c.prec=P;c.rounding=ROUND_FLOOR;l=D(f.numerator)/D(f.denominator)\n  c.rounding=ROUND_CEILING;u=D(f.numerator)/D(f.denominator)\n return l,u\ndef add(a,b):\n with localcontext() as c:\n  c.prec=P;c.rounding=ROUND_FLOOR;l=a[0]+b[0]\n  c.rounding=ROUND_CEILING;u=a[1]+b[1]\n return l,u\ndef neg(a):\n # Decimal.copy_negate is context-free and exact.\n return a[1].copy_negate(),a[0].copy_negate()\ndef sub(a,b):return add(a,neg(b))\ndef mul(a,b):\n with localcontext() as c:\n  c.prec=P;c.rounding=ROUND_FLOOR;l=min(x*y for x in a for y in b)\n  c.rounding=ROUND_CEILING;u=max(x*y for x in a for y in b)\n return l,u\ndef divide_positive(a,b):\n assert b[0]>0\n with localcontext() as c:\n  c.prec=P;c.rounding=ROUND_FLOOR;l=D(1)/b[1]\n  c.rounding=ROUND_CEILING;u=D(1)/b[0]\n return mul(a,(l,u))\ndef square(a):\n if a[0]>=0:return mul(a,a)\n if a[1]<=0:return mul(neg(a),neg(a))\n return D(0),max(mul((a[0],a[0]),(a[0],a[0]))[1],mul((a[1],a[1]),(a[1],a[1]))[1])\ndef ln(a):\n assert a[0]>0\n with localcontext() as c:\n  c.prec=P\n  return a[0].ln().next_minus(),a[1].ln().next_plus()\ndef exp(a):\n with localcontext() as c:\n  c.prec=P\n  return a[0].exp().next_minus(),a[1].exp().next_plus()\ndef sqrt(a):\n assert a[0]>=0\n with localcontext() as c:\n  c.prec=P\n  return a[0].sqrt().next_minus(),a[1].sqrt().next_plus()\ndef isum(items):\n v=enclosure(0)\n for x in items:v=add(v,x)\n return v\n\ndef check_source(meta,source):\n name=meta[\'name\']\n if name.startswith(\'LOCAL_\'):\n  pairs=source[\'local_upper\'][name.removeprefix(\'LOCAL_\')]\n  remap={i:i for i in range(4)}\n else:\n  kept=[int(c[1:])-1 for c in meta[\'ids\']]\n  remap={old:new for new,old in enumerate(kept)}\n  pairs=[q for q in source[\'criteria_upper\'] if q[\'i\'] in remap and q[\'j\'] in remap]\n expected=[]\n for q in pairs:\n  l,m,u=map(F,q[\'exact_lmu\'].split());i,j=remap[q[\'i\']],remap[q[\'j\']]\n  for sign,a,b in [(1,m/l,l),(-1,u/m,1/u)]:\n   e=[0]*meta[\'n\'];e[i]=sign;e[j]=-sign;expected.append((e,a,b))\n assert len(expected)==len(meta[\'edge_E\'])\n for ix,(e,a,b) in enumerate(expected):\n  assert e==meta[\'edge_E\'][ix]\n  assert a==F(meta[\'edge_a_args\'][ix]) and b==F(meta[\'edge_b_args\'][ix])\n\ndef qp(meta,source):\n check_source(meta,source)\n E=meta[\'edge_E\'];x=list(map(F,meta[\'x_exact\']));lam=F(meta[\'lambda_exact\'])\n s=list(map(F,meta[\'slacks_exact\']));mu=list(map(F,meta[\'dual_mu_exact\']))\n assert min(x)>=0 and lam>=0 and min(s)>=0 and min(mu)>=0\n for j in range(len(x)):assert sum(F(row[j])*m for row,m in zip(E,mu))==0\n a=[ln(enclosure(F(q))) for q in meta[\'edge_a_args\']]\n b=[ln(enclosure(F(q))) for q in meta[\'edge_b_args\']]\n residuals=[]\n for row,aa,bb,ss in zip(E,a,b,s):\n  ex=sum(v*xx for v,xx in zip(row,x))\n  residuals.append(sub(sub(enclosure(ex+ss),mul(aa,enclosure(lam))),bb))\n assert min(v[0] for v in residuals)>=0,(meta[\'name\'],\'primal infeasible\',min(v[0] for v in residuals))\n primal=F(1-lam)**2+1000*sum(z*z for z in s)\n q=sub(enclosure(1),mul(enclosure(F(1,2)),isum(mul(aa,enclosure(m)) for aa,m in zip(a,mu))))\n q=(max(D(0),q[0]),max(D(0),q[1]))\n dual=sub(sub(add(isum(mul(bb,enclosure(m)) for bb,m in zip(b,mu)),enclosure(1)),square(q)),enclosure(sum(m*m for m in mu)/4000))\n gap=sub(enclosure(primal),dual)\n assert F(meta[\'objective_primal_upper\'])>=primal\n assert D(meta[\'dual_lower\'])<=dual[0]\n assert D(meta[\'gap_upper\'])>=gap[1]\n assert D(meta[\'lambda_error_upper\'])>=sqrt(enclosure(F(meta[\'gap_upper\'])))[1]\n assert D(meta[\'slack_error_upper\'])>=sqrt(enclosure(F(meta[\'gap_upper\'])/1000))[1]\n eps=F(meta[\'lambda_error_upper\']);eps_s=F(meta[\'slack_error_upper\']);llo=max(F(0),lam-eps)\n A=[]\n for ix,(row,aa,bb,ss,r) in enumerate(zip(E,a,b,s,meta[\'ratios_outer\'])):\n  lower=sub(add(bb,mul(aa,enclosure(llo))),enclosure(ss+eps_s));safe=exp(lower)\n  assert D(r)<=safe[0],(meta[\'name\'],ix,\'outer ratio not outward\',D(r),safe[0])\n  rr=[F(0)]*len(x);rr[row.index(1)]=-1;rr[row.index(-1)]=F(r);A.append(rr)\n # Check the support-stability certificate.\n support=[i for i,m in enumerate(mu) if m>0]\n assert support==meta[\'dual_support\']\n dual_radius=sqrt(enclosure(F(meta[\'gap_upper\'])*4000))[1]\n assert D(meta[\'dual_error_radius\'])>=dual_radius\n posmargin=sub(enclosure(min(mu[i] for i in support)),enclosure(F(meta[\'dual_error_radius\'])))\n assert 0<D(meta[\'positive_dual_margin_lower\'])<=posmargin[0]\n inactive=[sub(residuals[i],enclosure(s[i])) for i in range(len(E)) if i not in support]\n assert D(meta[\'inactive_slack_lower\'])<=min(v[0] for v in inactive)\n assert D(meta[\'max_positive_support_residual_upper\'])>=max(residuals[i][1] for i in support)\n maxa=max(aa[1] for aa in a)\n node_error=mul(enclosure(len(x)-1),add(add(mul((maxa,maxa),enclosure(eps)),enclosure(eps_s)),enclosure(F(meta[\'max_positive_support_residual_upper\']))))\n assert D(meta[\'true_optimum_tree_node_error_upper\'])>=node_error[1]\n margin=sub(sub(sub((min(v[0] for v in inactive),min(v[0] for v in inactive)),mul(enclosure(2),enclosure(F(meta[\'true_optimum_tree_node_error_upper\'])))),mul((maxa,maxa),enclosure(eps))),enclosure(eps_s))\n assert 0<D(meta[\'strict_inactive_margin_at_true_optimum_lower\'])<=margin[0]\n comps=[{j} for j in range(len(x))]\n for i in support:\n  aidx=E[i].index(1);bidx=E[i].index(-1)\n  ca=next(z for z in comps if aidx in z);cb=next(z for z in comps if bidx in z)\n  if ca is not cb:ca.update(cb);comps.remove(cb)\n assert meta[\'dimension_after_gauge\']==len(comps)-1\n # Validate explicit near-optimal feasible alternate x witnesses at 180 digits.\n witness_weights=[]\n for witness in meta.get(\'witnesses\',[]):\n  xx=list(map(F,witness[\'x_exact\']));assert min(xx)>=0\n  for row,aa,bb,ss in zip(E,a,b,s):\n   ex=sum(v*xxx for v,xxx in zip(row,xx))\n   rr=sub(sub(enclosure(ex+ss),mul(aa,enclosure(lam))),bb)\n   assert rr[0]>=0\n  exps=[exp(enclosure(v)) for v in xx];den=isum(exps)\n  witness_weights.append([divide_positive(ex,den) for ex in exps])\n if len(witness_weights)==2:\n  assert any(sub(aa,bb)[0]>0 or sub(aa,bb)[1]<0 for aa,bb in zip(*witness_weights))\n return A,dict(name=meta[\'name\'],minimum_constraint_residual_lower=str(min(v[0] for v in residuals)),primal_exact=str(primal),primal_180=enclosure(primal),dual_180=tuple(map(str,dual)),gap_180=tuple(map(str,gap)),saved_gap=meta[\'gap_upper\'],positive_dual_min=str(min(z for z in mu if z)),ratio_count=len(A),dimension_after_gauge=meta[\'dimension_after_gauge\'],support_stability=\'VERIFIED\',alternate_witnesses_verified=len(witness_weights),status=\'VERIFIED\')\n\ncount=0\ndef lp(cert,A):\n global count\n c=list(map(F,cert[\'coefficient_exact\']));y=list(map(F,cert[\'dual_y_exact\']));t=F(cert[\'certificate_t_exact\'])\n assert len(A)==len(y) and min(y)<=0 and max(y)<=0\n reduced=[c[j]-sum(row[j]*yy for row,yy in zip(A,y)) for j in range(len(c))]\n assert min(reduced)==t\n assert F(cert[\'lower\'])<=t\n assert F(cert[\'certificate_t\'])<=t\n assert all(v-t>=0 for v in reduced)\n count+=1\n return t\n\ndef recurse(v,A):\n if isinstance(v,dict):\n  if \'certificate_t_exact\' in v:\n   lp(v,A);return\n  for z in v.values():recurse(z,A)\n elif isinstance(v,list):\n  for z in v:recurse(z,A)\n\ndef main():\n data=json.loads(IN.read_text());source=json.loads((OUT/\'source_transcription.json\').read_text())\n faces={k:v for k,v in data.items() if k!=\'LOCAL_FACES\'}\n faces.update({\'LOCAL_\'+k:v for k,v in data[\'LOCAL_FACES\'].items()})\n report=[];matrices={}\n for key,meta in faces.items():\n  A,r=qp(meta,source);matrices[key]=A;report.append(r);recurse(meta.get(\'bounds\',{}),A);recurse(meta.get(\'weight_ranges\',{}),A)\n pair_count=0\n for key,meta in data.items():\n  if key==\'LOCAL_FACES\':continue\n  for pair,item in meta[\'bounds\'][\'frozen\'].items():\n   if pair==\'score_ranges\':continue\n   lo=lp(item[\'lower_certificate\'],matrices[key]);up=-lp(item[\'negative_upper_certificate\'],matrices[key])\n   assert lo>0 or up<0,(key,pair,\'unidentified sign\');pair_count+=1\n all_local_inner_available=all(bool(x.get(\'bounds\',{})) for x in data[\'LOCAL_FACES\'].values())\n all_local_pairs=0;other_sensitivity_pairs=0\n for key,meta in data.items():\n  if key==\'LOCAL_FACES\':continue\n  for pair,outer in meta[\'bounds\'][\'all_local_optima\'].items():\n   lo=lp(outer[\'lower_certificate\'],matrices[key]);hi=-lp(outer[\'negative_upper_certificate\'],matrices[key]);assert lo>0 or hi<0\n   clo=list(map(F,outer[\'lower_certificate\'][\'coefficient_exact\']));cneg_hi=list(map(F,outer[\'negative_upper_certificate\'][\'coefficient_exact\']))\n   for j,criterion in enumerate(meta[\'ids\']):\n    inner=data[\'LOCAL_FACES\'][criterion][\'bounds\'][pair]\n    assert clo[j]==F(inner[\'lower_certificate\'][\'certificate_t_exact\'])\n    assert cneg_hi[j]==F(inner[\'negative_upper_certificate\'][\'certificate_t_exact\'])\n   all_local_pairs+=1\n  for label in [\'published_rounded\',\'published_row_normalized\']:\n   for pair,item in meta[\'bounds\'][label].items():\n    if pair==\'score_ranges\':continue\n    lo=lp(item[\'lower_certificate\'],matrices[key]);hi=-lp(item[\'negative_upper_certificate\'],matrices[key]);assert lo>0 or hi<0\n    other_sensitivity_pairs+=1\n result=dict(source_certificate_sha256=hashlib.sha256(IN.read_bytes()).hexdigest(),precision=P,qp_witnesses=len(report),main_pair_signs_verified=pair_count,all_local_pair_signs_and_composition_verified=all_local_pairs,published_rounding_pair_signs_verified=other_sensitivity_pairs,total_lp_certificate_checks=count,all_local_inner_certificates_stored=all_local_inner_available,qp_checks=report)\n (OUT/\'certificate_review_results.json\').write_text(json.dumps(result,indent=2,default=str))\n print(json.dumps({k:v for k,v in result.items() if k!=\'qp_checks\'},indent=2))\n for r in report:print(r[\'name\'],r[\'status\'],\'gap\',r[\'gap_180\'],\'min_constraint\',r[\'minimum_constraint_residual_lower\'])\n\nif __name__==\'__main__\':main()\n'

from pathlib import Path
from fractions import Fraction
import argparse, csv, hashlib, itertools, json, math, platform, sys
import numpy as np
import scipy
from scipy import sparse
from scipy.optimize import minimize, LinearConstraint, Bounds, linprog
from scipy.special import softmax
import clarabel
import osqp

M = 1000.0


def model(pairs, ids):
    """Source Eq. (3), full x coordinates and source nonnegative bounds.

    q-vector order is x, lambda, lower deviations, upper deviations. B z >= b.
    Input exact fractions are converted once to binary64 for solver crosschecks.
    The separate rigorous certificate uses their rational values directly.
    """
    n = len(ids)
    k = len(pairs)
    N = n + 1 + 2*k
    B = np.zeros((2*k, N))
    b = np.zeros(2*k)
    for t, r in enumerate(pairs):
        i,j = r['i'],r['j']
        l,md,u = [float(Fraction(s)) for s in r['exact_lmu'].split()]
        B[2*t,i], B[2*t,j] = 1., -1.
        B[2*t,n], B[2*t,n+1+t] = -math.log(md/l), 1.
        b[2*t] = math.log(l)
        B[2*t+1,i], B[2*t+1,j] = -1., 1.
        B[2*t+1,n], B[2*t+1,n+1+k+t] = -math.log(u/md), 1.
        b[2*t+1] = -math.log(u)
    diag = np.r_[np.zeros(n), 2., np.repeat(2*M, 2*k)]
    c = np.zeros(N)
    c[n] = -2.
    return dict(n=n,k=k,N=N,B=B,b=b,diag=diag,c=c,ids=ids,pairs=pairs)


def objective(z, m):
    return float((1-z[m['n']])**2+M*np.dot(z[m['n']+1:],z[m['n']+1:]))


def kkt_metrics(z, alpha, beta, m):
    """Numerical, not interval, KKT metrics in original nonnegative formulation."""
    grad = m['diag']*z + m['c']
    slack = m['B']@z-m['b']
    stationarity = grad-m['B'].T@alpha-beta
    return dict(primal_violation=float(max(0.,-min(slack))),
                bound_violation=float(max(0.,-min(z))),
                dual_violation=float(max(0.,-min(alpha),-min(beta))),
                stationarity_inf=float(max(abs(stationarity))),
                complementarity_inf=float(max(max(abs(alpha*slack)),max(abs(beta*z)))))


def solve(m, solver):
    n,k,N,B,b = [m[s] for s in ['n','k','N','B','b']]
    P = sparse.diags(m['diag'],format='csc')
    G = sparse.csc_matrix(np.vstack([B,np.eye(N)]))
    h = np.r_[b,np.zeros(N)]
    settings = {}
    if solver == 'SLSQP':
        z0=np.r_[np.ones(n),.5,np.full(2*k,.1)]
        settings=dict(ftol=1e-14,maxiter=20000)
        r=minimize(lambda z:objective(z,m),z0,jac=lambda z:m['diag']*z+m['c'],
                   method='SLSQP',bounds=Bounds(np.zeros(N),np.full(N,np.inf)),
                   constraints=LinearConstraint(B,b,np.inf),options=settings)
        z=np.array(r.x)
        alpha=np.asarray(r.multipliers)
        beta=m['diag']*z+m['c']-B.T@alpha
        # SLSQP does not return bound multipliers. Recover them from stationarity;
        # their sign and complementarity are independently reported.
        status=str(r.status); message=str(r.message); success=bool(r.success)
        it=int(r.nit); solver_gap=None
    elif solver == 'CLARABEL':
        cfg=clarabel.DefaultSettings()
        cfg.verbose=False
        cfg.max_iter=300
        cfg.tol_gap_abs=1e-12; cfg.tol_gap_rel=1e-12; cfg.tol_feas=1e-12
        settings=dict(max_iter=300,tol_gap_abs=1e-12,tol_gap_rel=1e-12,tol_feas=1e-12)
        r=clarabel.DefaultSolver(P,m['c'],-G,-h,[clarabel.NonnegativeConeT(len(h))],cfg).solve()
        z=np.asarray(r.x); dual=np.asarray(r.z)
        alpha=dual[:2*k];beta=dual[2*k:]
        status=str(r.status);message=status;success=status in ['Solved','AlmostSolved']
        it=int(r.iterations); solver_gap=float(r.obj_val-r.obj_val_dual)
    elif solver == 'OSQP':
        settings=dict(eps_abs=1e-11,eps_rel=1e-11,max_iter=200000,polishing=True,
                      adaptive_rho=True,verbose=False)
        qp=osqp.OSQP();qp.setup(P=P,q=m['c'],A=G,l=h,u=np.full(len(h),np.inf),**settings)
        r=qp.solve(raise_error=False);z=np.asarray(r.x)
        alpha=-np.asarray(r.y[:2*k]);beta=-np.asarray(r.y[2*k:])
        status=str(r.info.status_val);message=str(r.info.status)
        success=r.info.status_val in [1,2];it=int(r.info.iter);solver_gap=None
    else:
        raise ValueError(solver)
    weights=softmax(z[:n])
    result=dict(solver=solver,solver_status=status,solver_message=message,
                solver_success=success,iterations=it,settings=settings,z=z.tolist(),
                dual_pairs=alpha.tolist(),dual_bounds=beta.tolist(),
                objective=objective(z,m),lambda_value=float(z[n]),weights=weights.tolist(),
                solver_reported_gap=solver_gap,**kkt_metrics(z,alpha,beta,m))
    # A direct numerical dual expression is a useful diagnostic only: exact
    # circulation and outward rounding are handled by the certificate module.
    a=-B[:,n]
    result['dual_circulation_residual']=float(max(abs(B[:,:n].T@alpha)))
    result['dual_value_numeric']=float(b@alpha+1.-max(0.,2.-a@alpha)**2/4.-(alpha@alpha)/(4*M))
    result['primal_dual_gap_numeric']=result['objective']-result['dual_value_numeric']
    return result


def reduced(pairs, drop):
    old=[i for i in range(6) if i!=drop]
    ix={v:i for i,v in enumerate(old)}
    pp=[dict(i=ix[p['i']],j=ix[p['j']],exact_lmu=p['exact_lmu']) for p in pairs
        if p['i'] in ix and p['j'] in ix]
    return pp,[f'C{i+1}' for i in old],old


def frozen_locals(repo):
    path=repo/'data/standardized/native/NP11/NP11_CALCULATED_INTERMEDIATES.csv'
    vals=np.zeros((6,4))
    with path.open(newline='',encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            if r['stage']=='local_system' and r['metric']=='weight':
                vals[int(r['basis'][1:])-1,int(r['item'][1:])-1]=float(r['value'])
    assert np.allclose(vals.sum(axis=1),1,atol=2e-11,rtol=0)
    return vals


def run_solver_crosschecks(source,repo,out):
    out.mkdir(parents=True,exist_ok=True)
    local=frozen_locals(repo)
    pub=np.asarray(source['source_local_table5'])
    allresults=[]
    for drop in [None,*range(6)]:
        pp,ids,keep=reduced(source['criteria_upper'],drop)
        m=model(pp,ids);case='BASELINE' if drop is None else f'DELETE_C{drop+1}'
        for solver in ['SLSQP','CLARABEL','OSQP']:
            r=solve(m,solver)
            r.update(case=case,n=m['n'],pairs=m['k'],variables=m['N'],constraints=2*m['k'],
                     local_basis='FROZEN_REPOSITORY_12_DECIMAL_LOCALS',ids=ids,
                     source_exact_triplets=pp)
            for label,lc in [('frozen',local),('published_raw',pub),('published_row_normalized',pub/pub.sum(axis=1)[:,None])]:
                # Compare row-normalized published weights as a separate rounding analysis.
                score=np.asarray(r['weights'])@lc[keep,:]
                r[label+'_scores']=score.tolist()
                r[label+'_ranking']='>'.join(f'S{i+1}' for i in np.argsort(-score))
            allresults.append(r)
            print(case,solver,r['solver_success'],f"f={r['objective']:.14f}",
                  f"primal={r['primal_violation']:.3g}",r['frozen_ranking'],flush=True)
    localresults=[]
    for c,pp in source['local_upper'].items():
        m=model(pp,[f'S{i}' for i in range(1,5)])
        for solver in ['SLSQP','CLARABEL','OSQP']:
            r=solve(m,solver);r.update(case='LOCAL_'+c,n=m['n'],pairs=m['k'],variables=m['N'])
            localresults.append(r)
    payload=dict(environment=dict(python=sys.version,numpy=np.__version__,scipy=scipy.__version__,
                                  clarabel=clarabel.__version__,osqp=osqp.__version__,platform=platform.platform()),
                 main=allresults,local=localresults,source=source,
                 frozen_locals=local.tolist(),published_locals=pub.tolist())
    (out/'solver_results.json').write_text(json.dumps(payload,indent=2))
    return payload



#!/usr/bin/env python3
"""LFPP optimum-face enclosures and rational/interval verification.

Uses exact-rational source TFNs, convex QP candidates, rational dual
circulations, outward Decimal bounds and exact-rational LP dual certificates.
"""
import sys, csv, json, math, argparse, itertools
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal as D, localcontext, getcontext, ROUND_FLOOR, ROUND_CEILING
import numpy as np
from scipy import sparse
from scipy.optimize import linprog
import clarabel, mpmath as mp, sympy as sp

PREC=90
getcontext().prec=PREC
mp.mp.dps=110
M=1000

class I:
    def __init__(self,a,b=None):
        self.a=self.convert(a,ROUND_FLOOR); self.b=self.convert(a if b is None else b,ROUND_CEILING)
    @staticmethod
    def convert(x,rd):
        with localcontext() as ctx:
            ctx.prec=PREC; ctx.rounding=rd
            if isinstance(x,F): return D(x.numerator)/D(x.denominator)
            return +D(str(x))
    @staticmethod
    def wrap(v): return v if isinstance(v,I) else I(v)
    def __add__(self,v):
        v=self.wrap(v)
        with localcontext() as ctx:
            ctx.prec=PREC; ctx.rounding=ROUND_FLOOR; a=self.a+v.a
            ctx.rounding=ROUND_CEILING; b=self.b+v.b
        return I(a,b)
    __radd__=__add__
    def __neg__(self): return I(-self.b,-self.a)
    def __sub__(self,v): return self+-self.wrap(v)
    def __rsub__(self,v): return self.wrap(v)+-self
    def __mul__(self,v):
        v=self.wrap(v)
        with localcontext() as ctx:
            ctx.prec=PREC; ctx.rounding=ROUND_FLOOR
            a=min(x*y for x in (self.a,self.b) for y in (v.a,v.b))
            ctx.rounding=ROUND_CEILING
            b=max(x*y for x in (self.a,self.b) for y in (v.a,v.b))
        return I(a,b)
    __rmul__=__mul__
    def __truediv__(self,v):
        v=self.wrap(v); assert v.a>0 or v.b<0
        with localcontext() as ctx:
            ctx.prec=PREC; ctx.rounding=ROUND_FLOOR; a=1/v.b
            ctx.rounding=ROUND_CEILING; b=1/v.a
        return self*I(a,b)
    def square(self):
        if self.a>=0: return self*self
        if self.b<=0: return (-self)*(-self)
        return I(0,max((I(self.a)*I(self.a)).b,(I(self.b)*I(self.b)).b))
    def sqrt(self):
        assert self.a>=0
        with localcontext() as ctx:
            ctx.prec=PREC
            return I(self.a.sqrt().next_minus(),self.b.sqrt().next_plus())
    def ln(self):
        assert self.a>0
        with localcontext() as ctx:
            ctx.prec=PREC
            return I(self.a.ln().next_minus(),self.b.ln().next_plus())
    def exp(self):
        with localcontext() as ctx:
            ctx.prec=PREC
            return I(self.a.exp().next_minus(),self.b.exp().next_plus())

def mpf(f):
    if isinstance(f,F): return mp.mpf(f.numerator)/f.denominator
    return mp.mpf(str(f))

def exact_float(x): return F(str(float(x)))

def fq(x): return str(x.numerator)+'/'+str(x.denominator)

def build(pairs,ids):
    n=len(ids); index={v:k for k,v in enumerate(ids)}; edges=[]
    for r in pairs:
        i,j=index[r['row_id']],index[r['col_id']]
        # All source entries are integers or reciprocals of integers <=9.
        l,m,u=([F(z) for z in r['exact_lmu'].split()] if 'exact_lmu' in r else [F(r[k]).limit_denominator(100) for k in ('l','m','u')])
        for s,lval,ar in [(1,l,m/l),(-1,1/u,u/m)]:
            e=np.zeros(n,dtype=int); e[i]=s; e[j]=-s
            edges.append({'i':i,'j':j,'sign':s,'e':e.tolist(),'b_arg':lval,'a_arg':ar,'pair':r['input_id']})
    E=np.array([e['e'] for e in edges],dtype=int)
    b=np.array([math.log(float(e['b_arg'])) for e in edges])
    a=np.array([math.log(float(e['a_arg'])) for e in edges])
    return n,E,b,a,edges

def rational_circulation(E,a,b,mu):
    support=np.flatnonzero(mu>1e-6)
    basis=sp.Matrix(E[support].T.tolist()).nullspace()
    assert basis
    Bs=sp.Matrix.hstack(*basis)
    B=[[F(int(z.p),int(z.q)) for z in Bs.row(i)] for i in range(Bs.rows)]
    Bm=mp.matrix([[mpf(z) for z in row] for row in B]); am=mp.matrix([a[i] for i in support]); bm=mp.matrix([b[i] for i in support])
    H=Bm.T*(am*am.T+mp.eye(len(support))/M)*Bm
    rhs=2*Bm.T*(am+bm)
    ys=mp.lu_solve(H,rhs)
    yq=[F(mp.nstr(v,80)) for v in ys]
    mus=[sum((v*y for v,y in zip(row,yq)),F()) for row in B]
    allmu=[F() for _ in a]
    for ix,v in zip(support,mus): allmu[int(ix)]=v
    assert min(allmu)>=0
    for j in range(E.shape[1]): assert sum((int(E[i,j])*allmu[i] for i in range(len(a))),F())==0
    return allmu,support.tolist()

def solve_face(name,pairs,ids):
    n,E,b,a,edges=build(pairs,ids); k=len(edges); N=n-1+1+k
    P=np.zeros(N); P[n-1]=2;P[n:]=2*M
    q=np.zeros(N);q[n-1]=-2
    A=np.column_stack([E[:,:n-1],-a,np.eye(k)])
    G=np.vstack([-A,np.column_stack([np.zeros((k+1,n-1)),-np.eye(k+1)])]); h=np.r_[-b,np.zeros(k+1)]
    sett=clarabel.DefaultSettings();sett.verbose=False;sett.tol_gap_abs=1e-13;sett.tol_gap_rel=1e-13;sett.tol_feas=1e-13;sett.max_iter=500
    sol=clarabel.DefaultSolver(sparse.diags(P,format='csc'),q,sparse.csc_matrix(G),h,[clarabel.NonnegativeConeT(G.shape[0])],sett).solve()
    z=np.array(sol.x); mu=np.array(sol.z[:k]); x=np.r_[z[:n-1],0.]
    am=[mp.log(mpf(e['a_arg'])) for e in edges]; bm=[mp.log(mpf(e['b_arg'])) for e in edges]
    muq,supp=rational_circulation(E,am,bm,mu)
    # Refine a primal witness using a spanning forest of positive-multiplier edges.
    lmp=1-sum((am[i]*mpf(muq[i]) for i in range(k)),mp.mpf(0))/2
    assert lmp>0
    xmp=[None]*n
    for root in range(n):
        if xmp[root] is not None: continue
        xmp[root]=mp.mpf(str(float(x[root])))
        todo=[root]
        while todo:
            p=todo.pop()
            for hix in supp:
                e=edges[hix];i,j,s=e['i'],e['j'],e['sign']
                diff=s*(bm[hix]+am[hix]*lmp-mpf(muq[hix])/(2*M))
                if i==p and xmp[j] is None: xmp[j]=xmp[i]-diff;todo.append(j)
                if j==p and xmp[i] is None: xmp[i]=xmp[j]+diff;todo.append(i)
    shift=min(xmp)
    xq=[F(mp.nstr(v-shift+1,75)) for v in xmp];lamq=F(mp.nstr(lmp,75))
    bi=[I(e['b_arg']).ln() for e in edges];ai=[I(e['a_arg']).ln() for e in edges]
    # Set each slack to an outward upper bound of its exact requirement.
    sq=[]
    for i in range(k):
        ex=sum((int(E[i,j])*xq[j] for j in range(n)),F())
        req=bi[i]+ai[i]*I(lamq)-I(ex)
        sq.append(F(max(D(0),req.b)))
    primal=(I(1)-I(lamq)).square()+M*sum((I(v).square() for v in sq),I(0))
    dual_lam=I(1)-sum((ai[i]*I(muq[i]) for i in range(k)),I(0))/2
    dual_lam=I(max(D(0),dual_lam.a),max(D(0),dual_lam.b))
    dual=sum((bi[i]*I(muq[i]) for i in range(k)),I(0))+1-dual_lam.square()-sum((I(v).square()/(4*M) for v in muq),I(0))
    gap=(primal-dual).b; assert gap>=0
    eps=I(gap).sqrt().b; eps_s=(I(gap)/M).sqrt().b
    llo=max(D(0),(I(lamq)-I(eps)).a)
    # The outer ratio polytope is encoded by exact rational inequalities Aw<=0.
    Ar=[]; ratios=[]
    for i,e in enumerate(edges):
        # e.x >= b + a*lambda - s. Use weak lower RHS.
        lower=(bi[i]+ai[i]*I(llo)-(I(sq[i])+I(eps_s))).a
        ratio=I(lower).exp().a
        r=[F() for _ in range(n)]
        if e['sign']==1: first,second=e['i'],e['j']
        else: first,second=e['j'],e['i']
        r[first]=-1;r[second]=F(ratio)
        Ar.append(r);ratios.append(str(ratio))
    components=[{i} for i in range(n)]
    for hix in supp:
        v=list(np.flatnonzero(E[hix]));first=next(z for z in components if v[0] in z);second=next(z for z in components if v[1] in z)
        if first is not second:first.update(second);components.remove(second)
    inactive=[]
    support_residual=[]
    for i in range(k):
        ex=sum((int(E[i,j])*xq[j] for j in range(n)),F())
        if i in supp:
            support_residual.append((I(sq[i])-(bi[i]+ai[i]*I(lamq)-I(ex))).b)
        else:
            inactive.append((I(ex)-bi[i]-ai[i]*I(lamq)).a)
    dual_radius=(I(gap)*4*M).sqrt().b
    positive_dual_margin=(I(min(muq[i] for i in supp))-I(dual_radius)).a
    assert positive_dual_margin>0
    max_a=max(v.b for v in ai)
    node_error=((n-1)*(I(max_a)*I(eps)+I(eps_s)+I(max(support_residual)))).b
    strict_inactive_margin=(I(min(inactive))-2*I(node_error)-I(max_a)*I(eps)-I(eps_s)).a if inactive else D(1)
    assert strict_inactive_margin>0
    witnesses=[]
    if len(components)>1:
        for sign in [-1,1]:
            xx=[v+(F(sign,1000) if j in components[-1] else 0) for j,v in enumerate(xq)]
            rr=[]
            for i in range(k):
                ex=sum((int(E[i,j])*xx[j] for j in range(n)),F())
                req=bi[i]+ai[i]*I(lamq)-I(ex)
                rr.append((I(sq[i])-req).a)
            assert min(rr)>=0
            ww=[mp.exp(mpf(v)) for v in xx];ws=sum(ww)
            witnesses.append({'x_exact':[fq(v) for v in xx],'weights':[mp.nstr(v/ws,30) for v in ww],'min_constraint_residual_lower':str(min(rr)),'same_exact_lambda_slacks':True})
    meta={'name':name,'ids':ids,'n':n,'constraint_edges':k,'solver_status':str(sol.status),'objective_primal_upper':str(primal.b),'dual_lower':str(dual.a),'gap_upper':str(gap),'lambda':str(float(lamq)),'lambda_error_upper':str(eps),'slack_error_upper':str(eps_s),'dual_support':supp,'dual_flow_exact':True,'x':[str(v.numerator/v.denominator) for v in xq],'slacks':[str(float(v)) for v in sq],'dual_mu':[str(float(v)) for v in muq],'x_exact':[fq(v) for v in xq],'lambda_exact':fq(lamq),'slacks_exact':[fq(v) for v in sq],'dual_mu_exact':[fq(v) for v in muq],'edge_E':E.tolist(),'edge_a_args':[fq(e['a_arg']) for e in edges],'edge_b_args':[fq(e['b_arg']) for e in edges],'weight':[float(v) for v in np.exp(np.array([float(v) for v in xq])-max(float(v) for v in xq))/np.exp(np.array([float(v) for v in xq])-max(float(v) for v in xq)).sum()],'ratios_outer':ratios,'bounds':{},'positive_dual_components':[[ids[i] for i in sorted(comp)] for comp in components],'dimension_after_gauge':len(components)-1,'inactive_slack_lower':str(min(inactive)) if inactive else None,'dual_error_radius':str(dual_radius),'positive_dual_margin_lower':str(positive_dual_margin),'max_positive_support_residual_upper':str(max(support_residual)),'true_optimum_tree_node_error_upper':str(node_error),'strict_inactive_margin_at_true_optimum_lower':str(strict_inactive_margin),'witnesses':witnesses}
    return {'name':name,'A':Ar,'meta':meta,'xq':xq,'lamq':lamq,'sq':sq,'muq':muq,'E':E,'a':ai,'b':bi}

def lp_lower(face,c):
    A=face['A'];n=len(c)
    res=linprog(np.array([float(x) for x in c]),A_ub=np.array([[float(x) for x in r] for r in A]),b_ub=np.zeros(len(A)),A_eq=np.ones((1,n)),b_eq=[1],bounds=(0,None),method='highs',options={'primal_feasibility_tolerance':1e-10,'dual_feasibility_tolerance':1e-10})
    if not res.success: raise RuntimeError(res.message)
    y=[min(F(),exact_float(v)) for v in res.ineqlin.marginals]
    reduced=[c[j]-sum((A[i][j]*y[i] for i in range(len(A))),F()) for j in range(n)]
    t=min(reduced)
    # This exact rational lower bound needs no assumption that solver optimum or dual is accurate.
    return t,{'lower':str(I(t).a),'solver_value':float(res.fun),'weights':res.x.tolist(),'dual_y':[str(float(v)) for v in y],'dual_y_exact':[fq(v) for v in y],'coefficient_exact':[fq(v) for v in c],'certificate_t':str(I(t).a),'certificate_t_exact':fq(t),'slack_dual_min':str(I(min(v-t for v in reduced)).a)}

def lp_range(face,c):
    lo,lc=lp_lower(face,c);neghi,hc=lp_lower(face,[-v for v in c])
    return lo,-neghi,{'lower':lc['lower'],'upper':str(I(-neghi).b),'min_w':lc['weights'],'max_w':hc['weights'],'lower_certificate':lc,'negative_upper_certificate':hc}

def run_certification(source,repo_root,out):
    from types import SimpleNamespace
    args=SimpleNamespace(repo_root=repo_root,out=out)
    args.out.mkdir(exist_ok=True,parents=True)
    extracted=list(csv.DictReader((args.repo_root/'data/extracted/native/NP11/NP11_EXTRACTION.csv').open()))
    rows=[]
    for kind,basis,prefix,values in [('criteria_pairwise','criteria','C',source['criteria_upper'])]+[('alternative_pairwise',c,'S',v) for c,v in source['local_upper'].items()]:
        for r in values:
            rowid=prefix+str(r['i']+1);colid=prefix+str(r['j']+1)
            rr={'kind':kind,'basis':basis,'row_id':rowid,'col_id':colid,'exact_lmu':r['exact_lmu'],'input_id':kind+'_'+basis+'_'+rowid+'_'+colid}
            frozen=next(v for v in extracted if v['kind']==kind and v['basis']==basis and v['row_id']==rowid and v['col_id']==colid)
            assert all(float(F(v))==float(frozen[k]) for v,k in zip(r['exact_lmu'].split(),('l','m','u')))
            rows.append(rr)
    inter=list(csv.DictReader((args.repo_root/'results/reference/native/NP11/NP11_CALCULATED_INTERMEDIATES.csv').open()))
    ids=[f'C{i}' for i in range(1,7)];cp=[r for r in rows if r['kind']=='criteria_pairwise']
    local_frozen=[[F(next(r['value'] for r in inter if r['stage']=='local_system' and r['basis']==c and r['item']==f'S{s}' and r['metric']=='weight')) for s in range(1,5)] for c in ids]
    local_pub=[[F(str(v)) for v in row] for row in source['source_local_table5']]
    faces={}
    for d in [None]+ids:
        keep=[c for c in ids if c!=d];key='BASELINE' if d is None else 'DELETE_'+d
        f=solve_face(key,[r for r in cp if r['row_id']!=d and r['col_id']!=d],keep); faces[key]=f
        indices=[ids.index(c) for c in keep]
        for witness in f['meta']['witnesses']:
            witness['terminal_scores_frozen']=[mp.nstr(sum((mp.mpf(witness['weights'][j])*mpf(local_frozen[i][s]) for j,i in enumerate(indices)),mp.mpf(0)),25) for s in range(4)]
        for label,local in [('frozen',local_frozen),('published_rounded',local_pub),('published_row_normalized',[[v/sum(row) for v in row] for row in local_pub])]:
            f['meta']['bounds'][label]={}
            for a,b in itertools.combinations(range(4),2):
                coeff=[local[i][a]-local[i][b] for i in indices]
                lo,hi,res=lp_range(f,coeff);f['meta']['bounds'][label][f'S{a+1}-S{b+1}']=res
            f['meta']['bounds'][label]['score_ranges']={}
            for a in range(4):
                lo,hi,res=lp_range(f,[local[i][a] for i in indices]);f['meta']['bounds'][label]['score_ranges'][f'S{a+1}']=res
        f['meta']['weight_ranges']={}
        for i,c in enumerate(keep):
            lo,hi,res=lp_range(f,[F(int(i==j)) for j in range(len(keep))]);f['meta']['weight_ranges'][c]=res
        print(key,'gap',f['meta']['gap_upper'],'lambda',f['meta']['lambda'])
        print({k:(v['lower'],v['upper']) for k,v in f['meta']['bounds']['frozen'].items() if k!='score_ranges'})
    # Global baseline allowing every local LFPP global optimizer independently.
    local_faces={}
    local_pair_bounds={}
    for c in ids:
        local_faces[c]=solve_face('LOCAL_'+c,[r for r in rows if r['kind']=='alternative_pairwise' and r['basis']==c],[f'S{i}' for i in range(1,5)])
        local_pair_bounds[c]={}
        for a,b in itertools.combinations(range(4),2):
            lo,hi,cert=lp_range(local_faces[c],[F(int(i==a)-int(i==b)) for i in range(4)])
            local_pair_bounds[c][(a,b)]=(lo,hi)
            local_faces[c]['meta']['bounds'][f'S{a+1}-S{b+1}']=cert
        local_faces[c]['meta']['weight_ranges']={}
        for a in range(4):
            lo,hi,cert=lp_range(local_faces[c],[F(int(i==a)) for i in range(4)])
            local_faces[c]['meta']['weight_ranges'][f'S{a+1}']=cert
    for key,f in faces.items():
        f['meta']['bounds']['all_local_optima']={}
        for a,b in itertools.combinations(range(4),2):
            lower=[];upper=[]
            for c in f['meta']['ids']:
                lo,hi=local_pair_bounds[c][(a,b)];lower.append(lo);upper.append(hi)
            lo,lc=lp_lower(f,lower);nhi,hc=lp_lower(f,[-v for v in upper]);hi=-nhi
            f['meta']['bounds']['all_local_optima'][f'S{a+1}-S{b+1}']={'lower':str(I(lo).a),'upper':str(I(hi).b),'lower_certificate':lc,'negative_upper_certificate':hc}
        print(key,'ALL LOCALS',{k:(v['lower'],v['upper']) for k,v in f['meta']['bounds']['all_local_optima'].items()})
    result={k:f['meta'] for k,f in faces.items()}; result['LOCAL_FACES']={k:f['meta'] for k,f in local_faces.items()}
    (args.out/'face_certificates.json').write_text(json.dumps(result,indent=2))
    # Emit standalone, sparse summary for fast audit.
    with (args.out/'pair_bounds.csv').open('w',newline='') as h:
        w=csv.writer(h);w.writerow(['model','locals','contrast','lower_certificate','upper_certificate'])
        for key,f in faces.items():
            for src,br in f['meta']['bounds'].items():
                for pair,v in br.items():
                    if pair!='score_ranges':w.writerow([key,src,pair,v['lower'],v['upper']])


    return result,faces,local_faces






def verify_saved_certificates(certificates):
    """Independent serialized-proof check; does not invoke any optimizer.

    Rebuilds every LP lower bound with exact Fraction operations, and checks
    rational primal/dual witnesses at 180-digit mpmath precision. High precision
    replay is QA; outward interval construction is the actual enclosure proof.
    """
    models={k:v for k,v in certificates.items() if k!='LOCAL_FACES'}
    models.update({'LOCAL_'+k:v for k,v in certificates['LOCAL_FACES'].items()})
    counts=dict(qp=0,lp=0,feasible_witnesses=0)
    with mp.workdps(180):
        for key,meta in models.items():
            E=meta['edge_E'];a=[mp.log(mpf(F(v))) for v in meta['edge_a_args']]
            b=[mp.log(mpf(F(v))) for v in meta['edge_b_args']]
            x=[F(v) for v in meta['x_exact']];lam=F(meta['lambda_exact'])
            s=[F(v) for v in meta['slacks_exact']];mu=[F(v) for v in meta['dual_mu_exact']]
            assert min(x)>=0 and lam>=0 and min(s)>=0 and min(mu)>=0
            assert all(sum((F(E[i][j])*mu[i] for i in range(len(E))),F())==0 for j in range(len(x)))
            for xx in [x]+[[F(v) for v in w['x_exact']] for w in meta['witnesses']]:
                residual=[sum((E[i][j]*mpf(xx[j]) for j in range(len(x))),mp.mpf(0))-a[i]*mpf(lam)+mpf(s[i])-b[i] for i in range(len(E))]
                assert min(residual)>=-mp.mpf('1e-150')
                counts['feasible_witnesses']+=1
            primal=(1-mpf(lam))**2+M*sum((mpf(v)**2 for v in s),mp.mpf(0))
            dual=sum((b[i]*mpf(mu[i]) for i in range(len(E))),mp.mpf(0))+1-max(mp.mpf(0),1-sum((a[i]*mpf(mu[i]) for i in range(len(E))),mp.mpf(0))/2)**2-sum((mpf(v)**2 for v in mu),mp.mpf(0))/(4*M)
            assert -mp.mpf('1e-150')<=primal-dual<=mp.mpf(meta['gap_upper'])
            counts['qp']+=1
            A=[]
            for edge,ratio in zip(E,meta['ratios_outer']):
                rr=[F() for _ in x];rr[edge.index(1)]=-1;rr[edge.index(-1)]=F(ratio);A.append(rr)
            def check_node(obj):
                if isinstance(obj,dict):
                    if 'certificate_t_exact' in obj:
                        c=[F(v) for v in obj['coefficient_exact']];y=[F(v) for v in obj['dual_y_exact']]
                        assert max(y)<=0
                        t=min(c[j]-sum((A[i][j]*y[i] for i in range(len(A))),F()) for j in range(len(c)))
                        assert t==F(obj['certificate_t_exact'])
                        assert mpf(t)>=mp.mpf(obj['lower'])
                        counts['lp']+=1
                    else:
                        for v in obj.values(): check_node(v)
                elif isinstance(obj,list):
                    for v in obj:check_node(v)
            check_node(meta.get('bounds',{}));check_node(meta.get('weight_ranges',{}))
    return counts




def interval_softmax_exact(x_exact):
    x=[F(v) for v in x_exact]; shift=max(x)
    e=[I(v-shift).exp() for v in x];den=sum(e,I(0))
    return [v/den for v in e]


def verify_score_nonuniqueness(certificates,frozen_locals):
    """Return proof bounds for fixed frozen and jointly optimal local vectors.

    If |h|_infinity<=epsilon, the softmax score T=a^T softmax(x)
    satisfies |T(x+h)-T(x)|<=range(a)*epsilon. This follows from
    grad_j(T)=w_j(a_j-T) and sum_j|grad_j(T)|<=range(a).
    Each coordinate of a local softmax also has range=1 as a score functional.
    Thus a joint score changes by at most epsilon_criteria+max epsilon_local,
    taking a deliberately conservative unit range for all normalized locals.
    """
    local_centers={k:interval_softmax_exact(v['x_exact']) for k,v in certificates['LOCAL_FACES'].items()}
    result={}
    for model,cert in certificates.items():
        if model=='LOCAL_FACES':continue
        assert len(cert['witnesses'])==2
        # The witnesses move one component by 0.001. The certified inactive
        # center margin remains positive, so true-v transport is still feasible.
        transport_feasible_margin=(I(cert['strict_inactive_margin_at_true_optimum_lower'])-I('0.001')).a
        assert transport_feasible_margin>0
        ew=I(cert['true_optimum_tree_node_error_upper'])
        witness_weights=[interval_softmax_exact(w['x_exact']) for w in cert['witnesses']]
        model_result={'true_optimum_transport_feasible_margin_lower':str(transport_feasible_margin),'scenarios':{}}
        for scenario in ('frozen_locals','joint_local_optima'):
            if scenario=='frozen_locals':
                local=[[I(v) for v in frozen_locals[k]] for k in cert['ids']]
                errors=[ew*I(max(frozen_locals[k][s] for k in cert['ids'])-min(frozen_locals[k][s] for k in cert['ids'])) for s in range(4)]
            else:
                local=[local_centers[k] for k in cert['ids']]
                el=I(max(D(certificates['LOCAL_FACES'][k]['true_optimum_tree_node_error_upper']) for k in cert['ids']))
                errors=[ew+el for _ in range(4)]
            scores=[[sum((w[j]*local[j][s] for j in range(len(local))),I(0)) for s in range(4)] for w in witness_weights]
            proof={}
            for s in range(4):
                diff=scores[1][s]-scores[0][s]
                if diff.a>0:
                    separation=I(diff.a)-2*errors[s]
                elif diff.b<0:
                    separation=I(-diff.b)-2*errors[s]
                else:
                    separation=I(0)-2*errors[s]
                proof[f'S{s+1}']={
                    'witness_minus_score_interval':[str(scores[0][s].a),str(scores[0][s].b)],
                    'witness_plus_score_interval':[str(scores[1][s].a),str(scores[1][s].b)],
                    'rational_witness_score_difference_interval':[str(diff.a),str(diff.b)],
                    'per_witness_score_transport_error_upper':str(errors[s].b),
                    'true_optimum_score_separation_lower':str(separation.a),
                    'score_nonunique_certified':separation.a>0,
                }
            assert all(v['score_nonunique_certified'] for v in proof.values())
            model_result['scenarios'][scenario]={'terminal_vector_nonunique_certified':True,'coordinates':proof}
        result[model]=model_result
    return result






