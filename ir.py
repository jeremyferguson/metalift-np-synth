from enum import Enum

class Expr:
  class Kind(Enum):
    Var = "var"
    Lit = "lit"

    Add = "+"

    Eq = "="
    Lt = "<"
    Lte = "<="

    And = "and"
    Or = "or"
    Not = "not"

    Implies = "=>"
    Iff = "iff"

    Ite = "ite"

    Pred = "pred"

    Assert = "assert"

  def __init__(self, kind, args):
    self.kind = kind
    self.args = args

  def __repr__(self):
    kind = self.kind
    if kind == Expr.Kind.Var or kind == Expr.Kind.Lit:
      return str(self.args[0])
    elif kind == Expr.Kind.Pred:
      return "(" + " ".join([str(a) for a in self.args]) + ")"
    else:
      return "(" + self.kind.value + " " + " ".join([str(a) for a in self.args]) + ")"

  def __eq__(self, other):
    if isinstance(other, Expr):
      if self.kind != other.kind or len(self.args) != len(other.args):
        return False
      else:
        return all( a1.__eq__(a2) for a1,a2 in zip(self.args, other.args))
    return NotImplemented

  def __ne__(self, other):
    x = self.__eq__(other)
    if x is not NotImplemented:
      return not x
    return NotImplemented

  def __hash__(self):
    return hash(tuple(sorted({'kind': self.kind, 'args': tuple(self.args)})))

  @staticmethod
  def Var(name, ty): return Expr(Expr.Kind.Var, [name, ty])
  @staticmethod
  def Lit(val): return Expr(Expr.Kind.Lit, [val])

  @staticmethod
  def Add(*args): return Expr(Expr.Kind.Add, args)

  @staticmethod
  def Eq(e1, e2): return Expr(Expr.Kind.Eq, [e1, e2])
  @staticmethod
  def Lt(e1, e2): return Expr(Expr.Kind.Lt, [e1, e2])
  @staticmethod
  def Lte(e1, e2): return Expr(Expr.Kind.Lte, [e1, e2])

  @staticmethod
  def And(*args): return Expr(Expr.Kind.And, args)
  @staticmethod
  def Or(*args): return Expr(Expr.Kind.Or, args)
  @staticmethod
  def Not(e): return Expr(Expr.Kind.Not, [e])

  @staticmethod
  def Implies(e1, e2): return Expr(Expr.Kind.Implies, [e1, e2])
  @staticmethod
  def Iff(e1, e2): return Expr(Expr.Kind.Iff, [e1, e2])

  @staticmethod
  def Ite(c, e1, e2): return Expr(Expr.Kind.Ite, [c, e1, e2])

  @staticmethod
  def Pred(name, *args): return Expr(Expr.Kind.Pred, [name, *args])

  @staticmethod
  def Assert(e): return Expr(Expr.Kind.Assert, [e])
