import os
import sys
from llvmlite import binding as llvm

from analysis import CodeInfo, setupBlocks, parseSrets, parseLoops, processLoops, processBranches
from ir import Choose, Lit, And, Ge, Eq, Le, Sub, Synth, Or, Pred, Int
from synthesis import synthesize_new
from vc import VC


# # programmatically generated grammar

# (synth-fun ps ( (tmp14 Int) (arg Int) ) Bool
#  ((B Bool) (C Bool) (D Bool) (E Int) (F Int))
#  ((B Bool ((or C D)))
#  (C Bool ((>= F arg)))
#  (D Bool ((= E (sum_n (- arg F)))))
#  (E Int (tmp14))
#  (F Int (1))))

# (synth-fun inv0 ((tmp1 Int) (tmp2 Int) (arg Int) ) Bool
#    ((B Bool) (C Bool) (D Bool) (E Int) (F Int))
#    ((B Bool ((or C D)))
#    (C Bool ((>= 1 arg) ))
#    (D Bool ((and (>= E 1) (<= E arg) (= E (sum_n (- E F))))))
#    (E Int (tmp1 tmp2))
#    (F Int (1))))

def genGrammar_while3(ci: CodeInfo):
  name = ci.name

  if name.startswith("inv"):
    f = Choose(Lit(1, Int()))
    e = Choose(*ci.modifiedVars)
    d = And(Ge(e, Lit(1, Int())), Le(e, ci.readVars[0]),
            Eq(e, Pred("sum_n", Int(), Sub(e, f))))
    c = Ge(Lit(1, Int()), ci.readVars[0])
    b = Or(c, d)
    return Synth(ci.name, b, *ci.modifiedVars, *ci.readVars)

  else:  # ps
    arg = ci.readVars[0]
    rv = ci.modifiedVars[0]

    f = Choose(Lit(1, Int()))
    e = Choose(rv)
    d = Eq(e, Pred("sum_n", Int(), Sub(arg, f)))
    c = Ge(f, arg)
    b = Or(c, d)
    return Synth(name, b, *ci.modifiedVars, *ci.readVars)


if __name__ == "__main__":
  filename = sys.argv[1]
  basename = os.path.splitext(os.path.basename(filename))[0]

  targetLangFile = sys.argv[2]
  fnName = sys.argv[3]
  loopsFile = sys.argv[4]
  cvcPath = sys.argv[5]


  with open(filename, mode="r") as file:
    ref = llvm.parse_assembly(file.read())

    fn = ref.get_function(fnName)
    blocksMap = setupBlocks(fn.blocks)

    parseSrets(list(fn.arguments), blocksMap.values())

    loops = parseLoops(loopsFile, fnName) if loopsFile else None
    loopAndPsInfo = []
    for l in loops:
      # assume for now there is only one header block
      if len(l.header) > 1: raise Exception("multiple loop headers: %s" % l)
      loopAndPsInfo.append(processLoops(blocksMap[l.header[0]], [blocksMap[n] for n in l.body],
                           [blocksMap[n] for n in l.exits], [blocksMap[n] for n in l.latches],
                           list(fn.arguments)))

    # add ps code info
    loopAndPsInfo = loopAndPsInfo + processBranches(blocksMap, list(fn.arguments))

    print("====== after transforms")
    for b in blocksMap.values():
      print("blk: %s" % b.name)
      for i in b.instructions:
        print("%s" % i)

    print("====== compute vc")
    (vars, invAndPs, preds, vc) = VC().computeVC(blocksMap, list(fn.blocks)[0].name, list(fn.arguments))

    print("====== synthesis")
    invAndPs = [genGrammar_while3(ci) for ci in loopAndPsInfo]

    targetLang = open(targetLangFile, mode="r").read()

    synthesize_new(targetLang, invAndPs, vars, preds, vc, cvcPath, basename)