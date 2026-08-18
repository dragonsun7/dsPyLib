# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2026-08-18 18:00:00'

"""
    dsPyLib/types/rust_style_result.py 的单元测试
    覆盖全部构造/判断/取值/转换/组合/收集/迭代/异步/魔法方法
"""

import asyncio
import unittest

from dsPyLib.types.rust_style_result import Result, Ok, Err


class 测试构造(unittest.TestCase):
    """构造器: 模块级函数/类方法/直接构造"""

    def test_模块级Ok函数(self):
        r = Ok(42)
        self.assertTrue(r.is_ok())
        self.assertEqual(r.ok_value(), 42)

    def test_模块级Err函数(self):
        r = Err('出错了')
        self.assertTrue(r.is_err())
        self.assertEqual(r.err_value(), '出错了')

    def test_类方法ok(self):
        r = Result.ok(42)
        self.assertTrue(r.is_ok())
        self.assertEqual(r.ok_value(), 42)

    def test_类方法err(self):
        r = Result.err('出错了')
        self.assertTrue(r.is_err())
        self.assertEqual(r.err_value(), '出错了')

    def test_直接构造成功(self):
        r = Result(value=42, error=None)
        self.assertTrue(r.is_ok())

    def test_直接构造失败(self):
        r = Result(value=None, error='出错了')
        self.assertTrue(r.is_err())

    def test_直接构造值错误同时给出时以错误为准(self):
        r = Result(value=42, error='出错了')
        self.assertTrue(r.is_err())
        self.assertEqual(r.err_value(), '出错了')


class 测试从其它类型转换(unittest.TestCase):
    """from_optional / from_try"""

    def test_from_optional有值(self):
        r = Result.from_optional(42, '值为空')
        self.assertEqual(r.ok_value(), 42)

    def test_from_optional为None(self):
        r = Result.from_optional(None, '值为空')
        self.assertEqual(r.err_value(), '值为空')

    def test_from_try成功(self):
        r = Result.from_try(lambda: int('123'), lambda e: f'转换失败: {e}')
        self.assertEqual(r.ok_value(), 123)

    def test_from_try抛异常(self):
        r = Result.from_try(lambda: int('abc'), lambda e: f'转换失败: {e}')
        self.assertTrue(r.is_err())
        self.assertIn('转换失败', r.err_value())


class 测试状态判断(unittest.TestCase):
    """is_ok / is_err / is_ok_and / is_err_and"""

    def test_is_ok(self):
        self.assertTrue(Ok(1).is_ok())
        self.assertFalse(Err('e').is_ok())

    def test_is_err(self):
        self.assertTrue(Err('e').is_err())
        self.assertFalse(Ok(1).is_err())

    def test_is_ok_and满足(self):
        self.assertTrue(Ok(10).is_ok_and(lambda v: v > 5))

    def test_is_ok_and不满足(self):
        self.assertFalse(Ok(10).is_ok_and(lambda v: v > 20))

    def test_is_ok_and失败时不调用函数(self):
        调用次数 = 0

        def fn(_v):
            nonlocal 调用次数
            调用次数 += 1
            return True

        self.assertFalse(Err('e').is_ok_and(fn))
        self.assertEqual(调用次数, 0)

    def test_is_err_and满足(self):
        self.assertTrue(Err('连接超时').is_err_and(lambda e: '超时' in str(e)))

    def test_is_err_and成功时不调用函数(self):
        调用次数 = 0

        def fn(_e):
            nonlocal 调用次数
            调用次数 += 1
            return True

        self.assertFalse(Ok(1).is_err_and(fn))
        self.assertEqual(调用次数, 0)


class 测试安全取值(unittest.TestCase):
    """ok_value / err_value"""

    def test_ok_value成功(self):
        self.assertEqual(Ok(42).ok_value(), 42)

    def test_ok_value失败返回None(self):
        self.assertIsNone(Err('e').ok_value())

    def test_err_value失败(self):
        self.assertEqual(Err('e').err_value(), 'e')

    def test_err_value成功返回None(self):
        self.assertIsNone(Ok(42).err_value())


