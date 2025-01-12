import pdb
from functools import partial
import os.path
from pathlib import Path

DBG = pdb.set_trace

TMPDIR = Path("/tmp/")
LOGGER_LEVEL = 0
DO_MP = True  # use multiprocessing
DO_SIMPLIFY = True  # simplify results, e.g., removing weaker invariants
DO_FILTER = True  # remove ieqs and min/max terms that unlikely interesting
DO_SS = True  # use symbolic states to check results
DO_EQTS = True  # support equalities
DO_IEQS = True  # support (octagonal) inequalities
DO_CONGRUENCES = False  # support congruence relations
DO_ARRAYS = False  # support array relations
DO_MINMAXPLUS = False  # support minmax-plus inequalities
DO_PREPOSTS = False  # support prepostconditions #TODO not well-tested
DO_INCR_DEPTH = True
DO_SOLVER_STATS = False  # collect solver usage stats
WRITE_VTRACES = None  # write vtraces to csv
WRITE_SSTATES = None  # write symbolic states to a json file
READ_SSTATES = None  # read symbolic states from a json file
BENCHMARK_TIMEOUT = 15 * 60  # mins

N_RAND_INPS = 100  # number of random inputs, only used when DO_SS is False
INP_MAX_V = 300
SE_DEPTH_NOCHANGES_MAX = 3
SE_MAXDEPTH = 30
SOLVER_TIMEOUT = 1  # secs
EQT_RATE = 1.5
UGLY_FACTOR = 20  # remove equalities that have lots of terms and "large" coefficients
MAX_TERM = 200

TRACE_MAX_VAL = 1_000_000_000
TRACE_MULTIPLIER = 5
INP_RANGE_V = 4  # use more inp ranges when # of inputs is <= this
UTERMS = None  # terms that the user's interested in, e.g., "y^2 xy"

# Iequalities
IUPPER = 128  # t <= iupper, upper bound of the inequality constant
IUPPER_MMP = 2  # for min/max ieqs
IDEG = 1  # deg (if 1 then linear)
ITERMS = 2  # octagonal
ICOEFS = 1  # from -ICOEFS to ICOEFS, e.g., -1,0,1

# options for full specs analysis
CTR_VAR = "Ct"  # counter variable contains this string
POST_LOC = "post"  # vtraceX_post  indicates postconditions

# Program Paths
SRC_DIR = Path(__file__).parent

TRACE_DIR = "traces"
SYMEXE_DIR = "symexe"
TRACE_INDICATOR = "vtrace"
MAINQ_FUN = "mainQ"

def setup(settings, args):
    import helpers.vcommon

    opts = []
    if args.nosimplify:
        if settings:
            settings.DO_SIMPLIFY = not args.nosimplify
        else:
            opts.append("-nosimplify")

    if args.nofilter:
        if settings:
            settings.DO_FILTER = not args.nofilter
        else:
            opts.append("-nofilter")

    if args.noss:
        if settings:
            settings.DO_SS = not args.noss
        else:
            opts.append("-noss")

    if args.nomp:
        if settings:
            settings.DO_MP = not args.nomp
        else:
            opts.append("-nomp")

    if args.noeqts:
        if settings:
            settings.DO_EQTS = not args.noeqts
        else:
            opts.append("-noeqts")

    if args.noieqs:
        if settings:
            settings.DO_IEQS = not args.noieqs
        else:
            opts.append("-noieqs")

    if args.nocongruences:
        if settings:
            settings.DO_CONGRUENCES = not args.nocongruences
        else:
            opts.append("-nocongruences")

    if args.noarrays:
        if settings:
            settings.DO_ARRAYS = not args.noarrays
        else:
            opts.append("-noarrays")

    if args.nominmaxplus:
        if settings:
            settings.DO_MINMAXPLUS = not args.nominmaxplus
        else:
            opts.append("-nominmaxplus")

    if args.nopreposts:
        if settings:
            settings.DO_PREPOSTS = not args.nopreposts
        else:
            opts.append("-nopreposts")

    if args.noincrdepth:
        if settings:
            settings.DO_INCR_DEPTH = not args.noincrdepth
        else:
            opts.append("-noincredepth")

    if args.dosolverstats:
        if settings:
            settings.DO_SOLVER_STATS = args.dosolverstats
        else:
            opts.append("-dosolverstats")

    if args.writevtraces:
        if settings:
            settings.WRITE_VTRACES = args.writevtraces
        else:
            opts.append("-writevtraces")
    
    if args.writesstates:
        if settings:
            settings.WRITE_SSTATES = args.writesstates
        else:
            opts.append("-writesstates")

    if args.readsstates:
        if settings:
            settings.READ_SSTATES = args.readsstates
        else:
            opts.append("-readsstates")

    if args.inpMaxV and args.inpMaxV >= 1:
        if settings:
            settings.INP_MAX_V = args.inpMaxV
        else:
            opts.append(f"-inpMaxV {args.inpMaxV}")

    if args.iupper and args.iupper >= 1:
        if settings:
            settings.IUPPER = args.iupper
        else:
            opts.append(f"-iupper {args.iupper}")

    if args.ideg and args.ideg >= 1:
        if settings:
            settings.IDEG = args.ideg
        else:
            opts.append(f"-ideg {args.ideg}")

    if args.iterms and args.iterms >= 1:
        if settings:
            settings.ITERMS = args.iterms
        else:
            opts.append(f"-iterms {args.iterms}")

    if args.icoefs and args.icoefs >= 1:
        if settings:
            settings.ICOEFS = args.icoefs
        else:
            opts.append(f"-icoefs {args.icoefs}")

    if args.maxterm and args.maxterm >= 1:
        if settings:
            settings.MAX_TERM = args.maxterm
        else:
            opts.append(f"-maxterm {args.maxterm}")

    if args.nrandinps and args.nrandinps >= 1:
        if settings:
            settings.N_RAND_INPS = args.nrandinps
        else:
            opts.append(f"-nrandinps {args.nrandinps}")

    if args.uterms:
        if settings:
            settings.UTERMS = set(args.uterms.split(';'))
        else:
            opts.append(f'-uterms "{args.uterms}"')  # not tested

    if args.se_mindepth and args.se_mindepth >= 1:
        if settings:
            pass
        else:
            opts.append(f"-se_mindepth {args.se_mindepth}")

    if args.se_maxdepth and args.se_maxdepth >= 1:
        if settings:
            settings.SE_MAXDEPTH = args.se_maxdepth
        else:
            opts.append(f"-se_maxdepth {args.se_maxdepth}")

    if args.tmpdir:
        if settings:
            settings.TMPDIR = Path(args.tmpdir)
            assert settings.TMPDIR.is_dir()
        else:
            opts.append(f"-tmpdir {args.tmpdir}")

    if settings:
        settings.LOGGER_LEVEL = helpers.vcommon.getLogLevel(args.log_level)
        mlog = helpers.vcommon.getLogger(__name__, settings.LOGGER_LEVEL)
        return mlog
    else:
        opts.append(f"-log_level {args.log_level}")
        return " ".join(opts)
    

