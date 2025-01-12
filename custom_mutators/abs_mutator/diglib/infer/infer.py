import abc
import pdb
import sympy

from time import time
from beartype import beartype

import diglib.helpers.vcommon as CM
from diglib.helpers.miscs import Miscs, MP

import diglib.settings as settings

import diglib.data.prog
import diglib.data.symstates
import diglib.infer.inv

DBG = pdb.set_trace
mlog = CM.getLogger(__name__, settings.LOGGER_LEVEL)


class _Infer(metaclass=abc.ABCMeta):
    """
    Base class for inference
    """
    @beartype
    def __init__(self, symstates, 
                 prog:diglib.data.prog.Prog):
        self.symstates = symstates
        self.inv_decls = prog.inv_decls
        self.inp_decls = prog.inp_decls
        self.prog = prog

    @beartype
    @abc.abstractmethod
    def gen(self):
        pass

    @beartype
    @classmethod
    @abc.abstractmethod
    def gen_from_traces(cls, traces: diglib.data.traces.DTraces, 
                        symbols):
        """
        Generating invariants directly from traces
        """
        pass

    @beartype
    def get_traces(self, inps: diglib.data.traces.Inps,
                   dtraces: diglib.data.traces.DTraces):
        """
        run inps to get new traces (and update them)
        """

        new_dtraces = self.prog.get_traces(inps)
        new_dtraces = dtraces.merge(new_dtraces)
        return new_dtraces

    @beartype
    def check(self, dinvs:diglib.infer.inv.DInvs, 
              inps):
        if self.symstates:
            cexs, dinvs = self.symstates.check(dinvs, inps)
        else:
            # no symbolic states, not performing checking
            assert False, "shouldn't get here"
            for loc in dinvs:
                for inv in dinvs[loc]:
                    inv.stat = diglib.infer.inv.Inv.UNKNOWN
            cexs = {}
        return cexs, dinvs


class _CEGIR(_Infer, metaclass=abc.ABCMeta):
    """
    Find invs using a guess and check iterative CEGIR approach
    """
    pass


class _Opt(_Infer, metaclass=abc.ABCMeta):
    """
    Find upperbounds of polynomials and min/max terms 
    using an SMT solver optimizer
    """

    @beartype
    def __init__(self, symstates,
                 prog:diglib.data.prog.Prog):
        # need prog because symstates could be None
        super().__init__(symstates, prog)

    @beartype
    def gen(self):
        
        locs = self.inv_decls.keys()

        def _terms(loc):
            return self.inv_decls[loc].symbolic

        # remove terms exceeding maxV
        termss = [self.get_terms(_terms(loc)) for loc in locs]

        dinvs = diglib.infer.inv.DInvs()

        if not termss:
            return dinvs

        mlog.debug(f"checking upperbounds for {sum(map(len, termss))} "
                   f"terms at {len(locs)} locs")

        refs = {
            loc: {self.inv_cls(t.mk_le(self.IUPPER)): t for t in terms}
            for loc, terms in zip(locs, termss)
        }
        ieqs = diglib.infer.inv.DInvs()
        for loc in refs:
            for inv in refs[loc].keys():
                ieqs.setdefault(loc, diglib.infer.inv.Invs()).add(inv)

        _, ieqs = self.check(ieqs, inps=None)
        ieqs = ieqs.remove_disproved()
        tasks = [(loc, refs[loc][t]) for loc in ieqs for t in ieqs[loc]]

        mlog.debug(
            f"inferring upperbounds for {len(tasks)} terms at {len(locs)} locs")

        # computing convex hull
        def f(tasks):
            return [
                (loc, term, self.symstates.maximize(
                    loc, self.to_expr(term), self.IUPPER))
                for loc, term in tasks
            ]

        wrs = MP.run_mp("optimizing upperbound", tasks, f, settings.DO_MP)

        dinvs = diglib.infer.inv.DInvs()
        for loc, term, v in wrs:
            if v is None:
                continue
            inv = self.inv_cls(term.mk_le(v))
            inv.set_stat(diglib.infer.inv.Inv.PROVED)
            dinvs.setdefault(loc, diglib.infer.inv.Invs()).add(inv)

        return dinvs

    @beartype
    def get_terms(self,
                  symbols):

        terms = self.my_get_terms(symbols)
        mlog.debug(f"{len(terms)} terms for {self.__class__.__name__}")

        inps = set(self.inp_decls.names)
        if settings.DO_FILTER and inps:
            st = time()
            excludes = self.get_excludes(terms, inps)
            new_terms = [term for term in terms if term not in excludes]
            Miscs.show_removed("filter terms", len(
                terms), len(new_terms), time() - st)
            terms = new_terms
        return terms

    @staticmethod
    @abc.abstractmethod
    def to_expr(term):
        pass

    @staticmethod
    @abc.abstractmethod
    def inv_cls(term):
        pass

    @classmethod
    @abc.abstractmethod
    def my_get_terms(cls, terms, inps):
        pass

    @staticmethod
    @abc.abstractmethod
    def get_excludes(term):
        pass

    @beartype
    @classmethod
    def gen_from_traces(cls, 
                        traces: diglib.data.traces.Traces,
                        symbols:diglib.data.prog.Symbs):
        """
        Compute convex hulls from traces
        """
        maxV = cls.IUPPER
        minV = -1 * maxV

        tasks = cls.my_get_terms(symbols.symbolic)

        def f(tasks):
            rs = [(term, int(max(term.eval_traces(traces)))) 
                    for term in tasks]
            return rs

        wrs = MP.run_mp("getting upperbounds", tasks, f, settings.DO_MP)

        ps: list[diglib.infer.inv.Inv] = []
        for term, upperbound in wrs:
            if minV <= upperbound <= maxV:
                p = cls.inv_cls(term.mk_le(upperbound))
                ps.append(p)
        return ps