class 测试危险取值(unittest.TestCase):
    """unwrap / unwrap_err / expect / expect_err"""

    def test_unwrap成功(self):
        self.assertEqual(Ok(42).unwrap(), 42)

    def test_unwrap失败抛异常(self):
        with self.assertRaises(RuntimeError):
            Err('出错了').unwrap()

    def test_unwrap_err失败(self):
        self.assertEqual(Err('出错了').unwrap_err(), '出错了')

    def test_unwrap_err成功抛异常(self):
        with self.assertRaises(RuntimeError):
            Ok(42).unwrap_err()

    def test_expect成功(self):
        self.assertEqual(Ok(42).expect('必须成功'), 42)

    def test_expect失败异常包含自定义信息(self):
        with self.assertRaises(RuntimeError) as cm:
            Err('连接拒绝').expect('数据库连接必须成功')
        self.assertIn('数据库连接必须成功', str(cm.exception))
        self.assertIn('连接拒绝', str(cm.exception))

    def test_expect_err失败(self):
        self.assertEqual(Err('e').expect_err('必然失败'), 'e')

    def test_expect_err成功抛异常(self):
        with self.assertRaises(RuntimeError) as cm:
            Ok(42).expect_err('必然失败')
        self.assertIn('必然失败', str(cm.exception))


class 测试兜底取值(unittest.TestCase):
    """unwrap_or / unwrap_or_else / unwrap_or_default"""

    def test_unwrap_or成功(self):
        self.assertEqual(Ok(10).unwrap_or(0), 10)

    def test_unwrap_or失败(self):
        self.assertEqual(Err('e').unwrap_or(0), 0)

    def test_unwrap_or_else失败时用错误计算(self):
        self.assertEqual(Err('e').unwrap_or_else(lambda e: len(str(e))), 1)

    def test_unwrap_or_else成功时不调用(self):
        调用次数 = 0

        def fn(_e):
            nonlocal 调用次数
            调用次数 += 1
            return -1

        self.assertEqual(Ok(10).unwrap_or_else(fn), 10)
        self.assertEqual(调用次数, 0)

    def test_unwrap_or_default成功(self):
        self.assertEqual(Ok(10).unwrap_or_default(), 10)

    def test_unwrap_or_default失败返回None(self):
        self.assertIsNone(Err('e').unwrap_or_default())


class 测试转换(unittest.TestCase):
    """map / map_or / map_or_else / map_err / flatten"""

    def test_map成功(self):
        r = Ok(10).map(lambda x: x * 2)
        self.assertEqual(r.ok_value(), 20)

    def test_map失败透传且不调用(self):
        调用次数 = 0

        def fn(x):
            nonlocal 调用次数
            调用次数 += 1
            return x * 2

        r = Err('e').map(fn)
        self.assertEqual(r.err_value(), 'e')
        self.assertEqual(调用次数, 0)

    def test_map_or成功(self):
        self.assertEqual(Ok(10).map_or(0, lambda x: x * 2), 20)

    def test_map_or失败(self):
        self.assertEqual(Err('e').map_or(0, lambda x: x * 2), 0)

    def test_map_or_else失败时用错误计算(self):
        self.assertEqual(Err('e').map_or_else(lambda e: -1, lambda x: x * 2), -1)

    def test_map_err失败转换错误类型(self):
        r = Err('出错了').map_err(lambda e: RuntimeError(e))
        self.assertIsInstance(r.err_value(), RuntimeError)

    def test_map_err成功原样(self):
        self.assertEqual(Ok(42).map_err(lambda e: RuntimeError(e)).ok_value(), 42)

    def test_flatten嵌套(self):
        r = Ok(Ok(5)).flatten()
        self.assertEqual(r.ok_value(), 5)

    def test_flatten非嵌套原样(self):
        r = Ok(5).flatten()
        self.assertEqual(r.ok_value(), 5)

    def test_flatten错误透传(self):
        self.assertEqual(Err('e').flatten().err_value(), 'e')


