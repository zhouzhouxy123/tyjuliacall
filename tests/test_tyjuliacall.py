def test_all():
    # test_invoke
    from tyjuliasetup import invoke_julia, use_sysimage

    invoke_julia("julia", ["-e", 'error("a")'], supress_errors=False)
    sysimage = invoke_julia(
        "julia", ["-e", "println(Base.unsafe_string(Base.JLOptions().image_file))"]
    )
    assert sysimage
    use_sysimage(sysimage.decode("utf-8").strip())

    # test conversion
    from tyjuliacall import JV, JuliaEvaluator, Base
    from tyjuliasetup import _get_pyjulia_core_provider
    import numpy as np

    xs = JuliaEvaluator["zs = String[]"]
    push_ = JuliaEvaluator["push!"]
    push_(xs, "2")

    assert JuliaEvaluator["x -> typeof(x) == ComplexF64"](1j)
    assert JuliaEvaluator["x -> typeof(x) == String"]("2")
    assert JuliaEvaluator["x -> typeof(x) == Float64"](1.0)
    assert JuliaEvaluator["x -> typeof(x) == Int"](1)
    assert JuliaEvaluator["x -> typeof(x) == Bool"](True)
    assert JuliaEvaluator["x -> typeof(x) <: AbstractArray"](np.ones((100, 100)))
    assert JuliaEvaluator["x -> x isa Tuple{Int, String}"]((1, "2")) 
    assert JuliaEvaluator["x -> x isa Nothing"](None)

    # Vector{String} 没有对应Python类型
    assert isinstance(JuliaEvaluator["String[]"], JV)

    x = JuliaEvaluator["Int32[]"]
    assert isinstance(x, np.ndarray) and x.dtype == np.int32

    x = JuliaEvaluator["Int8[]"]
    assert isinstance(x, np.ndarray) and x.dtype == np.int8

    x = JuliaEvaluator["zeros(Float32, 2, 2)"]
    assert isinstance(x, np.ndarray) and x.dtype == np.float32

    x = JuliaEvaluator["ComplexF32[]"]
    assert isinstance(x, np.ndarray) and x.dtype == np.complex64


    x = JuliaEvaluator['(2, "2", (1.0, 2.0), ComplexF32[])']
    assert isinstance(x, tuple) and len(x) == 4
    assert isinstance(x[0], int) and x[0] == 2
    assert isinstance(x[1], str) and x[1] == "2"
    assert isinstance(x[2], tuple) and len(x[2]) == 2
    assert isinstance(x[2][0], float) and x[2][0] == 1.0
    assert isinstance(x[2][1], float) and x[2][1] == 2.0
    assert isinstance(x[3], np.ndarray) and x[3].dtype == np.complex64

    x = JuliaEvaluator['(3, "hello", (1.5, 2.5), ComplexF64[])']

    # 使用 assert 语句来比较结果
    assert isinstance(x, tuple) and len(x) == 4
    assert isinstance(x[0], int) and x[0] == 3
    assert isinstance(x[1], str) and x[1] == "hello"
    assert isinstance(x[2], tuple) and len(x[2]) == 2
    assert isinstance(x[2][0], float) and x[2][0] == 1.5
    assert isinstance(x[2][1], float) and x[2][1] == 2.5
    assert isinstance(x[3], np.ndarray) and x[3].dtype == np.complex128

    s1 = JuliaEvaluator[
        r"""
        struct S1
            x::Int
            y::Int
            z::String
        end
        """,
        'S1(1, 2, "3")',
    ]
    assert isinstance(s1, JV) and s1.x == 1 and s1.y == 2 and s1.z == "3"

    s2 = JuliaEvaluator[
        r"""
        mutable struct S2
            x::Int
            y::Int
            z::String
        end
        """,
        's2 = S2(1, 2, "3")',
    ]
    assert isinstance(s2, JV) and s1.x == 1 and s1.y == 2 and s1.z == "3"
    s2.y = 10
    assert JuliaEvaluator["s2.y == 10"]

    s3 = JuliaEvaluator[
        r"""
        mutable struct S3
            a::Float64
            b::String
            c::Bool
        end
        """,
        's3 = S3(3.14, "hello", true)',
    ]

    assert isinstance(s3, JV) and  s3.a == 3.14 and  s3.b == "hello" and  s3.c is True
    s3.a = 2.71
    assert JuliaEvaluator["s3.a == 2.71"]

    # 不支持传入规定以外的参数
    try:
        Base.identity([])
    except Exception as e:
        pass

    x = JuliaEvaluator["x -> x^2"](5)
    assert x == 25

    _r = repr(JuliaEvaluator['String["1"]'])
    assert str.startswith(_r, "<JV(")
    assert r'["1"]' in _r

    ts = list(JuliaEvaluator[r'Any[1, "2", []]'])
    assert ts[0] == 1
    assert ts[1] == "2"
    assert isinstance(ts[2], JV) and list(ts[2]) == []

    jdict = Base.Dict()
    jdict[1, 2] = 3
    assert jdict[1, 2] == 3
    assert Base.haskey(jdict, (1, 2))

    jdict = Base.Dict()
    jdict["one", "two"] = 1
    jdict["three", "four"] = 2
    assert jdict["one", "two"] == 1
    assert Base.haskey(jdict, ("three", "four"))

    pi = JuliaEvaluator["pi"]
    assert pi + 1 == JuliaEvaluator["pi + 1"]
    assert pi - 1 == JuliaEvaluator["pi - 1"]
    assert pi * 5 == JuliaEvaluator["pi * 5"]
    assert pi / 2 == JuliaEvaluator["pi / 2"]
    assert pi // 2 == JuliaEvaluator["div(pi, 2)"]
    assert (pi > 2) == JuliaEvaluator["pi > 2"]
    assert (pi >= 2) == JuliaEvaluator["pi >= 2"]
    assert (pi < 2) == JuliaEvaluator["pi < 2"]
    assert (pi <= 2) == JuliaEvaluator["pi <= 2"]
    assert (pi == 2) == JuliaEvaluator["pi == 2"]
    assert (pi != 2) == JuliaEvaluator["pi != 2"]
    assert (pi**2) == JuliaEvaluator["pi ^ 2"]
    assert (pi % 2) == JuliaEvaluator["pi % 2"]
    assert (abs(pi)) == JuliaEvaluator["abs(pi)"]
    assert (-(pi)) == JuliaEvaluator["-(pi)"]
    assert (hash(pi)) == JuliaEvaluator["hash(pi) % Int64"]
    assert (+(pi)) == JuliaEvaluator["+(pi)"]

    # 获取 Julia 的黄金比例 "φ"（phi）
    phi = JuliaEvaluator["(1 + sqrt(5)) / 2"]
    assert phi + 1 == JuliaEvaluator["(1 + sqrt(5)) / 2 + 1"]
    assert phi - 1 == JuliaEvaluator["(1 + sqrt(5)) / 2 - 1"]
    assert phi * 5 == JuliaEvaluator["(1 + sqrt(5)) / 2 * 5"]
    assert phi / 2 == JuliaEvaluator["(1 + sqrt(5)) / 2 / 2"]
    assert phi // 2 == JuliaEvaluator["div((1 + sqrt(5)) / 2, 2)"]
    assert (phi > 2) == JuliaEvaluator["(1 + sqrt(5)) / 2 > 2"]
    assert (phi >= 2) == JuliaEvaluator["(1 + sqrt(5)) / 2 >= 2"]
    assert (phi < 2) == JuliaEvaluator["(1 + sqrt(5)) / 2 < 2"]
    assert (phi <= 2) == JuliaEvaluator["(1 + sqrt(5)) / 2 <= 2"]
    assert (phi == 2) == JuliaEvaluator["(1 + sqrt(5)) / 2 == 2"]
    assert (phi != 2) == JuliaEvaluator["(1 + sqrt(5)) / 2 != 2"]
    assert (phi**2) == JuliaEvaluator["((1 + sqrt(5)) / 2)^2"]
    assert (phi % 2) == JuliaEvaluator["(1 + sqrt(5)) / 2 % 2"]
    assert abs(phi) == JuliaEvaluator["abs((1 + sqrt(5)) / 2)"]
    assert -(phi) == JuliaEvaluator["-(1 + sqrt(5)) / 2"]
    assert +(phi) == JuliaEvaluator["+(1 + sqrt(5)) / 2"]

    bitarray = JuliaEvaluator["bitarray = BitArray([1, 0])"]
    assert True in bitarray

    assert (bitarray >> 2) == JuliaEvaluator["bitarray >> 2"]
    assert (bitarray << 2) == JuliaEvaluator["bitarray << 2"]

    missing = JuliaEvaluator["missing"]
    assert (missing | 2) == JuliaEvaluator["missing | 2"]
    assert (missing & 2) == JuliaEvaluator["missing & 2"]
    assert (missing ^ 2) == JuliaEvaluator["missing  ⊻ 2"]
    assert (~missing) == JuliaEvaluator["~missing"]


    # test miscellaneous
    from tyjuliasetup import Environment

    Environment._env = None
    Environment.TYPY_JL_OPTS = ""
    import os

    os.environ["TYPY_JL_OPTS"] = ""
    assert Environment.TYPY_JL_OPTS == ""

    import tyjuliacall.Base.Multimedia as Multimedia  # type: ignore

    dir(Multimedia)
    repr(Multimedia)
    from tyjuliacall.Base.Multimedia import display  # type: ignore

    try:
        exec("from tyjuliacall.Base.Multimedia import *", {})
    except Exception:
        pass

    try:
        JuliaEvaluator[1]
    except TypeError:
        pass

    try:
        JuliaEvaluator[1, 2]
    except TypeError:
        pass
