# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2026-08-18 14:57:22'

"""
    实现 Rust 风格的 Result(成功/失败二选一的结果类型)

    ── 快速开始 ───────────────────────────────────────────────
        from dsPyLib.types.rust_style_result import Result, Ok, Err

        r = Ok(42)            # 成功结果(贴近 Rust 的 Ok(42) 语法)
        r = Err('出错了')     # 失败结果(贴近 Rust 的 Err(...) 语法)

        r.is_ok()             # True / False
        r.ok_value()          # 成功值(失败时为 None)
        r.err_value()         # 错误值(成功时为 None)
        r.unwrap()            # 取值(失败时抛 RuntimeError)
        r.map(lambda x: x * 2)          # Ok(84)
        r.and_then(lambda v: Ok(v + 1)) # 链式调用

    ── 与 Rust std::result::Result 的对应关系 ──────────────────
        Rust                          本实现(差异说明)
        ──────────────────────────────────────────────────────
        Ok(T) / Err(E) 变体           Result.ok()/err() 类方法 + 模块级 Ok()/Err() 函数
        is_ok / is_err                is_ok / is_err (一致)
        is_ok_and / is_err_and        is_ok_and / is_err_and (一致)
        ok() / err() -> Option        ok_value / err_value (因与构造器同名冲突而改名)
        unwrap / unwrap_err           unwrap / unwrap_err (一致; panic -> RuntimeError)
        expect / expect_err           expect / expect_err (一致)
        unwrap_or / unwrap_or_else    unwrap_or / unwrap_or_else (一致)
        unwrap_or_default             unwrap_or_default (偏离: Rust 返回 T::default(), Python 无 Default trait, 统一返回 None)
        map / map_or / map_or_else    map / map_or / map_or_else (一致)
        map_err                       map_err (一致)
        inspect / inspect_err         inspect / inspect_err (一致)
        contains / contains_err       contains / contains_err (一致)
        and_then / or_else            and_then / or_else (一致)
        and / or                      and_ / or_ (因 and/or 是 Python 关键字, 加下划线)
        zip / zip_with                zip / zip_with (一致)
        transpose                     transpose (一致)
        flatten                       flatten (宽松版: 仅识别 Result 实例)
        IntoIterator                  __iter__ (成功迭代出 0 或 1 个值, 失败 0 个)
        ? 运算符                      无等价物; 用 unwrap/and_then 链或异常替代

    ── Rust 有但 Python 无意义, 故未实现 ────────────────────────
        copied/cloned (Copy/Clone 语义)  as_ref/as_mut (引用语义)
        into_ok/into_err (never 类型)     iter/iter_mut (借用语义)

    ── 扩展方法(非 Rust 标准, 便利扩展) ─────────────────────────
        from_optional (对应 Option::ok_or)
        from_try (try/catch 包装, 类似 Scala Try)
        all / any (批量收集)
        filter (条件保留/转错)
        and_then_async (异步链式)
"""

from typing import TypeVar, Generic, Union, Optional, Callable, Any, Coroutine, Iterator

T = TypeVar('T')
E = TypeVar('E')
U = TypeVar('U')


# ---------- 模块级构造函数(贴近 Rust 的 Ok/Err 语法) ---------- #


def Ok(value: T) -> 'Result[T, Any]':
    """
    创建成功结果(Rust 语法的 Ok(值) 对应物)

    功能: 包装成功值, 等价于 Result.ok(value)
    参数: value - 成功值(任意类型)
    返回: Result[T, Any]
    演示:
        >>> r = Ok(42)
        >>> r
        Ok(42)
    """
    return Result.ok(value)


def Err(error: E) -> 'Result[Any, E]':
    """
    创建失败结果(Rust 语法的 Err(错误) 对应物)

    功能: 包装错误值, 等价于 Result.err(error)
    参数: error - 错误值(任意类型: str/Exception/自定义对象)
    返回: Result[Any, E]
    演示:
        >>> r = Err('除数不能为零')
        >>> r
        Err(除数不能为零)
    """
    return Result.err(error)