class 测试组合(unittest.TestCase):
    """and_then / or_else / and_ / or_"""

    def test_and_then成功继续(self):
        r = Ok(10).and_then(lambda v: Ok(v + 1))
        self.assertEqual(r.ok_value(), 11)

    def test_and_then失败透传且不调用(self):
        调用次数 = 0

        def fn(v):
            nonlocal 调用次数
            调用次数 += 1
            return Ok(v + 1)

        r = Err('e').and_then(fn)
        self.assertEqual(r.err_value(), 'e')
        self.assertEqual(调用次数, 0)

    def test_or_else成功原样(self):
        r = Ok(42).or_else(lambda e: Ok(0))
        self.assertEqual(r.ok_value(), 42)

    def test_or_else失败恢复(self):
        r = Err('e').or_else(lambda e: Ok(0))
        self.assertEqual(r.ok_value(), 0)

    def test_and_双成功返回第二个(self):
        self.assertEqual(Ok(1).and_(Ok('a')).ok_value(), 'a')

    def test_and_自身失败(self):
        self.assertEqual(Err('e1').and_(Ok('a')).err_value(), 'e1')

    def test_and_自身成功对方失败(self):
        self.assertEqual(Ok(1).and_(Err('e')).err_value(), 'e')

    def test_or_自身失败返回对方(self):
        self.assertEqual(Err('e').or_(Ok(42)).ok_value(), 42)

    def test_or_自身成功保留自身(self):
        self.assertEqual(Ok(1).or_(Ok(42)).ok_value(), 1)


class 测试检查(unittest.TestCase):
    """contains / contains_err / inspect / inspect_err"""

    def test_contains命中(self):
        self.assertTrue(Ok(42).contains(42))

    def test_contains不命中(self):
        self.assertFalse(Ok(42).contains(0))

    def test_contains失败永远False(self):
        self.assertFalse(Err('e').contains(42))

    def test_contains_err命中(self):
        self.assertTrue(Err('e').contains_err('e'))

    def test_contains_err不命中(self):
        self.assertFalse(Err('e').contains_err('x'))

    def test_contains_err成功永远False(self):
        self.assertFalse(Ok(42).contains_err('e'))

    def test_inspect成功执行副作用且返回自身(self):
        记录 = []

        r = Ok(42).inspect(lambda v: 记录.append(v))
        self.assertEqual(记录, [42])
        self.assertEqual(r.ok_value(), 42)

    def test_inspect失败不执行(self):
        记录 = []
        Err('e').inspect(lambda v: 记录.append(v))
        self.assertEqual(记录, [])

    def test_inspect_err失败执行副作用(self):
        记录 = []
        Err('e').inspect_err(lambda e: 记录.append(e))
        self.assertEqual(记录, ['e'])

    def test_inspect_err成功不执行(self):
        记录 = []
        Ok(42).inspect_err(lambda e: 记录.append(e))
        self.assertEqual(记录, [])


class 测试配对(unittest.TestCase):
    """zip / zip_with / transpose"""

    def test_zip都成功(self):
        self.assertEqual(Ok(1).zip(Ok('a')).ok_value(), (1, 'a'))

    def test_zip右失败(self):
        self.assertEqual(Ok(1).zip(Err('e')).err_value(), 'e')

    def test_zip左失败(self):
        self.assertEqual(Err('e1').zip(Ok('a')).err_value(), 'e1')

    def test_zip_with都成功(self):
        self.assertEqual(Ok(1).zip_with(Ok(2), lambda a, b: a + b).ok_value(), 3)

    def test_zip_with右失败(self):
        self.assertEqual(Ok(1).zip_with(Err('e'), lambda a, b: a + b).err_value(), 'e')

    def test_transpose有值(self):
        self.assertEqual(Ok(5).transpose().ok_value(), 5)

    def test_transpose为None(self):
        self.assertIsNone(Ok(None).transpose())

    def test_transpose错误(self):
        self.assertEqual(Err('e').transpose().err_value(), 'e')


