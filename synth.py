import subprocess

import ir
import visitor
from rosette import RosetteTranslator
from vcgen import VarIdentifier


class ChoiceReplacer(visitor.PassthruVisitor):
  def __init__(self, choices):
    super().__init__(self.__class__.__name__)
    self.choices = choices
    self.choice_num = 0

  def visit_Choose(self, n):
    r = n.args[self.choices[self.choice_num]]
    self.choice_num = self.choice_num + 1
    return r

def remove_choices(p, choices):
  return ChoiceReplacer(choices).visit(p)

rosette_synfile = '/tmp/s.rkt'
rosette_verfile = '/tmp/v.rkt'
racket_path = 'racket'  # path to racket exe
def synthesize(n: ir.Program, lang: ir.Program, info, inv_fn, ps_fn):
  new_stmts = []

  # add language definition
  for s in lang.stmts:
    if isinstance(s, ir.FnDecl):
      new_stmts.append(s)

  for s in n.stmts:
    if isinstance(s, ir.FnDecl):
      if s.name.startswith('inv') or s.name == 'ps':
        ast_info = info[s]
        read_vars = {a.name: a for a in ast_info[1]}
        write_vars = {a.name: a for a in ast_info[2]}
        new_body = inv_fn(ast_info[0], read_vars, write_vars) if s.name.startswith('inv') else\
                   ps_fn(ast_info[0], read_vars, write_vars)
        new_stmts.append(ir.FnDecl(s.name, s.args, s.rtype, new_body))
    else:
      new_stmts.append(s)

  mod_prog = ir.Program(n.imports, new_stmts)

  # synthesis
  rt = RosetteTranslator(True, max_num=4)
  with open(rosette_synfile, 'w') as f:
    f.write(rt.to_rosette(mod_prog))

  result = subprocess.check_output([racket_path, rosette_synfile], stderr=subprocess.STDOUT)
  print('synthesis result: %s' % result)

  choices = rt.parse_output(result)
  print('choices: %s' % choices)

  mod_prog = remove_choices(mod_prog, choices)

  # verification
  rt = RosetteTranslator(False)
  with open(rosette_verfile, 'w') as f:
    f.write(rt.to_rosette(mod_prog))

  result = subprocess.check_output([racket_path, rosette_verfile], stderr=subprocess.STDOUT)
  print('verification result: %s' % str(result))

  return mod_prog