class Result(Generic[T, E]):

    # ---------- 构造 ---------- #

    def __init__(self, value: Optional[T] = None, error: Optional[E] = None):
        """
        直接构造一个 Result(一般不直接使用, 推荐 Ok()/Err()/Result.ok()/Result.err())

        功能: 创建结果对象; 当 error 不为 None 时视为失败状态
        参数: value  - 成功值(默认 None)
              error  - 错误值(默认 None)
        注意: value 与 error 同时非 None 时, 以 error 为准(视为失败)
        演示:
            >>> Result(value=42, error=None)
            Ok(42)
            >>> Result(value=None, error='e')
            Err(e)
        """
        self._value: Optional[T] = value
        self._error: Optional[E] = error
        self._is_ok: bool = error is None

    @classmethod
    def ok(cls, value: T) -> 'Result[T, E]':
        """
        创建成功结果(对应 Rust 的 Result::Ok 变体)

        功能: 包装成功值
        参数: value - 成功值
        返回: 成功状态的 Result
        演示:
            >>> Result.ok(42)
            Ok(42)
            >>> Result.ok(42).is_ok()
            True
        """
        return cls(value=value, error=None)

    @classmethod
    def err(cls, error: E) -> 'Result[T, E]':
        """
        创建失败结果(对应 Rust 的 Result::Err 变体)

        功能: 包装错误值
        参数: error - 错误值(任意类型: str/Exception/自定义错误对象均可)
        返回: 失败状态的 Result
        演示:
            >>> Result.err('连接超时')
            Err(连接超时)
            >>> Result.err('连接超时').is_err()
            True
        """
        return cls(value=None, error=error)

    @classmethod
    def from_optional(cls, optional: Optional[T], err: E) -> 'Result[T, E]':
        """
        从 Optional 值创建 Result(扩展方法, 对应 Rust 的 Option::ok_or)

        功能: optional 非 None 时返回成功结果, 为 None 时返回指定错误
        参数: optional - Optional 值
              err      - optional 为 None 时使用的错误值
        返回: Result[T, E]
        演示:
            >>> Result.from_optional(42, '值为空')
            Ok(42)
            >>> Result.from_optional(None, '值为空')
            Err(值为空)
        """
        if optional is not None:
            return cls.ok(optional)
        return cls.err(err)

    @classmethod
    def from_try(cls, fn: Callable[[], T], err_fn: Callable[[Exception], E]) -> 'Result[T, E]':
        """
        从可能抛异常的函数调用创建 Result(扩展方法, 类似 Scala Try)

        注意: 这不是 Rust Result 的方法; Rust 的 Result::from(T) 只是包装 Ok 不捕获异常
        功能: 执行 fn, 成功则包装返回值; 抛异常则调用 err_fn(异常) 转换后包装为失败
        参数: fn     - 要执行的无参函数(可能抛异常)
              err_fn - 异常转换函数, 接收 Exception 返回错误值
        返回: Result[T, E]
        演示:
            >>> Result.from_try(lambda: int('123'), lambda e: f'转换失败: {e}')
            Ok(123)
            >>> Result.from_try(lambda: int('abc'), lambda e: f'转换失败: {e}')
            Err(转换失败: invalid literal for int() with base 10: 'abc')
        """
        try:
            return cls.ok(fn())
        except Exception as e1:
            return cls.err(err_fn(e1))

    # ---------- 状态判断(Rust 对应) ---------- #

    def is_ok(self) -> bool:
        """
        判断是否为成功状态(对应 Rust 的 is_ok)

        功能: 成功返回 True, 失败返回 False
        返回: bool
        演示:
            >>> Ok(42).is_ok()
            True
            >>> Err('e').is_ok()
            False
        """
        return self._is_ok

    def is_err(self) -> bool:
        """
        判断是否为失败状态(对应 Rust 的 is_err)

        功能: 失败返回 True, 成功返回 False
        返回: bool
        演示:
            >>> Ok(42).is_err()
            False
            >>> Err('e').is_err()
            True
        """
        return not self._is_ok

    def is_ok_and(self, fn: Callable[[T], bool]) -> bool:
        """
        判断是否成功且满足条件(对应 Rust 的 is_ok_and, 1.70+)

        功能: 仅当成功且 fn(值) 为真时返回 True; 失败时不调用 fn 直接返回 False
        参数: fn - 对成功值做判断的函数, 返回 bool
        返回: bool
        演示:
            >>> Ok(10).is_ok_and(lambda v: v > 5)
            True
            >>> Err('e').is_ok_and(lambda v: v > 5)
            False
        """
        if not self._is_ok:
            return False
        assert self._value is not None  # 类型收窄: 成功时必有值
        return fn(self._value)

    def is_err_and(self, fn: Callable[[E], bool]) -> bool:
        """
        判断是否失败且满足条件(对应 Rust 的 is_err_and, 1.70+)

        功能: 仅当失败且 fn(错误) 为真时返回 True; 成功时不调用 fn 直接返回 False
        参数: fn - 对错误值做判断的函数, 返回 bool
        返回: bool
        演示:
            >>> Err('连接超时').is_err_and(lambda e: '超时' in str(e))
            True
            >>> Ok(1).is_err_and(lambda e: '超时' in str(e))
            False
        """
        if self._is_ok:
            return False
        assert self._error is not None  # 类型收窄: 失败时必有错误
        return fn(self._error)

    # ---------- 取值: 安全(Rust 对应 ok()/err()) ---------- #

    def ok_value(self) -> Optional[T]:
        """
        安全获取成功值(对应 Rust 的 result.ok() 返回 Option)

        功能: 成功时返回内部值, 失败时返回 None
        返回: Optional[T]
        注意: 因与类构造器 Result.ok 同名冲突, 在 Rust 中名为 ok(), 此处改名 ok_value()
        演示:
            >>> Ok(42).ok_value()
            42
            >>> Err('e').ok_value()
            None
        """
        return self._value if self._is_ok else None

    def err_value(self) -> Optional[E]:
        """
        安全获取错误值(对应 Rust 的 result.err() 返回 Option)

        功能: 失败时返回错误值, 成功时返回 None
        返回: Optional[E]
        注意: 因与类构造器 Result.err 同名冲突, 在 Rust 中名为 err(), 此处改名 err_value()
        演示:
            >>> Err('e').err_value()
            'e'
            >>> Ok(42).err_value()
            None
        """
        return self._error if not self._is_ok else None

    # ---------- 取值: 危险(失败时抛异常, Rust 对应 unwrap 系列) ---------- #

    def unwrap(self) -> T:
        """
        取出成功值, 失败时抛 RuntimeError(对应 Rust 的 unwrap)

        功能: 成功返回内部值; 失败抛出 RuntimeError(异常消息包含错误值)
        返回: T
        异常: RuntimeError - 当结果为失败状态时
        演示:
            >>> Ok(42).unwrap()
            42
            >>> Err('出错了').unwrap()
            Traceback (most recent call last):
            ...
            RuntimeError: 调用了 unwrap(), 但 Result 是错误状态: 出错了
        """
        if not self._is_ok:
            raise RuntimeError(f"调用了 unwrap(), 但 Result 是错误状态: {self._error}")
        assert self._value is not None  # 类型收窄
        return self._value

    def unwrap_err(self) -> E:
        """
        取出错误值, 成功时抛 RuntimeError(对应 Rust 的 unwrap_err)

        功能: 失败返回错误值; 成功抛出 RuntimeError(异常消息包含成功值)
        返回: E
        异常: RuntimeError - 当结果为成功状态时
        演示:
            >>> Err('e').unwrap_err()
            'e'
            >>> Ok(42).unwrap_err()
            Traceback (most recent call last):
            ...
            RuntimeError: 调用了 unwrap_err(), 但 Result 是成功状态: 42
        """
        if self._is_ok:
            raise RuntimeError(f"调用了 unwrap_err(), 但 Result 是成功状态: {self._value}")
        assert self._error is not None  # 类型收窄
        return self._error

    def expect(self, msg: str) -> T:
        """
        取出成功值, 失败时抛带自定义信息的 RuntimeError(对应 Rust 的 expect)

        功能: 与 unwrap 相同, 但异常消息由调用方指定(更适合排查)
        参数: msg - 自定义错误信息
        返回: T
        异常: RuntimeError - 当结果为失败状态时(消息 = msg + 错误值)
        演示:
            >>> Ok(42).expect('数据库连接必须成功')
            42
            >>> Err('连接拒绝').expect('数据库连接必须成功')
            Traceback (most recent call last):
            ...
            RuntimeError: 数据库连接必须成功: 连接拒绝
        """
        if not self._is_ok:
            raise RuntimeError(f"{msg}: {self._error}")
        assert self._value is not None  # 类型收窄
        return self._value

    def expect_err(self, msg: str) -> E:
        """
        取出错误值, 成功时抛带自定义信息的 RuntimeError(对应 Rust 的 expect_err)

        功能: 与 unwrap_err 相同, 但异常消息由调用方指定
        参数: msg - 自定义错误信息
        返回: E
        异常: RuntimeError - 当结果为成功状态时(消息 = msg + 成功值)
        演示:
            >>> Err('e').expect_err('此操作必然失败')
            'e'
            >>> Ok(42).expect_err('此操作必然失败')
            Traceback (most recent call last):
            ...
            RuntimeError: 此操作必然失败: 42
        """
        if self._is_ok:
            raise RuntimeError(f"{msg}: {self._value}")
        assert self._error is not None  # 类型收窄
        return self._error

    # ---------- 取值: 兜底(Rust 对应 unwrap_or 系列) ---------- #

    def unwrap_or(self, default: T) -> T:
        """
        成功返回内部值, 失败返回默认值(对应 Rust 的 unwrap_or)

        功能: 安全的兜底取值
        参数: default - 失败时返回的默认值
        返回: T
        演示:
            >>> Ok(10).unwrap_or(0)
            10
            >>> Err('e').unwrap_or(0)
            0
        """
        if self._is_ok:
            assert self._value is not None  # 类型收窄
            return self._value
        return default

    def unwrap_or_else(self, fn: Callable[[E], T]) -> T:
        """
        成功返回内部值, 失败时用错误值计算替代值(对应 Rust 的 unwrap_or_else)

        功能: 失败时通过 fn(错误) 生成返回值(延迟计算, 比 unwrap_or 更灵活)
        参数: fn - 接收错误值返回替代值的函数
        返回: T
        演示:
            >>> Ok(10).unwrap_or_else(lambda e: -1)
            10
            >>> Err('e').unwrap_or_else(lambda e: -1)
            -1
        """
        if self._is_ok:
            assert self._value is not None  # 类型收窄
            return self._value
        assert self._error is not None  # 类型收窄
        return fn(self._error)

    def unwrap_or_default(self) -> Optional[T]:
        """
        成功返回内部值, 失败返回 None(偏离 Rust 语义, 见注意)

        注意: Rust 的 unwrap_or_default 返回 T::default()(如 int 的 0, str 的空串);
              Python 无 Default trait 无法推断类型, 故统一返回 None;
              需要指定默认值时请使用 unwrap_or(default)
        功能: 成功返回内部值, 失败返回 None
        返回: Optional[T]
        演示:
            >>> Ok(10).unwrap_or_default()
            10
            >>> Err('e').unwrap_or_default()
            None
        """
        if self._is_ok:
            assert self._value is not None  # 类型收窄
            return self._value
        return None

    # ---------- 转换(Rust 对应 map 系列) ---------- #

    def map(self, fn: Callable[[T], U]) -> 'Result[U, E]':
        """
        对成功值做转换(对应 Rust 的 map)

        功能: 成功时返回 Ok(fn(值)); 失败时原样保留错误(fn 不被调用)
        参数: fn - 成功值转换函数
        返回: Result[U, E]
        演示:
            >>> Ok(10).map(lambda x: x * 2)
            Ok(20)
            >>> Err('e').map(lambda x: x * 2)
            Err(e)
        """
        if self._is_ok:
            assert self._value is not None  # 类型收窄
            return Result.ok(fn(self._value))
        assert self._error is not None  # 类型收窄
        return Result.err(self._error)

    def map_or(self, default: U, fn: Callable[[T], U]) -> U:
        """
        转换成功值, 失败时返回默认值(对应 Rust 的 map_or)

        功能: 成功返回 fn(值); 失败返回 default
        参数: default - 失败时的默认值
              fn      - 成功值转换函数
        返回: U(不再是 Result)
        演示:
            >>> Ok(10).map_or(0, lambda x: x * 2)
            20
            >>> Err('e').map_or(0, lambda x: x * 2)
            0
        """
        if self._is_ok:
            assert self._value is not None  # 类型收窄
            return fn(self._value)
        return default

    def map_or_else(self, default_fn: Callable[[E], U], fn: Callable[[T], U]) -> U:
        """
        转换成功值, 失败时用错误值计算(对应 Rust 的 map_or_else)

        功能: 成功返回 fn(值); 失败返回 default_fn(错误)(延迟计算)
        参数: default_fn - 接收错误值返回替代值的函数
              fn        - 成功值转换函数
        返回: U(不再是 Result)
        演示:
            >>> Ok(10).map_or_else(lambda e: -1, lambda x: x * 2)
            20
            >>> Err('e').map_or_else(lambda e: -1, lambda x: x * 2)
            -1
        """
        if self._is_ok:
            assert self._value is not None  # 类型收窄
            return fn(self._value)
        assert self._error is not None  # 类型收窄
        return default_fn(self._error)

    def map_err(self, fn: Callable[[E], U]) -> 'Result[T, U]':
        """
        转换错误值(对应 Rust 的 map_err)

        功能: 成功原样返回; 失败返回 Err(fn(错误))(常用于把 str 错误转成 Exception)
        参数: fn - 错误值转换函数
        返回: Result[T, U](错误类型变为 U)
        演示:
            >>> Err('出错了').map_err(lambda e: RuntimeError(e))
            Err(出错了)
            >>> Ok(42).map_err(lambda e: RuntimeError(e))
            Ok(42)
        """
        if self._is_ok:
            assert self._value is not None  # 类型收窄
            return Result.ok(self._value)
        assert self._error is not None  # 类型收窄
        return Result.err(fn(self._error))

    def flatten(self) -> Union['Result', T]:
        """
        展平嵌套的 Result(对应 Rust 的 flatten, 宽松版)

        功能: Result[Result[T, E], E] 展平为 Result[T, E]; 非嵌套则原样返回
        返回: Result 或 T
        注意: Rust 用 Into 约束, 本实现只识别 isinstance(Result)
        演示:
            >>> Result.ok(Result.ok(5)).flatten()
            Ok(5)
            >>> Result.ok(5).flatten()
            Ok(5)
        """
        if self._is_ok and isinstance(self._value, Result):
            return self._value.flatten()
        return self

    # ---------- 组合(Rust 对应 and/or 系列) ---------- #

    def and_then(self, fn: Callable[[T], 'Result[U, E]']) -> 'Result[U, E]':
        """
        成功时继续执行返回 Result 的函数(对应 Rust 的 and_then, 链式调用核心)

        功能: 成功则调用 fn(值) 并把其结果作为新 Result; 失败直接透传错误(fn 不被调用)
        参数: fn - 接收成功值返回新 Result 的函数
        返回: Result[U, E]
        演示:
            >>> Ok(10).and_then(lambda v: Result.ok(v + 1))
            Ok(11)
            >>> Err('e').and_then(lambda v: Result.ok(v + 1))
            Err(e)
        """
        if self._is_ok:
            assert self._value is not None  # 类型收窄
            return fn(self._value)
        assert self._error is not None  # 类型收窄
        return Result.err(self._error)

    def or_else(self, fn: Callable[[E], 'Result[T, U]']) -> 'Result[T, U]':
        """
        失败时用错误值恢复(对应 Rust 的 or_else)

        功能: 成功原样返回; 失败调用 fn(错误) 返回新 Result(可实现错误恢复/降级)
        参数: fn - 接收错误值返回新 Result 的函数
        返回: Result[T, U](错误类型变为 U)
        演示:
            >>> Ok(42).or_else(lambda e: Result.ok('回退值'))
            Ok(42)
            >>> Err('e').or_else(lambda e: Result.ok('回退值'))
            Ok(回退值)
        """
        if self._is_ok:
            assert self._value is not None  # 类型收窄
            return Result.ok(self._value)
        assert self._error is not None  # 类型收窄
        return fn(self._error)

    def and_(self, other: 'Result[U, E]') -> 'Result[U, E]':
        """
        自身成功时返回另一个结果(对应 Rust 的 and; 因 Python 关键字改名 and_)

        功能: 自身成功则返回 other(不论 other 成败); 自身失败则返回自身错误(other 被忽略)
        参数: other - 另一个 Result
        返回: Result[U, E]
        演示:
            >>> Result.ok(1).and_(Result.ok('a'))
            Ok(a)
            >>> Result.ok(1).and_(Result.err('e'))
            Err(e)
            >>> Result.err('e1').and_(Result.ok('a'))
            Err(e1)
        """
        if self._is_ok:
            return other
        assert self._error is not None  # 类型收窄
        return Result.err(self._error)

    def or_(self, other: 'Result[T, E]') -> 'Result[T, E]':
        """
        自身失败时返回另一个结果(对应 Rust 的 or; 因 Python 关键字改名 or_)

        功能: 自身成功则返回自身; 自身失败则返回 other
        参数: other - 备选 Result
        返回: Result[T, E]
        演示:
            >>> Result.err('e').or_(Result.ok(42))
            Ok(42)
            >>> Result.ok(1).or_(Result.ok(42))
            Ok(1)
        """
        if self._is_ok:
            assert self._value is not None  # 类型收窄
            return Result.ok(self._value)
        return other

    # ---------- 检查(Rust 对应 contains/inspect) ---------- #

    def contains(self, value: T) -> bool:
        """
        判断成功值是否等于给定值(对应 Rust 的 contains)

        功能: 仅当成功且内部值 == value 时返回 True
        参数: value - 要比较的值
        返回: bool
        演示:
            >>> Ok(42).contains(42)
            True
            >>> Ok(42).contains(0)
            False
            >>> Err('e').contains(42)
            False
        """
        return self._is_ok and self._value == value

    def contains_err(self, error: E) -> bool:
        """
        判断错误值是否等于给定值(对应 Rust 的 contains_err)

        功能: 仅当失败且错误值 == error 时返回 True
        参数: error - 要比较的错误值
        返回: bool
        演示:
            >>> Err('e').contains_err('e')
            True
            >>> Err('e').contains_err('x')
            False
            >>> Ok(42).contains_err('e')
            False
        """
        return not self._is_ok and self._error == error

    def inspect(self, fn: Callable[[T], None]) -> 'Result[T, E]':
        """
        对成功值执行副作用, 返回自身(对应 Rust 的 inspect)

        功能: 成功时调用 fn(值)(打印/记录等)但不改变结果; 失败时无操作
        参数: fn - 副作用函数(返回 None)
        返回: 自身(便于继续链式调用)
        演示:
            >>> Ok(42).inspect(lambda v: print(f'调试: {v}')).is_ok()
            调试: 42
            True
        """
        if self._is_ok:
            assert self._value is not None  # 类型收窄
            fn(self._value)
        return self

    def inspect_err(self, fn: Callable[[E], None]) -> 'Result[T, E]':
        """
        对错误值执行副作用, 返回自身(对应 Rust 的 inspect_err)

        功能: 失败时调用 fn(错误)(打印/记录等)但不改变结果; 成功时无操作
        参数: fn - 副作用函数(返回 None)
        返回: 自身(便于继续链式调用)
        演示:
            >>> Err('e').inspect_err(lambda e: print(f'警告: {e}')).is_err()
            警告: e
            True
        """
        if not self._is_ok:
            assert self._error is not None  # 类型收窄
            fn(self._error)
        return self

    # ---------- 配对(Rust 对应 zip 系列) ---------- #

    def zip(self, other: 'Result[U, E]') -> 'Result[tuple[T, U], E]':
        """
        两个 Result 都成功时合并为元组(对应 Rust 的 zip)

        功能: 都成功 -> Ok((值1, 值2)); 任一失败 -> 返回先出现的错误
        参数: other - 另一个 Result
        返回: Result[tuple[T, U], E]
        演示:
            >>> Result.ok(1).zip(Result.ok('a'))
            Ok((1, 'a'))
            >>> Result.ok(1).zip(Result.err('e'))
            Err(e)
            >>> Result.err('e1').zip(Result.ok('a'))
            Err(e1)
        """
        if self._is_ok and other.is_ok():
            assert self._value is not None and other._value is not None  # 类型收窄
            return Result.ok((self._value, other._value))
        if self._is_ok:
            assert other._error is not None  # 类型收窄
            return Result.err(other._error)
        assert self._error is not None  # 类型收窄
        return Result.err(self._error)

    def zip_with(self, other: 'Result[U, E]', fn: Callable[[T, U], Any]) -> 'Result[Any, E]':
        """
        两个 Result 都成功时用函数合并(对应 Rust 的 zip_with)

        功能: 都成功 -> Ok(fn(值1, 值2)); 任一失败 -> 返回先出现的错误
        参数: other - 另一个 Result
              fn    - 合并函数, 接收两个成功值返回任意结果
        返回: Result[Any, E]
        演示:
            >>> Result.ok(1).zip_with(Result.ok(2), lambda a, b: a + b)
            Ok(3)
            >>> Result.ok(1).zip_with(Result.err('e'), lambda a, b: a + b)
            Err(e)
        """
        if self._is_ok and other.is_ok():
            assert self._value is not None and other._value is not None  # 类型收窄
            return Result.ok(fn(self._value, other._value))
        if self._is_ok:
            assert other._error is not None  # 类型收窄
            return Result.err(other._error)
        assert self._error is not None  # 类型收窄
        return Result.err(self._error)

    # ---------- 互转(Rust 对应 transpose) ---------- #

    def transpose(self) -> Optional['Result[T, E]']:
        """
        Result[Optional[T], E] 与 Optional[Result[T, E]] 互转(对应 Rust 的 transpose)

        功能: Ok(None) -> None; Ok(值) -> Ok(值); Err(e) -> Err(e)
        返回: Optional[Result[T, E]]
        演示:
            >>> Result.ok(None).transpose()
            None
            >>> Result.ok(5).transpose()
            Ok(5)
            >>> Result.err('e').transpose()
            Err(e)
        """
        if self._is_ok:
            if self._value is None:
                return None
            return Result.ok(self._value)
        assert self._error is not None  # 类型收窄
        return Result.err(self._error)

    # ---------- 收集(扩展方法, 非 Rust 标准) ---------- #

    @classmethod
    def all(cls, results: list) -> 'Result[list, E]':
        """
        批量收集: 全部成功时返回成功列表(扩展方法, Rust 标准库无此方法)

        功能: 所有元素 is_ok 时返回 Ok([值1, 值2, ...]); 遇到第一个失败立即返回该错误
        参数: results - Result 列表
        返回: Result[list, E]
        演示:
            >>> Result.all([Ok(1), Ok(2), Ok(3)])
            Ok([1, 2, 3])
            >>> Result.all([Ok(1), Err('e'), Ok(3)])
            Err(e)
        """
        values = []
        for result in results:
            if result.is_err():
                err_value = result.err_value()
                assert err_value is not None  # 类型收窄: 失败时必有错误
                return Result.err(err_value)
            ok_value = result.ok_value()
            assert ok_value is not None  # 类型收窄: 成功时必有值
            values.append(ok_value)
        return Result.ok(values)

    @classmethod
    def any(cls, results: list) -> 'Result[T, E]':
        """
        批量收集: 任一成功时返回第一个成功结果(扩展方法, Rust 标准库无此方法)

        功能: 依次检查, 返回第一个 is_ok 的 Result; 全部失败时返回最后一个错误
        异常: ValueError - 列表为空时
        参数: results - Result 列表
        返回: Result[T, E]
        演示:
            >>> Result.any([Err('a'), Ok(1), Ok(2)])
            Ok(1)
            >>> Result.any([Err('a'), Err('b')])
            Err(b)
        """
        for result in results:
            if result.is_ok():
                return result
        if results:
            return results[-1]  # 全部失败: 返回最后一个错误
        raise ValueError('Result.any: 结果列表为空')

    # ---------- 过滤(扩展方法, 非 Rust 标准) ---------- #

    def filter(self, fn: Callable[[T], bool], err: E) -> 'Result[T, E]':
        """
        成功值满足条件则保留, 否则转为指定错误(扩展方法, Rust 的 filter 位于 Option)

        注意: Rust 的 Option::filter 失败返回 None; 此处改为 Result 语义, 失败返回指定错误
        功能: 成功且 fn(值) 为真 -> Ok(值); 成功但不满足 -> Err(err); 已失败 -> 原样返回
        参数: fn  - 判断函数, 接收成功值返回 bool
              err - 条件不满足时使用的错误值
        返回: Result[T, E]
        演示:
            >>> Ok(5).filter(lambda v: v > 3, '太小')
            Ok(5)
            >>> Ok(1).filter(lambda v: v > 3, '太小')
            Err(太小)
            >>> Err('e').filter(lambda v: v > 3, '太小')
            Err(e)
        """
        if not self._is_ok:
            return self
        assert self._value is not None  # 类型收窄
        return Result.ok(self._value) if fn(self._value) else Result.err(err)

    # ---------- 迭代(Rust 对应 IntoIterator) ---------- #

    def __iter__(self) -> Iterator[T]:
        """
        迭代支持(对应 Rust 的 IntoIterator: 成功产生 0 或 1 个元素, 失败产生 0 个)

        功能: 成功时迭代出内部值, 失败时无元素; 可直接 for ... in / list() / 解包
        返回: Iterator[T]
        演示:
            >>> list(Ok(5))
            [5]
            >>> list(Err('e'))
            []
            >>> for v in Ok(10): print(v)
            10
        """
        if self._is_ok:
            assert self._value is not None  # 类型收窄
            yield self._value

    # ---------- 异步(扩展方法, 非 Rust 标准) ---------- #

    async def and_then_async(self, fn: Callable[[T], 'Coroutine[Any, Any, Result[U, E]]']) -> 'Result[U, E]':
        """
        异步版 and_then(扩展方法, 对成功值执行异步函数)

        功能: 成功时 await fn(值) 并返回其结果; 失败时直接返回自身错误(fn 不被调用)
        参数: fn - 异步函数(协程), 接收成功值返回 Result
        返回: Result[U, E](由 await 得到)
        演示:
            import asyncio

            async def 加一(v: int) -> Result[int, str]:
                await asyncio.sleep(0.1)
                return Result.ok(v + 1)

            r = asyncio.run(Ok(1).and_then_async(加一))  # Ok(2)
        """
        if self._is_ok:
            assert self._value is not None  # 类型收窄
            return await fn(self._value)
        assert self._error is not None  # 类型收窄
        return Result.err(self._error)

    # ---------- 魔法方法 ---------- #

    def __repr__(self) -> str:
        """
        字符串表示(对应 Rust 的 Debug 输出)

        功能: 成功显示 Ok(值), 失败显示 Err(错误); 用于打印与调试
        返回: str
        演示:
            >>> repr(Ok(42))
            'Ok(42)'
            >>> repr(Err('e'))
            'Err(e)'
            >>> print(Ok([1, 2]))
            Ok([1, 2])
        """
        if self._is_ok:
            return f"Ok({self._value})"
        return f"Err({self._error})"

    def __bool__(self) -> bool:
        """
        布尔转换(真值判断; Rust 无此概念, 为 Python 便利而设)

        功能: 成功为 True, 失败为 False
        返回: bool
        注意: 布尔判断会丢失错误信息, 复杂逻辑请用 is_ok()/is_err() 显式判断
        演示:
            >>> bool(Ok(42))
            True
            >>> bool(Err('e'))
            False
            >>> if Ok(42): print('成功')
            成功
        """
        return self._is_ok

    def __eq__(self, other) -> bool:
        """
        相等比较(对应 Rust 的 PartialEq)

        功能: 同为 Result 且状态、值、错误都相等时返回 True
        参数: other - 比较对象(非 Result 时返回 False)
        返回: bool
        演示:
            >>> Ok(1) == Ok(1)
            True
            >>> Ok(1) == Ok(2)
            False
            >>> Ok(1) == Err(1)
            False
        """
        if not isinstance(other, Result):
            return False
        return self._is_ok == other._is_ok and self._value == other._value and self._error == other._error

    # 支持 Python 3.10+ 模式匹配(match), 见 __match_args__
    __match_args__ = ('_is_ok', '_value', '_error')