class 测试收集(unittest.TestCase):
    """Result.all / Result.any"""

    def test_all全成功(self):
        self.assertEqual(Result.all([Ok(1), Ok(2), Ok(3)]).ok_value(), [1, 2, 3])

    def test_all遇到错误立即返回(self):
        r = Result.all([Ok(1), Err('e'), Ok(3)])
        self.assertEqual(r.err_value(), 'e')

    def test_all空列表成功(self):
        self.assertEqual(Result.all([]).ok_value(), [])

    def test_any第一个成功(self):
        self.assertEqual(Result.any([Err('a'), Ok(1), Ok(2)]).ok_value(), 1)

    def test_any全失败返回最后一个错误(self):
        self.assertEqual(Result.any([Err('a'), Err('b')]).err_value(), 'b')

    def test_any空列表抛异常(self):
        with self.assertRaises(ValueError):
            Result.any([])


class 测试过滤(unittest.TestCase):
    """filter(扩展方法)"""

    def test_filter满足条件(self):
        self.assertEqual(Ok(5).filter(lambda v: v > 3, '太小').ok_value(), 5)

    def test_filter不满足条件(self):
        self.assertEqual(Ok(1).filter(lambda v: v > 3, '太小').err_value(), '太小')

    def test_filter已失败原样返回(self):
        self.assertEqual(Err('e').filter(lambda v: v > 3, '太小').err_value(), 'e')


class 测试迭代(unittest.TestCase):
    """__iter__(对应 Rust IntoIterator)"""

    def test_成功迭代出一个值(self):
        self.assertEqual(list(Ok(5)), [5])

    def test_失败迭代为空(self):
        self.assertEqual(list(Err('e')), [])

    def test_可在for循环中使用(self):
        收集 = [v for v in Ok(10)]
        self.assertEqual(收集, [10])


class 测试异步(unittest.TestCase):
    """and_then_async(扩展方法)"""

    def test_成功执行异步函数(self):
        async def 加一(v: int) -> Result[int, str]:
            await asyncio.sleep(0.01)
            return Ok(v + 1)

        r = asyncio.run(Ok(1).and_then_async(加一))
        self.assertEqual(r.ok_value(), 2)

    def test_失败透传且不调用(self):
        调用次数 = 0

        async def fn(v):
            nonlocal 调用次数
            调用次数 += 1
            return Ok(v + 1)

        r = asyncio.run(Err('e').and_then_async(fn))
        self.assertEqual(r.err_value(), 'e')
        self.assertEqual(调用次数, 0)


class 测试魔法方法(unittest.TestCase):
    """__repr__ / __bool__ / __eq__ / 模式匹配"""

    def test_repr成功(self):
        self.assertEqual(repr(Ok(42)), 'Ok(42)')

    def test_repr失败(self):
        self.assertEqual(repr(Err('出错了')), 'Err(出错了)')

    def test_bool成功为真(self):
        self.assertTrue(bool(Ok(42)))

    def test_bool失败为假(self):
        self.assertFalse(bool(Err('e')))

    def test_eq相同(self):
        self.assertEqual(Ok(1), Ok(1))
        self.assertEqual(Err('e'), Err('e'))

    def test_eq不同(self):
        self.assertNotEqual(Ok(1), Ok(2))
        self.assertNotEqual(Ok(1), Err(1))

    def test_eq非Result对象(self):
        self.assertNotEqual(Ok(1), 1)
        self.assertNotEqual(Ok(1), None)

    def test_模式匹配成功分支(self):
        match Ok(7):
            case Result(True, 值, _):
                self.assertEqual(值, 7)
            case _:
                self.fail('应匹配成功分支')

    def test_模式匹配失败分支(self):
        match Err('e'):
            case Result(False, _, 错误):
                self.assertEqual(错误, 'e')
            case _:
                self.fail('应匹配失败分支')


if __name__ == '__main__':
    unittest.main()