if __name__ == '__main__':
    # 使用示例
    def 除法(a: float, b: float) -> Result[float, str]:
        if b == 0:
            return Err('除数不能为零')
        return Ok(a / b)

    # 构造与判断
    print(除法(10, 2))             # Ok(5.0)
    print(除法(10, 0))             # Err(除数不能为零)

    # 取值
    print(除法(10, 2).unwrap())    # 5.0
    print(除法(10, 0).unwrap_or(-1))  # -1

    # 转换与链式
    print(除法(10, 2).map(lambda x: x * 100))              # Ok(500.0)
    print(除法(10, 0).or_else(lambda e: Ok(0.0)))           # Ok(0.0)
    print(除法(10, 2).and_then(lambda x: 除法(x, 0)))       # Err(除数不能为零)

    # 收集
    print(Result.all([除法(10, 2), 除法(20, 4)]))           # Ok([5.0, 5.0])
    print(Result.all([除法(10, 2), 除法(20, 0)]))           # Err(除数不能为零)
    print(Result.any([除法(10, 0), 除法(30, 3)]))           # Ok(10.0)

    # 迭代(IntoIterator)
    print(list(除法(10, 2)))       # [5.0]
    print(list(除法(10, 0)))       # []

    # 模式匹配(Python 3.10+)
    结果 = 除法(1, 0)
    match 结果:
        case Result(True, 值, _):
            print(f'成功: {值}')
        case Result(False, _, 错误):
            print(f'失败: {错误}')
